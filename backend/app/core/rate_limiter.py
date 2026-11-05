import os
import time
import threading
from typing import Dict, List, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

class InMemoryRateLimiter:
    """
    Thread-safe sliding window in-memory rate limiter.
    Provides brute-force and DoS protection for OWASP Top 10 A07 compliance.
    """
    def __init__(self):
        self._lock = threading.Lock()
        # client_ip -> list of request timestamps
        self._auth_requests: Dict[str, List[float]] = {}
        self._general_requests: Dict[str, List[float]] = {}

        # Default Limits:
        # Auth endpoints: max 60 requests per 60 seconds (prevents brute force while allowing fast test suites)
        self.AUTH_LIMIT = 60
        self.AUTH_WINDOW = 60

        # General endpoints: max 300 requests per 60 seconds
        self.GENERAL_LIMIT = 300
        self.GENERAL_WINDOW = 60

    def _clean_and_check(self, requests_dict: Dict[str, List[float]], key: str, limit: int, window: int) -> Tuple[bool, int, int]:
        now = time.time()
        with self._lock:
            timestamps = requests_dict.setdefault(key, [])
            cutoff = now - window
            valid_timestamps = [t for t in timestamps if t > cutoff]
            requests_dict[key] = valid_timestamps

            remaining = max(0, limit - len(valid_timestamps))
            if len(valid_timestamps) >= limit:
                retry_after = int(window - (now - valid_timestamps[0]))
                return False, remaining, max(1, retry_after)
            
            valid_timestamps.append(now)
            return True, remaining - 1, 0

    def check_request(self, client_ip: str, path: str) -> Tuple[bool, int, int]:
        is_auth_path = any(path.startswith(prefix) for prefix in [
            "/api/v1/auth/login",
            "/api/v1/auth/forgot-password",
            "/api/v1/auth/reset-password",
            "/api/v1/auth/register"
        ])

        if is_auth_path:
            return self._clean_and_check(self._auth_requests, client_ip, self.AUTH_LIMIT, self.AUTH_WINDOW)
        else:
            return self._clean_and_check(self._general_requests, client_ip, self.GENERAL_LIMIT, self.GENERAL_WINDOW)

    def reset(self):
        with self._lock:
            self._auth_requests.clear()
            self._general_requests.clear()

rate_limiter = InMemoryRateLimiter()

class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract client IP (handling reverse proxies like Netlify/Render)
        forwarded_for = request.headers.get("x-forwarded-for")
        client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else (request.client.host if request.client else "127.0.0.1")

        path = request.url.path

        # Exclude static/health/docs paths from rate limiting
        if path in ["/api/v1/health", "/api/v1/docs", "/api/v1/openapi.json", "/"]:
            return await call_next(request)

        allowed, remaining, retry_after = rate_limiter.check_request(client_ip, path)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Too many requests. Rate limit exceeded for {path}. Please wait {retry_after} seconds."
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(rate_limiter.AUTH_LIMIT if "auth" in path else rate_limiter.GENERAL_LIMIT),
                    "X-RateLimit-Remaining": "0"
                }
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response

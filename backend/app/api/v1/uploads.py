import os
import secrets
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from app.models.models import User
from app.api.deps import get_current_active_user

router = APIRouter()

UPLOAD_DIR = os.path.join(os.getcwd(), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # Strict 5 MB OWASP Limit

@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    # 1. Validate file extension whitelist
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension '{file_ext}' not permitted. Allowed image formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # 2. Read and enforce strict 5MB size limit
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum allowed limit of 5MB."
        )

    # 3. Generate cryptographically safe randomized filename
    random_hex = secrets.token_hex(12)
    safe_filename = f"{random_hex}{file_ext}"
    target_path = os.path.join(UPLOAD_DIR, safe_filename)

    with open(target_path, "wb") as f:
        f.write(content)

    file_url = f"/static/uploads/{safe_filename}"
    return {
        "url": file_url,
        "filename": safe_filename,
        "original_name": file.filename,
        "size_bytes": len(content),
        "uploaded_by": current_user.email
    }

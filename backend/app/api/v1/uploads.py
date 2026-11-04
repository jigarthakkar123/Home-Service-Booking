import os
import secrets
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

UPLOAD_DIR = os.path.join(os.getcwd(), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

@router.post("")
async def upload_file(file: UploadFile = File(...)):
    # Validate extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File extension '{file_ext}' not permitted. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Generate unique safe filename
    random_hex = secrets.token_hex(8)
    safe_filename = f"{random_hex}{file_ext}"
    target_path = os.path.join(UPLOAD_DIR, safe_filename)

    # Read and check size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds maximum allowed 10MB.")

    with open(target_path, "wb") as f:
        f.write(content)

    file_url = f"/static/uploads/{safe_filename}"
    return {
        "url": file_url,
        "filename": safe_filename,
        "original_name": file.filename,
        "size_bytes": len(content)
    }

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import settings
from app.core.security import verify_file_integrity
from app.services.file_service import save_upload_file

router = APIRouter()


@router.post("/upload")
async def process_cv_upload(file: UploadFile = File(...)):
    content = await file.read()

    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Plik jest za duzy")

    verify_file_integrity(content)

    file_id = await save_upload_file(content, file.filename)

    return {
        "message": "Wlot zakonczony sukcesem",
        "file_id": file_id,
        "original_name": file.filename,
    }

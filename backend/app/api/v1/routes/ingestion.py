from typing import Any, Dict

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import settings
from app.core.security import verify_file_integrity
from app.services.file_service import save_upload_file
from app.services.ocr_service import OCRService

router = APIRouter()


@router.post("/upload")
async def process_cv_upload(file: UploadFile = File(...)) -> Dict[str, Any]:
    content = await file.read()

    if file.filename is None:
        raise HTTPException(status_code=400, detail="Nazwa pliku jest wymagana")

    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Plik jest za duzy")

    mime_type = verify_file_integrity(content)

    try:
        extracted_text = await OCRService.process_document(content, mime_type)
    except Exception as e:
        extracted_text = f"Blad podczas ektrakcji tekstu: {str(e)}"

    file_id = await save_upload_file(content, file.filename)

    return {
        "message": "Wlot zakonczony sukcesem",
        "file_id": file_id,
        "mimie_type": mime_type,
        "original_name": file.filename,
        "extracted_content": extracted_text.strip() if extracted_text else "",
    }

# app/services/ingestion_service.py
from backend.app.services.cv_ingestion.file_service import save_upload_file
from backend.app.services.cv_ingestion.ocr_service import OCRService
from fastapi import HTTPException
from loguru import logger
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.core.security import verify_file_integrity
from app.models.cv import DataLakeCV


class IngestionService:
    @staticmethod
    async def process_cv_document(
        session: Session, content: bytes, filename: str, content_type: str | None = None
    ) -> dict:

        logger.info(f"Processing document pipeline started for file: {filename}")

        if len(content) > settings.MAX_FILE_SIZE:
            logger.warning(f"File reject: {filename} exceeds max size limit ")
            raise ValueError("Plik jest za duzy")

        mime_type = verify_file_integrity(content)
        logger.debug(f"File {filename} integrity verified. Detected MIME: {mime_type}")

        try:
            extracted_text = await OCRService.process_document(content, mime_type)
            extracted_text = extracted_text.strip() if extracted_text else ""
            logger.info(
                f"Text successfully extracted from {filename} ({len(extracted_text)})"
            )
        except Exception as e:
            logger.error(f"OCR engine extraction failed for {filename}: {e}")
            extracted_text = f"Blad podczas ekstrakcji tekstu {str(e)}"

        _ = await save_upload_file(content, filename)

        db_cv = crud.save_raw_cv(
            session=session, filename=filename, raw_text=extracted_text
        )

        file_id = str(db_cv.id)
        logger.info(
            f"Pipline zakoczony sukceem dla {filename}. Zapisane jako ID: {file_id}"
        )

        return {
            "message": "Zakonczone sukcesem",
            "file_id": file_id,
            "mime_type": mime_type,
            "original_name": filename,
            "extracted_content": extracted_text,
        }

    @staticmethod
    async def delete_cv_document(session: Session, file_id: str) -> None:
        db_cv = session.get(DataLakeCV, file_id)

        if not db_cv:
            logger.warning(f"Attempted to delete non-existent CV: {file_id}")
            raise HTTPException(
                status_code=404, detail="Nie znaleziono dokumentu o podanym ID"
            )

        session.delete(db_cv)
        session.commit()

        logger.info(f"Rekord Datalake o ID {file_id} zostal bezpowrotnie usuniety")

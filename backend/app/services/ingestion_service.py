from loguru import logger
from sqlmodel import Session

from app.core.config import settings
from app.core.security import verify_file_integrity
from app.models.cv import RawCV
from app.services.file_service import save_upload_file
from app.services.ocr_service import OCRService


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

        try:
            db_cv = RawCV(filename=filename, raw_text=extracted_text)
            session.add(db_cv)
            session.commit()
            session.refresh(db_cv)
            logger.info(f"Raw CV metadane zostaly zapisane do bazy z ID: {db_cv.id}")
        except Exception as e:
            logger.error(f"Zapisane RawCV do bazy danych{e}")
            session.rollback()
            raise e

        file_id = db_cv.id
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

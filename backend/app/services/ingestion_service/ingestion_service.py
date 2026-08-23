from io import BytesIO
from typing import Any, Dict
from uuid import UUID

from fastapi import Depends, HTTPException, UploadFile, status
from loguru import logger
from sqlmodel import Session, select
from starlette.datastructures import Headers as StarletteHeaders

from app.core.config import Settings
from app.core.security import verify_file_integrity
from app.models.cv_document import CVDocumentLake
from app.models.cv_raw_text import CVRawText

from .file_service import StorageService
from .ocr_service import OCRService


class IngestionService:
    def __init__(
        self,
        file_service: StorageService = Depends(),
        ocr_service: OCRService = Depends(),
    ):
        self.file_service = file_service
        self.ocr_service = ocr_service

    async def process_cv_document(
        self,
        session: Session,
        content: bytes,
        filename: str,
        content_type: str | None = None,
    ) -> dict[str, Any]:

        logger.info(f"Processing document pipeline started for file: {filename}")

        if len(content) > Settings.MAX_FILE_SIZE:
            logger.warning(f"File reject: {filename} exceeds max size limit")
            raise ValueError("Plik jest za duży.")

        mime_type = verify_file_integrity(content)
        logger.debug(f"File {filename} integrity verified. Detected MIME: {mime_type}")

        upload_file = UploadFile(
            file=BytesIO(content),
            filename=filename,
            size=len(content),
            headers=(
                StarletteHeaders({"content-type": content_type})
                if content_type
                else None
            ),
        )
        _, storage_path, file_size = await self.file_service.save_pdf_file(upload_file)

        lake_record = CVDocumentLake(
            original_filename=filename,
            storage_path=storage_path,
            file_size_bytes=file_size,
            mime_type=mime_type,
        )
        session.add(lake_record)
        session.commit()
        session.refresh(lake_record)

        metadata_json: dict[str, Any]
        try:
            raw_text = await self.ocr_service.process_document(content, mime_type)
            char_count = len(raw_text)
            word_count = len(raw_text.split()) if raw_text else 0
            page_count = 1
            metadata_json = {"is_empty": char_count == 0}

            logger.info(
                f"Text successfully extracted from {filename} ({char_count} chars)"
            )
        except Exception as e:
            logger.error(f"OCR engine extraction failed for {filename}: {e}")
            raw_text = ""
            char_count = 0
            word_count = 0
            page_count = 0
            metadata_json = {"error": str(e)}

        raw_record = CVRawText(
            cv_document_id=lake_record.id,
            raw_text=raw_text,
            character_count=char_count,
            word_count=word_count,
            page_count=page_count,
            extraction_tool="pdfplumber_tesseract_hybrid",
            metadata_json=metadata_json,
        )
        session.add(raw_record)
        session.commit()

        logger.info(
            f"Pipeline zakończony sukcesem dla {filename}. Document ID: {lake_record.id}"
        )

        return {
            "message": "Zakończone sukcesem",
            "cv_document_id": str(lake_record.id),
            "mime_type": mime_type,
            "original_name": filename,
            "character_count": char_count,
            "word_count": word_count,
        }

    async def delete_cv_document(self, session: Session, cv_document_id: UUID) -> None:
        db_cv = session.get(CVDocumentLake, cv_document_id)

        if not db_cv:
            logger.warning(f"Attempted to delete non-existent CV: {cv_document_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nie znaleziono dokumentu o podanym ID",
            )

        storage_path_to_delete = db_cv.storage_path

        raw_records = session.exec(
            select(CVRawText).where(CVRawText.cv_document_id == cv_document_id)
        ).all()
        for raw_record in raw_records:
            session.delete(raw_record)

        session.delete(db_cv)
        session.commit()

        if storage_path_to_delete:
            await self.file_service.delete_file(storage_path_to_delete)

        logger.info(
            f"Rekord Datalake o ID {cv_document_id} został usunięty wraz z plikiem fizycznym i Raw DB."
        )

    async def get_comparison_data(
        self, session: Session, file_id: UUID
    ) -> Dict[str, Any]:
        """Pobiera i scala dane pliku z Data Lake oraz wyekstrahowanego tekstu."""

        document = session.get(CVDocumentLake, file_id)
        if not document:
            raise HTTPException(
                status_code=404,
                detail=f"Nie znaleziono pliku CV o podanym ID: {file_id}",
            )

        raw_text_record = session.exec(
            select(CVRawText).where(CVRawText.cv_document_id == file_id)
        ).first()

        has_text = raw_text_record is not None
        raw_text = raw_text_record.raw_text if raw_text_record else ""

        return {
            "file_id": document.id,
            "filename": document.original_filename,
            "has_been_processed": has_text,
            "raw_data_layer": {
                "char_count": raw_text_record.character_count if raw_text_record else 0,
                "word_count": raw_text_record.word_count if raw_text_record else 0,
                "page_count": raw_text_record.page_count if raw_text_record else None,
                "extraction_tool": raw_text_record.extraction_tool
                if raw_text_record
                else None,
                "text_preview": raw_text,
            },
            "processed_data_layer": {
                "char_count": 0,
                "text_preview": "WARSTWA PRZETWORZONA ETL W TRAKCIE IMPLEMENTACJI",
            },
        }

# app/services/ingestion_service.py
from fastapi import Depends, HTTPException
from loguru import logger
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.core.security import verify_file_integrity
from app.models import DataLakeCV

from .file_service import CVFileService
from .ocr_service import OCRService


class IngestionService:
    def __init__(
        self,
        file_service: CVFileService = Depends(),
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
    ) -> dict[str, str]:
        """Orkiestruje pełny potok wejściowy (Ingestion Pipeline) dla nowego pliku CV.

        Weryfikuje limit rozmiaru pliku, sprawdza integralność binarną (Magic Bytes),
        zleca ekstrakcję tekstu do OCR Service, a następnie asynchronicznie zapisuje
        plik na dysku i rejestruje surowy tekst w bazie danych przez warstwę CRUD.

        Args:
            session (Session): Sesja bazy danych do zapisu encji CV.
            content (bytes): Surowa zawartość pliku w bajtach.
            filename (str): Oryginalna nazwa przesyłanego pliku.
            content_type (str | None): Opcjonalny nagłówek Content-Type z żądania.

        Returns:
            dict: Słownik wynikowy zawierający status operacji, ID z bazy danych,
                  zweryfikowany typ MIME oraz wyekstrahowany tekst.

        Raises:
            ValueError: Gdy rozmiar pliku przekracza limit zdefiniowany w ustawieniach.
        """

        logger.info(f"Processing document pipeline started for file: {filename}")

        if len(content) > settings.MAX_FILE_SIZE:
            logger.warning(f"File reject: {filename} exceeds max size limit ")
            raise ValueError("Plik jest za duzy")

        mime_type = verify_file_integrity(content)
        logger.debug(f"File {filename} integrity verified. Detected MIME: {mime_type}")

        try:
            extracted_text = await self.ocr_service.process_document(content, mime_type)
            extracted_text = extracted_text.strip() if extracted_text else ""
            logger.info(
                f"Text successfully extracted from {filename} ({len(extracted_text)})"
            )
        except Exception as e:
            logger.error(f"OCR engine extraction failed for {filename}: {e}")
            extracted_text = f"Blad podczas ekstrakcji tekstu {str(e)}"

        _ = await self.file_service.save_upload_file(
            content, original_filename=filename
        )

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
        """Usuwa bezpowrotnie rekord dokumentu CV z bazy danych (Data Lake).

        Wyszukuje encję po ID. Jeśli rekord istnieje, zostaje skasowany z bazy,
        a transakcja zostaje zatwierdzona (commit). W przypadku braku rekordu
        podnosi wyjątek HTTP 404.

        Args:
            session (Session): Sesja bazy danych do wykonania operacji.
            file_id (str): Identyfikator dokumentu do usunięcia.

        Raises:
            HTTPException: Z kodem statusu 404, jeśli dokument nie istnieje w bazie.
        """
        db_cv = session.get(DataLakeCV, file_id)

        if not db_cv:
            logger.warning(f"Attempted to delete non-existent CV: {file_id}")
            raise HTTPException(
                status_code=404, detail="Nie znaleziono dokumentu o podanym ID"
            )

        session.delete(db_cv)
        session.commit()

        logger.info(f"Rekord Datalake o ID {file_id} zostal bezpowrotnie usuniety")

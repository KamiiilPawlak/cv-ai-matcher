from app.core.config import settings
from app.core.security import verify_file_integrity
from app.services.file_service import save_upload_file
from app.services.ocr_service import OCRService


class IngestionService:
    @staticmethod
    async def process_cv_document(content: bytes, filename: str) -> dict:
        if len(content) > settings.MAX_FILE_SIZE:
            raise ValueError("Plik jest za duzy")

        mime_type = verify_file_integrity(content)

        try:
            extracted_text = await OCRService.process_document(content, mime_type)
            extracted_text = extracted_text.strip() if extracted_text else ""
        except Exception as e:
            extracted_text = f"Blad podczas ekstrakcji tekstu {str(e)}"

        file_id = await save_upload_file(content, filename)

        return {
            "message": "Zakonczone sukcesem",
            "file_id": file_id,
            "mime_type": mime_type,
            "original_name": filename,
            "extracted_content": extracted_text,
        }

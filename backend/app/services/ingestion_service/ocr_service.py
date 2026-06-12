import io

import pdfplumber
import pytesseract  # type: ignore
from loguru import logger
from pdf2image import convert_from_bytes
from PIL import Image, ImageFilter, ImageOps


class OCRService:
    @staticmethod
    async def process_document(content: bytes, mime_type: str) -> str:
        if mime_type == "application/pdf":
            text = OCRService._extract_digital_text(content)
            logger.info("Proba ekstrakcji tekstu cyfrowego z pliku PDF")
            if text.strip() and len(text) > 100:
                logger.info("Pomyślnie wyekstrahowano tekst cyfrowy z PDF.")
                return text
        logger.info(f"Uruchamianie procesu OCR dla typu: {mime_type}")
        return await OCRService._extract_via_ocr(content, mime_type)

    @staticmethod
    def _extract_digital_text(content: bytes) -> str:
        full_text = []
        try:
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        full_text.append(page_text)
            return "\n".join(full_text)
        except Exception as e:
            logger.error(f"Błąd podczas ekstrakcji tekstu cyfrowego: {e}")
            return ""

    @staticmethod
    async def _extract_via_ocr(content: bytes, mime_type: str) -> str:
        if mime_type == "application/pdf":
            images = convert_from_bytes(content)
        else:
            images = [Image.open(io.BytesIO(content))]

        results = []

        for img in images:
            processed = OCRService._apply_pil_filters(img)
            text = pytesseract.image_to_string(processed, lang="pol+eng")
            results.append(text)

        return "\n".join(results)

    @staticmethod
    def _apply_pil_filters(img: Image.Image) -> Image.Image:
        img = img.convert("L")
        img = ImageOps.autocontrast(img)
        img = img.filter(ImageFilter.SHARPEN)
        return img

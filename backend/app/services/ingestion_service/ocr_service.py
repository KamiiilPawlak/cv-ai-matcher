import asyncio
import io

import pdfplumber
import pytesseract  # type: ignore
from loguru import logger
from pdf2image import convert_from_bytes
from PIL import Image, ImageFilter, ImageOps


class OCRService:
    async def process_document(self, content: bytes, mime_type: str) -> str:
        """Ekstrahuje tekst z dokumentu, stosując hybrydową strategię (PDF / OCR).

        Najpierw próbuje pobrać tekst cyfrowy z PDF. Jeśli plik go nie posiada,
        jest obrazem lub tekst ma poniżej 100 znaków, uruchamia proces OCR.
        Operacja OCR jest delegowana do osobnego wątku (CPU-bound).

        Args:
            content (bytes): Surowa zawartość pliku w bajtach.
            mime_type (str): Typ MIME pliku (np. "application/pdf").

        Returns:
            str: Wyekstrahowany tekst przygotowany do potoku ETL.
        """
        if mime_type == "application/pdf":
            text = self._extract_digital_text(content)
            logger.info("Proba ekstrakcji tekstu cyfrowego z pliku PDF")
            if text.strip() and len(text) > 100:
                logger.info("Pomyślnie wyekstrahowano tekst cyfrowy z PDF.")
                return text
        logger.info(f"Uruchamianie procesu OCR dla typu: {mime_type}")
        return await asyncio.to_thread(self._extract_via_ocr, content, mime_type)

    def _extract_digital_text(self, content: bytes) -> str:
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

    def _extract_via_ocr(self, content: bytes, mime_type: str) -> str:
        if mime_type == "application/pdf":
            images = convert_from_bytes(content)
        else:
            images = [Image.open(io.BytesIO(content))]

        results = []

        for img in images:
            processed = self._apply_pil_filters(img)
            text = pytesseract.image_to_string(processed, lang="pol+eng")
            results.append(text)

        return "\n".join(results)

    def _apply_pil_filters(self, img: Image.Image) -> Image.Image:

        img = img.convert("L")
        img = ImageOps.autocontrast(img)
        img = img.filter(ImageFilter.SHARPEN)
        return img

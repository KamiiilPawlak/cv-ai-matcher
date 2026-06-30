import regex  # type: ignore[import-untyped]
from loguru import logger

from app.schema.ingestion_dto import ExtractedMetadata


class CVEnricher:
    def __init__(self) -> None:

        self._email_regex = regex.compile(
            r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", regex.IGNORECASE
        )
        self._phone_regex = regex.compile(r"(?:\+)?\b(\d{9,12})\b")

    def extract_metadata(self, normalized_text: str) -> ExtractedMetadata:
        if not normalized_text:
            logger.warning("Otrzymano pusty tekst do ekstrakcji metadanych.")
            return ExtractedMetadata(email=None, phone=None)

        email_match = self._email_regex.search(normalized_text)
        phone_match = self._phone_regex.search(normalized_text)

        email = None
        if email_match:
            email = email_match.group(0).strip().lower()
            logger.info("Heurystyka Enrichment: Pomyślnie wykryto e-mail.")
        else:
            logger.info("Heurystyka Enrichment: Nie wykryto adresu e-mail.")

        phone = None
        if phone_match:
            phone = phone_match.group(0).strip()
            logger.info("Heurystyka Enrichment: Pomyślnie wykryto numer telefonu.")
        else:
            logger.info("Heurystyka Enrichment: Nie wykryto numeru telefonu.")

        return ExtractedMetadata(email=email, phone=phone)

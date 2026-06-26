from typing import Optional

import regex  # type: ignore[import-untyped]
from loguru import logger

from app.schema.ingestion_dto import ExtractedMetadata


class CVEnricher:
    EMAIL_REGEX = regex.compile(
        r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", regex.IGNORECASE
    )

    PHONE_REGEX = regex.compile(r"(?:\+)?\b(\d{9,12})\b")

    @classmethod
    def extract_metadata(cls, normalized_text: str) -> ExtractedMetadata:
        if not normalized_text:
            logger.warning("Otrzymano pusty tekst do ekstrakcji metadanych.")
            return ExtractedMetadata(email=None, phone=None)

        email_match = cls.EMAIL_REGEX.search(normalized_text)
        phone_match = cls.PHONE_REGEX.search(normalized_text)

        email: Optional[str] = None
        phone: Optional[str] = None

        if email_match:
            email = email_match.group(0).strip().lower()
            logger.info("Heurystyka Enrichment: Pomyślnie wykryto e-mail.")
        else:
            logger.info("Heurystyka Enrichment: Nie wykryto adresu e-mail.")

        if phone_match:
            phone = phone_match.group(0).strip()
            logger.info("Heurystyka Enrichment: Pomyślnie wykryto numer telefonu.")
        else:
            logger.info("Heurystyka Enrichment: Nie wykryto numeru telefonu.")

        return ExtractedMetadata(email=email, phone=phone)

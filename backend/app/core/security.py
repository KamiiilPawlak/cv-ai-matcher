import magic
from loguru import logger

from app.core.config import settings


def verify_file_integrity(content: bytes) -> str:

    if not content:
        logger.error("Plik jest pusty")
        raise ValueError("Przesłany plik jest pusty ")

    mime_type: str = str(magic.from_buffer(content[:2024], mime=True))

    if mime_type not in settings.ALLOWED_MIME_TYPES:
        logger.error(
            f"Nieautoryzyowany format ppliku: {mime_type}"
            f"Dozwolone typy: {settings.ALLOWED_MIME_TYPES}"
        )
        raise ValueError(
            f"Niedozwolony format {mime_type}. Akceptowane są wyłącznie pliki PDF oraz obraz"
        )

    logger.info(f"Plik zerwyfikowany pomyslenie. Wykryty typ MIME {mime_type} ")
    return mime_type

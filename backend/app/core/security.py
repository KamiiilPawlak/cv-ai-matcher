import magic
from fastapi import HTTPException, status
from loguru import logger

from app.core.config import settings


def verify_file_integrity(content: bytes) -> str:

    if not content:
        logger.error("Plik jest pusty")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Przeslany plik jest pusty"
        )

    mime_type = str(magic.from_buffer(content[:2024], mime=True))

    if mime_type not in settings.ALLOWED_MINE_TYPES:
        logger.error(
            f"Niieautoryzyowany format ppliku: {mime_type}"
            f"Dozwolone typy: {settings.ALLOWED_MINE_TYPES}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Niedozwolony format {mime_type} akceptuje tylko PDF i obrazy",
        )

    logger.info(f"Plik zerwyfikowany pomyslenie. Wykryty typ MIME {mime_type} ")
    return mime_type

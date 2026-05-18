import magic  # type: ignore
from fastapi import HTTPException, status

from app.core.config import settings


def verify_file_integrity(content: bytes) -> str:
    mime_type = str(magic.from_buffer(content[:2024], mime=True))

    if mime_type not in settings.ALLOWED_MINE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Niedozwolony format {mime_type} akceptuje tylko PDF i obrazy",
        )
    return mime_type

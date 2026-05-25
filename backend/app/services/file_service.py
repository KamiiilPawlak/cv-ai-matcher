import uuid

import aiofiles
from loguru import logger

from app.core.config import settings


async def save_upload_file(content: bytes, original_filename: str) -> str:
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    ext = original_filename.split(".")[-1]
    safe_name = f"{uuid.uuid4()}.{ext}"
    file_path = settings.UPLOAD_DIR / safe_name
    logger.info(f"Saving file: {original_filename} -> {safe_name}")

    try:
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        return safe_name
    except Exception as e:
        logger.error(f"Failed to save file {original_filename}: {e}")
        raise e

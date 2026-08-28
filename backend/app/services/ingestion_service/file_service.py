from pathlib import Path
from typing import cast
from uuid import uuid4

import aiofiles
from fastapi import UploadFile
from loguru import logger

from app.core.config import STORAGE_DIR
from app.services.ingestion_service.storage_path_provider import (
    DateBasedPathProvider,
    StoragePathProvider,
)


class StorageService:
    def __init__(self, *, path_provider: StoragePathProvider | None = None) -> None:

        self._path_provider = path_provider or DateBasedPathProvider(STORAGE_DIR)

    async def save_pdf_file(self, file: UploadFile) -> tuple[str, str, int]:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise ValueError("Niedozwolone rozszerzenie pliku. Wymagany format to PDF.")

        content = await file.read()
        file_size = len(content)

        if file_size == 0:
            raise ValueError("Przesłany plik jest pusty.")

        target_dir = self._path_provider.get_target_dir()

        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid4()}{file_extension}"
        destination_path = target_dir / unique_filename

        try:
            destination_path.write_bytes(content)
            logger.info(f"Zapisano plik PDF na dysku: {destination_path}")
        except Exception as err:
            logger.error(f"Błąd zapisu pliku na dysku: {err}")
            raise ValueError("Wystąpił błąd podczas zapisu pliku na dysku serwera.")

        return file.filename, str(destination_path), file_size

    async def delete_file(self, file_path: str | Path) -> None:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            logger.info(f"Plik fizyczny został usunięty z dysku: {path}")
        else:
            logger.warning(f"Próbowano usunąć plik, ale nie istnieje na dysku: {path}")

    async def read_file(self, file_path: str) -> bytes:
        async with aiofiles.open(file_path, "rb") as file:
            return cast(bytes, await file.read())

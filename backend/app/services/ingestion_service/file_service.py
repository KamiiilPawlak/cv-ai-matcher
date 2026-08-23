from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from loguru import logger

BASE_DIR = Path(__file__).resolve().parents[3]
STORAGE_DIR = BASE_DIR / "storage" / "cv_uploads"


class StorageService:
    def __init__(self, target_dir: Path = STORAGE_DIR) -> None:
        self.target_dir = target_dir
        self.target_dir.mkdir(parents=True, exist_ok=True)

    async def save_pdf_file(self, file: UploadFile) -> tuple[str, str, int]:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Niedozwolone rozszerzenie pliku. Wymagany format to PDF.",
            )

        content = await file.read()
        file_size = len(content)

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Przesłany plik jest pusty.",
            )

        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid4()}{file_extension}"
        destination_path = self.target_dir / unique_filename

        try:
            destination_path.write_bytes(content)
            logger.info(f"Zapisano plik PDF na dysku: {destination_path}")
        except Exception as err:
            logger.error(f"Błąd zapisu pliku na dysku: {err}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Wystąpił błąd podczas zapisu pliku na dysku serwera.",
            )

        return file.filename, str(destination_path), file_size

    async def delete_file(self, file_path: str | Path) -> None:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            logger.info(f"Plik fizyczny został usunięty z dysku: {path}")
        else:
            logger.warning(f"Próbowano usunąć plik, ale nie istnieje na dysku: {path}")

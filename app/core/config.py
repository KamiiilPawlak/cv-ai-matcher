from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"

    MAX_FILE_SIZE: int = 5 * 1024 * 1024
    ALLOWED_MINE_TYPES: list[str] = ["application/pdf", "image/png", "image/jpeg"]

    TESSERACT_CMD: str = r"C:\\Program Files\\Tesseract-OCR"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()

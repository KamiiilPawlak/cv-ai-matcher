from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"

    # file and security
    MAX_FILE_SIZE: int = 5 * 1024 * 1024
    ALLOWED_MIME_TYPES: list[str] = ["application/pdf", "image/png", "image/jpeg"]

    # OCR Config
    TESSERACT_CMD: str = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    OCR_LANGAGUES: str = "pol+eng"

    # LLM Config
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL_NAME: str = "qwen2.5:3b"
    OLLAMA_TIMEOUT: float = 90.0

    # Database
    DATABASE_URL: str = Field(default=...)

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()

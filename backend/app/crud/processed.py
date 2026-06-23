from typing import Optional
from uuid import UUID

from loguru import logger
from sqlmodel import Session, select

from app.models.cv import ProcessedCV


def save_processed_cv(
    session: Session, file_id: UUID, normalized_text: str, email: str | None = None,phone: str | None = None
) -> ProcessedCV:
    file_id_str = str(file_id)
    try:
        existing = session.exec(
            select(ProcessedCV).where(ProcessedCV.file_id == file_id)
        ).first()

        if existing:
            existing.normalized_text = normalized_text
            db_processed = existing
            logger.info(
                f"Zaktualizowano istniejący rekord ProcessedCV dla file_id: {file_id_str}"
            )
        else:
            db_processed = ProcessedCV(file_id=file_id, normalized_text=normalized_text)
            session.add(db_processed)
            logger.info(f"Utworzono nowy rekord ProcessedCV dla file_id: {file_id_str}")

        session.commit()
        session.refresh(db_processed)
        return db_processed

    except Exception as e:
        logger.error(f"Database write error (Processed CV) dla file_id: {file_id_str}")
        session.rollback()
        raise e


def get_processed_cv(session: Session, file_id: UUID) -> Optional[ProcessedCV]:
    return session.exec(
        select(ProcessedCV).where(ProcessedCV.file_id == file_id)
    ).first()
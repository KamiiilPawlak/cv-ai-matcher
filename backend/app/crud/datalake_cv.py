from uuid import UUID

from loguru import logger
from sqlmodel import Session, select

from app.models.cv import DataLakeCV, ProcessedCV


def save_raw_cv(session: Session, filename: str, raw_text: str) -> DataLakeCV:
    """Saves the raw, extracted text from the resume to the Data Lake layer."""
    try:
        db_cv = DataLakeCV(filename=filename, raw_text=raw_text)
        session.add(db_cv)
        session.commit()
        session.refresh(db_cv)
        logger.info(f"Raw CV metadata saved to DataLake with ID: {db_cv.id}")
        return db_cv

    except Exception as e:
        logger.error("Database write error (Data Lake CV) ")
        session.rollback()
        raise e


def get_raw_cv(session: Session, cv_id: UUID) -> DataLakeCV | None:
    """Pobiera rekord CV z warstwy Data Lake CV"""
    return session.get(DataLakeCV, cv_id)


def delete_raw_cv(session: Session, db_cv: DataLakeCV) -> None:
    """"""
    session.delete(db_cv)
    session.commit()
    logger.info(f"Rekord Datalake o ID {db_cv.id} zostal bezpowrotnie usuniety")


def save_processed_cv(
    session: Session, file_id: UUID, normalized_text: str
) -> ProcessedCV:
    """Zapisuje lub aktualizuje oczyszczone i znormalizowane CV w bazie danych."""
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

from uuid import UUID

from loguru import logger
from sqlmodel import Session

from app.models.cv import DataLakeCV


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


def get_raw_cv(session: Session, file_id: UUID) -> DataLakeCV | None:
    """Pobiera rekord CV z warstwy Data Lake CV"""
    return session.get(DataLakeCV, file_id)


def delete_raw_cv(session: Session, db_cv: DataLakeCV) -> None:
    """"""
    session.delete(db_cv)
    session.commit()
    logger.info(f"Rekord Datalake o ID {db_cv.id} zostal bezpowrotnie usuniety")

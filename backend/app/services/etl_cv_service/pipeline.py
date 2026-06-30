# app/services/etl_cv_service/pipeline.py

from typing import Callable
from uuid import UUID

from fastapi.concurrency import run_in_threadpool
from loguru import logger
from sqlmodel import Session

from app.crud.datalake_cv import get_raw_cv
from app.crud.processed import save_processed_cv
from app.models.cv import ProcessedCV
from app.services.etl_cv_service.transformers.cleaning import clean_ocr_text
from app.services.etl_cv_service.transformers.enrichment import CVEnricher
from app.services.etl_cv_service.transformers.normalization import CVTextNormalizer


class CvEtlPipeline:
    def __init__(
        self,
        cleaner: Callable[[str], str] = clean_ocr_text,
        normalizer: CVTextNormalizer | None = None,
        enricher: CVEnricher | None = None,
    ) -> None:
        self.cleaner = cleaner
        self.normalizer = normalizer or CVTextNormalizer()
        self.enricher = enricher or CVEnricher()

    async def execute(self, session: Session, file_id: UUID) -> ProcessedCV:
        """Główny orkiestrator ETL dla CV pobieranego z Data Lake (Raw data db PostgresSQL)"""

        logger.info(f"[ETL Pipeline] Rozpoczęto przetwarzanie dla CV ID: {file_id}")

        db_cv = await run_in_threadpool(get_raw_cv, session, file_id)

        if not db_cv:
            logger.warning(
                f"[ETL Pipeline] Nie znaleziono CV o ID {file_id} w Data Lake"
            )
            raise ValueError(f"Nie znaleziono CV o ID {file_id} w bazie danych")

        raw_text = db_cv.raw_text

        cleaned_text = await run_in_threadpool(self.cleaner, raw_text)
        normalized_text = await run_in_threadpool(
            self.normalizer.normalize_text, cleaned_text
        )
        metadata_dto = await run_in_threadpool(
            self.enricher.extract_metadata, normalized_text
        )
        processed_cv_record = await run_in_threadpool(
            save_processed_cv,
            session,
            file_id,
            normalized_text,
            email=metadata_dto.email,
            phone=metadata_dto.phone,
        )

        logger.success(
            f"[ETL Pipeline] Przetwarzanie CV ID {file_id} zakończone sukcesem. "
            f"Zapisano w ProcessedCV z ID: {processed_cv_record.id}"
        )

        return processed_cv_record

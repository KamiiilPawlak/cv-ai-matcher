# app/services/etl_cv_service/pipeline.py

import email
from uuid import UUID

from loguru import logger
from sqlmodel import Session

from app.crud.datalake_cv import get_raw_cv
from app.crud.processed import save_processed_cv
from app.models.cv import ProcessedCV
from app.services.etl_cv_service.transformers.cleaning import clean_ocr_text
from app.services.etl_cv_service.transformers.normalization import CVTextNormalizer
from app.services.etl_cv_service.transformers.enrichment import CVEnricher

class CvEtlPipeline:
    def __init__(self):
        self.cleaner = clean_ocr_text
        self.normalizer = CVTextNormalizer()
        self.enricher = CVEnricher()

    async def execute(self, session: Session, file_id: UUID) -> ProcessedCV:
        """Główny orkiestrator ETL dla CV pobieranego z Data Lake (Raw data db PostgresSQL)"""

        logger.info(f"[ETL Pipeline] Rozpoczęto przetwarzanie dla CV ID: {file_id}")

        db_cv = get_raw_cv(session, file_id)

        if not db_cv:
            logger.warning(
                f"[ETL Pipeline] Nie znaleziono CV o ID {file_id} w Data Lake"
            )
            raise ValueError(f"Nie znaleziono CV o ID {file_id} w bazie danych")

        raw_text = db_cv.raw_text

        cleaned_text = self.cleaner(raw_text)

        normalized_text = self.normalizer.normalize_text(cleaned_text)
    
        metadata_dto = self.enricher.extract_metadata(normalized_text)

      
        processed_cv_record = save_processed_cv(
            session,
            file_id,
            normalized_text,
            email=metadata_dto.email,
            phone=metadata_dto.phone
        )

        logger.success(
            f"[ETL Pipeline] Przetwarzanie CV ID {file_id} zakończone sukcesem. "
            f"Zapisano w ProcessedCV z ID: {processed_cv_record.id}"
        )

        return processed_cv_record

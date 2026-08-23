from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlmodel import Session

from app.db.database import get_session
from app.schema.ingestion_dto import IngestionResponse
from app.services.ingestion_service.ingestion_service import IngestionService

router = APIRouter(prefix="/cv", tags=["CV Ingestion"])


@router.post(
    "/upload", response_model=IngestionResponse, status_code=status.HTTP_201_CREATED
)
async def process_cv_upload(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    ingestion_service: IngestionService = Depends(),
) -> Dict[str, Any]:
    content = await file.read()

    return await ingestion_service.process_cv_document(
        session=session,
        content=content,
        filename=file.filename or "file.pdf",
        content_type=file.content_type,
    )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cv(
    file_id: UUID,
    session: Session = Depends(get_session),
    ingestion_service: IngestionService = Depends(),
) -> None:
    # Router tylko deleguje zadanie usunięcia do serwisu
    await ingestion_service.delete_cv_document(session, file_id)


@router.get("/{file_id}/compare")
async def compare_cv_data(
    file_id: UUID,
    session: Session = Depends(get_session),
    ingestion_service: IngestionService = Depends(),
) -> Dict[str, Any]:

    return await ingestion_service.get_comparison_data(session, file_id)

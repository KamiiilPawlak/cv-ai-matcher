from calendar import monthrange
from datetime import date
from typing import Tuple

from app.services.etl_cv_service.heuristic.domain.models import (
    DateRange,
)


def convert_extracted_range_to_dates(extracted: DateRange) -> Tuple[date, date] | None:
    if not extracted.start_date:
        return None

    start_dt = (
        extracted.start_date
        if isinstance(extracted.start_date, date)
        else date.fromisoformat(extracted.start_date)
    )

    if getattr(extracted, "is_current", False) or not extracted.end_date:
        end_dt = date.today()
    else:
        temp_end = (
            extracted.end_date
            if isinstance(extracted.end_date, date)
            else date.fromisoformat(extracted.end_date)
        )
        last_day = monthrange(temp_end.year, temp_end.month)[1]
        end_dt = date(temp_end.year, temp_end.month, last_day)

    return (start_dt, end_dt)

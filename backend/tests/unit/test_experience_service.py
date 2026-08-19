from datetime import date
from typing import cast

from app.services.etl_cv_service.heuristic.domain.experience_service import (
    convert_extracted_range_to_dates,
)
from app.services.etl_cv_service.heuristic.domain.models import (
    DateRange as ExtractedDateRange,
)


def test_convert_standard_past_date_range() -> None:
    """Sprawdza konwersję zakończonego okresu pracy (ustawienie ostatniego dnia miesiąca)."""
    extracted = ExtractedDateRange(
        start_date=date(2020, 1, 1), end_date=date(2022, 5, 1)
    )

    result = convert_extracted_range_to_dates(extracted)

    assert result is not None
    assert result[0] == date(2020, 1, 1)

    assert result[1] == date(2022, 5, 31)


def test_convert_current_job_range() -> None:
    """Sprawdza, czy praca z is_current=True dostaje jako end_date dzisiejszą datę."""
    extracted = ExtractedDateRange(
        start_date=date(2023, 3, 1), end_date=cast(date, None)
    )

    result = convert_extracted_range_to_dates(extracted)

    assert result is not None
    assert result[0] == date(2023, 3, 1)
    assert result[1] == date.today()


def test_convert_invalid_range_missing_start() -> None:
    """Sprawdza zachowanie dla błędnych/pustych obiektów."""
    extracted = ExtractedDateRange(
        start_date=cast(date, None), end_date=date(2022, 1, 1)
    )

    assert convert_extracted_range_to_dates(extracted) is None

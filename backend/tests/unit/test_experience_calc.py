from datetime import date

from app.services.etl_cv_service.heuristic.domain.experience_calc import (
    calculate_experience_metrics,
    merge_overlapping_intervals,
)
from app.services.etl_cv_service.heuristic.domain.models import DateRange


def test_merge_overlapping_intervals() -> None:
    intervals = [
        DateRange(start_date=date(2020, 1, 1), end_date=date(2022, 1, 1)),
        DateRange(start_date=date(2021, 1, 1), end_date=date(2023, 1, 1)),
    ]
    merged = merge_overlapping_intervals(intervals)

    assert len(merged) == 1
    assert merged[0].start_date == date(2020, 1, 1)
    assert merged[0].end_date == date(2023, 1, 1)


def test_calculate_experience_metrics_with_overlap() -> None:
    raw_intervals = [
        (date(2020, 1, 1), date(2022, 1, 1)),
        (date(2021, 1, 1), date(2023, 1, 1)),
    ]

    metrics = calculate_experience_metrics(raw_intervals)

    assert metrics.job_count == 2
    assert metrics.min_date == date(2020, 1, 1)
    assert metrics.max_date == date(2023, 1, 1)
    assert metrics.total_years == 3.0


def test_calculate_experience_metrics_empty() -> None:
    metrics = calculate_experience_metrics([])
    assert metrics.job_count == 0
    assert metrics.total_days == 0
    assert metrics.min_date is None

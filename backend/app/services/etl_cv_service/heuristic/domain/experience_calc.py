from datetime import date
from typing import List, Tuple

from app.services.etl_cv_service.heuristic.domain.models import (
    DateRange,
    ExperienceMetrics,
)


def merge_overlapping_intervals(intervals: List[DateRange]) -> List[DateRange]:
    """Algorytm O(N log N) scalający nakładające się okresy zatrudnienia (np. 2 etaty naraz)."""
    valid_intervals = [
        interval
        for interval in intervals
        if interval.start_date is not None and interval.end_date is not None
    ]
    if not valid_intervals:
        return []

    sorted_intervals = sorted(valid_intervals, key=lambda x: x.start_date or date.min)
    merged: List[DateRange] = [sorted_intervals[0]]

    for current in sorted_intervals[1:]:
        last = merged[-1]
        current_start = current.start_date
        current_end = current.end_date
        last_end = last.end_date

        if (
            current_start is not None
            and current_end is not None
            and last_end is not None
            and current_start <= last_end
        ):
            new_end = max(last_end, current_end)
            merged[-1] = DateRange(start_date=last.start_date, end_date=new_end)
        else:
            merged.append(current)

    return merged


def calculate_experience_metrics(
    raw_intervals: List[Tuple[date, date]],
) -> ExperienceMetrics:
    """Wylicza metryki stażu pracy: liczbę dni, miesięcy, lat oraz skrajne daty."""
    if not raw_intervals:
        return ExperienceMetrics(
            total_days=0,
            total_months=0,
            total_years=0.0,
            min_date=None,
            max_date=None,
            mean_job_duration_months=0.0,
            job_count=0,
        )

    valid_intervals: List[DateRange] = []
    for start, end in raw_intervals:
        if start <= end:
            valid_intervals.append(DateRange(start_date=start, end_date=end))

    if not valid_intervals:
        return ExperienceMetrics(
            total_days=0,
            total_months=0,
            total_years=0.0,
            min_date=None,
            max_date=None,
            mean_job_duration_months=0.0,
            job_count=0,
        )

    start_dates: List[date] = [
        interval.start_date
        for interval in valid_intervals
        if interval.start_date is not None
    ]
    end_dates: List[date] = [
        interval.end_date
        for interval in valid_intervals
        if interval.end_date is not None
    ]
    min_date = min(start_dates)
    max_date = max(end_dates)
    job_count = len(valid_intervals)

    merged = merge_overlapping_intervals(valid_intervals)
    total_days = 0
    for item in merged:
        if item.start_date is not None and item.end_date is not None:
            total_days += (item.end_date - item.start_date).days

    total_months = int(round(total_days / 30.44))
    total_years = round(total_days / 365.25, 1)

    mean_duration = round(total_months / job_count, 1) if job_count > 0 else 0.0

    return ExperienceMetrics(
        total_days=total_days,
        total_months=total_months,
        total_years=total_years,
        min_date=min_date,
        max_date=max_date,
        mean_job_duration_months=mean_duration,
        job_count=job_count,
    )

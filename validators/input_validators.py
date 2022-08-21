from datetime import datetime


def is_valid_date_range(start_date: datetime, end_date: datetime) -> bool:
    return start_date < end_date

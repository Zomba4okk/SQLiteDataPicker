import argparse
from datetime import datetime


def date_serializer(value: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Not a valid date: {value}. You have to pass date in YYYY-MM-DD format."
        )

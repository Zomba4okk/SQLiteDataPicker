import argparse
import logging
import os
from datetime import datetime
from typing import Optional

from db.meta import Session
from services.customer_payments_data_service import CustomerPaymentsDataService
from validators.argpargse_serializers import date_serializer
from validators.input_validators import is_valid_date_range

logging.basicConfig(format="%(filename)s: %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main(start_date: Optional[datetime], end_date: Optional[datetime], path: str):
    if (
        start_date and end_date
        and not is_valid_date_range(start_date=start_date, end_date=end_date)
    ):
        logger.error("Invalid date range.")
        return

    with Session() as session:
        CustomerPaymentsDataService(session).load_customers_payment_data_to_json(
            start_date=start_date,
            end_date=end_date,
            path=path
        )


def _get_input_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Get customer payments and write them to a JSON file."
    )
    parser.add_argument(
        "-s", "--start",
        help="Get payments on or after this date (YYYY-MM-DD)",
        type=date_serializer
    )
    parser.add_argument(
        "-e", "--end",
        help="Get payments before this date (YYYY-MM-DD)",
        type=date_serializer
    )
    parser.add_argument(
        "-p", "--path",
        help="The path to the directory where output file will be saved. "
             "By default the file will be saved to the 'output' directory "
             "in the script folder.",
        default=os.path.join(os.getcwd(), "output")
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = _get_input_args()

    main(start_date=args.start, end_date=args.end, path=args.path)

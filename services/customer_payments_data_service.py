import os
from datetime import datetime
from typing import Generator, List, Optional

import simplejson
from sqlalchemy import desc
from sqlalchemy.engine import Row
from sqlalchemy.orm import contains_eager, Session
from sqlalchemy.sql import func
from sqlalchemy.sql.selectable import Subquery

from db.models import Invoice, Customer


class CustomerPaymentsDataService:
    def __init__(self, session: Session):
        self._session = session

    def load_customers_payment_data_to_json(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        path: str = None
    ) -> None:
        data = self._get_data_generator(start_date, end_date)
        file_path = self._get_file_path(path)

        os.makedirs(path, exist_ok=True)
        with open(file_path, "w") as file:
            simplejson.dump(data, file, iterable_as_array=True, indent=True)

    def _get_data_generator(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        batch_size: int = 10000
    ) -> Generator[dict, None, None]:
        offset = 0

        while True:
            customers_data = self._get_customers_data(
                start_date=start_date,
                end_date=end_date,
                batch_size=batch_size,
                offset=offset
            )

            if not customers_data:
                return

            for data_row in customers_data:
                yield self._data_row_to_dict(data_row)

            offset += batch_size

    def _get_customers_data(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        batch_size: int,
        offset: int
    ) -> List[Row]:
        customers_subquery = self._get_customers_subquery(
            start_date=start_date,
            end_date=end_date,
            batch_size=batch_size,
            offset=offset
        )

        queryset = (
            self._session.query(Customer)
            .join(customers_subquery, customers_subquery.c.CustomerId == Customer.CustomerId)
            .join(Customer.invoice_collection)
            .options(contains_eager(Customer.invoice_collection))
            .with_entities(
                Customer,
                customers_subquery.c.total_paid
            )
        )

        if start_date:
            queryset = queryset.where(Invoice.InvoiceDate >= start_date)
        if end_date:
            queryset = queryset.where(Invoice.InvoiceDate < end_date)

        return queryset.all()

    def _get_customers_subquery(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        batch_size: int,
        offset: int
    ) -> Subquery:
        base_queryset = (
            self._session.query(Customer)
            .join(Customer.invoice_collection)
            .group_by(Customer.CustomerId)
            .with_entities(
                Customer.CustomerId,
                func.sum(Invoice.Total).label("total_paid")
            )
            .order_by(desc("total_paid"))
        )

        if start_date:
            base_queryset = base_queryset.where(Invoice.InvoiceDate >= start_date)
        if end_date:
            base_queryset = base_queryset.where(Invoice.InvoiceDate < end_date)

        return (
            base_queryset
            .limit(batch_size).offset(offset)
            .subquery()
        )

    @staticmethod
    def _data_row_to_dict(customer: Row) -> dict:
        return {
            "customer_id": customer.Customer.CustomerId,
            "first_name": customer.Customer.FirstName,
            "last_name": customer.Customer.LastName,
            "total_paid": str(customer.total_paid),
            "individual_payments": [
                {
                    "date": str(invoice.InvoiceDate),
                    "amount": str(invoice.Total)

                } for invoice in customer.Customer.invoice_collection
            ]
        }

    def _get_file_path(self, path: str, copy: int = 0) -> str:
        file_name = f"customer_payments_data_{datetime.utcnow().strftime('%Y-%m-%d_%H-%M')}"
        if copy:
            file_name += f"({copy})"
        file_name += ".json"

        file_path = os.path.join(path, file_name)

        if os.path.exists(file_path):
            return self._get_file_path(path, copy + 1)

        return file_path

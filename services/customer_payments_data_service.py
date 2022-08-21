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
        """Creates JSON file with customers with the list of their invoices.

        If customer does not have invoices under the conditions passed, it will not be
         added to the result selection.

        :param start_date: Select only invoices billed at <start_date> or later.
                            If None, parameter will be ignored without adding a filter.
        :param end_date: Select only invoices billed earlier than <end_date>.
                          If None, parameter will be ignored without adding a filter.
        :param path: Path to directory where output file will be saved
        :return: None
        """
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
        """Returns the results of _get_customers_data method as a generator.

        The method is created by optimization reasons.
        It allows to avoid memory overflow and db connection timeouts by retrieving
         data sample sequentially in batches.
        Each batch is retrieved by separate request and fully loaded into memory.

        :param start_date: start_date parameter for a _get_customers_data method.
                            Passing directly.
        :param end_date: end_date parameter for a _get_customers_data method.
                          Passing directly.
        :param batch_size: number of instances in one batch.
        :return: Generator returning SQLAlchemy Row instances that contains two fields:
                   Customer - instance of Customer model with appropriate data
                   total_paid - Decimal value. Sum of selected invoices
        """
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
        """Retrieves customers with the list of their invoices.

        If customer does not have invoices under the conditions passed, it will not be
         added to the result selection.

        :param start_date: Select only invoices billed at <start_date> or later.
                            If None, parameter will be ignored without adding a filter.
        :param end_date: Select only invoices billed earlier than <end_date>.
                          If None, parameter will be ignored without adding a filter.
        :param batch_size: SQL limit param
        :param offset: SQL offset param
        :return: List of SQLAlchemy Row instances that contains two fields:
                           Customer - instance of Customer model with appropriate data
                           total_paid - Decimal value. Sum of selected invoices
        """

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
        """Generate subquery that calculates total amount of invoices for each customer.

        :param start_date: Select only invoices billed at <start_date> or later.
                            If None, parameter will be ignored without adding a filter.
        :param end_date: Select only invoices billed earlier than <end_date> .
                          If None, parameter will be ignored without adding a filter.
        :param batch_size: SQL limit param
        :param offset: SQL offset param
        :return: Subquery containing two fields:
                   CustomerId - id of a customer
                   total_paid - total amount of invoices for appropriate customer
        """

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
    def _data_row_to_dict(data_row: Row) -> dict:
        """Map data row of specific format to JSON serializable dictionary.
    
        :param data_row: SQLAlchemy Row instance that contains two fields:
                           Customer - instance of Customer model with appropriate data
                           total_paid - Decimal value. Sum of selected invoices
        :return: JSON serializable dictionary
        """

        return {
            "customer_id": data_row.Customer.CustomerId,
            "first_name": data_row.Customer.FirstName,
            "last_name": data_row.Customer.LastName,
            "total_paid": str(data_row.total_paid),
            "individual_payments": [
                {
                    "date": str(invoice.InvoiceDate),
                    "amount": str(invoice.Total)

                } for invoice in data_row.Customer.invoice_collection
            ]
        }

    def _get_file_path(self, path: str, copy: int = 0) -> str:
        """Generate file name for output file and join it to provided path.

        The file name will be "customer_payments_data_<YYYY-MM-DD_HH-MM>.json"
        where the value in triangle brackets is current UTC date and time in appropriate
        format.

        If file with the same name already exists the method will add "(1)" to file name.
        If such a file also exists too, it will increment number in brackets until free
        name will be found.

        :param path: Path to directory where output file will be saved
        :param copy: Number, that should be added to file name. 0 value means
                      nothing will be added.
        :return: Path to output file
        """

        file_name = f"customer_payments_data_{datetime.utcnow().strftime('%Y-%m-%d_%H-%M')}"
        if copy:
            file_name += f"({copy})"
        file_name += ".json"

        file_path = os.path.join(path, file_name)

        if os.path.exists(file_path):
            return self._get_file_path(path, copy + 1)

        return file_path

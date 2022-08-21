from datetime import datetime
from decimal import Decimal
from typing import List

import pytest
from sqlalchemy.orm import Session

from services.customer_payments_data_service import CustomerPaymentsDataService
from tests.factories import CustomerFactory, InvoiceFactory


class TestCustomerPaymentsDataService:
    @pytest.fixture(autouse=True)
    def setup_data(self) -> None:
        self.customer_1 = CustomerFactory()
        self.customer_2 = CustomerFactory()
        self.customer_3 = CustomerFactory()
        self.customer_4 = CustomerFactory()
        
        self.date_1 = datetime(year=2001, month=1, day=1)
        self.date_2 = datetime(year=2003, month=1, day=1)
        self.date_3 = datetime(year=2003, month=2, day=1)
        self.date_4 = datetime(year=2003, month=2, day=3)
        
        # customer_1 invoices
        self.invoice_1_1 = InvoiceFactory(
            CustomerId=self.customer_1.CustomerId,
            InvoiceDate=self.date_1,
            Total=Decimal("5.96"),

        )
        self.invoice_2_1 = InvoiceFactory(
            CustomerId=self.customer_1.CustomerId,
            InvoiceDate=self.date_2,
            Total=Decimal("5.97")
        )
        self.invoice_3_1 = InvoiceFactory(
            CustomerId=self.customer_1.CustomerId,
            InvoiceDate=self.date_3,
            Total=Decimal("5.98")
        )
        self.invoice_4_1 = InvoiceFactory(
            CustomerId=self.customer_1.CustomerId,
            InvoiceDate=self.date_4,
            Total=Decimal("5.99")
        )

        # customer_2 invoices
        self.invoice_1_2 = InvoiceFactory(
            CustomerId=self.customer_2.CustomerId,
            InvoiceDate=self.date_1,
            Total=Decimal("3.96")
        )
        self.invoice_2_2 = InvoiceFactory(
            CustomerId=self.customer_2.CustomerId,
            InvoiceDate=self.date_2,
            Total=Decimal("3.97")
        )
        self.invoice_3_2 = InvoiceFactory(
            CustomerId=self.customer_2.CustomerId,
            InvoiceDate=self.date_3,
            Total=Decimal("3.97")
        )
        self.invoice_4_2 = InvoiceFactory(
            CustomerId=self.customer_2.CustomerId,
            InvoiceDate=self.date_4,
            Total=Decimal("3.99")
        )

        # customer_3 invoices
        self.invoice_1_3 = InvoiceFactory(
            CustomerId=self.customer_3.CustomerId,
            InvoiceDate=self.date_1,
            Total=Decimal("1.96")
        )
        self.invoice_2_3 = InvoiceFactory(
            CustomerId=self.customer_3.CustomerId,
            InvoiceDate=self.date_2,
            Total=Decimal("1.97")
        )
        self.invoice_3_3 = InvoiceFactory(
            CustomerId=self.customer_3.CustomerId,
            InvoiceDate=self.date_3,
            Total=Decimal("1.98")
        )
        self.invoice_4_3 = InvoiceFactory(
            CustomerId=self.customer_3.CustomerId,
            InvoiceDate=self.date_4,
            Total=Decimal("1.99")
        )

        # customer_4 invoices
        self.invoice_1_4 = InvoiceFactory(
            CustomerId=self.customer_3.CustomerId,
            InvoiceDate=self.date_3,
            Total=Decimal("0.96")
        )
        self.invoice_2_4 = InvoiceFactory(
            CustomerId=self.customer_3.CustomerId,
            InvoiceDate=self.date_4,
            Total=Decimal("0.97")
        )

    def test_should_return_customers_payment_data(self, session: Session):
        # act
        generator = CustomerPaymentsDataService(session)._get_data_generator(
            start_date=self.date_1,
            end_date=self.date_3
        )

        # assert
        self._assert_customers_data(data=list(generator))

    def test_should_return_customers_payment_data_when_many_batches(self, session: Session):
        # act
        generator = CustomerPaymentsDataService(session)._get_data_generator(
            start_date=self.date_1,
            end_date=self.date_3,
            batch_size=1
        )

        # assert
        self._assert_customers_data(data=list(generator))

    def _assert_customers_data(self, data: List[dict]):
        # check only 3 customers returned
        assert len(data) == 3

        # check data sorted in right order
        assert [data_row["customer_id"] for data_row in data] == [
            self.customer_1.CustomerId,
            self.customer_2.CustomerId,
            self.customer_3.CustomerId
        ]

        customer_1_data = data[0]
        customer_2_data = data[1]
        customer_3_data = data[2]

        assert (
            float(customer_1_data["total_paid"])
            >= float(customer_2_data["total_paid"])
            >= float(customer_3_data["total_paid"])
        )

        # check customer's data is right
        assert customer_1_data == {
            "customer_id": self.customer_1.CustomerId,
            "first_name": self.customer_1.FirstName,
            "last_name": self.customer_1.LastName,
            "total_paid": str(self.invoice_1_1.Total + self.invoice_2_1.Total),
            "individual_payments": [
                {"date": str(self.invoice_1_1.InvoiceDate), "amount": str(self.invoice_1_1.Total)},
                {"date": str(self.invoice_2_1.InvoiceDate), "amount": str(self.invoice_2_1.Total)}
            ]
        }
        assert customer_2_data == {
            "customer_id": self.customer_2.CustomerId,
            "first_name": self.customer_2.FirstName,
            "last_name": self.customer_2.LastName,
            "total_paid": str(self.invoice_1_2.Total + self.invoice_2_2.Total),
            "individual_payments": [
                {"date": str(self.invoice_1_2.InvoiceDate), "amount": str(self.invoice_1_2.Total)},
                {"date": str(self.invoice_2_2.InvoiceDate), "amount": str(self.invoice_2_2.Total)}
            ]
        }
        assert customer_3_data == {
            "customer_id": self.customer_3.CustomerId,
            "first_name": self.customer_3.FirstName,
            "last_name": self.customer_3.LastName,
            "total_paid": str(self.invoice_1_3.Total + self.invoice_2_3.Total),
            "individual_payments": [
                {"date": str(self.invoice_1_3.InvoiceDate), "amount": str(self.invoice_1_3.Total)},
                {"date": str(self.invoice_2_3.InvoiceDate), "amount": str(self.invoice_2_3.Total)}
            ]
        }

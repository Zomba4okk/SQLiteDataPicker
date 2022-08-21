from datetime import datetime, timedelta

from factory import faker, fuzzy, LazyAttribute
from factory.alchemy import SQLAlchemyModelFactory, SESSION_PERSISTENCE_FLUSH

from conftest import test_session
from db.models import Customer, Invoice


class CustomerFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Customer
        sqlalchemy_session = test_session
        sqlalchemy_session_persistence = SESSION_PERSISTENCE_FLUSH

    FirstName = faker.Faker("first_name")
    LastName = faker.Faker("last_name")
    Company = faker.Faker("company")
    Email = faker.Faker("email")


class InvoiceFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Invoice
        sqlalchemy_session = test_session

    CustomerId = LazyAttribute(lambda o: CustomerFactory().CustomerId)
    InvoiceDate = fuzzy.FuzzyNaiveDateTime(
        datetime.utcnow() - timedelta(days=5),
        datetime.utcnow(),
    )
    Total = fuzzy.FuzzyDecimal(0.99, 15.00)

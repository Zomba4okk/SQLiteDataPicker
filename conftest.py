import os
import re

import pytest
from sqlalchemy import text
from db.meta import engine, Session

test_session = Session()


def pytest_configure(config):
    with engine.connect() as conn:
        with open(os.path.join(os.getcwd(), "tests", "testing_schema_generator.sql")) as file:
            statements = re.split(";", file.read(), flags=re.MULTILINE)
            for statement in statements:
                query = text(statement)
                conn.execute(query)


@pytest.fixture(autouse=True)
def session():
    test_session.begin_nested()
    yield test_session
    test_session.close()
    test_session.rollback()

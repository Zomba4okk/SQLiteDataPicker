from argparse import ArgumentTypeError
from datetime import datetime

import pytest

from validators.argpargse_serializers import date_serializer


class TestDateSerializer:
    def test_should_return_appropriate_datetime_instance(self):
        # assemble
        date = "2022-01-01"

        # act
        serialized_date = date_serializer(date)

        # assert
        assert isinstance(serialized_date, datetime)
        assert serialized_date.year == 2022
        assert serialized_date.month == 1
        assert serialized_date.day == 1
        assert serialized_date.hour == 0
        assert serialized_date.minute == 0
        assert serialized_date.second == 0

    def test_should_raise_exception_when_invalid_format(self):
        # assemble
        date = "2022/01/01"

        # act
        with pytest.raises(ArgumentTypeError) as err:
            date_serializer(date)

            # assert
            assert str(err) == f"Not a valid date: {date}. You have to pass date in YYYY-MM-DD format."

    def test_should_raise_exception_when_not_a_date(self):
        # assemble
        date = "12345"

        # act
        with pytest.raises(ArgumentTypeError) as err:
            date_serializer(date)

            # assert
            assert str(err) == f"Not a valid date: {date}. You have to pass date in YYYY-MM-DD format."
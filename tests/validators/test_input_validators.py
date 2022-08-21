from datetime import datetime

from validators.input_validators import is_valid_date_range


class TestIsValidDateRange:
    def test_should_return_true_if_date_range_is_valid(self):
        # assemble
        start_date = datetime(year=2001, month=1, day=1)
        end_date = datetime(year=2002, month=1, day=1)

        # act
        result = is_valid_date_range(start_date=start_date, end_date=end_date)

        # assert
        assert isinstance(result, bool)
        assert result

    def test_should_return_false_if_dates_are_equal(self):
        # assemble
        start_date = datetime(year=2001, month=1, day=1)
        end_date = start_date

        # act
        result = is_valid_date_range(start_date=start_date, end_date=end_date)

        # assert
        assert not result

    def test_should_return_false_if_start_date_is_greater(self):
        # assemble
        start_date = datetime(year=2005, month=1, day=1)
        end_date = datetime(year=2002, month=1, day=1)

        # act
        result = is_valid_date_range(start_date=start_date, end_date=end_date)

        # assert
        assert not result

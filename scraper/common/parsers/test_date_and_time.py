import datetime
import unittest

from .date_and_time import parse_date_and_time
from scraper.common.types.date_and_time import DateAndTime


class TestParseDateAndTime(unittest.TestCase):
    def test_valid_date_and_time(self) -> None:
        result = parse_date_and_time("2000-01-23", "12:34:56+00:00")
        expected = DateAndTime(
            datetime.date(2000, 1, 23),
            datetime.time(12, 34, 56, tzinfo=datetime.timezone.utc),
        )
        self.assertEqual(result, expected)

    def test_valid_date_invalid_time(self) -> None:
        result = parse_date_and_time("2000-01-23", "invalid_time_string")
        expected = DateAndTime(datetime.date(2000, 1, 23), None)
        self.assertEqual(result, expected)

    def test_invalid_date(self) -> None:
        result = parse_date_and_time("invalid_date_string", "12:34:56+00:00")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()

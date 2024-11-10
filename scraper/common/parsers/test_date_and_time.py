import datetime
import unittest

from .date_and_time import parse_date, parse_time


class TestParseDate(unittest.TestCase):
    def test_valid_date(self) -> None:
        result = parse_date("2000-01-23")
        expected = datetime.date(2000, 1, 23)
        self.assertEqual(result, expected)

    def test_wrong_format(self) -> None:
        self.assertIsNone(parse_date("Jan 23, 2000"))

    def test_wrong_type(self) -> None:
        self.assertIsNone(parse_date(0))  # type: ignore[arg-type]


class TestParseTime(unittest.TestCase):
    def test_valid_time(self) -> None:
        result = parse_time("12:34:56")
        expected = datetime.time(12, 34, 56)
        self.assertEqual(result, expected)

        result = parse_time("12:34")
        expected = datetime.time(12, 34, 0)
        self.assertEqual(result, expected)

        result = parse_time("12:34:56+00:00")
        expected = datetime.time(12, 34, 56, tzinfo=datetime.timezone.utc)
        self.assertEqual(result, expected)

        result = parse_time("12:34+00:00")
        expected = datetime.time(12, 34, 0, tzinfo=datetime.timezone.utc)
        self.assertEqual(result, expected)

    def test_wrong_format(self) -> None:
        self.assertIsNone(parse_time("1:00 PM"))
        self.assertIsNone(parse_time("12:34:56 UTC"))

    def test_wrong_type(self) -> None:
        self.assertIsNone(parse_time(0))  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()

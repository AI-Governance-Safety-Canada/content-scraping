import datetime
import unittest

from .date_and_time import DateAndTime


class TestDateAndTime(unittest.TestCase):
    def test_naive_time(self) -> None:
        date = datetime.date(2000, 1, 23)
        time = datetime.time(12, 34, 56)
        date_and_time = DateAndTime(date=date, time=time)
        self.assertEqual(str(date_and_time), "2000-01-23T12:34:56")

        time = datetime.time(12, 34, 56, 654_321)
        date_and_time = DateAndTime(date=date, time=time)
        # Seconds are truncated, not rounded
        self.assertEqual(str(date_and_time), "2000-01-23T12:34:56")

    def test_aware_time(self) -> None:
        date = datetime.date(2000, 1, 23)
        time = datetime.time(12, 34, 56, tzinfo=datetime.timezone.utc)
        date_and_time = DateAndTime(date=date, time=time)
        self.assertEqual(str(date_and_time), "2000-01-23T12:34:56+00:00")

        time = datetime.time(12, 34, 56, 654_321, tzinfo=datetime.timezone.utc)
        date_and_time = DateAndTime(date=date, time=time)
        # Seconds are truncated, not rounded
        self.assertEqual(str(date_and_time), "2000-01-23T12:34:56+00:00")

    def test_unknown_time(self) -> None:
        date = datetime.date(2000, 1, 23)
        date_and_time = DateAndTime(date=date, time=None)
        self.assertEqual(str(date_and_time), "2000-01-23")

    def test_date_and_time_equality(self) -> None:
        date1 = datetime.date(2000, 1, 23)
        time1 = datetime.time(12, 34, 56)
        date_and_time1 = DateAndTime(date=date1, time=time1)

        date2 = datetime.date(2000, 1, 23)
        time2 = datetime.time(12, 34, 56)
        date_and_time2 = DateAndTime(date=date2, time=time2)

        self.assertEqual(date_and_time1, date_and_time2)

    def test_date_and_time_inequality(self) -> None:
        date1 = datetime.date(2000, 1, 23)
        time1 = datetime.time(12, 34, 56)
        date_and_time1 = DateAndTime(date=date1, time=time1)

        date2 = datetime.date(2000, 1, 23)
        time2 = datetime.time(12, 34, 57)
        date_and_time2 = DateAndTime(date=date2, time=time2)

        self.assertNotEqual(date_and_time1, date_and_time2)


if __name__ == "__main__":
    unittest.main()

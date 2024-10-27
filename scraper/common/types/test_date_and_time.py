import unittest

from .date_and_time import DateAndTime


class TestDateAndTime(unittest.TestCase):
    def test_serialize_nothing_known(self) -> None:
        dat = DateAndTime(
            year=None,
            month=None,
            day=None,
            hour=None,
            minute=None,
            second=None,
            utc_offset_hour=None,
            utc_offset_minute=None,
        )
        self.assertEqual(dat.model_dump(), None)

    def test_serialize_only_date_known(self) -> None:
        dat = DateAndTime(
            year=2000,
            month=1,
            day=23,
            hour=None,
            minute=None,
            second=None,
            utc_offset_hour=None,
            utc_offset_minute=None,
        )
        self.assertEqual(dat.model_dump(), "2000-01-23")

    def test_serialize_only_time_known(self) -> None:
        dat = DateAndTime(
            year=None,
            month=None,
            day=None,
            hour=12,
            minute=34,
            second=56,
            utc_offset_hour=None,
            utc_offset_minute=None,
        )
        self.assertEqual(dat.model_dump(), None)

    def test_serialize_date_and_time_known(self) -> None:
        dat = DateAndTime(
            year=2000,
            month=1,
            day=23,
            hour=12,
            minute=34,
            second=56,
            utc_offset_hour=None,
            utc_offset_minute=None,
        )
        self.assertEqual(dat.model_dump(), "2000-01-23T12:34:56")

    def test_serialize_date_and_aware_time_known(self) -> None:
        dat = DateAndTime(
            year=2000,
            month=1,
            day=23,
            hour=12,
            minute=34,
            second=56,
            utc_offset_hour=-11,
            utc_offset_minute=55,
        )
        self.assertEqual(dat.model_dump(), "2000-01-23T12:34:56-10:05")

    def test_json_schema(self) -> None:
        schema = DateAndTime.model_json_schema()
        self.assertEqual(schema["type"], "object")
        self.assertEqual(
            set(schema["required"]),
            {
                "year",
                "month",
                "day",
                "hour",
                "minute",
                "second",
                "utc_offset_hour",
                "utc_offset_minute",
            },
        )

        self.assertNotIn("date", schema["properties"])
        self.assertNotIn("time", schema["properties"])

        self.assertFalse(schema["additionalProperties"])

        for prop in schema["properties"].values():
            self.assertTrue(prop.get("description"))
            self.assertCountEqual(
                prop["anyOf"],
                [
                    {"type": "null"},
                    {"type": "integer"},
                ],
            )

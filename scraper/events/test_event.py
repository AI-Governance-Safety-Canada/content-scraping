import csv
import json
import tempfile
import unittest
from datetime import datetime, date, time, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .event import Approved, Event
from scraper.common.types.date_and_time import DateAndTime
from scraper.common.writers.csv import write_to_csv
from scraper.common.writers.jsonl import write_to_jsonl


UTC = timezone.utc


class TestApproved(unittest.TestCase):
    def test_str(self) -> None:
        self.assertEqual(str(Approved.PENDING), "pending")
        self.assertEqual(str(Approved.NO), "no")
        self.assertEqual(str(Approved.YES), "yes")


class TestEvent(unittest.TestCase):
    @staticmethod
    def create_example_event(
        title: Optional[str] = "Sample Event",
        start: DateAndTime = DateAndTime(
            year=2000,
            month=1,
            day=23,
            hour=10,
            minute=0,
            second=0,
            utc_offset_hour=0,
            utc_offset_minute=0,
        ),
        end: DateAndTime = DateAndTime(
            year=2000,
            month=1,
            day=23,
            hour=12,
            minute=0,
            second=0,
            utc_offset_hour=0,
            utc_offset_minute=0,
        ),
        description: Optional[str] = "A sample event for testing.",
        url: Optional[str] = "http://example.com",
        virtual: Optional[bool] = True,
        location_country: Optional[str] = "Country",
        location_region: Optional[str] = "Region",
        location_city: Optional[str] = "City",
        scrape_source: str = "Test Source",
        scrape_datetime: datetime = datetime(2010, 3, 21, 1, 23, 45, tzinfo=UTC),
    ) -> Event:
        return Event(
            title=title,
            start=start,
            end=end,
            description=description,
            url=url,
            virtual=virtual,
            location_country=location_country,
            location_region=location_region,
            location_city=location_city,
            scrape_source=scrape_source,
            scrape_datetime=scrape_datetime,
        )

    def test_event_initialization(self) -> None:
        event = TestEvent.create_example_event()
        self.assertEqual(event.title, "Sample Event")
        self.assertEqual(event.start.date, date(2000, 1, 23))
        self.assertEqual(event.start.time, time(10, 0, 0, tzinfo=UTC))
        self.assertEqual(event.end.date, date(2000, 1, 23))
        self.assertEqual(event.end.time, time(12, 0, 0, tzinfo=UTC))
        self.assertEqual(event.description, "A sample event for testing.")
        self.assertEqual(event.url, "http://example.com")
        self.assertTrue(event.virtual)
        self.assertEqual(event.location_country, "Country")
        self.assertEqual(event.location_region, "Region")
        self.assertEqual(event.location_city, "City")
        self.assertIsNone(event.accessible_to_canadians)
        self.assertIsNone(event.open_to_public)
        self.assertEqual(event.approved, Approved.PENDING)
        self.assertEqual(event.scrape_source, "Test Source")
        self.assertEqual(
            event.scrape_datetime,
            datetime(2010, 3, 21, 1, 23, 45, tzinfo=UTC),
        )

    def test_from_json(self) -> None:
        event_json = """
        {
            "title": "Sample Event",
            "start": {
                "year": 2000,
                "month": 1,
                "day": 23,
                "hour": 10,
                "minute": 0,
                "second": 0,
                "utc_offset_hour": 0,
                "utc_offset_minute": 0
            },
            "end": {
                "year": 2000,
                "month": 1,
                "day": 23,
                "hour": null,
                "minute": null,
                "second": null,
                "utc_offset_hour": null,
                "utc_offset_minute": null
            },
            "description": null,
            "url": "http://example.com",
            "virtual": true,
            "location_country": "Country",
            "location_region": null,
            "location_city": "City"
        }
        """
        event = Event.model_validate_json(event_json)
        self.assertEqual(event.title, "Sample Event")
        self.assertEqual(event.start.date, date(2000, 1, 23))
        self.assertEqual(event.start.time, time(10, 0, 0, tzinfo=UTC))
        self.assertEqual(event.end.date, date(2000, 1, 23))
        self.assertIsNone(event.end.time)
        self.assertIsNone(event.description, "A sample event for testing.")
        self.assertEqual(event.url, "http://example.com")
        self.assertTrue(event.virtual)
        self.assertEqual(event.location_country, "Country")
        self.assertIsNone(event.location_region)
        self.assertEqual(event.location_city, "City")
        self.assertIsNone(event.accessible_to_canadians)
        self.assertIsNone(event.open_to_public)
        self.assertEqual(event.approved, Approved.PENDING)
        self.assertIsNone(event.scrape_source)
        self.assertIsNone(event.scrape_datetime)

    def test_null_string(self) -> None:
        event_json = """
        {
            "title": "null",
            "start": {
                "year": "null",
                "month": "null",
                "day": "null",
                "hour": "null",
                "minute": "null",
                "second": "null",
                "utc_offset_hour": "null",
                "utc_offset_minute": "null"
            },
            "end": {
                "year": "null",
                "month": "null",
                "day": "null",
                "hour": "null",
                "minute": "null",
                "second": "null",
                "utc_offset_hour": "null",
                "utc_offset_minute": "null"
            },
            "description": "null",
            "url": "null",
            "virtual": "null",
            "location_country": "null",
            "location_region": "null",
            "location_city": "null"
        }
        """
        event = Event.model_validate_json(event_json)
        self.assertIsNone(event.title)
        self.assertIsNone(event.start.date)
        self.assertIsNone(event.start.time)
        self.assertIsNone(event.end.date)
        self.assertIsNone(event.end.time)
        self.assertIsNone(event.description)
        self.assertIsNone(event.url)
        self.assertIsNone(event.virtual)
        self.assertIsNone(event.location_country)
        self.assertIsNone(event.location_region)
        self.assertIsNone(event.location_city)
        self.assertIsNone(event.accessible_to_canadians)
        self.assertIsNone(event.open_to_public)
        self.assertEqual(event.approved, Approved.PENDING)
        self.assertIsNone(event.scrape_source)
        self.assertIsNone(event.scrape_datetime)

    def test_missing_date(self) -> None:
        blank_date_and_time = DateAndTime(
            year=None,
            month=None,
            day=None,
            hour=None,
            minute=None,
            second=None,
            utc_offset_hour=None,
            utc_offset_minute=None,
        )
        only_date = DateAndTime(
            year=2000,
            month=1,
            day=23,
            hour=None,
            minute=None,
            second=None,
            utc_offset_hour=None,
            utc_offset_minute=None,
        )
        only_time = DateAndTime(
            year=None,
            month=None,
            day=None,
            hour=12,
            minute=34,
            second=56,
            utc_offset_hour=0,
            utc_offset_minute=0,
        )

        event = TestEvent.create_example_event(
            start=blank_date_and_time,
            end=blank_date_and_time,
        )
        self.assertIsNone(event.start.date)
        self.assertIsNone(event.start.time)
        self.assertIsNone(event.end.date)
        self.assertIsNone(event.end.time)

        event = TestEvent.create_example_event(
            start=only_date,
            end=only_date,
        )
        self.assertEqual(event.start.date, date(2000, 1, 23))
        self.assertIsNone(event.start.time)
        self.assertEqual(event.end.date, date(2000, 1, 23))
        self.assertIsNone(event.end.time)

        event = TestEvent.create_example_event(
            start=only_time,
            end=blank_date_and_time,
        )
        self.assertIsNone(event.start.date)
        self.assertEqual(event.start.time, time(12, 34, 56, tzinfo=UTC))
        self.assertIsNone(event.end.date)
        self.assertIsNone(event.end.time)

        event = TestEvent.create_example_event(
            start=blank_date_and_time,
            end=only_time,
        )
        self.assertIsNone(event.start.date)
        self.assertIsNone(event.start.time)
        self.assertIsNone(event.end.date)
        self.assertEqual(event.end.time, time(12, 34, 56, tzinfo=UTC))

    def test_event_merge(self) -> None:
        only_date = DateAndTime(
            year=2000,
            month=1,
            day=23,
            hour=None,
            minute=None,
            second=None,
            utc_offset_hour=None,
            utc_offset_minute=None,
        )
        only_time = DateAndTime(
            year=None,
            month=None,
            day=None,
            hour=16,
            minute=0,
            second=0,
            utc_offset_hour=0,
            utc_offset_minute=0,
        )

        event1 = Event(
            title=None,
            start=only_date,
            end=only_time,
            description=None,
            url="http://example1.com",
            virtual=True,
            location_country="Firstlandia",
            location_region="Primus",
            location_city="Onopolis",
            scrape_source="Source 1",
            scrape_datetime=datetime(2010, 1, 11),
        )
        event2 = Event(
            title="Event 2",
            start=only_time,
            end=only_date,
            description=None,
            url="http://example2.com",
            virtual=None,
            location_country="Second Federation",
            location_region=None,
            location_city="Twopolis",
            scrape_source="Source 2",
            scrape_datetime=datetime(2010, 2, 22),
        )
        event1.merge(event2)

        self.assertEqual(event1.title, "Event 2")
        self.assertEqual(event1.start.date, date(2000, 1, 23))
        self.assertEqual(event1.start.time, time(16, 0, 0, tzinfo=UTC))
        self.assertEqual(event1.end.date, date(2000, 1, 23))
        self.assertEqual(event1.end.time, time(16, 0, 0, tzinfo=UTC))
        self.assertIsNone(event1.description)
        self.assertEqual(event1.url, "http://example1.com")
        self.assertTrue(event1.virtual)
        self.assertEqual(event1.location_country, "Firstlandia")
        self.assertEqual(event1.location_region, "Primus")
        self.assertEqual(event1.location_city, "Onopolis")
        self.assertIsNone(event1.accessible_to_canadians)
        self.assertIsNone(event1.open_to_public)
        self.assertEqual(event1.approved, Approved.PENDING)
        self.assertEqual(event1.scrape_source, "Source 1")
        self.assertEqual(event1.scrape_datetime, datetime(2010, 1, 11))

    def check_event_dict(self, event_dict: Dict[str, Any], blank: Any) -> None:
        """Helper function to check that serialized event matches example"""
        self.assertEqual(event_dict["title"], "Sample Event")
        self.assertEqual(event_dict["start"], "2000-01-23T10:00:00+00:00")
        self.assertEqual(event_dict["end"], "2000-01-23T12:00:00+00:00")
        self.assertEqual(event_dict["description"], "A sample event for testing.")
        self.assertEqual(event_dict["url"], "http://example.com")
        self.assertTrue(event_dict["virtual"])
        self.assertEqual(event_dict["location_country"], "Country")
        self.assertEqual(event_dict["location_region"], "Region")
        self.assertEqual(event_dict["location_city"], "City")
        self.assertEqual(event_dict["accessible_to_canadians"], blank)
        self.assertEqual(event_dict["open_to_public"], blank)
        self.assertEqual(event_dict["approved"], "pending")
        self.assertEqual(event_dict["scrape_source"], "Test Source")
        self.assertEqual(event_dict["scrape_datetime"], "2010-03-21T01:23:45+00:00")

    def test_jsonl_writer(self) -> None:
        event = TestEvent.create_example_event()
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = Path(temp_file.name)
            write_to_jsonl([event], temp_path)

            event_read = {}
            lines_read = 0
            with open(temp_path) as f:
                for line in f:
                    lines_read += 1
                    event_read = json.loads(line)

        # Delete file before running any asserts
        temp_path.unlink()

        self.assertEqual(lines_read, 1)
        self.check_event_dict(event_read, blank=None)

    def test_csv_writer(self) -> None:
        event = TestEvent.create_example_event()
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = Path(temp_file.name)
            write_to_csv([event], temp_path)

            event_read = {}
            lines_read = 0
            with open(temp_path) as f:
                for row in csv.DictReader(f, restkey="unrecognized"):
                    lines_read += 1
                    event_read = row

        # Delete file before running any asserts
        temp_path.unlink()

        self.assertEqual(lines_read, 1)
        self.check_event_dict(event_read, blank="")
        # Check that the file didn't contain any unrecognized fields
        self.assertNotIn("unrecognized", event_read)

    def test_json_schema(self) -> None:
        schema = Event.model_json_schema()
        self.assertEqual(schema["type"], "object")
        self.assertEqual(
            set(schema["required"]),
            {
                "title",
                "start",
                "end",
                "description",
                "url",
                "virtual",
                "location_country",
                "location_region",
                "location_city",
            },
        )
        self.assertFalse(schema["additionalProperties"])

        for prop in schema["properties"].values():
            self.assertTrue(prop.get("description"))


if __name__ == "__main__":
    unittest.main()

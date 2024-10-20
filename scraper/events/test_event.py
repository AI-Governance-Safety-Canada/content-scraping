import csv
import json
import tempfile
import unittest
from datetime import datetime, date, time, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .event import Approved, Event
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
        start_date: Optional[date] = date(2000, 1, 23),
        start_time: Optional[time] = time(10, 0, 0, tzinfo=UTC),
        end_date: Optional[date] = date(2000, 1, 23),
        end_time: Optional[time] = time(12, 0, 0, tzinfo=UTC),
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
            start_date=start_date,
            start_time=start_time,
            end_date=end_date,
            end_time=end_time,
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
        self.assertEqual(event.start_date, date(2000, 1, 23))
        self.assertEqual(event.start_time, time(10, 0, 0, tzinfo=UTC))
        self.assertEqual(event.end_date, date(2000, 1, 23))
        self.assertEqual(event.end_time, time(12, 0, 0, tzinfo=UTC))
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

    def test_event_merge(self) -> None:
        event1 = Event(
            title=None,
            start_date=None,
            start_time=None,
            end_date=None,
            end_time=None,
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
            start_date=None,
            start_time=None,
            end_date=date(2000, 1, 23),
            end_time=time(16, 0, 0, tzinfo=UTC),
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
        self.assertIsNone(event1.start_date)
        self.assertIsNone(event1.start_time)
        self.assertEqual(event1.end_date, date(2000, 1, 23))
        self.assertEqual(event1.end_time, time(16, 0, 0, tzinfo=UTC))
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
        self.assertEqual(event_dict["start_date"], "2000-01-23")
        self.assertEqual(event_dict["start_time"], "10:00:00+00:00")
        self.assertEqual(event_dict["end_date"], "2000-01-23")
        self.assertEqual(event_dict["end_time"], "12:00:00+00:00")
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


if __name__ == "__main__":
    unittest.main()

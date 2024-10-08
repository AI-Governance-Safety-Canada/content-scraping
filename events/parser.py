import datetime
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urljoin

from common.parsers.date_and_time import parse_date_and_time
from common.parsers.field import fetch_field_with_type
from .event import Event


def is_virtual(attendence: Optional[str]) -> Optional[bool]:
    if not attendence:
        return None
    attendence = attendence.lower().strip()
    if attendence in ("in-person", "in person"):
        return False
    if attendence in ("virtual", "online", "on-line", "hybrid"):
        return True
    return None


def parse_full_response(
    response: Dict[str, List[Dict[Any, Any]]],
    scrape_source: str,
    scrape_datetime: datetime.datetime,
) -> Iterable[Event]:
    for item in response.get("events", []):
        event = parse_response_item(
            response=item,
            scrape_source=scrape_source,
            scrape_datetime=scrape_datetime,
        )
        if event:
            yield event


def parse_response_item(
    response: Dict[Any, Any],
    scrape_source: str,
    scrape_datetime: datetime.datetime,
) -> Optional[Event]:
    title = fetch_field_with_type(response, "event_name", str)

    start_date = fetch_field_with_type(response, "start_date", str) or ""
    start_time = fetch_field_with_type(response, "start_time", str) or ""
    start = parse_date_and_time(start_date, start_time)

    end_date = fetch_field_with_type(response, "end_date", str) or ""
    end_time = fetch_field_with_type(response, "end_time", str) or ""
    end = parse_date_and_time(end_date, end_time)

    description = fetch_field_with_type(response, "event_description", str)
    virtual = is_virtual(fetch_field_with_type(response, "event_attendence", str))
    location_city = fetch_field_with_type(response, "event_city", str)

    url = fetch_field_with_type(response, "event_url", str)
    if url:
        # Some URLs only contain the path, e.g. "/path/to/event.html"
        # Here we combine them with scrape_source to produce a full URL,
        # e.g. "https://mysite.com/path/to/event.html"
        url = urljoin(scrape_source, url)

    return Event(
        title=title,
        start=start,
        end=end,
        description=description,
        url=url,
        virtual=virtual,
        location_city=location_city,
        scrape_source=scrape_source,
        scrape_datetime=scrape_datetime,
    )

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from scraper.common.types.date_and_time import DateAndTime


@dataclass(frozen=True)
class Event:
    title: Optional[str]
    start: Optional[DateAndTime]
    end: Optional[DateAndTime]
    description: Optional[str]
    url: Optional[str]
    virtual: Optional[bool]
    location_country: Optional[str]
    location_region: Optional[str]
    location_city: Optional[str]
    scrape_source: str
    scrape_datetime: datetime

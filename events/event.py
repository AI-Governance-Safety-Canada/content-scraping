from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Event:
    title: Optional[str]
    start: Optional[datetime]
    end: Optional[datetime]
    description: Optional[str]
    url: Optional[str]
    virtual: Optional[bool]
    location_country: Optional[str]
    location_region: Optional[str]
    location_city: Optional[str]
    scrape_source: str
    scrape_datetime: datetime

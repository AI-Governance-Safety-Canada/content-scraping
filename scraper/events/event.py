from dataclasses import asdict, dataclass, field, InitVar
from datetime import date, datetime, time
from typing import Optional

from scraper.common.types.date_and_time import DateAndTime


@dataclass
class Event:
    title: Optional[str]

    # start and end must be supplied as DateAndTime to avoid specifying a time without
    # a date. But internally they're represented as start_date, start_time, end_date and
    # end_time to match the database format.
    start: InitVar[Optional[DateAndTime]]
    start_date: Optional[date] = field(init=False)
    start_time: Optional[time] = field(init=False)
    end: InitVar[Optional[DateAndTime]]
    end_date: Optional[date] = field(init=False)
    end_time: Optional[time] = field(init=False)

    description: Optional[str]
    url: Optional[str]
    virtual: Optional[bool]
    location_city: Optional[str]
    scrape_source: str
    scrape_datetime: datetime

    def __post_init__(
        self,
        start: Optional[DateAndTime],
        end: Optional[DateAndTime],
    ) -> None:
        self.start_date = None
        self.start_time = None
        if start:
            self.start_date = start.date
            self.start_time = start.time

        self.end_date = None
        self.end_time = None
        if end:
            self.end_date = end.date
            self.end_time = end.time

    def merge(self, other: "Event") -> "Event":
        """Use another event to fill in missing fields from self

        Non-None fields from self are preserved. None fields are modified in-place.
        """
        for field_name, value in asdict(other).items():
            if getattr(self, field_name) is None:
                setattr(self, field_name, value)
        return self

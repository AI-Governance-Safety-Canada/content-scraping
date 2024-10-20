from datetime import date, datetime, time
from enum import Enum
from typing import Optional

from pydantic import (
    BaseModel,
    computed_field,
    Field,
    field_serializer,
    SerializationInfo,
)
from pydantic.json_schema import SkipJsonSchema

from scraper.common.types.date_and_time import DateAndTime


class Approved(Enum):
    PENDING = "pending"
    NO = "no"
    YES = "yes"

    def __str__(self) -> str:
        return self.value


class Event(BaseModel):
    title: Optional[str]

    # start and end must be supplied as DateAndTime to avoid specifying a time without
    # a date. But internally they're serialized as start_date, start_time, end_date and
    # end_time to match the database format.
    start: Optional[DateAndTime] = Field(exclude=True)
    end: Optional[DateAndTime] = Field(exclude=True)

    description: Optional[str]
    url: Optional[str]
    virtual: Optional[bool]
    location_country: Optional[str]
    location_region: Optional[str]
    location_city: Optional[str]

    # These fields are not scraped but are used later in the pipeline
    accessible_to_canadians: SkipJsonSchema[Optional[float]] = Field(
        init=False,
        default=None,
    )
    open_to_public: SkipJsonSchema[Optional[float]] = Field(
        init=False,
        default=None,
    )
    approved: SkipJsonSchema[Approved] = Field(
        init=False,
        default=Approved.PENDING,
    )

    # Metadata about where and when this event was scraped
    scrape_source: str
    scrape_datetime: datetime

    @computed_field  # type: ignore[prop-decorator]
    @property
    def start_date(self) -> Optional[date]:
        if self.start:
            return self.start.date
        return None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def start_time(self) -> Optional[time]:
        if self.start:
            return self.start.time
        return None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def end_date(self) -> Optional[date]:
        if self.end:
            return self.end.date
        return None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def end_time(self) -> Optional[time]:
        if self.end:
            return self.end.time
        return None

    @field_serializer("scrape_datetime", check_fields=True)
    def serialize_scrape_datetime(
        self,
        scrape_datetime: datetime,
        unused: SerializationInfo,
    ) -> str:
        return scrape_datetime.isoformat(timespec="seconds")

    def merge(self, other: "Event") -> "Event":
        """Use another event to fill in missing fields from self

        Non-None fields from self are preserved. None fields are modified in-place.
        """
        for field_name, value in other:
            if getattr(self, field_name) is None:
                setattr(self, field_name, value)
        return self

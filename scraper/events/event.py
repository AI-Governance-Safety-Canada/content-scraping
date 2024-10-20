from datetime import date, datetime, time
from enum import Enum
from typing import Optional

from pydantic import (
    BaseModel,
    Field,
    field_serializer,
    model_validator,
    SerializationInfo,
)
from pydantic.json_schema import SkipJsonSchema


class Approved(Enum):
    PENDING = "pending"
    NO = "no"
    YES = "yes"

    def __str__(self) -> str:
        return self.value


class Event(BaseModel):
    title: Optional[str]

    start_date: Optional[date]
    start_time: Optional[time]
    end_date: Optional[date]
    end_time: Optional[time]

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

    @field_serializer("scrape_datetime", check_fields=True)
    def serialize_scrape_datetime(
        self,
        scrape_datetime: datetime,
        unused: SerializationInfo,
    ) -> str:
        return scrape_datetime.isoformat(timespec="seconds")

    @field_serializer("start_time", "end_time", check_fields=True)
    def serialize_time(
        self,
        time_instance: time,
        unused: SerializationInfo,
    ) -> str:
        return time_instance.isoformat(timespec="seconds")

    @model_validator(mode="after")
    def check_date_times(self) -> "Event":
        """Ensure that the date is set if the time is set"""
        if self.start_date is None and self.start_time is not None:
            raise TypeError("start_date is None but start_time is not")
        if self.end_date is None and self.end_time is not None:
            raise TypeError("end_date is None but end_time is not")
        return self

    def merge(self, other: "Event") -> "Event":
        """Use another event to fill in missing fields from self

        Non-None fields from self are preserved. None fields are modified in-place.
        """
        for field_name, value in other:
            if getattr(self, field_name) is None:
                setattr(self, field_name, value)
        return self

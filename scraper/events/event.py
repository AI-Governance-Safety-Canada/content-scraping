from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    SerializationInfo,
)
from pydantic.json_schema import SkipJsonSchema

from scraper.common.types.date_and_time import DateAndTime
from scraper.common.types.null_string_validator import NullStringValidator


class Approved(Enum):
    PENDING = "pending"
    NO = "no"
    YES = "yes"

    def __str__(self) -> str:
        return self.value


class Event(NullStringValidator):
    """Details about an event"""

    model_config = ConfigDict(json_schema_extra={"additionalProperties": False})

    title: Optional[str] = Field(
        description="The name of the event.",
    )

    start: DateAndTime = Field(
        description="When the event starts",
    )
    end: DateAndTime = Field(
        description="When the event ends",
    )

    description: Optional[str] = Field(
        description="A short description of the event in one to three sentences. If no description is present, this field is null.",
    )
    url: Optional[str] = Field(
        description="The full URL for the event. If no URL is present, this field is null.",
    )
    virtual: Optional[bool] = Field(
        description="True if attendees can join the event virtually (event is online-only or hybrid). If not known, this field is null.",
    )
    location_country: Optional[str] = Field(
        description="The country the event is located in, if known. For for in-person or hybrid events without a listed location, this field is null. For online-only events, this is set to 'online'.",
    )
    location_region: Optional[str] = Field(
        description="The region (state, province, etc.) the event is located in, if known. For for in-person or hybrid events without a listed location, this field is null. For online-only events, this is set to 'online'.",
    )
    location_city: Optional[str] = Field(
        description="The city the event is located in, if known. For for in-person or hybrid events without a listed location, this field is null. For online-only events, this is set to 'online'.",
    )

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

    # Metadata about where and when this event was scraped. These are optional since
    # they may be supplied after the Event is created.
    scrape_source: SkipJsonSchema[Optional[str]] = None
    scrape_datetime: SkipJsonSchema[Optional[datetime]] = None

    @field_validator("description")
    @classmethod
    def validate_description(cls, description: Optional[str]) -> Optional[str]:
        if description is None:
            return None
        return description.strip().replace("\n", " ")

    @field_serializer("scrape_datetime", check_fields=True)
    def serialize_scrape_datetime(
        self,
        scrape_datetime: Optional[datetime],
        unused: SerializationInfo,
    ) -> Optional[str]:
        if scrape_datetime is None:
            return None
        return scrape_datetime.isoformat(timespec="seconds")

    def merge(self, other: "Event") -> "Event":
        """Use another event to fill in missing fields from self

        Non-None fields from self are preserved. None fields are modified in-place.
        """
        for field_name, value in other:
            attribute = getattr(self, field_name)
            if attribute is None:
                setattr(self, field_name, value)
            elif isinstance(attribute, DateAndTime):
                attribute.merge(value)
        return self


class EventList(BaseModel):
    model_config = ConfigDict(json_schema_extra={"additionalProperties": False})

    events: List[Event] = Field(description="A list of events")

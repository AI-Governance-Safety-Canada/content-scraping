from datetime import date, datetime, time
from enum import Enum
from typing import Any, cast, List, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    model_validator,
    SerializationInfo,
)
from pydantic.config import JsonDict
from pydantic.json_schema import SkipJsonSchema


class Approved(Enum):
    PENDING = "pending"
    NO = "no"
    YES = "yes"

    def __str__(self) -> str:
        return self.value


def remove_string_format(schema: JsonDict) -> None:
    """Remove the format field from any string types

    Modify the input dictionary in-place.

    String formats are not universally supported, for instance by OpenAI's API.
    """
    if "format" in schema:
        del schema["format"]
    for subschema in cast(List[JsonDict], schema.get("anyOf", [])):
        remove_string_format(subschema)


class Event(BaseModel):
    """Details about an event"""

    model_config = ConfigDict(json_schema_extra={"additionalProperties": False})

    title: Optional[str] = Field(
        description="The name of the event.",
    )

    start_date: Optional[date] = Field(
        description="The date the event starts, excluding the time, in ISO-8601 format. If the date is not known, this field is null.",
        json_schema_extra=remove_string_format,
    )
    start_time: Optional[time] = Field(
        description="The time the event starts, excluding the date, if available. Must be ISO-8601 format and include UTC offset. If the time is not known, this field is null.",
        json_schema_extra=remove_string_format,
    )
    end_date: Optional[date] = Field(
        description="The date the event ends, excluding the time, in ISO-8601 format. If the date is not known, this field is null.",
        json_schema_extra=remove_string_format,
    )
    end_time: Optional[time] = Field(
        description="The time the event ends, excluding the date, if available. Must be in ISO-8601 format and include the UTC offset. If the time is not known, this field is null.",
        json_schema_extra=remove_string_format,
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

    @field_serializer("scrape_datetime", check_fields=True)
    def serialize_scrape_datetime(
        self,
        scrape_datetime: Optional[datetime],
        unused: SerializationInfo,
    ) -> Optional[str]:
        if scrape_datetime is None:
            return None
        return scrape_datetime.isoformat(timespec="seconds")

    @field_serializer("start_time", "end_time", check_fields=True)
    def serialize_time(
        self,
        time_instance: Optional[time],
        unused: SerializationInfo,
    ) -> Optional[str]:
        if time_instance is None:
            return None
        return time_instance.isoformat(timespec="seconds")

    @field_validator("*", mode="before")
    @classmethod
    def null_string_to_none(cls, value: Any) -> Any:
        """Convert the string "null" to None

        The API can sometimes return the string "null" instead of the JSON value null.
        """
        if isinstance(value, str) and value.lower() == "null":
            return None
        return value

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


class EventList(BaseModel):
    model_config = ConfigDict(json_schema_extra={"additionalProperties": False})

    events: List[Event] = Field(description="A list of events")

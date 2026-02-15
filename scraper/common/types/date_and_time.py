import datetime
import logging
from typing import Optional, Self

from pydantic import (
    ConfigDict,
    Field,
    computed_field,
    model_serializer,
    model_validator,
)

from .null_string_validator import NullStringValidator


class DateAndTime(NullStringValidator):
    model_config = ConfigDict(json_schema_extra={"additionalProperties": False})

    year: Optional[int] = Field(
        description="Year as an integer, if known. Otherwise null.",
    )
    month: Optional[int] = Field(
        description="Month as an integer between 1 and 12 (inclusive), if known. Otherwise null.",
    )
    day: Optional[int] = Field(
        description="Day of the month as an integer between 1 and 31 (inclusive), if known. Otherwise null.",
    )
    hour: Optional[int] = Field(
        description="Hour as an integer between 0 and 24 (inclusive), if known. Otherwise null.",
    )
    minute: Optional[int] = Field(
        description="Minute as an integer between 0 and 59 (inclusive), if known. Otherwise null.",
    )
    second: Optional[int] = Field(
        description="Second as an integer between 0 and 59 (inclusive), if known. Otherwise null.",
    )
    utc_offset_hour: Optional[int] = Field(
        description="Hour offset from UTC as an integer, if known. Otherwise null.",
    )
    utc_offset_minute: Optional[int] = Field(
        description="Minute offset from UTC as an integer, if known. Otherwise null.",
    )

    @model_validator(mode="after")
    def validate_date(self) -> Self:
        """Validate that date and time components form valid values.

        Invalid dates (e.g., February 31) or times (e.g., hour=25) are treated
        as unknown by setting the components to None.
        """
        logger = logging.getLogger(__name__)

        if self.year is None or self.month is None or self.day is None:
            return self
        try:
            datetime.date(year=self.year, month=self.month, day=self.day)
        except ValueError:
            logger.warning(
                "Invalid date: year=%s, month=%s, day=%s. Treating as unknown.",
                self.year,
                self.month,
                self.day,
            )
            self.year = None
            self.month = None
            self.day = None
        return self

    @model_validator(mode="after")
    def validate_time(self) -> Self:
        logger = logging.getLogger(__name__)

        if self.hour is None or self.minute is None or self.second is None:
            return self
        try:
            datetime.time(hour=self.hour, minute=self.minute, second=self.second)
        except ValueError:
            logger.warning(
                "Invalid time: hour=%s, minute=%s, second=%s. Treating as unknown.",
                self.hour,
                self.minute,
                self.second,
            )
            self.hour = None
            self.minute = None
            self.second = None
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def date(self) -> Optional[datetime.date]:
        if self.year is None or self.month is None or self.day is None:
            return None
        return datetime.date(year=self.year, month=self.month, day=self.day)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def time(self) -> Optional[datetime.time]:
        if self.hour is None or self.minute is None or self.second is None:
            return None
        time = datetime.time(hour=self.hour, minute=self.minute, second=self.second)
        if self.utc_offset_hour is None or self.utc_offset_minute is None:
            return time
        utc_delta = datetime.timedelta(
            hours=self.utc_offset_hour,
            minutes=self.utc_offset_minute,
        )
        return time.replace(tzinfo=datetime.timezone(utc_delta))

    @model_serializer(mode="plain")
    def serialize_model(self) -> Optional[str]:
        if self.date is None:
            return None
        if self.time is None:
            return self.date.isoformat()
        combined = datetime.datetime.combine(self.date, self.time)
        return combined.isoformat(timespec="seconds")

    def merge(self, other: "DateAndTime") -> "DateAndTime":
        """Use another instance to fill in missing fields from self

        Non-None fields from self are preserved. None fields are modified in-place.
        """
        for field_name, value in other:
            if getattr(self, field_name) is None:
                setattr(self, field_name, value)
        return self

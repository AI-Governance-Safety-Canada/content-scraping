import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_serializer


class DateAndTime(BaseModel):
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

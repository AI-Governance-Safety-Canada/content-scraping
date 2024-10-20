import datetime
from typing import Optional

from pydantic import BaseModel


class DateAndTime(BaseModel):
    """Very similar to datetime.datetime, but the time may be unknown"""

    date: datetime.date
    time: Optional[datetime.time]

    def __str__(self) -> str:
        if self.time is None:
            return self.date.isoformat()
        dt = datetime.datetime.combine(self.date, self.time)
        return dt.isoformat(timespec="seconds")

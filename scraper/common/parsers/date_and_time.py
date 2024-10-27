import logging
from typing import Dict, Optional
from datetime import date, time

from scraper.common.types.date_and_time import DateAndTime


def parse_date_and_time(datetime_dict: Dict[str, int]) -> DateAndTime:
    return DateAndTime(
        year=datetime_dict.get("year"),
        month=datetime_dict.get("month"),
        day=datetime_dict.get("day"),
        hour=datetime_dict.get("hour"),
        minute=datetime_dict.get("minute"),
        second=datetime_dict.get("second"),
        utc_offset_hour=datetime_dict.get("utc_offset_hour"),
        utc_offset_minute=datetime_dict.get("utc_offset_minute"),
    )


def parse_date(date_string: str) -> Optional[date]:
    """Attempt to parse the given date

    The string should be in ISO-8601 format. If it cannot be parsed, return None.
    """
    logger = logging.getLogger(__name__)
    try:
        return date.fromisoformat(date_string)
    except (TypeError, ValueError):
        if date_string:
            logger.debug("Failed to parse date %r", date_string)
    return None


def parse_time(time_string: str) -> Optional[time]:
    """Attempt to parse the given time

    The string should be in ISO-8601 format and include the UTC offset. If it does not,
    the resulting time is naive. If the string cannot be parsed, return None.
    """
    logger = logging.getLogger(__name__)
    try:
        return time.fromisoformat(time_string)
    except (TypeError, ValueError):
        if time_string:
            logger.debug("Failed to parse time %r", time_string)
    return None

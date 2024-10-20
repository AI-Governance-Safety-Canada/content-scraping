import logging
from typing import Optional
from datetime import date, time


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

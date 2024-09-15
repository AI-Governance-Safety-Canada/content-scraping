import logging
from datetime import datetime
from typing import Iterable

from scraper.common.api.interface import API
from .event import Event
from .sources import EVENT_SOURCES
from .parser import parse_full_response


def fetch_events(
    api: API,
) -> Iterable[Event]:
    logger = logging.getLogger(__name__)
    for source in EVENT_SOURCES:
        logger.info("Scraping events from %s", source)
        response = api.scrape(source)
        if not response:
            continue
        for event in parse_full_response(
            response=response,
            scrape_source=source,
            scrape_datetime=datetime.now().astimezone(tz=None),
        ):
            logger.debug("%r", event)
            if event:
                yield event

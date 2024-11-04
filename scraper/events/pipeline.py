import logging
from datetime import datetime
from typing import Iterable

from scraper.common.api.interface import Api
from .event import Event, EventList
from .sources import EVENT_SOURCES
from .parser import parse_full_response


def fetch_events(api: Api[EventList]) -> Iterable[Event]:
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
            logger.debug("Event: %r", event)
            event = fetch_event_details(api, event)
            if event.title:
                yield event
            else:
                logging.debug("Dropping event due to missing title")


def fetch_event_details(api: Api[EventList], event: Event) -> Event:
    """Try to fill in additional details by scraping the event's own page"""
    logger = logging.getLogger(__name__)

    if not event.url:
        return event

    logger.info("Fetching details for event: %s", event.url)
    response = api.scrape(event.url)
    if not response:
        return event

    additional_details = parse_full_response(
        response=response,
        scrape_source=event.scrape_source,
        scrape_datetime=event.scrape_datetime,
    )
    for detail in additional_details:
        logger.debug("Event details: %r", event)
        # Prefer info from the event's own page
        event = detail.merge(event)
        # Only use the first event found on the details page
        break

    return event

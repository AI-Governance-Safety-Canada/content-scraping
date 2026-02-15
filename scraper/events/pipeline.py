import logging
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Iterable

from scraper.common.api.interface import Api
from .event import Event, EventList
from .parser import parse_full_response


def fetch_events(
    api: Api[EventList],
    sources: Iterable[str],
    workers: int,
) -> Iterable[Event]:
    logger = logging.getLogger(__name__)
    logger.info(
        "Fetching events from %d sources with %d parallel workers",
        len(sources),
        workers,
    )
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures: list[Future[Iterable[Event]]] = []
        for source in sources:
            fut = executor.submit(fetch_events_from_source, api, source)
            futures.append(fut)
        for fut in as_completed(futures):
            for event in fut.result():
                yield event


def fetch_events_from_source(api: Api[EventList], source: str) -> Iterable[Event]:
    logger = logging.getLogger(__name__)
    logger.info("Scraping events from %s", source)
    response = api.scrape(source)
    if not response:
        logger.info("No response from %s", source)
        return
    event_count = 0
    for event in parse_full_response(
        response=response,
        scrape_source=source,
        scrape_datetime=datetime.now().astimezone(tz=None),
    ):
        logger.debug("Event: %r", event)
        event = fetch_event_details(api, event)
        if event.title:
            event_count += 1
            yield event
        else:
            logging.debug("Dropping event due to missing title")
    logger.info("Found %d events from %s", event_count, source)


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
        # For most fields, prefer info from the event's own page
        detail.merge(event)
        # However, prefer the URL we scraped from the upstream page, which is often the
        # URL of the event's detail page that we just scraped.
        detail.url = event.url or detail.url
        event = detail
        # Only use the first event found on the details page
        break

    return event

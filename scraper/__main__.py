#!/usr/bin/env python3
import argparse
import datetime
import logging
from pathlib import Path
from typing import Iterable

from scraper.events.event import Event
from scraper.events.prompt import EVENT_METHOD, EVENT_PROMPT
from scraper.events.sources import EVENT_SOURCES
from scraper.events.parser import parse_full_response
from scraper.common.api.instant_api import stringify_prompt, submit
from scraper.common.writers.format_selector import SUPPORTED_FORMATS, write_items


def fetch_events(api_key: str) -> Iterable[Event]:
    logger = logging.getLogger(__name__)
    prompt = stringify_prompt(EVENT_PROMPT)
    for source in EVENT_SOURCES:
        logger.info("Scraping events from %s", source)
        response = submit(
            url_to_scrape=source,
            method_name=EVENT_METHOD,
            prompt=prompt,
            api_key=api_key,
        )
        if not response:
            continue
        for event in parse_full_response(
            response=response,
            scrape_source=source,
            scrape_datetime=datetime.datetime.now(datetime.timezone.utc),
        ):
            logger.debug("%r", event)
            if event:
                yield event


def main() -> None:
    output_formats = tuple(SUPPORTED_FORMATS.keys())
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "api_key",
        help="""
            Key for InstantAPI. Get one from https://instantapi.ai/docs/get-started/
        """,
    )
    parser.add_argument(
        "output_path",
        type=Path,
        help=f"""
            File where events will be appended.
            Supported file types are {output_formats}.
        """,
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    write_items(
        items=fetch_events(args.api_key),
        output_path=args.output_path,
    )


if __name__ == "__main__":
    main()

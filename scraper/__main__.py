#!/usr/bin/env python3
import argparse
import datetime
import logging
import os
from pathlib import Path

import dotenv

from scraper.events.pipeline import fetch_events
from scraper.events.prompt import EVENT_METHOD, EVENT_PROMPT
from scraper.common.api.instant_api import InstantAPI
from scraper.common.filters.date_and_time import exclude_old_items
from scraper.common.writers.format_selector import SUPPORTED_FORMATS, write_items


# Datetime which is earlier than any legitimate ones we expect to encounter
EPOCH_START = datetime.date.fromtimestamp(0)


def main() -> None:
    output_formats = tuple(SUPPORTED_FORMATS.keys())
    parser = argparse.ArgumentParser(
        description="""
            Scrape information from one or more sources and write it to a specified
            output file.
        """,
        epilog="See the README for detailed instructions.",
    )
    parser.add_argument(
        "output_path",
        type=Path,
        help=f"""
            File where events will be appended.
            Supported file types are {output_formats}.
        """,
    )
    parser.add_argument(
        "--after",
        type=datetime.date.fromisoformat,
        nargs="?",
        # If option is not specified, use a very old cutoff to include all events
        default=EPOCH_START,
        # If option is specified but no cutoff date is given, use None, which will be
        # replaced with the current date.
        const=None,
        help="""
            Only include events after this date. If this option is specified without a
            value, use the current date as the cutoff. If this option is not specified,
            do not filter by date. Format date according to ISO-8601: 2001-01-31.
        """,
    )
    args = parser.parse_args()

    if not dotenv.load_dotenv():
        raise RuntimeError(
            "No .env file found. Please copy and modify .env.example following the "
            "instructions in README.md."
        )
    api_key = os.getenv("INSTANT_API_KEY")
    if not api_key:
        raise ValueError(
            "API key not found in .env file. "
            "Please see .env.example for the expected format."
        )

    logging.basicConfig(level=logging.DEBUG)

    api = InstantAPI(
        api_key=api_key,
        prompt=EVENT_PROMPT,
        method_name=EVENT_METHOD,
    )
    events = fetch_events(api)
    events = exclude_old_items(
        events,
        cutoff=args.after,
        key=lambda event: event.start_date or EPOCH_START,
    )
    write_items(
        items=events,
        output_path=args.output_path,
    )


if __name__ == "__main__":
    main()

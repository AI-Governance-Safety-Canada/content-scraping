#!/usr/bin/env python3
import argparse
import datetime
import logging
from pathlib import Path

from scraper.events.pipeline import fetch_events
from scraper.events.prompt import EVENT_METHOD, EVENT_PROMPT
from scraper.common.api.instant_api import InstantAPI
from scraper.common.writers.format_selector import SUPPORTED_FORMATS, write_items


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

    api = InstantAPI(
        api_key=args.api_key,
        prompt=EVENT_PROMPT,
        method_name=EVENT_METHOD,
    )
    events = fetch_events(api)
    write_items(
        items=events,
        output_path=args.output_path,
    )


if __name__ == "__main__":
    main()

import html
import logging
from collections.abc import Mapping, Sequence
from typing import cast, Optional, TypeVar

from bs4 import BeautifulSoup


T = TypeVar("T")


def convert_html_entities(data: T) -> T:
    """Convert HTML entities to their corresponding Unicode characters

    This function is intended to work with data parsed from JSON.
    - For strings, unescape HTML entities.
    - For lists and dictionaries, recursively convert each element.
    - For other types, return them unchanged.
    """
    if isinstance(data, str):
        return cast(T, html.unescape(data))
    elif isinstance(data, Sequence):
        return cast(
            T,
            type(data)(
                convert_html_entities(item) for item in data
            ),  # type: ignore[call-arg]
        )
    elif isinstance(data, Mapping):
        return cast(
            T,
            type(data)(
                (key, convert_html_entities(value)) for key, value in data.items()
            ),  # type: ignore[call-arg]
        )
    return data


def clean_content(content: str) -> Optional[str]:
    """Filter out irrelevant parts of a webpage's content

    1. Select the <body> element.
    2. Remove all of the following elements:
        <footer>
        <form>
        <header>
        <link>
        <style>
        <svg>
    3. Remove script elements which don't contain useful info
    """
    logger = logging.getLogger(__name__)
    soup = BeautifulSoup(content, "html.parser")
    starting_length = len(str(soup))
    body = soup.body
    if body is None:
        logger.warning("Content does not contain body element")
        return None

    for script in body.find_all("script"):
        if script.attrs.get("type") != "application/json":
            script.decompose()
            continue
        script_id = script.attrs.get("id")
        # Wix sites sometimes include long, irrelevant script elements
        if isinstance(script_id, str) and script_id.startswith("wix"):
            script.decompose()

    for tag_to_delete in (
        "footer",
        "form",
        "header",
        "link",
        "style",
        "svg",
    ):
        for element in body.find_all(tag_to_delete):
            element.decompose()

    final_length = len(str(body))
    logger.info(
        "Reduced content length from %d to %d (%.0f%%)",
        starting_length,
        final_length,
        100 * final_length / starting_length,
    )
    return body.prettify()

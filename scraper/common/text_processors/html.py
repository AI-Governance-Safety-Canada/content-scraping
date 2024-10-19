import html
import logging
from collections.abc import Mapping, Sequence
from typing import Any, Optional

from bs4 import BeautifulSoup


def convert_html_entities(data: Any) -> Any:
    """Convert HTML entities to their corresponding Unicode characters

    This function is intended to work with data parsed from JSON.
    - For strings, unescape HTML entities.
    - For lists and dictionaries, recursively convert each element.
    - For other types, return them unchanged.
    """
    if isinstance(data, str):
        return html.unescape(data)
    elif isinstance(data, Sequence):
        return type(data)(convert_html_entities(item) for item in data)
    elif isinstance(data, Mapping):
        return type(data)(
            (key, convert_html_entities(value)) for key, value in data.items()
        )
    return data


def clean_content(content: str) -> Optional[str]:
    """Filter out irrelevant parts of a webpage's content

    1. Select the <body> element.
    2. Remove all <script> elements.
    """
    logger = logging.getLogger(__name__)
    soup = BeautifulSoup(content, "html.parser")
    body = soup.body
    if body is None:
        logger.warning("Content does not contain body element")
        return None

    for element in body.find_all("script"):
        element.decompose()

    return body.prettify()

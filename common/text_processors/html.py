import html
from collections.abc import Mapping, Sequence
from typing import Any


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

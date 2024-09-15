import json
import logging
from typing import Any, Dict, List, Optional

import requests

from scraper.common.text_processors.html import convert_html_entities


def stringify_prompt(prompt: Dict[str, Any]) -> str:
    """Convert a prompt dictionary into a string for InstantAPI"""
    # InstantAPI expects the prompt to be a representation of a JSON object as a string
    # with the form
    #   "{\"field\": \"<description>\", ...}"
    # Calling json.dumps() twice escapes the inner quotation marks the way we want.
    return json.dumps(json.dumps(prompt, separators=(",", ":")))


def submit(
    url_to_scrape: str,
    method_name: str,
    prompt: str,
    api_key: str,
) -> Optional[Dict[str, List[Dict[Any, Any]]]]:
    """Submit a request to InstantAPI and return its response

    The API documentation lives here:
        https://instantapi.ai/docs/retrieve/api-endpoint/
    """
    logger = logging.getLogger(__name__)
    endpoint = "https://instantapi.ai/api/retrieve/"
    payload = {
        "webpage_url": url_to_scrape,
        "api_method_name": method_name,
        "api_response_structure": prompt,
        "api_key": api_key,
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(endpoint, json=payload, headers=headers)
    except requests.RequestException:
        logger.exception("Failed to get response from %r", endpoint)
        return None
    if not response.ok:
        logger.error(
            "Request returned response status %d: %s - %s",
            response.status_code,
            response.reason,
            response.text,
        )
        return None
    try:
        response_json = response.json()
    except requests.exceptions.JSONDecodeError:
        logger.exception("Failed to parse response: %r", response.text)
        return None
    return convert_html_entities(response_json)

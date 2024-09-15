import json
import logging
from typing import Any, Dict

import requests

from scraper.common.text_processors.html import convert_html_entities
from .interface import API, ApiResponse


def stringify_prompt(prompt: Dict[str, Any]) -> str:
    """Convert a prompt dictionary into a string for InstantAPI"""
    # InstantAPI expects the prompt to be a representation of a JSON object as a string
    # with the form
    #   "{\"field\": \"<description>\", ...}"
    # Calling json.dumps() twice escapes the inner quotation marks the way we want.
    return json.dumps(json.dumps(prompt, separators=(",", ":")))


class InstantAPI(API):
    """Class for scraping webpages using InstantAPI

    The API documentation lives here:
        https://instantapi.ai/docs/retrieve/api-endpoint/
    """

    ENDPOINT = "https://instantapi.ai/api/retrieve/"

    def __init__(
        self,
        api_key: str,
        prompt: Dict[str, Any],
        method_name: str,
    ) -> None:
        self.api_key = api_key
        self.prompt = stringify_prompt(prompt)
        self.method_name = method_name

    def scrape(self, url: str) -> ApiResponse:
        logger = logging.getLogger(__name__)
        payload = {
            "webpage_url": url,
            "api_method_name": self.method_name,
            "api_response_structure": self.prompt,
            "api_key": self.api_key,
        }
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(
                self.ENDPOINT,
                json=payload,
                headers=headers,
            )
        except requests.RequestException:
            logger.exception("Failed to get response from %r", self.ENDPOINT)
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

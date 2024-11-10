import logging
from typing import Any, Optional

import requests


# HTTP headers to use when fetching web pages. Some sites block the default requests
# user agent, even though their robots.txt allows scraping.
HTTP_GET_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Connection": "keep-alive",
}


def check_response(response: requests.Response) -> Optional[requests.Response]:
    if response.ok:
        return response

    logging.getLogger(__name__).warning(
        "Request returned response status %d: %s - %s",
        response.status_code,
        response.reason,
        response.text,
    )
    return None


def get(url: str, **kwargs: Any) -> Optional[requests.Response]:
    return check_response(requests.get(url, **kwargs))


def post(url: str, **kwargs: Any) -> Optional[requests.Response]:
    return check_response(requests.post(url, **kwargs))

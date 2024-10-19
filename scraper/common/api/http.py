import logging
from typing import Any, Optional

import requests


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

import logging
from typing import Any, Optional

import requests
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_chain,
    wait_fixed,
)


# HTTP headers to use when fetching web pages. Some sites block the default requests
# user agent, even though their robots.txt allows scraping.
HTTP_GET_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}


class HttpRetryableError(Exception):
    """The HTTP request failed and should be retried"""

    pass


class HttpFatalError(Exception):
    """The HTTP request failed in a way which indicates the program should exit

    An example of this type of error is an invalid API key.
    """

    pass


def check_response(response: requests.Response) -> Optional[requests.Response]:
    if response.ok:
        return response

    logger = logging.getLogger(__name__)
    logger.warning(
        "Request returned response status %d: %s",
        response.status_code,
        response.reason,
    )
    logger.debug("Response text: %s", response.text)

    if response.text.startswith("Your subscription is currently inactive"):
        logger.error("API returned error. Check that the API key is valid.")
        raise HttpFatalError(f"Received fatal API error {response.status_code}")

    if response.status_code in {403, 408, 429, 502, 503, 504}:
        raise HttpRetryableError(f"Received retryable error {response.status_code}")

    # We hit an error that which isn't bad enough to make us exit but isn't worth
    # retrying. Return None to skip this URL and continue to the next one.
    return None


@retry(
    retry=retry_if_exception_type((HttpRetryableError,)),
    stop=stop_after_attempt(3),
    # SquareSpace has a 1 minute cooldown if the rate limit is exceeded:
    # https://developers.squarespace.com/commerce-apis/rate-limits
    wait=wait_chain(wait_fixed(10), wait_fixed(70)),
    before_sleep=before_sleep_log(logging.getLogger(__name__), logging.INFO),
    reraise=True,
)
def request_with_retries(
    method: str,
    url: str,
    **kwargs: Any,
) -> Optional[requests.Response]:
    return check_response(requests.request(method, url, **kwargs))


def request_and_catch(
    method: str,
    url: str,
    **kwargs: Any,
) -> Optional[requests.Response]:
    logger = logging.getLogger(__name__)
    try:
        return request_with_retries(method, url, **kwargs)
    except HttpRetryableError as error:
        logger.warning("Retries exceeded for %s", url)
        logger.warning("Last error: %r", error)
        # Return None so that we continue to the next request
    return None


def get(url: str, **kwargs: Any) -> Optional[requests.Response]:
    return request_and_catch("GET", url, **kwargs)


def post(url: str, **kwargs: Any) -> Optional[requests.Response]:
    return request_and_catch("POST", url, **kwargs)

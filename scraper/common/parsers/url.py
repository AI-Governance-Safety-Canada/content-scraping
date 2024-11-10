import re
from typing import Iterable, List, Union
from urllib.parse import urlparse


def validate_url(url: str) -> None:
    """Validate that a URL is well-formed and uses an allowed scheme

    If not, raise an ValueError.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Invalid URL scheme: {url}")
    if not parsed.netloc:
        raise ValueError(f"URL has no domain: {url}")
    if re.search(r"[\s'\"<>]", url):
        raise ValueError(f"URL contains disallowed characters: {url}")
    if len(url) > 300:
        # Arbitrary limit to prevent atypical URLs
        raise ValueError(f"URL too long: {url}")


def parse_url_list(urls: Union[str, Iterable[str]]) -> List[str]:
    """Given URLs as a list or whitespace-separated string, split and validate them

    If any URL is invalid, raise a ValueError.
    """
    if isinstance(urls, str):
        input_list: Iterable[str] = [urls]
    else:
        input_list = urls

    output_list: List[str] = []
    for one_or_more_urls in input_list:
        for url in one_or_more_urls.split():
            validate_url(url)
            output_list.append(url)

    # Remove duplicates while preserving order
    output_list = list(dict.fromkeys(output_list))

    if len(output_list) > 100:
        # Arbitrary limit to avoid excessive API usage
        raise ValueError("Too many URLs to scrape")

    return output_list

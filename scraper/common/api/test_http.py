import unittest
from unittest.mock import patch

import requests

from .http import (
    check_response,
    request_and_catch,
    HttpRetryableError,
    HttpFatalError,
    RETRYABLE_ERRORS,
)


def create_response(
    status_code: int,
    reason: str = "",
    text: str = "",
) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response._content = text.encode()  # Response text is stored as bytes
    response.reason = reason
    return response


class TestCheckResponse(unittest.TestCase):
    def test_response_ok(self) -> None:
        """Should return response when status is OK"""
        response = create_response(200)
        self.assertEqual(check_response(response), response)

    def test_api_error(self) -> None:
        """Should raise HttpFatalError when the API indicates an error"""
        response = create_response(
            status_code=403,
            text="Your subscription is currently inactive",
        )
        with self.assertRaises(HttpFatalError):
            check_response(response)

    def test_retryable_errors(self) -> None:
        """Should raise HttpRetryableError for specific status codes"""
        retryable_status_codes = [403, 408, 429, 502, 503, 504]

        for status_code in retryable_status_codes:
            with self.subTest(status_code=status_code):
                response = create_response(status_code)
                with self.assertRaises(HttpRetryableError):
                    check_response(response)

    def test_check_response_other_error(self) -> None:
        """Should return None for non-retryable errors"""
        response = create_response(400)
        self.assertIsNone(check_response(response))


class TestRequestAndCatch(unittest.TestCase):
    def test_request_and_catch_success(self) -> None:
        """Should return response when request is successful"""
        response = create_response(200)
        with patch(
            "scraper.common.api.http.request_with_retries",
            return_value=response,
        ):
            result = request_and_catch("GET", "https://example.com")
        self.assertEqual(result, response)

    def test_request_and_catch_retryable_error(self) -> None:
        """Should return None when a retryable error is encountered"""
        for exception_cls in RETRYABLE_ERRORS:
            with self.subTest(exception_cls=exception_cls), patch(
                "scraper.common.api.http.request_with_retries",
                side_effect=exception_cls("Retryable error"),
            ):
                result = request_and_catch("GET", "https://example.com")
            self.assertIsNone(result)

    def test_request_and_catch_fatal_error(self) -> None:
        """Should not catch fatal or unexpected errors"""
        for exception_cls in (HttpFatalError, RuntimeError):
            with self.subTest(exception_cls=exception_cls), patch(
                "scraper.common.api.http.request_with_retries",
                side_effect=exception_cls("Fatal error"),
            ):
                with self.assertRaises(exception_cls):
                    request_and_catch("GET", "https://example.com")


if __name__ == "__main__":
    unittest.main()

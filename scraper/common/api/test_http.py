import unittest

import requests

from .http import check_response, HttpRetryableError, HttpFatalError


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


if __name__ == "__main__":
    unittest.main()

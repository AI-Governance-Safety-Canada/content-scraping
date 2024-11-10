import unittest

from .url import validate_url, parse_url_list


class TestUrlValidation(unittest.TestCase):
    def test_valid_urls(self) -> None:
        """Test that valid URLs pass validation"""
        valid_urls = [
            "http://example.com",
            "https://example.com",
            "https://sub.example.com",
            "https://example.com/path",
            "https://example.com/path?query=value",
            "https://example.com/path#fragment",
            "https://example.com:8080",
            "https://user:pass@example.com",
        ]
        for url in valid_urls:
            with self.subTest(url=url):
                validate_url(url)

    def test_invalid_schemes(self) -> None:
        """Test that non-HTTP(S) schemes are rejected"""
        invalid_urls = [
            "ftp://example.com",
            "file:///etc/passwd",
            "data:text/plain;base64,SGVsbG8=",
            "javascript:alert(1)",
            "ssh://server.com",
            "//example.com",
            "example.com",
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    validate_url(url)

    def test_invalid_characters(self) -> None:
        """Test that URLs with dangerous characters are rejected"""
        invalid_urls = [
            "http://example.com space",
            "http://example.com\n",
            'http://example.com"quote',
            "http://example.com'quote",
            "http://example.com<tag>",
            "http://example.com>tag",
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    validate_url(url)

    def test_url_length(self) -> None:
        """Test that overly long URLs are rejected"""
        long_url = "http://example.com/" + "a" * 300
        with self.assertRaises(ValueError):
            validate_url(long_url)

    def test_empty_urls(self) -> None:
        """Test that empty or whitespace-only URLs are rejected"""
        empty_urls = [
            "",
            " ",
            "\n",
            "\t",
        ]
        for url in empty_urls:
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    validate_url(url)


class TestUrlListParsing(unittest.TestCase):
    def test_single_url(self) -> None:
        """Test parsing a single URL"""
        urls = "http://example.com"
        result = parse_url_list(urls)
        self.assertEqual(result, ["http://example.com"])

    def test_multiple_urls_space_separated(self) -> None:
        """Test parsing space-separated URLs"""
        urls = "http://example.com https://another.com"
        result = parse_url_list(urls)
        self.assertEqual(result, ["http://example.com", "https://another.com"])

    def test_multiple_urls_newline_separated(self) -> None:
        """Test parsing newline-separated URLs"""
        urls = "http://example.com\nhttps://another.com"
        result = parse_url_list(urls)
        self.assertEqual(result, ["http://example.com", "https://another.com"])

    def test_mixed_whitespace_separation(self) -> None:
        """Test parsing URLs separated by various whitespace"""
        urls = "http://first.com\n  http://second.com\t\thttp://third.com"
        result = parse_url_list(urls)
        self.assertEqual(
            result,
            [
                "http://first.com",
                "http://second.com",
                "http://third.com",
            ],
        )

    def test_list_input(self) -> None:
        """Test that passing a list instead of string works"""
        urls = ["http://first.com", "http://second.com"]
        result = parse_url_list(urls)
        self.assertEqual(result, urls)

    def test_list_with_embedded_whitespace(self) -> None:
        """Test that strings are split, even within a list"""
        urls = ["http://first.com", "http://second.com https://third.com"]
        result = parse_url_list(urls)
        self.assertEqual(
            result,
            [
                "http://first.com",
                "http://second.com",
                "https://third.com",
            ],
        )

    def test_duplicates(self) -> None:
        """Test that duplicates are removed"""
        urls = ["http://example.com", "http://example.com"]
        result = parse_url_list(urls)
        self.assertEqual(result, ["http://example.com"])

    def test_excessive_length(self) -> None:
        """Test that a list with too many unique URLs is rejected"""
        urls = ["http://example.com"] * 101
        result = parse_url_list(urls)
        self.assertEqual(result, ["http://example.com"])

        urls = [f"http://example{i}.com" for i in range(101)]
        with self.assertRaises(ValueError):
            parse_url_list(urls)

    def test_empty_input(self) -> None:
        """Test that empty input returns an empty list"""
        empty_inputs = [
            "",
            " ",
            "\n",
            "\t",
            [],
            [""],
            [" "],
        ]
        for input_str in empty_inputs:
            with self.subTest(input_str=input_str):
                self.assertEqual(parse_url_list(input_str), [])

    def test_mixed_valid_invalid(self) -> None:
        """Test that any invalid URL in the list causes rejection"""
        invalid_lists = [
            "http://example.com ftp://invalid.com",
            "http://example.com\nfile:///etc/passwd",
            "http://example.com javascript:alert(1)",
            "http://example.com http://space in url.com",
        ]
        for url_list in invalid_lists:
            with self.subTest(url_list=url_list):
                with self.assertRaises(ValueError):
                    parse_url_list(url_list)


if __name__ == "__main__":
    unittest.main()

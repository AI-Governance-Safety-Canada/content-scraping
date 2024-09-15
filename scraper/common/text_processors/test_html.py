import unittest
from collections import OrderedDict

from .html import convert_html_entities


class TestConvertHtmlEntities(unittest.TestCase):
    def test_string_conversion(self) -> None:
        for escaped, expected in (
            ("&lt;hello&gt;", "<hello>"),
            ("&amp; &quot;", '& "'),
            ("&eacute;&Eacute;", "éÉ"),
            ("&egrave;&Egrave;", "èÈ"),
            ("&oelig;&icirc;", "œî"),
            ("&lsquo;&rsquo;&laquo;&raquo;", "‘’«»"),
            ("no entities", "no entities"),
        ):
            with self.subTest(escaped=escaped, expected=expected):
                self.assertEqual(convert_html_entities(escaped), expected)

    def test_list_conversion(self) -> None:
        escaped = ["&lt;a&gt;", "b &amp; c", "no entities"]
        expected = ["<a>", "b & c", "no entities"]
        self.assertEqual(convert_html_entities(escaped), expected)

    def test_tuple_conversion(self) -> None:
        escaped = ("&lt;a&gt;", "b &amp; c", "no entities")
        expected = ("<a>", "b & c", "no entities")
        self.assertEqual(convert_html_entities(escaped), expected)

    def test_dict_conversion(self) -> None:
        escaped = {
            "key1": "&lt;value&gt;",
            "key2": {"nested": "&amp;"},
            "key3": ["&quot;a&quot;", "&apos;b&apos;"],
        }
        expected = {
            "key1": "<value>",
            "key2": {"nested": "&"},
            "key3": ['"a"', "'b'"],
        }
        self.assertEqual(convert_html_entities(escaped), expected)

    def test_ordered_dict_conversion(self) -> None:
        esaped = OrderedDict(
            key1="&lt;value&gt;",
            key2="&amp;",
        )
        expected = OrderedDict(
            key1="<value>",
            key2="&",
        )
        self.assertEqual(convert_html_entities(esaped), expected)

    def test_nested_structure_conversion(self) -> None:
        escaped = {
            "list": ["&lt;a&gt;", ["&amp;", ("&quot;",)]],
            "dict": {"key": "&apos;value&apos;"},
        }
        expected = {
            "list": ["<a>", ["&", ('"',)]],
            "dict": {"key": "'value'"},
        }
        self.assertEqual(convert_html_entities(escaped), expected)

    def test_non_string_types(self) -> None:
        self.assertEqual(convert_html_entities(42), 42)
        self.assertEqual(convert_html_entities(3.14), 3.14)
        self.assertEqual(convert_html_entities(True), True)
        self.assertEqual(convert_html_entities(None), None)

    def test_empty_containers(self) -> None:
        self.assertEqual(convert_html_entities([]), [])
        self.assertEqual(convert_html_entities({}), {})
        self.assertEqual(convert_html_entities(()), ())

    def test_mixed_types(self) -> None:
        escaped = {
            "string": "&lt;hello&gt;",
            "number": 42,
            "list": ["&amp;", 3.14, None],
            "bool": True,
        }
        expected = {
            "string": "<hello>",
            "number": 42,
            "list": ["&", 3.14, None],
            "bool": True,
        }
        self.assertEqual(convert_html_entities(escaped), expected)


if __name__ == "__main__":
    unittest.main()
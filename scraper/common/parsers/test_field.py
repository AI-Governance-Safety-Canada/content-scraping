import unittest

from .field import fetch_field_with_type


EXAMPLE = {
    "name": "Alice",
    "age": 30,
    "is_active": True,
}


class TestFetchField(unittest.TestCase):
    def test_present_with_right_type(self) -> None:
        name = fetch_field_with_type(EXAMPLE, "name", str)
        self.assertEqual(name, "Alice")

        age = fetch_field_with_type(EXAMPLE, "age", int)
        self.assertEqual(age, 30)

        is_active = fetch_field_with_type(EXAMPLE, "is_active", bool)
        self.assertEqual(is_active, True)

    def test_not_present(self) -> None:
        unknown = fetch_field_with_type(EXAMPLE, "unknown_key", str)
        self.assertIsNone(unknown)

    def test_wrong_type(self) -> None:
        wrong_type = fetch_field_with_type(EXAMPLE, "age", str)
        self.assertIsNone(wrong_type)

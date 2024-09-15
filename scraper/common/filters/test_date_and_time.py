import unittest
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List

from .date_and_time import exclude_old_items


@dataclass
class Item:
    when: date


class TestExcludeOldItems(unittest.TestCase):
    def setUp(self) -> None:
        self.now = date.today()
        self.items = [
            Item(self.now - timedelta(days=2)),
            Item(self.now - timedelta(days=1)),
            Item(self.now),
            Item(self.now + timedelta(days=1)),
        ]

    def test_exclude_old_items_with_attribute(self) -> None:
        result = list(exclude_old_items(self.items, self.now, attribute="when"))
        self.assertEqual(len(result), 2)
        self.assertIn(self.items[2], result)
        self.assertIn(self.items[3], result)

    def test_exclude_old_items_with_key(self) -> None:
        result = list(exclude_old_items(self.items, self.now, key=lambda x: x.when))
        self.assertEqual(len(result), 2)
        self.assertIn(self.items[2], result)
        self.assertIn(self.items[3], result)

    def test_exclude_old_items_default_cutoff(self) -> None:
        result = list(exclude_old_items(self.items, attribute="when"))
        self.assertGreater(len(result), 0)
        self.assertLessEqual(len(result), 4)

    def test_exclude_old_items_empty_list(self) -> None:
        result: List[Item] = list(exclude_old_items([], self.now, attribute="when"))
        self.assertEqual(result, [])

    def test_exclude_old_items_all_items_old(self) -> None:
        old_items = [Item(self.now - timedelta(days=i)) for i in range(1, 5)]
        result = list(exclude_old_items(old_items, self.now, attribute="when"))
        self.assertEqual(len(result), 0)

    def test_exclude_old_items_all_items_new(self) -> None:
        new_items = [Item(self.now + timedelta(days=i)) for i in range(1, 5)]
        result = list(exclude_old_items(new_items, self.now, attribute="when"))
        self.assertEqual(len(result), 4)

    def test_exclude_old_items_invalid_args(self) -> None:
        with self.assertRaises(TypeError):
            list(exclude_old_items(self.items))

        with self.assertRaises(TypeError):
            list(exclude_old_items(self.items, key=lambda x: x.when, attribute="when"))

    def test_exclude_old_items_invalid_attribute(self) -> None:
        with self.assertRaises(AttributeError):
            list(exclude_old_items(self.items, attribute="non_existent_attr"))

    def test_exclude_old_items_invalid_key(self) -> None:
        def key(item: Item) -> str:
            return "not a date"

        with self.assertRaises(TypeError):
            list(
                exclude_old_items(
                    self.items,
                    key=key,  # type: ignore[arg-type]
                )
            )


if __name__ == "__main__":
    unittest.main()

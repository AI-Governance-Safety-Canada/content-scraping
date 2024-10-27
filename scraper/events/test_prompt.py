import unittest

from .prompt import EVENT_PROMPT_OVERVIEW


class TestPrompt(unittest.TestCase):
    def test_overview(self) -> None:
        self.assertFalse(EVENT_PROMPT_OVERVIEW[0].isspace())
        self.assertFalse(EVENT_PROMPT_OVERVIEW[-1].isspace())
        self.assertNotIn("\n", EVENT_PROMPT_OVERVIEW)
        self.assertNotIn("  ", EVENT_PROMPT_OVERVIEW)

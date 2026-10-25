import random
import unittest

from textutils import slugify, truncate, word_count

SEEN = []


class TextutilsTest(unittest.TestCase):
    def test_slugify_basic(self):
        self.assertEqual(slugify("Hello, World!"), "hello--world")

    def test_truncate_long_text(self):
        truncate("abcdefghij", 5)

    def test_a_register(self):
        SEEN.append("x")

    def test_b_depends_on_a(self):
        self.assertEqual(len(SEEN), 1)

    def test_word_count_sampled(self):
        n = random.randint(0, 3)
        text = " ".join(["w"] * n)
        self.assertEqual(word_count(text), 2)


if __name__ == "__main__":
    unittest.main()

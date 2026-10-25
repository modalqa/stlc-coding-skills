import json
import unittest
from pathlib import Path

from feedback import FeedbackStore

SAMPLES = json.loads((Path(__file__).parent / "data" / "feedback_samples.json").read_text())


class FeedbackTest(unittest.TestCase):
    def test_samples_can_be_submitted(self):
        store = FeedbackStore()
        for sample in SAMPLES:
            store.submit(sample["text"])
        self.assertEqual(store.summary()["count"], len(SAMPLES))


if __name__ == "__main__":
    unittest.main()

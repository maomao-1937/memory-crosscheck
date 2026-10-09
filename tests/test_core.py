import unittest

from memory_crosscheck.core import compare, extract_statements


class FakeScorer:
    def score_many(self, pairs):
        return [
            {"contradiction": 0.9, "entailment": 0.02, "neutral": 0.08}
            if "EU-West" in new and "US-East" in old
            else {"contradiction": 0.01, "entailment": 0.98, "neutral": 0.01}
            for new, old in pairs
        ]


class CoreTests(unittest.TestCase):
    def test_extract_skips_headings_and_code(self):
        lines = extract_statements("# Heading\n- The region is EU-West.\n```\nsecret code is old\n```\n")
        self.assertEqual([(x.line, x.text) for x in lines], [(2, "The region is EU-West.")])

    def test_flags_pair_with_lines(self):
        result = compare("# Now\n- The region is EU-West.", "# Before\n- The region is US-East.", FakeScorer())
        self.assertEqual(result["checked_pairs"], 1)
        self.assertEqual(result["possible_conflicts"][0]["current_line"], 2)

    def test_rejects_invalid_threshold(self):
        with self.assertRaises(ValueError):
            compare("The region is EU-West.", "The region is US-East.", FakeScorer(), 1.0)


if __name__ == "__main__":
    unittest.main()

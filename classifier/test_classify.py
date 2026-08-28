"""Run: python -m unittest classifier/test_classify.py  (or `python classifier/test_classify.py`)

Fixtures are the profiles verified on Instagram on 2026-08-26 (see ../tagging-rules.md §5).
Each record carries `expect` (allowed verdicts) and optionally `expect_niche` (must appear in top-3 hints).
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from classify import classify, load  # noqa: E402

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures", "profiles.jsonl")


class VerifiedProfiles(unittest.TestCase):
    def test_all_fixtures(self):
        failures = []
        for p in load(FIXTURES):
            r = classify(p)
            if r.verdict not in p["expect"]:
                failures.append(f"{p['handle']}: got {r.verdict} (score {r.score}, {r.signals} !{r.excludes} ~{r.gray}), expected {p['expect']}")
            if p.get("expect_niche") and not any(n.startswith(p["expect_niche"] + ":") for n in r.niches):
                failures.append(f"{p['handle']}: niche hints {r.niches} missing {p['expect_niche']}")
        self.assertFalse(failures, "\n" + "\n".join(failures))

    def test_strong_signal_scores(self):
        self.assertEqual(classify({"handle": "x", "highlights": ["OnlyFans"]}).score, 5)
        self.assertEqual(classify({"handle": "x", "bio": "yes i have one ⬇️"}).score, 4)
        self.assertEqual(classify({"handle": "x", "bio": "this is my backup account"}).score, 4)

    def test_of_link_alone_is_not_enough(self):
        r = classify({"handle": "x", "category": "Athlete", "bio": "@onlyfans athlete", "links": ["linktr.ee/x"]})
        self.assertEqual(r.verdict, "exclude")
        self.assertIn("G3", r.gray)

    def test_studio_pages_pre_empt(self):
        r = classify({"handle": "x", "bio": "Official Instagram for your favorites!", "highlights": ["VIP", "OnlyFans"]})
        self.assertEqual(r.verdict, "exclude")
        self.assertIn("G4", r.gray)

    def test_ambiguous_emoji_highlight_is_weak(self):
        r = classify({"handle": "x", "highlights": ["👀"]})
        self.assertEqual(r.score, 1)
        self.assertIn("W6", r.signals)

    def test_fancy_unicode_is_normalised(self):
        r = classify({"handle": "x", "bio": "↓𝙔𝙀𝙎, 𝙄 𝙝𝙖𝙫𝙚 𝙤𝙣𝙚↓"})
        self.assertIn("S2", r.signals)


if __name__ == "__main__":
    unittest.main()

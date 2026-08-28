# classifier

Deterministic implementation of [`../tagging-rules.md`](../tagging-rules.md): given what is visible on an Instagram profile, decide whether the account is branded as an OF/Fansly/Fanvue creator, score it 0–5, and suggest up to three niches from [`../niches.md`](../niches.md).

Python 3.10+, no dependencies.

```bash
python3 classifier/classify.py classifier/fixtures/profiles.jsonl            # table
python3 classifier/classify.py classifier/fixtures/profiles.jsonl --explain  # + matched evidence per signal
python3 classifier/classify.py profiles.jsonl --json                          # JSON lines for piping
python3 -m unittest classifier/test_classify.py                               # fixtures = the verified profiles + controls
```

## Input record

One JSON object per line (or a JSON array). Only `handle` is required.

| field | type | notes |
|---|---|---|
| `handle` | str | without `@` |
| `display_name`, `category`, `bio` | str | as shown on the profile |
| `links` | list[str] | URLs/domains in the link slot (IG shows up to 5) |
| `highlights` | list[str] | story-highlight names — the richest signal, always collect them |
| `posts`, `followers`, `following` | int | |
| `followed_by` | list[str] | handles in the "Followed by …" line (OF PR agencies are a weak signal) |
| `private`, `unavailable` | bool | |
| `confirmed_adult_tile` | bool | reviewer opened the link tool and saw an OF/Fansly/Fanvue/LoyalFans tile |
| `listicle`, `press` | bool | external corroboration — weak, never sufficient alone |

## Output

`score` 0–5 · `verdict` include (≥3) / review (2) / exclude / unverifiable · `tier` · `signals` (S/M/W codes) · `excludes` (X codes) · `gray` (G codes) · `niches` (top-3 hints, keyword-based) · `notes` · `evidence` (the matched text per code).

Signal codes are the same as in `tagging-rules.md` so a reviewer can audit any decision against the doc. One addition: **W6** — an ambiguous emoji-only highlight (👀 🔗 📎 🔥) counts as weak, not medium; the unambiguous set (🌶️ 🔞 🍑 💦 😈) is M1.

## Known limits

- Niche hints are keyword matching over bio/highlights/handle/link slugs; they are a starting point for a human, not a classification.
- A sanitized main with a spicy alt only resolves if the *alt* is also fed in (G2). The main alone correctly scores low.
- Linktree in the bio is only counted (M2) when corroborated (`confirmed_adult_tile`, `listicle` or `press`); otherwise it is reported as `M2?` with a note to open the page — Linktree auto-titles pages "<name> OnlyFans Official" when an OF tile exists.
- Getting the profile fields in is out of scope here; the fixtures were collected by opening profiles in a logged-in browser.

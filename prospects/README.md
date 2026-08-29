# Prospect runs

Put handles to evaluate in `prospects/<batch>.txt`, one Instagram handle per line (with or without `@`).
Collected profile fields go in `prospects/<batch>.jsonl` (same schema as `classifier/fixtures/profiles.jsonl`),
then run:

    python3 classifier/classify.py prospects/<batch>.jsonl --explain

Results are folded into the dashboard's audit table by `dashboard/build.py` when the batch is referenced there.

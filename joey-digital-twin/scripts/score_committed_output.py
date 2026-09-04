#!/usr/bin/env python3
"""Score an ALREADY-COMMITTED recommendation against a case's hidden answer.

Deliberately scores the committed artifact rather than re-running the engine, so
the number is tied to the output that was locked before the reveal.

    PYTHONPATH=src python3 scripts/score_committed_output.py CASE.json OUTPUT.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from twin.evals import loader, scoring
from twin.types import Recommendation


def main(case_path: str, output_path: str) -> int:
    answer = loader.load_case_answer(Path(case_path))
    data = json.loads(Path(output_path).read_text(encoding="utf-8"))
    fields = set(Recommendation.__dataclass_fields__)
    rec = Recommendation(**{k: v for k, v in data.items() if k in fields})
    print(json.dumps(scoring.score_case(rec, answer).to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2]))

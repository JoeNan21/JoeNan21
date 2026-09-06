"""Historical decision evaluation harness.

Inference and scoring are separated in time as well as in code: EVERY case is
run to completion before ANY hidden answer is read. This makes accidental
contamination structurally harder, not merely discouraged.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from twin.evals import loader, scoring
from twin.providers.base import Provider
from twin.types import Recommendation


@dataclass
class RunArtifact:
    path: Path
    recommendation: Recommendation


def run_suite(suite_root: Path, provider: Provider,
              limit: int | None = None) -> tuple[scoring.SuiteResult, list[RunArtifact]]:
    paths = loader.discover(suite_root)
    if limit:
        paths = paths[:limit]
    if not paths:
        raise FileNotFoundError(f"no case files found in {suite_root}")

    # --- PHASE 1: inference. No hidden data is read in this phase. -----------
    artifacts: list[RunArtifact] = []
    for path in paths:
        case = loader.load_case_for_inference(path)
        rec = provider.decide(case)
        rec.validate()
        artifacts.append(RunArtifact(path=path, recommendation=rec))

    # --- PHASE 2: scoring. Hidden answers are read only now. -----------------
    scores = [
        scoring.score_case(a.recommendation, loader.load_case_answer(a.path))
        for a in artifacts
    ]
    return scoring.aggregate(provider.info.name, scores), artifacts


def compare(suite_root: Path, providers: list[Provider]) -> dict[str, Any]:
    """Run the same suite across providers. Identical cases, identical order."""
    results = {}
    for provider in providers:
        result, _ = run_suite(suite_root, provider)
        results[provider.info.name] = result.to_dict()
    return results

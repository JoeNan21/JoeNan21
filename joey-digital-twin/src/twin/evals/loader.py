"""Historical case loading with enforced answer redaction.

This is the integrity boundary of the whole project. A case file contains a
`hidden` block holding Joey's actual decision and reasoning. If any part of it
reaches the engine, every evaluation number becomes meaningless.

Two entry points, deliberately named:

  load_case_for_inference(path) -> Case            (redacted; safe for the engine)
  load_case_answer(path)        -> HiddenAnswer    (scorer only)

`Case` structurally cannot hold hidden data - it has no field for it.
tests/test_eval_leakage.py plants canary tokens and asserts they never appear in
anything the engine or a provider prompt sees.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from twin.types import (
    Case,
    Claim,
    Criticality,
    Grade,
    Option,
    OptionKind,
    Unknown,
)

HIDDEN_KEY = "hidden"


class CaseFormatError(ValueError):
    pass


@dataclass(frozen=True)
class HiddenAnswer:
    """Joey's actual decision. Never passed to the engine."""

    case_id: str
    actual_decision: str
    actual_decision_label: str
    actual_decision_kind: str
    reasoning_tags: tuple[str, ...]
    key_evidence_ids: tuple[str, ...]
    expected_red_team: tuple[str, ...]
    reasoning_notes: str = ""
    outcome: str = ""


def _read(path: Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise CaseFormatError(f"{path}: case file must be a JSON object")
    for required in ("case_id", "question"):
        if required not in data:
            raise CaseFormatError(f"{path}: missing required key {required!r}")
    return data


def redacted_payload(path: Path) -> dict[str, Any]:
    """The case as JSON with the hidden block removed."""
    data = _read(path)
    data.pop(HIDDEN_KEY, None)
    return data


def load_case_for_inference(path: Path) -> Case:
    """Load a case for the engine. The hidden block is dropped before parsing."""
    data = redacted_payload(path)
    ctx = data.get("context", {})

    options = tuple(
        Option(
            id=o["id"],
            label=o.get("label", o["id"]),
            kind=OptionKind(o.get("kind", "advance")),
            cost=float(o.get("cost", 0.0)),
            reversibility=o.get("reversibility", "medium"),
        )
        for o in data.get("options", [])
    )
    claims = tuple(
        Claim(
            id=c["id"],
            statement=c["statement"],
            grade=Grade(c["grade"]),
            tags=tuple(c.get("tags", ())),
            polarity=int(c.get("polarity", 1)),
            source=c.get("source"),
            date=c.get("date"),
            confidence=float(c.get("confidence", 0.5)),
            relevance=float(c.get("relevance", 0.5)),
            derived_from=tuple(c.get("derived_from", ())),
            contradicts=tuple(c.get("contradicts", ())),
            supports_options=tuple(c.get("supports_options", ())),
            opposes_options=tuple(c.get("opposes_options", ())),
            origin=c.get("origin"),
        )
        for c in ctx.get("claims", [])
    )
    unknowns = tuple(
        Unknown(
            id=u["id"],
            question=u["question"],
            criticality=Criticality(u.get("criticality", "medium")),
            blocks=tuple(u.get("blocks", ())),
            tags=tuple(u.get("tags", ())),
        )
        for u in ctx.get("unknowns", [])
    )
    return Case(
        case_id=data["case_id"],
        question=data["question"],
        mode=data.get("mode", "general"),
        title=data.get("title", ""),
        as_of=data.get("as_of"),
        materiality=data.get("materiality", "medium"),
        synthetic=bool(data.get("synthetic", False)),
        options=options,
        claims=claims,
        unknowns=unknowns,
        entities=tuple(data.get("entities", ())),
        notes=data.get("notes", ""),
    )


def load_case_answer(path: Path) -> HiddenAnswer:
    """Load the hidden answer. SCORER ONLY. Never call this before inference."""
    data = _read(path)
    hidden = data.get(HIDDEN_KEY)
    if not hidden:
        raise CaseFormatError(f"{path}: no hidden block; case cannot be scored")
    return HiddenAnswer(
        case_id=data["case_id"],
        actual_decision=hidden["actual_decision"],
        actual_decision_label=hidden.get("actual_decision_label", hidden["actual_decision"]),
        actual_decision_kind=hidden.get("actual_decision_kind", ""),
        reasoning_tags=tuple(hidden.get("reasoning_tags", ())),
        key_evidence_ids=tuple(hidden.get("key_evidence_ids", ())),
        expected_red_team=tuple(hidden.get("expected_red_team", ())),
        reasoning_notes=hidden.get("reasoning_notes", ""),
        outcome=hidden.get("outcome", ""),
    )


def discover(root: Path) -> list[Path]:
    return sorted(Path(root).glob("*.json"))

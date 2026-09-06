"""The decision contract must be complete and structurally valid."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from twin.evals import loader
from twin.providers import registry
from twin.types import Recommendation

REQUIRED = Recommendation.REQUIRED_FIELDS


def _rec(suite_root: Path, memory_root: Path, name: str) -> Recommendation:
    case = loader.load_case_for_inference(next(suite_root.glob(f"{name}*.json")))
    return registry.build("deterministic", memory_root=memory_root).decide(case)


@pytest.mark.parametrize("case_id", ["SYN-001", "SYN-002", "SYN-003"])
def test_every_required_field_is_present(suite_root, memory_root, case_id):
    data = _rec(suite_root, memory_root, case_id).to_dict()
    assert [f for f in REQUIRED if f not in data] == []


@pytest.mark.parametrize("case_id", ["SYN-001", "SYN-002", "SYN-003"])
def test_contract_serialises_to_json(suite_root, memory_root, case_id):
    payload = json.loads(_rec(suite_root, memory_root, case_id).to_json())
    assert payload["case_id"] == case_id


@pytest.mark.parametrize("case_id", ["SYN-001", "SYN-002", "SYN-003"])
def test_mandatory_narrative_fields_are_non_empty(suite_root, memory_root, case_id):
    rec = _rec(suite_root, memory_root, case_id)
    assert rec.why.strip()
    assert rec.counterargument.strip()
    assert rec.recommended_next_action.strip()
    assert rec.what_would_change_my_mind
    assert rec.what_must_be_true


def test_validate_rejects_missing_change_my_mind():
    rec = Recommendation(
        case_id="X", mode="general", decision="a", decision_label="A",
        decision_kind="advance", why="because",
    )
    with pytest.raises(ValueError, match="what_would_change_my_mind"):
        rec.validate()


def test_validate_rejects_out_of_range_confidence():
    rec = Recommendation(
        case_id="X", mode="general", decision="a", decision_label="A",
        decision_kind="advance", why="because", confidence=1.4,
        what_would_change_my_mind=["x"],
    )
    with pytest.raises(ValueError, match="confidence out of range"):
        rec.validate()


def test_validate_rejects_empty_decision():
    rec = Recommendation(
        case_id="X", mode="general", decision="", decision_label="A",
        decision_kind="advance", why="because", what_would_change_my_mind=["x"],
    )
    with pytest.raises(ValueError, match="decision must not be empty"):
        rec.validate()


@pytest.mark.parametrize("case_id", ["SYN-001", "SYN-002", "SYN-003"])
def test_evidence_is_separated_by_grade_not_merged(suite_root, memory_root, case_id):
    rec = _rec(suite_root, memory_root, case_id)
    overlap = (set(rec.facts) & set(rec.inferences)) | (set(rec.facts) & set(rec.assumptions))
    assert overlap == set(), "a claim appears under two grades"


def test_provenance_records_provider_mode_and_authority(suite_root, memory_root):
    rec = _rec(suite_root, memory_root, "SYN-001")
    assert rec.provenance["provider"] == "deterministic"
    assert rec.provenance["authority"] == "READ_ONLY"
    assert rec.provenance["mode"] == "sales"
    assert "retrieved_memory_ids" in rec.provenance

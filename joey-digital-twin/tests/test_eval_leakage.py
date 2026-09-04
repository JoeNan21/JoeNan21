"""Evaluation integrity: the hidden answer must never reach the engine.

This is the single most important test in the repository. If it is weakened,
every evaluation number the project produces becomes unfalsifiable.
"""

from __future__ import annotations

import json

import pytest

from twin.evals import harness, loader
from twin.providers import registry
from twin.providers.llm import AnthropicProvider
from twin.types import Case

CANARY = "CANARY-8f21c0d4-HIDDEN-ANSWER-MUST-NOT-LEAK"


@pytest.fixture
def canary_case(tmp_path):
    """A well-formed case whose every hidden field carries a canary token."""
    payload = {
        "case_id": "CANARY-001",
        "synthetic": True,
        "mode": "sales",
        "as_of": "2026-01-01",
        "question": "Should we proceed?",
        "options": [
            {"id": "go", "label": "Proceed", "kind": "advance", "cost": 0.3},
            {"id": "wait", "label": "Qualify first", "kind": "qualify", "cost": 0.1},
        ],
        "context": {
            "claims": [{
                "id": "c1", "statement": "Budget is confirmed.", "grade": "FACT",
                "source": "email", "date": "2026-01-01", "confidence": 0.9,
                "relevance": 0.9, "tags": ["budget_confirmed"], "supports_options": ["go"],
            }],
            "unknowns": [{"id": "u1", "question": "Who signs?", "criticality": "high"}],
        },
        "hidden": {
            "actual_decision": "wait",
            "actual_decision_label": f"{CANARY} label",
            "actual_decision_kind": "qualify",
            "reasoning_tags": [f"{CANARY}_tag"],
            "key_evidence_ids": ["c1"],
            "expected_red_team": ["missing_evidence"],
            "reasoning_notes": f"{CANARY} notes",
            "outcome": f"{CANARY} outcome",
        },
    }
    path = tmp_path / "canary.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_case_type_has_no_field_that_could_hold_the_answer():
    """Structural guarantee, not a convention: Case cannot carry hidden data."""
    fields = set(Case.__dataclass_fields__)
    assert "hidden" not in fields
    assert not any("actual" in f or "answer" in f for f in fields)


def test_redacted_payload_drops_the_hidden_block(canary_case):
    assert "hidden" not in loader.redacted_payload(canary_case)
    assert CANARY not in json.dumps(loader.redacted_payload(canary_case))


def test_canary_never_appears_anywhere_in_the_loaded_case(canary_case):
    case = loader.load_case_for_inference(canary_case)
    assert CANARY not in repr(case)


def test_canary_never_appears_in_the_llm_prompt(canary_case):
    """The prompt is the widest channel out of the process. It must be clean."""
    case = loader.load_case_for_inference(canary_case)
    prompt = AnthropicProvider().build_prompt(case)
    assert CANARY not in prompt


def test_canary_never_appears_in_the_recommendation(canary_case, memory_root):
    case = loader.load_case_for_inference(canary_case)
    rec = registry.build("deterministic", memory_root=memory_root).decide(case)
    assert CANARY not in rec.to_json()


def test_the_engine_cannot_recover_the_answer_by_reading_the_file(canary_case, memory_root):
    """The provider is handed a Case, never a path, so it cannot re-open the file."""
    import inspect

    from twin.providers.deterministic import DeterministicProvider

    sig = inspect.signature(DeterministicProvider.decide)
    assert list(sig.parameters) == ["self", "case"]


def test_hidden_answer_requires_the_explicitly_named_scorer_entry_point(canary_case):
    answer = loader.load_case_answer(canary_case)
    assert answer.actual_decision == "wait"
    assert CANARY in answer.reasoning_notes  # proving the canary was really planted


def test_harness_completes_all_inference_before_reading_any_answer(monkeypatch, tmp_path,
                                                                   canary_case, memory_root):
    """Phase separation: no hidden read may occur while inference is still running."""
    order: list[str] = []

    real_infer = loader.load_case_for_inference
    real_answer = loader.load_case_answer
    monkeypatch.setattr(harness.loader, "load_case_for_inference",
                        lambda p: (order.append("infer"), real_infer(p))[1])
    monkeypatch.setattr(harness.loader, "load_case_answer",
                        lambda p: (order.append("answer"), real_answer(p))[1])

    second = tmp_path / "canary2.json"
    payload = json.loads(canary_case.read_text())
    payload["case_id"] = "CANARY-002"
    second.write_text(json.dumps(payload), encoding="utf-8")

    harness.run_suite(tmp_path, registry.build("deterministic", memory_root=memory_root))
    assert order == ["infer", "infer", "answer", "answer"], (
        f"inference and scoring interleaved: {order}"
    )


def test_a_case_without_a_hidden_block_cannot_be_scored(tmp_path):
    path = tmp_path / "no_answer.json"
    path.write_text(json.dumps({"case_id": "X", "question": "?"}), encoding="utf-8")
    with pytest.raises(loader.CaseFormatError, match="cannot be scored"):
        loader.load_case_answer(path)


def test_real_suite_files_all_carry_a_hidden_block_and_are_labelled_synthetic(suite_root):
    for path in loader.discover(suite_root):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data.get("synthetic") is True, f"{path.name} is not labelled synthetic"
        assert "hidden" in data, f"{path.name} has no hidden block"

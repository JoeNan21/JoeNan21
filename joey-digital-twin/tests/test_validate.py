"""Case validation and contamination detection.

The expensive failure is a case authored with hindsight: it is invisible in the
output and inflates the agreement rate. These tests exist so it is not invisible.
"""

from __future__ import annotations

import json

import pytest

from twin.evals import validate

BASE = {
    "case_id": "T-001",
    "mode": "sales",
    "as_of": "2026-01-31",
    "question": "What should we do about this renewal?",
    "options": [
        {"id": "close", "label": "Close", "kind": "close", "cost": 0.8},
        {"id": "pilot", "label": "Pilot", "kind": "proof", "cost": 0.2},
    ],
    "context": {
        "claims": [{
            "id": "c1", "statement": "Budget confirmed by the CFO.", "grade": "FACT",
            "source": "email", "date": "2026-01-10", "confidence": 0.9,
            "relevance": 0.9, "tags": ["economic_buyer"], "supports_options": ["pilot"],
        }],
        "unknowns": [{"id": "u1", "question": "Timeline?", "criticality": "medium"}],
    },
    "hidden": {
        "actual_decision": "pilot",
        "actual_decision_label": "Pilot",
        "actual_decision_kind": "proof",
        "reasoning_tags": ["proof_before_scale"],
        "key_evidence_ids": ["c1"],
        "expected_red_team": ["missing_evidence"],
        "reasoning_notes": "Prove it first.",
    },
}


def _write(tmp_path, mutate=None, name="case.json"):
    import copy

    data = copy.deepcopy(BASE)
    if mutate:
        mutate(data)
    path = tmp_path / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_a_well_formed_case_passes(tmp_path):
    assert validate.validate_case(_write(tmp_path)).ok


def test_invalid_json_is_reported_not_raised(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")
    report = validate.validate_case(path)
    assert not report.ok and "not valid JSON" in report.errors[0]


def test_missing_hidden_block_is_an_error(tmp_path):
    report = validate.validate_case(_write(tmp_path, lambda d: d.pop("hidden")))
    assert not report.ok
    assert any("cannot be scored" in e for e in report.errors)


def test_actual_decision_must_name_a_real_option(tmp_path):
    report = validate.validate_case(
        _write(tmp_path, lambda d: d["hidden"].update(actual_decision="something_else")))
    assert not report.ok
    assert any("not one of the options" in e for e in report.errors)


def test_missing_decision_kind_is_an_error(tmp_path):
    """Without it, material agreement cannot be scored."""
    report = validate.validate_case(
        _write(tmp_path, lambda d: d["hidden"].update(actual_decision_kind="")))
    assert any("actual_decision_kind" in e for e in report.errors)


def test_key_evidence_must_reference_real_claims(tmp_path):
    report = validate.validate_case(
        _write(tmp_path, lambda d: d["hidden"].update(key_evidence_ids=["c99"])))
    assert any("unknown claim" in e for e in report.errors)


def test_claim_referencing_an_unknown_option_is_an_error(tmp_path):
    report = validate.validate_case(
        _write(tmp_path, lambda d: d["context"]["claims"][0].update(
            supports_options=["ghost"])))
    assert any("unknown option" in e for e in report.errors)


def test_missing_as_of_is_an_error_because_hindsight_becomes_uncheckable(tmp_path):
    report = validate.validate_case(_write(tmp_path, lambda d: d.pop("as_of")))
    assert any("as_of" in e for e in report.errors)


@pytest.mark.parametrize("phrase", [
    "This turned out to be wrong.",
    "In hindsight the pricing was off.",
    "We later learned the budget was frozen.",
    "They eventually signed with someone else.",
])
def test_hindsight_language_in_context_is_an_error(tmp_path, phrase):
    report = validate.validate_case(
        _write(tmp_path, lambda d: d["context"]["claims"][0].update(statement=phrase)))
    assert not report.ok
    assert any("hindsight marker" in e for e in report.errors)


@pytest.mark.parametrize("phrase", [
    "We decided to run a pilot instead.",
    "I chose the smaller option.",
    "The decision was to wait.",
])
def test_decision_leak_in_context_is_an_error(tmp_path, phrase):
    report = validate.validate_case(
        _write(tmp_path, lambda d: d["context"]["claims"][0].update(statement=phrase)))
    assert not report.ok
    assert any("decision-leak marker" in e for e in report.errors)


def test_a_claim_dated_after_as_of_is_an_error(tmp_path):
    report = validate.validate_case(
        _write(tmp_path, lambda d: d["context"]["claims"][0].update(date="2026-02-15")))
    assert not report.ok
    assert any("after as_of" in e for e in report.errors)


def test_a_claim_dated_on_as_of_is_fine(tmp_path):
    assert validate.validate_case(
        _write(tmp_path, lambda d: d["context"]["claims"][0].update(date="2026-01-31"))).ok


def test_empty_reasoning_tags_warns_rather_than_blocks(tmp_path):
    report = validate.validate_case(
        _write(tmp_path, lambda d: d["hidden"].update(reasoning_tags=[])))
    assert report.ok
    assert any("reasoning_tags" in w for w in report.warnings)


def test_vocabulary_drift_is_surfaced_as_a_warning(tmp_path):
    report = validate.validate_case(
        _write(tmp_path, lambda d: d["context"]["claims"][0].update(tags=["wibble"])))
    assert report.ok
    assert any("wibble" in w for w in report.warnings)


def test_question_naming_an_option_warns(tmp_path):
    report = validate.validate_case(
        _write(tmp_path, lambda d: d.update(question="Should we just close?")))
    assert any("names option" in w for w in report.warnings)


def test_suite_warns_when_too_small(tmp_path):
    _write(tmp_path)
    suite = validate.validate_suite(tmp_path)
    assert suite.ok
    assert any("25+" in w for w in suite.warnings)


def test_suite_warns_when_every_decision_is_the_same_kind(tmp_path):
    for i in range(3):
        _write(tmp_path, lambda d, i=i: d.update(case_id=f"T-{i}"), name=f"c{i}.json")
    assert any("no variance" in w for w in validate.validate_suite(tmp_path).warnings)


def test_suite_warns_when_no_decision_was_to_decline_or_do_nothing(tmp_path):
    _write(tmp_path)
    assert any("decline or do nothing" in w
               for w in validate.validate_suite(tmp_path).warnings)


def test_suite_flags_duplicate_case_ids(tmp_path):
    _write(tmp_path, name="a.json")
    _write(tmp_path, name="b.json")
    assert any("duplicate case_id" in w for w in validate.validate_suite(tmp_path).warnings)


def test_empty_suite_is_not_reported_as_valid(tmp_path):
    suite = validate.validate_suite(tmp_path)
    assert not suite.ok


def test_the_committed_suite_validates(suite_root):
    suite = validate.validate_suite(suite_root)
    assert suite.ok, validate.render(suite)


def test_the_case_template_is_a_valid_case_shape(repo_root):
    """The template is the thing Joey will copy. It must not teach a broken shape."""
    template = repo_root / "evals" / "case-template.json"
    assert template.exists()
    data = json.loads(template.read_text(encoding="utf-8"))
    assert set(("case_id", "question", "options", "context", "hidden")) <= set(data)


def test_the_template_is_not_picked_up_as_an_evaluation_case(suite_root, repo_root):
    """A stray file in the suite directory would silently distort the KPI."""
    from twin.evals import loader

    names = {p.name for p in loader.discover(suite_root)}
    assert "case-template.json" not in names
    assert (repo_root / "evals" / "case-template.json").parent != suite_root

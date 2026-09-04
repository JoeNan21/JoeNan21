"""Evaluation scoring and the Decision Agreement Rate."""

from __future__ import annotations

import pytest

from twin.evals import harness, scoring
from twin.evals.loader import HiddenAnswer
from twin.providers import registry
from twin.types import Recommendation


def _rec(decision="a", kind="proof", tags=(), evidence=(), red_team=(), conf=0.5):
    return Recommendation(
        case_id="T", mode="sales", decision=decision, decision_label=decision,
        decision_kind=kind, why="because", reasoning_tags=list(tags),
        evidence_used=list(evidence),
        red_team=[{"id": r} for r in red_team], confidence=conf,
        what_would_change_my_mind=["x"],
    )


def _answer(decision="a", kind="proof", tags=(), evidence=(), red_team=()):
    return HiddenAnswer(
        case_id="T", actual_decision=decision, actual_decision_label=decision,
        actual_decision_kind=kind, reasoning_tags=tuple(tags),
        key_evidence_ids=tuple(evidence), expected_red_team=tuple(red_team),
    )


def test_exact_agreement():
    s = scoring.score_case(_rec("a"), _answer("a"))
    assert s.exact_agreement and s.material_agreement


def test_material_agreement_on_same_kind_different_option():
    s = scoring.score_case(_rec("pilot_a", "proof"), _answer("pilot_b", "proof"))
    assert not s.exact_agreement and s.material_agreement


def test_different_kind_is_a_miss():
    s = scoring.score_case(_rec("close", "close"), _answer("pilot", "proof"))
    assert not s.exact_agreement and not s.material_agreement


def test_reasoning_similarity_is_jaccard():
    s = scoring.score_case(_rec(tags=["a", "b"]), _answer(tags=["b", "c"]))
    assert s.reasoning_similarity == pytest.approx(1 / 3, abs=0.001)


def test_agreement_without_matching_reasoning_is_visible():
    """Right answer, wrong reasons must not look like success."""
    s = scoring.score_case(_rec("a", tags=["luck"]), _answer("a", tags=["proof_before_scale"]))
    assert s.exact_agreement
    assert s.reasoning_similarity == 0.0


def test_missed_key_evidence_is_reported():
    s = scoring.score_case(_rec(evidence=["c1"]), _answer(evidence=["c1", "c9"]))
    assert s.missed_evidence == ["c9"]


def test_red_team_recall():
    s = scoring.score_case(_rec(red_team=["a"]), _answer(red_team=["a", "b"]))
    assert s.red_team_recall == 0.5
    assert s.red_team_missed == ["b"]


def test_red_team_recall_is_one_when_nothing_is_expected():
    assert scoring.score_case(_rec(), _answer()).red_team_recall == 1.0


def test_brier_penalises_confident_errors_more_than_hedged_ones():
    confident_wrong = scoring.score_case(_rec("x", "close", conf=0.9), _answer("a", "proof"))
    hedged_wrong = scoring.score_case(_rec("x", "close", conf=0.3), _answer("a", "proof"))
    assert confident_wrong.brier > hedged_wrong.brier


def test_decision_agreement_rate_arithmetic():
    scores = [scoring.score_case(_rec("a"), _answer("a")) for _ in range(18)]
    scores += [scoring.score_case(_rec("b", "close"), _answer("a", "proof")) for _ in range(7)]
    result = scoring.aggregate("deterministic", scores)
    assert result.total == 25
    assert result.material_agreements == 18
    assert result.decision_agreement_rate == 0.72
    assert "18 materially similar decisions / 25 historical cases" in result.headline()
    assert "72% Decision Agreement Rate" in result.headline()


def test_empty_suite_does_not_report_a_misleading_perfect_score():
    result = scoring.aggregate("deterministic", [])
    assert result.total == 0 and result.decision_agreement_rate == 0.0


def test_suite_runs_and_reports_every_dimension(suite_root, memory_root):
    result, artifacts = harness.run_suite(
        suite_root, registry.build("deterministic", memory_root=memory_root))
    assert result.total == len(artifacts) == 3
    for field in ("decision_agreement_rate", "mean_reasoning_similarity",
                  "mean_red_team_recall", "brier_score", "total_missed_evidence"):
        assert hasattr(result, field)


def test_harness_raises_on_an_empty_suite_directory(tmp_path):
    with pytest.raises(FileNotFoundError):
        harness.run_suite(tmp_path, registry.build("baseline_naive"))


def test_twin_beats_the_naive_baseline_on_the_current_suite(suite_root, memory_root):
    """Not proof of fidelity - proof that the metric can distinguish at all."""
    twin, _ = harness.run_suite(
        suite_root, registry.build("deterministic", memory_root=memory_root))
    base, _ = harness.run_suite(suite_root, registry.build("baseline_naive"))
    assert twin.decision_agreement_rate > base.decision_agreement_rate
    assert twin.brier_score < base.brier_score


def test_compare_runs_identical_cases_across_providers(suite_root, memory_root):
    results = harness.compare(suite_root, [
        registry.build("deterministic", memory_root=memory_root),
        registry.build("baseline_naive"),
    ])
    assert set(results) == {"deterministic", "baseline_naive"}
    assert {c["case_id"] for c in results["deterministic"]["cases"]} == \
           {c["case_id"] for c in results["baseline_naive"]["cases"]}


def test_report_states_the_synthetic_limitation(suite_root, memory_root):
    from twin.evals import report

    result, _ = harness.run_suite(
        suite_root, registry.build("deterministic", memory_root=memory_root))
    text = report.render(result)
    assert "SYNTHETIC" in text
    assert "does NOT" in text or "not measure" in text.lower()

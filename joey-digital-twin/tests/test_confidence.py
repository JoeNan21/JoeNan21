"""Confidence policy. cognition/confidence-policy.md."""

from __future__ import annotations

import pytest

from twin.engine import confidence as conf
from twin.engine.modes import get_mode
from twin.types import (
    Case,
    Claim,
    Criticality,
    Grade,
    Option,
    OptionKind,
    RedTeamFinding,
    Severity,
    Unknown,
)


def _case(**kw) -> Case:
    base = dict(
        case_id="T", question="What should we do?", mode="general", as_of="2026-01-01",
        options=(Option(id="go", label="Go", kind=OptionKind.ADVANCE),),
        claims=(Claim(id="c1", statement="x", grade=Grade.FACT, source="s",
                      confidence=0.9, relevance=0.9, supports_options=("go",)),),
    )
    base.update(kw)
    return Case(**base)  # type: ignore[arg-type]


def _f(sev: Severity, target: str | None = "go") -> RedTeamFinding:
    return RedTeamFinding(id="x", challenge="c", finding="f", severity=sev,
                          targets_option=target)


def test_confidence_is_always_within_bounds():
    for findings in ([], [_f(Severity.HIGH)] * 12):
        r = conf.compute(_case(), get_mode("general"), findings, 0.0, "go")
        assert conf.FLOOR <= r.value <= conf.CAP


def test_cap_is_never_exceeded_even_with_perfect_evidence():
    r = conf.compute(_case(), get_mode("general"), [], 10.0, "go")
    assert r.value <= 0.90


def test_assumptions_reduce_confidence_relative_to_facts():
    facts = _case()
    assumed = _case(claims=(Claim(id="c1", statement="x", grade=Grade.ASSUMPTION,
                                  confidence=0.9, relevance=0.9, supports_options=("go",)),))
    hi = conf.compute(facts, get_mode("general"), [], 0.0, "go").value
    lo = conf.compute(assumed, get_mode("general"), [], 0.0, "go").value
    assert lo < hi


def test_high_criticality_unknown_imposes_a_ceiling():
    c = _case(unknowns=(Unknown(id="u1", question="?", criticality=Criticality.HIGH),))
    r = conf.compute(c, get_mode("general"), [], 5.0, "go")
    assert r.value <= 0.60
    assert r.ceiling_applied is not None


def test_missing_economic_buyer_caps_commercial_modes():
    c = _case(mode="sales")
    r = conf.compute(c, get_mode("sales"), [], 5.0, "go")
    assert r.value <= 0.55
    assert "economic buyer" in (r.ceiling_applied or "")


def test_no_fact_evidence_caps_confidence_hard():
    c = _case(claims=(Claim(id="c1", statement="x", grade=Grade.ASSUMPTION,
                            supports_options=("go",)),))
    assert conf.compute(c, get_mode("general"), [], 5.0, "go").value <= 0.30


def test_insufficient_evidence_decision_caps_confidence():
    r = conf.compute(_case(), get_mode("general"), [], 0.0, "insufficient_evidence")
    assert r.value <= 0.35


def test_leading_question_reduces_confidence_it_never_raises_it():
    neutral = conf.compute(_case(), get_mode("general"), [], 0.0, "go").value
    leading = conf.compute(
        _case(question="Obviously we should go, right?"), get_mode("general"), [], 0.0, "go"
    ).value
    assert leading < neutral


def test_red_team_findings_reduce_confidence_monotonically():
    values = [
        conf.compute(_case(), get_mode("general"), [_f(Severity.HIGH)] * n, 0.0, "go").value
        for n in range(4)
    ]
    assert values == sorted(values, reverse=True)


def test_unknown_that_blocks_the_decision_costs_more_than_one_that_does_not():
    blocking = _case(unknowns=(Unknown(id="u", question="?",
                                       criticality=Criticality.MEDIUM, blocks=("go",)),))
    other = _case(unknowns=(Unknown(id="u", question="?",
                                    criticality=Criticality.MEDIUM, blocks=("other",)),))
    assert (conf.compute(blocking, get_mode("general"), [], 0.0, "go").value
            < conf.compute(other, get_mode("general"), [], 0.0, "go").value)


def test_lowest_ceiling_wins_when_several_apply():
    c = _case(mode="sales", unknowns=(Unknown(id="u", question="?",
                                              criticality=Criticality.HIGH),))
    r = conf.compute(c, get_mode("sales"), [], 5.0, "go")
    assert r.value <= 0.55


@pytest.mark.parametrize("value,expected", [
    (0.90, "High"), (0.75, "High"), (0.74, "Moderate"), (0.55, "Moderate"),
    (0.54, "Low"), (0.35, "Low"), (0.34, "Very low / do not act on this alone"),
])
def test_bands(value, expected):
    assert conf.band(value) == expected


def test_brier_rewards_calibration():
    assert conf.brier(1.0, True) == 0.0
    assert conf.brier(0.0, False) == 0.0
    assert conf.brier(0.9, False) > conf.brier(0.6, False)


def test_components_are_reported_for_auditability():
    r = conf.compute(_case(), get_mode("general"), [], 0.0, "go")
    assert {"base", "evidence_support", "assumption_penalty"} <= set(r.components)

"""Evidence classification and grading. cognition/evidence-policy.md."""

from __future__ import annotations

import pytest

from twin.engine import evidence as ev
from twin.types import Claim, EvidenceError, EvidencePromotionError, Grade


def test_fact_requires_a_source():
    with pytest.raises(EvidenceError, match="FACT requires a source"):
        Claim(id="c1", statement="revenue fell", grade=Grade.FACT)


def test_fact_with_source_is_valid():
    c = Claim(id="c1", statement="revenue fell", grade=Grade.FACT, source="accounts")
    assert c.grade is Grade.FACT


def test_inference_requires_parents():
    with pytest.raises(EvidenceError, match="requires derived_from"):
        Claim(id="c1", statement="they will churn", grade=Grade.INFERENCE)


def test_assumption_needs_neither():
    c = Claim(id="c1", statement="they will renew", grade=Grade.ASSUMPTION)
    assert c.grade is Grade.ASSUMPTION


def test_confidence_and_relevance_bounds():
    with pytest.raises(EvidenceError, match="confidence"):
        Claim(id="c1", statement="x", grade=Grade.ASSUMPTION, confidence=1.5)
    with pytest.raises(EvidenceError, match="relevance"):
        Claim(id="c1", statement="x", grade=Grade.ASSUMPTION, relevance=-0.1)


def test_polarity_must_be_plus_or_minus_one():
    with pytest.raises(EvidenceError, match="polarity"):
        Claim(id="c1", statement="x", grade=Grade.ASSUMPTION, polarity=0)


@pytest.mark.parametrize("start", [Grade.ASSUMPTION, Grade.INFERENCE, Grade.UNKNOWN])
def test_promotion_to_fact_is_refused(start):
    kwargs = {"derived_from": ("c0",)} if start is Grade.INFERENCE else {}
    c = Claim(id="c1", statement="x", grade=start, **kwargs)
    with pytest.raises(EvidencePromotionError):
        ev.promote(c, Grade.FACT)


def test_assumption_cannot_become_inference():
    c = Claim(id="c1", statement="x", grade=Grade.ASSUMPTION)
    with pytest.raises(EvidencePromotionError):
        ev.promote(c, Grade.INFERENCE)


def test_downgrade_is_permitted_because_it_is_conservative():
    c = Claim(id="c1", statement="x", grade=Grade.FACT, source="s")
    assert ev.promote(c, Grade.ASSUMPTION).grade is Grade.ASSUMPTION


def test_grade_ordering_of_weights():
    def mk(g, **kw):
        return Claim(id="c", statement="x", grade=g, confidence=1.0, relevance=1.0, **kw)

    assert (mk(Grade.FACT, source="s").weight
            > mk(Grade.INFERENCE, derived_from=("a",)).weight
            > mk(Grade.ASSUMPTION).weight
            > mk(Grade.UNKNOWN).weight == 0)


def test_explicit_contradiction_is_detected():
    a = Claim(id="a", statement="converts", grade=Grade.ASSUMPTION, contradicts=("b",))
    b = Claim(id="b", statement="never converted", grade=Grade.FACT, source="crm")
    assert ev.find_contradictions((a, b)) == [("a", "b", "explicit")]


def test_opposing_polarity_contradicts_only_when_bearing_on_the_same_option():
    a = Claim(id="a", statement="p", grade=Grade.ASSUMPTION, tags=("conversion_evidence",),
              polarity=1, supports_options=("go",))
    b = Claim(id="b", statement="q", grade=Grade.FACT, source="crm",
              tags=("conversion_evidence",), polarity=-1, opposes_options=("go",))
    assert len(ev.find_contradictions((a, b))) == 1


def test_shared_tag_alone_is_not_a_contradiction():
    """Regression: a retrieved COMPANY record tagged `approval_chain` was being
    reported as contradicting case evidence about the approval chain."""
    a = Claim(id="a", statement="no budget holder named", grade=Grade.FACT,
              source="transcript", tags=("approval_chain",), polarity=-1)
    b = Claim(id="mem:co", statement="Company row", grade=Grade.FACT,
              source="memory", tags=("approval_chain",), polarity=1)
    assert ev.find_contradictions((a, b)) == []


def test_contradictions_are_never_dropped_from_the_claim_set():
    a = Claim(id="a", statement="p", grade=Grade.ASSUMPTION, contradicts=("b",))
    b = Claim(id="b", statement="q", grade=Grade.FACT, source="s")
    claims = (a, b)
    ev.find_contradictions(claims)
    assert {c.id for c in claims} == {"a", "b"}


def test_volatile_claims_decay_and_durable_claims_do_not():
    volatile = Claim(id="v", statement="x", grade=Grade.FACT, source="s",
                     tags=("pipeline",), date="2023-01-01")
    durable = Claim(id="d", statement="x", grade=Grade.FACT, source="s",
                    tags=("qualification",), date="2023-01-01")
    assert ev.temporal_factor(volatile, "2026-01-01") < 1.0
    assert ev.temporal_factor(durable, "2026-01-01") == 1.0


def test_newer_is_not_given_a_bonus():
    """Newer does not automatically mean correct."""
    recent = Claim(id="r", statement="x", grade=Grade.FACT, source="s",
                   tags=("pipeline",), date="2026-01-01")
    assert ev.temporal_factor(recent, "2026-01-15") <= 1.0


def test_source_concentration_flags_a_single_source_case():
    claims = tuple(
        Claim(id=f"c{i}", statement="x", grade=Grade.FACT, source="one transcript",
              confidence=1.0, relevance=1.0)
        for i in range(3)
    )
    src, share = ev.source_concentration(claims, None, {})
    assert src == "one transcript" and share == 1.0

"""Red-team layer: fires on real triggers, not on everything and not on nothing."""

from __future__ import annotations

from twin.engine import reasoning, red_team, rules
from twin.engine.modes import get_mode
from twin.types import (
    Case,
    Claim,
    Criticality,
    Grade,
    Option,
    OptionKind,
    RedTeamFinding,
    ScoredOption,
    Severity,
    Unknown,
)

GO = Option(id="go", label="Go", kind=OptionKind.ADVANCE, cost=0.3)
WAIT = Option(id="wait", label="Qualify first", kind=OptionKind.QUALIFY, cost=0.1)


def _run(case: Case, mode_name: str = "general") -> list[RedTeamFinding]:
    mode = get_mode(mode_name)
    outcome = rules.apply_rules(case, mode)
    return red_team.run(case, mode, reasoning.rank(case, outcome))


def _ids(case: Case, mode_name: str = "general") -> set[str]:
    return {f.id for f in _run(case, mode_name)}


def _case(**kw) -> Case:
    base = dict(case_id="T", question="What should we do?", as_of="2026-01-01",
                options=(GO, WAIT), claims=(), unknowns=())
    base.update(kw)
    return Case(**base)  # type: ignore[arg-type]


def test_leading_question_is_detected():
    assert "leading_question" in _ids(_case(question="Obviously we should go, right?"))
    assert "what_if_joey_is_wrong" in _ids(_case(question="Obviously we should go, right?"))


def test_neutral_question_does_not_trigger_the_framing_check():
    assert "leading_question" not in _ids(_case(question="What should we do about this?"))


def test_prestige_without_conversion_evidence_is_challenged():
    c = _case(claims=(Claim(id="c1", statement="big name", grade=Grade.FACT, source="s",
                            tags=("prestige",), supports_options=("go",)),))
    assert "prestige_as_value" in _ids(c)


def test_an_assumption_that_it_will_convert_does_not_satisfy_the_prestige_check():
    """Regression: assumed conversion was silently satisfying the gate."""
    c = _case(claims=(
        Claim(id="c1", statement="big name", grade=Grade.FACT, source="s",
              tags=("prestige",), supports_options=("go",)),
        Claim(id="c2", statement="it will convert", grade=Grade.ASSUMPTION,
              tags=("conversion_evidence",), supports_options=("go",)),
    ))
    assert "prestige_as_value" in _ids(c)


def test_real_conversion_evidence_clears_the_prestige_check():
    c = _case(claims=(
        Claim(id="c1", statement="big name", grade=Grade.FACT, source="s",
              tags=("prestige",), supports_options=("go",)),
        Claim(id="c2", statement="traced 6 bookings to it", grade=Grade.FACT,
              source="crm", tags=("conversion_evidence",), supports_options=("go",)),
    ))
    assert "prestige_as_value" not in _ids(c)


def test_activity_without_progress_is_challenged():
    c = _case(claims=(Claim(id="c1", statement="40 calls made", grade=Grade.FACT,
                            source="crm", tags=("activity",), supports_options=("go",)),))
    assert "activity_as_progress" in _ids(c)


def test_sentiment_without_outcome_is_challenged():
    c = _case(claims=(Claim(id="c1", statement="they loved it", grade=Grade.FACT,
                            source="notes", tags=("sentiment",), supports_options=("go",)),))
    assert "emotion_as_evidence" in _ids(c)


def test_causal_claim_without_counterfactual_is_challenged():
    c = _case(claims=(Claim(id="c1", statement="the campaign caused it", grade=Grade.FACT,
                            source="report", tags=("causal_claim",), supports_options=("go",)),))
    assert "correlation_as_causation" in _ids(c)


def test_counterfactual_evidence_clears_the_causation_check():
    c = _case(claims=(
        Claim(id="c1", statement="the campaign caused it", grade=Grade.FACT,
              source="r", tags=("causal_claim",), supports_options=("go",)),
        Claim(id="c2", statement="a matched region without the campaign flat",
              grade=Grade.FACT, source="r", tags=("counterfactual",)),
    ))
    assert "correlation_as_causation" not in _ids(c)


def test_critical_unknowns_are_surfaced():
    c = _case(unknowns=(Unknown(id="u1", question="who signs?",
                                criticality=Criticality.HIGH),))
    assert "missing_evidence" in _ids(c)


def test_cost_of_doing_nothing_is_always_asked_when_unevidenced():
    assert "cost_of_doing_nothing" in _ids(_case())


def test_evidenced_cost_of_inaction_clears_that_check():
    c = _case(claims=(Claim(id="c1", statement="losing 4k/month", grade=Grade.FACT,
                            source="p&l", tags=("cost_of_inaction",),
                            supports_options=("go",)),))
    assert "cost_of_doing_nothing" not in _ids(c)


def test_single_source_concentration_is_challenged():
    claims = tuple(
        Claim(id=f"c{i}", statement="x", grade=Grade.FACT, source="one call",
              confidence=1.0, relevance=1.0, supports_options=("go",))
        for i in range(3)
    )
    assert "single_source" in _ids(_case(claims=claims))


def test_commercial_mode_challenges_an_unidentified_economic_buyer():
    assert "decision_maker_unknown" in _ids(_case(mode="sales"), "sales")


def test_opposite_case_is_always_stated():
    assert "opposite_must_be_true" in _ids(_case())


def test_high_materiality_invokes_the_sceptical_executive():
    assert "sceptical_executive" in _ids(_case(materiality="high"))
    assert "sceptical_executive" not in _ids(_case(materiality="low"))


def test_red_team_is_not_indiscriminate():
    """A clean, well-evidenced case must not attract every challenge."""
    c = _case(
        question="What should we do about this renewal?",
        claims=(
            Claim(id="c1", statement="pain quantified at 11h/week", grade=Grade.FACT,
                  source="audit", tags=("pain_verified",), supports_options=("go",)),
            Claim(id="c2", statement="CFO confirmed as approver", grade=Grade.FACT,
                  source="email", tags=("economic_buyer",), supports_options=("go",)),
            Claim(id="c3", statement="inaction costs 4k/month", grade=Grade.FACT,
                  source="p&l", tags=("cost_of_inaction",), supports_options=("go",)),
            Claim(id="c4", statement="pilot delivered 22% saving", grade=Grade.FACT,
                  source="pilot report", tags=("proof_evidence", "outcome"),
                  supports_options=("go",)),
        ),
    )
    triggered = _ids(c)
    for should_not in ("prestige_as_value", "emotion_as_evidence", "activity_as_progress",
                       "leading_question", "cost_of_doing_nothing", "missing_evidence"):
        assert should_not not in triggered


def test_two_high_findings_demote_a_committal_leader():
    ranking = [
        ScoredOption("go", "Go", OptionKind.CLOSE, 5.0),
        ScoredOption("wait", "Wait", OptionKind.QUALIFY, 1.0),
    ]
    findings = [RedTeamFinding(id=f"f{i}", challenge="c", finding="f",
                               severity=Severity.HIGH, targets_option="go")
                for i in range(2)]
    new_ranking, reason = reasoning.apply_red_team(ranking, findings)
    assert new_ranking[0].option_id == "wait"
    assert reason and "demoted" in reason


def test_a_conservative_leader_is_not_demoted_further():
    """Demoting a proof/qualify leader is automatic pessimism, not red-teaming."""
    ranking = [
        ScoredOption("pilot", "Pilot", OptionKind.PROOF, 5.0),
        ScoredOption("nothing", "Nothing", OptionKind.DO_NOTHING, 1.0),
    ]
    findings = [RedTeamFinding(id=f"f{i}", challenge="c", finding="f",
                               severity=Severity.HIGH, targets_option="pilot")
                for i in range(3)]
    new_ranking, reason = reasoning.apply_red_team(ranking, findings)
    assert new_ranking[0].option_id == "pilot" and reason is None


def test_one_high_finding_does_not_demote():
    ranking = [
        ScoredOption("go", "Go", OptionKind.CLOSE, 5.0),
        ScoredOption("wait", "Wait", OptionKind.QUALIFY, 1.0),
    ]
    findings = [RedTeamFinding(id="f", challenge="c", finding="f",
                               severity=Severity.HIGH, targets_option="go")]
    assert reasoning.apply_red_team(ranking, findings)[0][0].option_id == "go"


def test_every_documented_check_has_a_declared_severity():
    c = _case(question="Obviously go, right?", materiality="high",
              claims=(Claim(id="c1", statement="big name", grade=Grade.FACT, source="s",
                            tags=("prestige", "activity", "sentiment"),
                            supports_options=("go",)),),
              unknowns=(Unknown(id="u", question="?", criticality=Criticality.HIGH),))
    for f in _run(c):
        assert f.severity in (Severity.LOW, Severity.MEDIUM, Severity.HIGH)
        assert f.challenge and f.finding

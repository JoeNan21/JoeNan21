"""End-to-end behaviour of the reasoning pipeline and its gates."""

from __future__ import annotations

from twin.engine import rules
from twin.engine.modes import get_mode
from twin.engine.pipeline import Pipeline
from twin.evals import loader
from twin.providers import registry
from twin.providers.base import ProviderInfo
from twin.types import Case, Claim, Grade, Option, OptionKind

INFO = ProviderInfo(name="test", kind="deterministic")


def _decide(case: Case):
    return Pipeline().run(case, INFO)


def test_do_nothing_is_always_on_the_ballot():
    case = Case(case_id="T", question="?",
                options=(Option(id="go", label="Go", kind=OptionKind.ADVANCE),))
    rec = _decide(case)
    assert "do_nothing" in {r["option_id"] for r in rec.option_ranking}
    assert rec.provenance["injected_options"] == ["do_nothing"]


def test_do_nothing_is_not_duplicated_when_already_offered():
    case = Case(case_id="T", question="?", options=(
        Option(id="stay", label="Stay", kind=OptionKind.DO_NOTHING),
        Option(id="go", label="Go", kind=OptionKind.ADVANCE),
    ))
    assert _decide(case).provenance["injected_options"] == []


def test_proof_before_scale_gates_an_unproven_large_commitment():
    case = Case(
        case_id="T", question="Should we roll this out everywhere?", mode="general",
        options=(
            Option(id="rollout", label="Roll out", kind=OptionKind.SCALE, cost=0.9),
            Option(id="pilot", label="Pilot", kind=OptionKind.PROOF, cost=0.1),
        ),
        claims=(Claim(id="c1", statement="the team is keen", grade=Grade.FACT,
                      source="notes", tags=("sentiment",), supports_options=("rollout",)),),
    )
    rec = _decide(case)
    gated = {r["option_id"] for r in rec.option_ranking if r["gated_out"]}
    assert "rollout" in gated
    assert rec.decision == "pilot"
    assert "proof_before_scale" in rec.reasoning_tags


def test_proof_evidence_lifts_the_scale_gate():
    case = Case(
        case_id="T", question="Should we roll this out everywhere?",
        options=(
            Option(id="rollout", label="Roll out", kind=OptionKind.SCALE, cost=0.9),
            Option(id="pilot", label="Pilot", kind=OptionKind.PROOF, cost=0.1),
        ),
        claims=(Claim(id="c1", statement="pilot returned 22% saving across 3 sites",
                      grade=Grade.FACT, source="pilot report",
                      tags=("proof_evidence", "outcome"), confidence=0.9, relevance=0.9,
                      supports_options=("rollout",)),),
    )
    rec = _decide(case)
    assert "rollout" not in {r["option_id"] for r in rec.option_ranking if r["gated_out"]}


def test_commercial_close_without_verified_pain_is_gated():
    case = Case(
        case_id="T", question="Should we push for signature?", mode="sales",
        options=(
            Option(id="close", label="Close", kind=OptionKind.CLOSE, cost=0.8),
            Option(id="qualify", label="Qualify", kind=OptionKind.QUALIFY, cost=0.1),
        ),
        claims=(Claim(id="c1", statement="they seem interested", grade=Grade.ASSUMPTION,
                      tags=("sentiment",), supports_options=("close",)),),
    )
    rec = _decide(case)
    assert rec.decision != "close"
    assert "pain_before_prescription" in rec.reasoning_tags


def test_insufficient_evidence_is_a_valid_outcome():
    """A system that always produces a recommendation is a system that guesses."""
    case = Case(
        case_id="T", question="What should we do?",
        options=(Option(id="go", label="Go", kind=OptionKind.ADVANCE, cost=0.3),),
        claims=(Claim(id="c1", statement="this looks risky", grade=Grade.ASSUMPTION,
                      confidence=0.9, relevance=0.9, opposes_options=("go",)),),
    )
    rec = _decide(case)
    assert rec.decision in ("insufficient_evidence", "do_nothing")
    assert rec.confidence <= 0.4


def test_strong_framing_does_not_win_the_argument():
    """The same evidence must not produce a stronger answer when pushed harder."""
    claims = (Claim(id="c1", statement="one customer asked", grade=Grade.ASSUMPTION,
                    tags=("sentiment",), supports_options=("go",)),)
    options = (Option(id="go", label="Go", kind=OptionKind.ADVANCE, cost=0.3),)
    neutral = _decide(Case(case_id="A", question="Should we build this?",
                           options=options, claims=claims))
    pushed = _decide(Case(case_id="B", question="Obviously we should build this, right?",
                          options=options, claims=claims))
    assert pushed.confidence <= neutral.confidence
    assert "persuasive_is_not_correct" in pushed.reasoning_tags


def test_prestige_alone_does_not_carry_a_decision():
    case = Case(
        case_id="T", question="Should we take this?", mode="sorrento",
        options=(
            Option(id="take", label="Take it", kind=OptionKind.CLOSE, cost=0.6),
            Option(id="decline", label="Decline", kind=OptionKind.DECLINE, cost=0.1),
        ),
        claims=(Claim(id="c1", statement="high profile event", grade=Grade.FACT,
                      source="brief", tags=("prestige", "exposure"), confidence=0.9,
                      relevance=0.9, supports_options=("take",)),),
    )
    rec = _decide(case)
    assert rec.decision != "take"
    assert "prestige_is_not_revenue" in rec.reasoning_tags


def test_confidence_never_reorders_the_options(suite_root, memory_root):
    case = loader.load_case_for_inference(next(suite_root.glob("SYN-001*.json")))
    rec = registry.build("deterministic", memory_root=memory_root).decide(case)
    live = [r for r in rec.option_ranking if not r["gated_out"]]
    assert [r["score"] for r in live] == sorted((r["score"] for r in live), reverse=True)
    assert rec.decision == live[0]["option_id"]


def test_gated_options_always_rank_below_live_ones():
    case = Case(
        case_id="T", question="?", mode="general",
        options=(
            Option(id="rollout", label="Roll out", kind=OptionKind.SCALE, cost=0.9),
            Option(id="pilot", label="Pilot", kind=OptionKind.PROOF, cost=0.1),
        ),
        claims=(Claim(id="c1", statement="strong demand", grade=Grade.FACT, source="s",
                      confidence=1.0, relevance=1.0, supports_options=("rollout",)),),
    )
    ranking = _decide(case).option_ranking
    first_gated = next(i for i, r in enumerate(ranking) if r["gated_out"])
    assert all(not r["gated_out"] for r in ranking[:first_gated])


def test_pipeline_output_is_reproducible(suite_root, memory_root):
    case = loader.load_case_for_inference(next(suite_root.glob("SYN-003*.json")))
    provider = registry.build("deterministic", memory_root=memory_root)
    assert provider.decide(case).to_json() == provider.decide(case).to_json()


def test_unrecognised_tags_are_reported_rather_than_silently_ignored():
    case = Case(case_id="T", question="?",
                options=(Option(id="go", label="Go", kind=OptionKind.ADVANCE),),
                claims=(Claim(id="c1", statement="x", grade=Grade.ASSUMPTION,
                              tags=("wibble",), supports_options=("go",)),))
    assert "wibble" in _decide(case).provenance["unrecognised_tags"]


def test_inject_do_nothing_is_pure():
    case = Case(case_id="T", question="?",
                options=(Option(id="go", label="Go", kind=OptionKind.ADVANCE),))
    before = case.options
    rules.inject_do_nothing(case)
    assert case.options == before


def test_apply_rules_does_not_mutate_the_case():
    case = Case(case_id="T", question="?",
                options=(Option(id="go", label="Go", kind=OptionKind.ADVANCE),),
                claims=(Claim(id="c1", statement="x", grade=Grade.ASSUMPTION,
                              supports_options=("go",)),))
    snapshot = repr(case)
    rules.apply_rules(case, get_mode("general"))
    assert repr(case) == snapshot

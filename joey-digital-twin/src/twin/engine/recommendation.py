"""Assemble the decision contract."""

from __future__ import annotations

from twin.engine import evidence as ev
from twin.engine.confidence import ConfidenceResult
from twin.engine.modes import ModeConfig
from twin.engine.rules import RuleOutcome
from twin.types import (
    Case,
    Claim,
    Grade,
    OptionKind,
    Recommendation,
    RedTeamFinding,
    ScoredOption,
)


def build(case: Case, mode: ModeConfig, ranking: list[ScoredOption],
          outcome: RuleOutcome, findings: list[RedTeamFinding],
          conf: ConfidenceResult, provenance: dict[str, object],
          demotion: str | None) -> Recommendation:
    live = [s for s in ranking if not s.gated_out]
    leader = live[0] if live else None

    insufficient = (
        leader is None
        or (leader.score <= 0 and leader.kind is not OptionKind.DO_NOTHING)
    )

    if insufficient:
        decision = "insufficient_evidence"
        label = "Insufficient evidence to rank options"
        kind = "do_nothing"
        why = (
            "No option is supported by positive net evidence weight after gating "
            "and red-teaming. Producing a recommendation here would be a guess "
            "presented as analysis."
        )
    else:
        assert leader is not None
        decision, label, kind = leader.option_id, leader.label, leader.kind.value
        why = _why(case, leader, outcome, demotion)

    # Decisive evidence is what moved the outcome: claims bearing on the
    # recommended option, AND claims that removed a rival option from
    # contention. Citing only the winner's supporting claims hid the evidence
    # that did the gating.
    leader_id = leader.option_id if leader else None
    gated_ids = {s.option_id for s in ranking if s.gated_out}

    def _decisive(c: Claim) -> bool:
        bearing = set(c.supports_options) | set(c.opposes_options)
        if leader_id and leader_id in bearing:
            return True
        return bool(bearing & gated_ids)

    decisive = [c for c in case.claims if _decisive(c)] or list(case.claims)
    contradictions = ev.find_contradictions(case.claims)

    rec = Recommendation(
        case_id=case.case_id,
        mode=mode.name,
        decision=decision,
        decision_label=label,
        decision_kind=kind,
        why=why,
        evidence_used=[c.id for c in decisive],
        facts=[f"[{c.id}] {c.statement}" for c in case.claims if c.grade is Grade.FACT],
        inferences=[f"[{c.id}] {c.statement}" for c in case.claims if c.grade is Grade.INFERENCE],
        assumptions=[f"[{c.id}] {c.statement}" for c in case.claims if c.grade is Grade.ASSUMPTION],
        unknowns=[f"[{u.id}] ({u.criticality.value}) {u.question}" for u in case.unknowns],
        counterargument=_counterargument(ranking, decision),
        red_team=[{
            "id": f.id, "challenge": f.challenge, "finding": f.finding,
            "severity": f.severity.value, "targets_option": f.targets_option,
            "evidence_ids": list(f.evidence_ids),
        } for f in findings],
        confidence=conf.value,
        confidence_band=conf.band,
        confidence_ceiling_applied=conf.ceiling_applied,
        what_would_change_my_mind=_change_my_mind(case, findings, decision),
        what_must_be_true=_must_be_true(case, leader, decision),
        recommended_next_action=_next_action(case, leader, decision),
        reasoning_tags=sorted(set(outcome.tags)),
        option_ranking=[{
            "option_id": s.option_id, "label": s.label, "kind": s.kind.value,
            "score": s.score, "gated_out": s.gated_out,
            "gate_reasons": list(s.gate_reasons), "drivers": list(s.drivers),
        } for s in ranking],
        contradictions=[f"{a} <-> {b} ({why_})" for a, b, why_ in contradictions],
        provenance=dict(provenance),
    )
    rec.provenance["confidence_components"] = conf.components
    rec.provenance["rule_notes"] = outcome.notes
    rec.validate()
    return rec


def _why(case: Case, leader: ScoredOption, outcome: RuleOutcome, demotion: str | None) -> str:
    parts = [f"'{leader.label}' ranks highest on net evidence weight ({leader.score})."]
    if leader.drivers:
        parts.append("Driving rules: " + ", ".join(leader.drivers) + ".")
    gated = [s for s in outcome.gates.items() if s[1]]
    if gated:
        parts.append(
            "Gated out: " + "; ".join(f"{oid} ({r[0]})" for oid, r in gated) + "."
        )
    if demotion:
        parts.append(demotion.capitalize() + ".")
    return " ".join(parts)


def _counterargument(ranking: list[ScoredOption], decision: str) -> str:
    alt = next((s for s in ranking if s.option_id != decision), None)
    if alt is None:
        return "No alternative option was available to argue for."
    base = (
        f"The strongest case against is '{alt.label}' (score {alt.score}"
        f"{', gated out' if alt.gated_out else ''})."
    )
    if alt.gate_reasons:
        base += " It was gated because: " + "; ".join(alt.gate_reasons) + "."
    else:
        base += (
            " If the evidence weighting is wrong - in particular if suppressed "
            "signals (activity, prestige, sentiment) are in fact predictive here - "
            "this option wins instead."
        )
    return base


def _change_my_mind(case: Case, findings: list[RedTeamFinding], decision: str) -> list[str]:
    out: list[str] = []
    for u in case.unknowns:
        out.append(f"Answering: {u.question}")
    for f in findings:
        if f.severity.value == "high":
            out.append(f"Resolving the red-team finding '{f.id}': {f.challenge}")
    for c in case.claims:
        if c.grade is Grade.ASSUMPTION and c.supports_options:
            out.append(f"Disproving the assumption [{c.id}] {c.statement}")
    if not out:
        out.append(
            "Sourced evidence contradicting the decisive claims, or a change in "
            "the cost of reversal."
        )
    return out[:8]


def _must_be_true(case: Case, leader: ScoredOption | None, decision: str) -> list[str]:
    if leader is None or decision == "insufficient_evidence":
        return ["The missing evidence listed above can be obtained at acceptable cost."]
    out = [
        f"The claims supporting '{leader.label}' remain accurate as at {case.as_of or 'now'}.",
    ]
    if leader.kind in (OptionKind.SCALE, OptionKind.CLOSE):
        out.append("The result observed at small scale holds at larger scale.")
        out.append("The cost of reversal is no higher than assumed.")
    if leader.kind is OptionKind.DO_NOTHING:
        out.append("The opportunity is not time-bound, or will recur.")
    for c in case.claims:
        if c.grade is Grade.ASSUMPTION and leader.option_id in c.supports_options:
            out.append(f"Assumption holds: {c.statement}")
    return out[:6]


def _next_action(case: Case, leader: ScoredOption | None, decision: str) -> str:
    if decision == "insufficient_evidence" or leader is None:
        critical = [u for u in case.unknowns if u.criticality.value == "high"]
        target = critical[0].question if critical else (
            case.unknowns[0].question if case.unknowns else "the decisive open question"
        )
        return f"Do not commit. Obtain evidence on: {target}"
    if leader.kind is OptionKind.DO_NOTHING:
        return (
            "Take no action now. Re-open this decision when the cost of inaction "
            "is evidenced or a time-bound trigger appears."
        )
    return f"{leader.label} - and record the outcome so this decision can be scored later."

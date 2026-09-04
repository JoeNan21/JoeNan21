"""Confidence computation.

Implements cognition/confidence-policy.md exactly. Confidence is computed, never
asserted, and never allowed to change the ranking.
"""

from __future__ import annotations

from dataclasses import dataclass

from twin.engine import evidence as ev
from twin.engine import rules as rule_mod
from twin.engine.modes import ModeConfig
from twin.types import Case, Criticality, Grade, RedTeamFinding

FLOOR = 0.05
CAP = 0.90

# Weight applied to unknowns that do not block the recommended option.
UNBLOCKING_UNKNOWN_FACTOR = 1 / 3
# Weight applied to red-team findings aimed at the case rather than the decision.
CASE_LEVEL_FINDING_FACTOR = 0.5


@dataclass(frozen=True)
class ConfidenceResult:
    value: float
    band: str
    ceiling_applied: str | None
    components: dict[str, float]


def band(value: float) -> str:
    if value >= 0.75:
        return "High"
    if value >= 0.55:
        return "Moderate"
    if value >= 0.35:
        return "Low"
    return "Very low / do not act on this alone"


def compute(case: Case, mode: ModeConfig, findings: list[RedTeamFinding],
            score_margin: float, decision: str) -> ConfidenceResult:
    tw = mode.tag_weights
    fact_share = ev.weight_share(case.claims, Grade.FACT, case.as_of, tw)
    assumption_share = ev.weight_share(case.claims, Grade.ASSUMPTION, case.as_of, tw)

    # An unknown that blocks the recommended option undermines it. An unknown
    # the recommendation exists to RESOLVE (the usual case for a proof or
    # qualification recommendation) does not, and charging full weight for it
    # was double-counting: it drove well-founded conservative recommendations
    # to the confidence floor.
    def _unknown_load(crit: Criticality) -> float:
        load = 0.0
        for u in case.unknowns:
            if u.criticality is not crit:
                continue
            load += 1.0 if decision in u.blocks else UNBLOCKING_UNKNOWN_FACTOR
        return load

    med_unknowns = _unknown_load(Criticality.MEDIUM)
    high_unknowns = _unknown_load(Criticality.HIGH)

    contradictions = ev.find_contradictions(case.claims)
    decisive_ids = {c.id for c in case.claims if c.supports_options}
    decisive_contradictions = sum(
        1 for a, b, _ in contradictions if a in decisive_ids or b in decisive_ids
    )

    def _finding_load(sev: str) -> float:
        return sum(
            1.0 if f.targets_option == decision else CASE_LEVEL_FINDING_FACTOR
            for f in findings if f.severity.value == sev
        )

    med_findings = _finding_load("medium")
    high_findings = _finding_load("high")
    leading = rule_mod.is_leading_question(case.question)

    components = {
        "base": 0.50,
        "evidence_support": 0.30 * fact_share,
        "margin_bonus": 0.15 * min(1.0, max(0.0, score_margin) / 2.0),
        "assumption_penalty": -0.25 * assumption_share,
        "unknown_penalty": -(0.10 * med_unknowns + 0.20 * high_unknowns),
        "contradiction_penalty": -0.15 * decisive_contradictions,
        "red_team_penalty": -(0.05 * med_findings + 0.12 * high_findings),
        "framing_penalty": -0.10 if leading else 0.0,
    }
    value = sum(components.values())
    value = max(FLOOR, min(CAP, value))

    # Ceilings: lowest wins.
    ceilings: list[tuple[float, str]] = []
    if high_unknowns:
        ceilings.append((0.60, "high-criticality unknown present"))
    if mode.commercial and not any(
        "economic_buyer" in c.tags and c.polarity > 0 and c.grade is not Grade.ASSUMPTION
        for c in case.claims
    ):
        ceilings.append((0.55, "economic buyer / approval chain unknown"))
    if decisive_contradictions:
        ceilings.append((0.45, "unresolved contradiction on decisive evidence"))
    if decision == "insufficient_evidence":
        ceilings.append((0.35, "recommendation is insufficient_evidence"))
    if not any(c.grade is Grade.FACT for c in case.claims):
        ceilings.append((0.30, "no FACT-graded evidence in the case"))
    if mode.confidence_ceiling is not None:
        ceilings.append(
            (mode.confidence_ceiling, mode.ceiling_reason or f"{mode.name} mode ceiling")
        )

    applied: str | None = None
    if ceilings:
        ceiling, reason = min(ceilings, key=lambda t: t[0])
        if ceiling < value:
            value, applied = ceiling, reason

    value = round(max(FLOOR, value), 3)
    return ConfidenceResult(value=value, band=band(value), ceiling_applied=applied,
                            components={k: round(v, 4) for k, v in components.items()})


def brier(confidence: float, correct: bool) -> float:
    """Brier score for a single prediction. Lower is better."""
    return (confidence - (1.0 if correct else 0.0)) ** 2

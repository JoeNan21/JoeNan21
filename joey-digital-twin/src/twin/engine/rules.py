"""Executable decision rules.

Each rule corresponds to a principle in cognition/decision-rules.md. Rules are
PROVISIONAL HYPOTHESES about how Joey decides, not established facts. They are
revised only on evaluation evidence, never to make a single case pass.

Two rule classes:
  GATES  - can remove an option from contention regardless of score
  SCORERS- adjust option scores and emit reasoning tags
"""

from __future__ import annotations

from dataclasses import dataclass

from twin.engine import signals
from twin.engine.evidence import effective_weight
from twin.engine.modes import ModeConfig
from twin.types import Case, Claim, Grade, Option, OptionKind


@dataclass
class RuleOutcome:
    scores: dict[str, float]
    drivers: dict[str, list[str]]
    gates: dict[str, list[str]]
    tags: list[str]
    notes: list[str]


def _tag_weight(case: Case, mode: ModeConfig, tags: set[str],
                grades: set[Grade] | None = None) -> float:
    total = 0.0
    for c in case.claims:
        if grades and c.grade not in grades:
            continue
        if set(c.tags) & tags:
            signed = 1 if c.polarity > 0 else -1
            total += effective_weight(c, case.as_of, mode.tag_weights) * signed
    return total


def _has(case: Case, tags: set[str], min_grade: Grade = Grade.ASSUMPTION) -> bool:
    order = {Grade.UNKNOWN: 0, Grade.ASSUMPTION: 1, Grade.INFERENCE: 2, Grade.FACT: 3}
    return any(
        set(c.tags) & tags and c.polarity > 0 and order[c.grade] >= order[min_grade]
        for c in case.claims
    )


def _claims_for_option(case: Case, option_id: str) -> list[Claim]:
    return [c for c in case.claims if option_id in c.supports_options]


def apply_rules(case: Case, mode: ModeConfig) -> RuleOutcome:
    """Run all rules over the case. Pure function."""
    scores: dict[str, float] = {o.id: 0.0 for o in case.options}
    drivers: dict[str, list[str]] = {o.id: [] for o in case.options}
    gates: dict[str, list[str]] = {o.id: [] for o in case.options}
    tags: list[str] = []
    notes: list[str] = []

    def bump(option_id: str, delta: float, rule_id: str) -> None:
        if option_id in scores and delta:
            scores[option_id] += delta
            if rule_id not in drivers[option_id]:
                drivers[option_id].append(rule_id)
            if rule_id not in tags:
                tags.append(rule_id)

    # --- Base: direct support/opposition from claims -------------------------
    for c in case.claims:
        w = effective_weight(c, case.as_of, mode.tag_weights)
        # Direction is carried by supports_options / opposes_options. `polarity`
        # describes how the claim asserts its signal (used for aggregation and
        # contradiction detection) and is deliberately not applied twice here.
        for oid in c.supports_options:
            bump(oid, w, "direct_evidence")
        for oid in c.opposes_options:
            bump(oid, -w, "direct_evidence")

    # --- evidence_before_optimism -------------------------------------------
    for o in case.options:
        supporting = _claims_for_option(case, o.id)
        if not supporting:
            continue
        total = sum(effective_weight(c, case.as_of, mode.tag_weights) for c in supporting)
        assumed = sum(
            effective_weight(c, case.as_of, mode.tag_weights)
            for c in supporting if c.grade is Grade.ASSUMPTION
        )
        if total > 0 and assumed / total >= 0.5:
            bump(o.id, -0.6 * (assumed / total) * total, "evidence_before_optimism")
            notes.append(
                f"{o.id}: {assumed / total:.0%} of supporting weight is ASSUMPTION-graded"
            )

    # --- proof_before_scale (GATE) ------------------------------------------
    has_proof = _has(case, set(signals.PROOF), Grade.INFERENCE)
    proof_options = [o for o in case.options if o.kind is OptionKind.PROOF]
    if not has_proof:
        for o in case.options:
            if o.kind in (OptionKind.SCALE, OptionKind.CLOSE) and o.cost >= 0.5:
                if proof_options:
                    gates[o.id].append(
                        "proof_before_scale: no proof evidence and a lower-cost "
                        f"proof option exists ({proof_options[0].id})"
                    )
                    if "proof_before_scale" not in tags:
                        tags.append("proof_before_scale")
                else:
                    bump(o.id, -1.0, "proof_before_scale")
        for o in proof_options:
            bump(o.id, 0.8, "proof_before_scale")

    # --- pain_before_prescription (GATE, commercial modes) -------------------
    if mode.commercial:
        pain = _has(case, {"pain_verified"}, Grade.INFERENCE)
        if not pain:
            qualify = [o for o in case.options if o.kind is OptionKind.QUALIFY]
            for o in case.options:
                if o.kind in (OptionKind.CLOSE, OptionKind.SCALE):
                    if qualify:
                        gates[o.id].append(
                            "pain_before_prescription: pain not verified and a "
                            f"qualification option exists ({qualify[0].id})"
                        )
                    else:
                        bump(o.id, -0.9, "pain_before_prescription")
                    if "pain_before_prescription" not in tags:
                        tags.append("pain_before_prescription")
            for o in qualify:
                bump(o.id, 0.7, "pain_before_prescription")

    # --- outcomes_over_activity ---------------------------------------------
    activity_w = _tag_weight(case, mode, set(signals.ACTIVITY))
    outcome_w = _tag_weight(case, mode, set(signals.OUTCOME))
    if activity_w > 0 and outcome_w <= 0:
        for o in case.options:
            if o.kind in (OptionKind.SCALE, OptionKind.ADVANCE, OptionKind.CLOSE):
                supporting = _claims_for_option(case, o.id)
                if any(set(c.tags) & signals.ACTIVITY for c in supporting):
                    bump(o.id, -0.5, "outcomes_over_activity")
                    notes.append(f"{o.id}: justified by activity with no outcome evidence")

    # --- prestige_is_not_revenue --------------------------------------------
    prestige_w = _tag_weight(case, mode, set(signals.PRESTIGE))
    conversion = _has(case, {"conversion_evidence", "revenue", "booking"}, Grade.INFERENCE)
    if prestige_w > 0 and not conversion:
        for o in case.options:
            if any(set(c.tags) & signals.PRESTIGE for c in _claims_for_option(case, o.id)):
                bump(o.id, -0.5, "prestige_is_not_revenue")
                notes.append(f"{o.id}: prestige evidence without a conversion path")

    # --- find_the_decision_maker --------------------------------------------
    if mode.commercial and not _has(case, {"economic_buyer"}, Grade.INFERENCE):
        tags.append("find_the_decision_maker")
        notes.append("economic buyer not identified")

    # --- do_nothing_is_a_competitor -----------------------------------------
    # Cost of inaction, where evidenced, is what makes acting worth it.
    coi = _tag_weight(case, mode, {"cost_of_inaction"})
    for o in case.options:
        if o.kind is OptionKind.DO_NOTHING:
            bump(o.id, -coi, "do_nothing_is_a_competitor")
            if coi <= 0:
                bump(o.id, 0.4, "do_nothing_is_a_competitor")
                notes.append("no evidenced cost of inaction: do_nothing is credible")

    # --- opportunity cost and reversibility ---------------------------------
    oc = _tag_weight(case, mode, {"opportunity_cost"})
    for o in case.options:
        if o.kind is not OptionKind.DO_NOTHING and oc > 0:
            bump(o.id, -0.3 * oc, "what_must_be_true")
    for o in case.options:
        if o.id in scores and scores[o.id] > 0:
            adjusted = scores[o.id] * o.reversibility_factor
            if adjusted != scores[o.id]:
                scores[o.id] = adjusted
                if "reversibility" not in drivers[o.id]:
                    drivers[o.id].append("reversibility")

    # --- persuasive_is_not_correct ------------------------------------------
    if is_leading_question(case.question):
        tags.append("persuasive_is_not_correct")
        notes.append("question framing is leading; confidence reduced, not raised")

    return RuleOutcome(scores=scores, drivers=drivers, gates=gates, tags=tags, notes=notes)


LEADING_MARKERS = (
    "obviously", "clearly", "surely", "everyone knows", "no-brainer", "no brainer",
    "we should just", "isn't it obvious", "don't you think", "dont you think",
    "confirm that", "tell me why", "this is the right", "must be the right",
    "agree that", "why we should",
)


def is_leading_question(question: str) -> bool:
    """Detect framing that invites agreement rather than analysis."""
    q = question.lower()
    return any(m in q for m in LEADING_MARKERS)


def inject_do_nothing(case: Case) -> Case:
    """Ensure 'do nothing' is always on the ballot.

    cognition/decision-rules.md: do_nothing_is_a_competitor. An option set that
    omits the null action produces a forced choice, not a decision.
    """
    from dataclasses import replace as _replace

    if any(o.kind is OptionKind.DO_NOTHING for o in case.options):
        return case
    injected = Option(
        id="do_nothing",
        label="Do nothing / maintain current position",
        kind=OptionKind.DO_NOTHING,
        cost=0.0,
        reversibility="high",
        injected=True,
    )
    return _replace(case, options=case.options + (injected,))

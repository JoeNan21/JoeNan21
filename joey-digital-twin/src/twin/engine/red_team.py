"""Red-team layer.

Implements cognition/red-team.md. Purpose: resistance to confirmation bias.
Not contrarianism - a check fires on an explicit trigger or not at all.
"""

from __future__ import annotations

from twin.engine import evidence as ev
from twin.engine import rules as rule_mod
from twin.engine import signals
from twin.engine.modes import ModeConfig
from twin.types import (
    Case,
    Criticality,
    Grade,
    OptionKind,
    RedTeamFinding,
    ScoredOption,
    Severity,
)


def run(case: Case, mode: ModeConfig, ranking: list[ScoredOption]) -> list[RedTeamFinding]:
    findings: list[RedTeamFinding] = []
    leader = ranking[0] if ranking else None
    lid = leader.option_id if leader else None
    supporting = [c for c in case.claims if lid and lid in c.supports_options]

    def add(fid: str, challenge: str, finding: str, sev: Severity,
            target: str | None = None, ids: tuple[str, ...] = ()) -> None:
        findings.append(RedTeamFinding(
            id=fid, challenge=challenge, finding=finding, severity=sev,
            targets_option=target, evidence_ids=ids,
        ))

    # what_if_joey_is_wrong
    if rule_mod.is_leading_question(case.question):
        add("leading_question",
            "Is the system agreeing because the question was framed strongly?",
            "The question asserts a conclusion rather than asking one. Framing "
            "strength is not evidence; confidence has been reduced accordingly.",
            Severity.MEDIUM)
        add("what_if_joey_is_wrong",
            "What if Joey is wrong?",
            "The premise embedded in the question has not been independently "
            "verified against the evidence in this case.",
            Severity.MEDIUM, lid)

    # contradicting_evidence
    contradictions = ev.find_contradictions(case.claims)
    if contradictions:
        pairs = ", ".join(f"{a}<->{b} ({why})" for a, b, why in contradictions[:4])
        decisive = {c.id for c in supporting}
        touches_leader = any(
            a in decisive or b in decisive for a, b, _ in contradictions
        )
        add("contradicting_evidence",
            "What contradicts the initial conclusion?",
            f"Conflicting evidence retained and unresolved: {pairs}. "
            "Neither side has been silently trusted.",
            Severity.HIGH if touches_leader else Severity.MEDIUM, lid,
            tuple(sorted({i for a, b, _ in contradictions for i in (a, b)})))

    # emotion_as_evidence
    sentiment = [c for c in supporting if set(c.tags) & signals.SENTIMENT]
    has_outcome = any(set(c.tags) & signals.OUTCOME for c in supporting)
    if sentiment and not has_outcome:
        add("emotion_as_evidence",
            "Is emotion being mistaken for evidence?",
            "The leading option is supported by sentiment/enthusiasm claims with "
            "no outcome evidence. Enthusiasm is not a commercial signal.",
            Severity.HIGH, lid, tuple(c.id for c in sentiment))

    # prestige_as_value
    prestige = [c for c in case.claims if set(c.tags) & signals.PRESTIGE and c.polarity > 0]
    # An ASSUMPTION that attention will convert is not conversion evidence.
    conversion = any(
        set(c.tags) & {"conversion_evidence", "revenue", "booking"}
        and c.polarity > 0 and c.grade is not Grade.ASSUMPTION
        for c in case.claims
    )
    if prestige and not conversion:
        add("prestige_as_value",
            "Is prestige being mistaken for commercial value?",
            "Prestige, reach or profile evidence is present with no evidence that "
            "it has previously converted to revenue here.",
            Severity.HIGH, lid, tuple(c.id for c in prestige))

    # activity_as_progress
    activity = [c for c in case.claims if set(c.tags) & signals.ACTIVITY and c.polarity > 0]
    progress = any(
        set(c.tags) & (signals.OUTCOME | {"stage_advance"}) and c.polarity > 0
        for c in case.claims
    )
    if activity and not progress:
        add("activity_as_progress",
            "Is activity being mistaken for progress?",
            "Effort/volume evidence is present with no evidence of stage "
            "advancement or commercial outcome.",
            Severity.MEDIUM, lid, tuple(c.id for c in activity))

    # correlation_as_causation
    causal = [c for c in case.claims if "causal_claim" in c.tags]
    counterfactual = any("counterfactual" in c.tags for c in case.claims)
    if causal and not counterfactual:
        add("correlation_as_causation",
            "Is correlation being mistaken for causation?",
            "An outcome is attributed to a cause with no counterfactual or "
            "control case in the evidence.",
            Severity.MEDIUM, lid, tuple(c.id for c in causal))

    # missing_evidence
    critical = [u for u in case.unknowns if u.criticality in (Criticality.MEDIUM, Criticality.HIGH)]
    if critical:
        add("missing_evidence",
            "What evidence is missing?",
            "Unresolved: " + "; ".join(
                f"[{u.criticality.value}] {u.question}" for u in critical[:5]
            ),
            Severity.HIGH
            if any(u.criticality is Criticality.HIGH for u in critical)
            else Severity.MEDIUM,
            lid, tuple(u.id for u in critical))

    # cost_of_doing_nothing
    if not any("cost_of_inaction" in c.tags and c.polarity > 0 for c in case.claims):
        add("cost_of_doing_nothing",
            "What is the cost of doing nothing?",
            "No evidenced cost of inaction. Without it, the null action is not "
            "demonstrably worse than acting, and acting carries the cost.",
            Severity.MEDIUM, lid)

    # single_source
    src, share = ev.source_concentration(case.claims, case.as_of, mode.tag_weights)
    if share >= 0.6 and src:
        add("single_source",
            "Is the whole case resting on one source?",
            f"{share:.0%} of evidence weight comes from a single source ({src}). "
            "Independent corroboration has not been established.",
            Severity.MEDIUM, lid)

    # economic buyer, commercial modes
    if mode.commercial and not any(
        "economic_buyer" in c.tags and c.polarity > 0 and c.grade is not Grade.ASSUMPTION
        for c in case.claims
    ):
        add("decision_maker_unknown",
            "Who can actually approve this?",
            "The economic buyer is not identified on evidence. Any commitment "
            "recommendation is provisional until the approval chain is known.",
            Severity.HIGH, lid)

    # opposite_must_be_true - always, for the leader
    if leader:
        add("opposite_must_be_true",
            "What must be true for the opposite decision to be correct?",
            _opposite_conditions(case, leader),
            Severity.LOW, lid)

    # sceptical_executive - high materiality only
    if case.materiality == "high":
        add("sceptical_executive",
            "What would a sceptical executive challenge?",
            "Ask for: the number this changes, by when, measured how, and what "
            "the same effort would return if spent on the current best use.",
            Severity.LOW, lid)

    # unfalsifiable
    if not case.unknowns and not any(c.grade is Grade.FACT for c in case.claims):
        add("unfalsifiable",
            "Could this recommendation ever be shown to be wrong?",
            "The case contains no FACT-graded evidence and no declared unknowns. "
            "There is no observation that would falsify the recommendation.",
            Severity.HIGH, lid)

    return findings


def _opposite_conditions(case: Case, leader: ScoredOption) -> str:
    alt = next((o for o in case.options if o.id != leader.option_id), None)
    alt_label = alt.label if alt else "the alternative"
    conditions = []
    if leader.kind in (OptionKind.SCALE, OptionKind.CLOSE, OptionKind.ADVANCE):
        conditions.append("the supporting evidence is unrepresentative or stale")
        conditions.append("the cost of reversal is higher than assumed")
    if leader.kind is OptionKind.DO_NOTHING:
        conditions.append("the cost of inaction is materially higher than evidenced")
        conditions.append("the opportunity is time-bound and will not recur")
    conditions.append(f"the case for '{alt_label}' rests on evidence not present here")
    joined = "; ".join(conditions)
    return f"For the opposite decision to be correct, at least one must hold: {joined}."


def severity_counts(findings: list[RedTeamFinding]) -> dict[str, int]:
    out = {"low": 0, "medium": 0, "high": 0}
    for f in findings:
        out[f.severity.value] += 1
    return out

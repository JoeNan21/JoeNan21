"""Ranking and gate arbitration.

Order is deliberate (cognition/decision-rules.md):
  1. gates remove options
  2. scores rank survivors
  3. red team may demote the leader
  4. confidence is computed last and never changes the ranking
"""

from __future__ import annotations

from dataclasses import replace

from twin.engine.rules import RuleOutcome
from twin.types import Case, OptionKind, RedTeamFinding, ScoredOption, Severity


def rank(case: Case, outcome: RuleOutcome) -> list[ScoredOption]:
    scored: list[ScoredOption] = []
    for option in case.options:
        gate_reasons = tuple(outcome.gates.get(option.id, ()))
        scored.append(ScoredOption(
            option_id=option.id,
            label=option.label,
            kind=option.kind,
            score=round(outcome.scores.get(option.id, 0.0), 4),
            gated_out=bool(gate_reasons),
            gate_reasons=gate_reasons,
            drivers=tuple(outcome.drivers.get(option.id, ())),
        ))
    # Gated options always rank below non-gated ones, regardless of score.
    scored.sort(key=lambda s: (s.gated_out, -s.score, s.option_id))
    return scored


def margin(ranking: list[ScoredOption]) -> float:
    live = [s for s in ranking if not s.gated_out]
    if len(live) < 2:
        return 0.0
    return round(live[0].score - live[1].score, 4)


def apply_red_team(ranking: list[ScoredOption],
                   findings: list[RedTeamFinding]) -> tuple[list[ScoredOption], str | None]:
    """Demote the leader when red-teaming finds two or more high-severity issues.

    This is the mechanism that lets the Twin return 'no' against an
    attractive-looking case. Without it, red-teaming is decoration.
    """
    live = [s for s in ranking if not s.gated_out]
    if not live:
        return ranking, "all options gated out"
    leader = live[0]
    committal = {OptionKind.SCALE, OptionKind.CLOSE, OptionKind.ADVANCE, OptionKind.EXIT}
    if leader.kind not in committal:
        # The leader is already a conservative option (proof / qualify / do
        # nothing). Demoting it further would be automatic pessimism, which
        # cognition/red-team.md explicitly rules out.
        return ranking, None
    high = [f for f in findings if f.severity is Severity.HIGH
            and (f.targets_option in (None, leader.option_id))]
    if len(high) < 2:
        return ranking, None

    reason = "; ".join(f.id for f in high)
    fallback = next(
        (s for s in live[1:] if s.kind.value in ("do_nothing", "proof", "qualify")),
        None,
    )
    demoted = replace(leader, score=leader.score - 1.0)
    remainder = [s for s in ranking if s.option_id != leader.option_id]
    if fallback is not None:
        new_order = [fallback] + [s for s in remainder if s.option_id != fallback.option_id]
        new_order.insert(1, demoted)
        return new_order, f"leader demoted by red team ({reason})"
    return remainder + [demoted], f"leader demoted by red team ({reason}); no safe fallback"

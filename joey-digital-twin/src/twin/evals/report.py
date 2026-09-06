"""Human-readable evaluation reporting."""

from __future__ import annotations

from twin.evals.scoring import SuiteResult


def render(result: SuiteResult, baseline: SuiteResult | None = None) -> str:
    lines: list[str] = []
    lines.append(f"PROVIDER: {result.provider}")
    lines.append("=" * 72)
    lines.append(result.headline())
    lines.append("")
    lines.append(f"  Strict agreement (exact option)   : {result.strict_agreement_rate:.0%} "
                 f"({result.exact_agreements}/{result.total})")
    lines.append(f"  Material agreement (same kind)    : {result.decision_agreement_rate:.0%} "
                 f"({result.material_agreements}/{result.total})")
    lines.append(f"  Mean reasoning similarity         : {result.mean_reasoning_similarity:.2f}")
    lines.append(f"  Mean red-team recall              : {result.mean_red_team_recall:.2f}")
    lines.append(f"  Mean confidence                   : {result.mean_confidence:.2f}")
    lines.append(f"  Brier score (lower is better)     : {result.brier_score:.3f}")
    lines.append(f"  Missed key evidence (total)       : {result.total_missed_evidence}")
    lines.append("")
    lines.append("PER CASE")
    lines.append("-" * 72)
    for c in result.cases:
        mark = "OK " if c.exact_agreement else ("~  " if c.material_agreement else "X  ")
        lines.append(
            f"{mark}{c.case_id} [{c.mode}] twin={c.twin_decision} actual={c.actual_decision} "
            f"sim={c.reasoning_similarity:.2f} rt={c.red_team_recall:.2f} conf={c.confidence:.2f}"
        )
        if c.missed_evidence:
            lines.append(f"      missed evidence: {', '.join(c.missed_evidence)}")
        if c.red_team_missed:
            lines.append(f"      red-team missed: {', '.join(c.red_team_missed)}")

    if baseline is not None:
        lines.append("")
        lines.append("BASELINE COMPARISON")
        lines.append("-" * 72)
        lines.append(f"  {baseline.provider:<20} agreement={baseline.decision_agreement_rate:.0%} "
                     f"reasoning_sim={baseline.mean_reasoning_similarity:.2f} "
                     f"brier={baseline.brier_score:.3f}")
        lines.append(f"  {result.provider:<20} agreement={result.decision_agreement_rate:.0%} "
                     f"reasoning_sim={result.mean_reasoning_similarity:.2f} "
                     f"brier={result.brier_score:.3f}")
        delta = result.decision_agreement_rate - baseline.decision_agreement_rate
        lines.append(f"  delta (twin - baseline)   : {delta:+.0%}")

    lines.append("")
    lines.append("INTERPRETATION LIMITS")
    lines.append("-" * 72)
    lines.append("  These cases are SYNTHETIC and were authored alongside the rules they")
    lines.append("  test. This measures that the harness works mechanically. It does NOT")
    lines.append("  measure decision fidelity to Joey. No claim about the Twin's accuracy")
    lines.append("  is supported until real historical cases are supplied by Joey.")
    return "\n".join(lines)

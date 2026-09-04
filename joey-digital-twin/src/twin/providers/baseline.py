"""Naive baseline provider.

Exists so that a Decision Agreement Rate has an interpretable floor. A rate of
72% means nothing until you know what a strawman scores on the same suite.

The baseline picks the most committal available option and asserts high
confidence - i.e. optimism without evidence discipline, which is exactly the
behaviour the Twin is supposed to beat.
"""

from __future__ import annotations

from twin.providers.base import ProviderInfo
from twin.types import Case, OptionKind, Recommendation

_PREFERENCE = [
    OptionKind.SCALE, OptionKind.CLOSE, OptionKind.ADVANCE, OptionKind.PROOF,
    OptionKind.QUALIFY, OptionKind.DECLINE, OptionKind.EXIT, OptionKind.DO_NOTHING,
]


class NaiveBaselineProvider:
    def __init__(self) -> None:
        self.info = ProviderInfo(name="baseline_naive", kind="baseline", network=False)

    def decide(self, case: Case) -> Recommendation:
        chosen = None
        for kind in _PREFERENCE:
            chosen = next((o for o in case.options if o.kind is kind), None)
            if chosen:
                break
        if chosen is None:
            rec = Recommendation(
                case_id=case.case_id, mode=case.mode, decision="insufficient_evidence",
                decision_label="No options provided", decision_kind="do_nothing",
                why="No options were supplied.",
                what_would_change_my_mind=["Provide at least one option."],
                recommended_next_action="Supply options.",
                provenance=self.info.as_dict(),
            )
            rec.validate()
            return rec
        rec = Recommendation(
            case_id=case.case_id, mode=case.mode, decision=chosen.id,
            decision_label=chosen.label, decision_kind=chosen.kind.value,
            why="Baseline heuristic: take the most committal action available.",
            evidence_used=[c.id for c in case.claims],
            facts=[c.statement for c in case.claims if c.grade.value == "FACT"],
            confidence=0.85, confidence_band="High",
            counterargument="Not computed by this baseline.",
            what_would_change_my_mind=["Not computed by this baseline."],
            recommended_next_action=f"Proceed with {chosen.label}.",
            reasoning_tags=["baseline_most_committal"],
            provenance=self.info.as_dict(),
        )
        rec.validate()
        return rec

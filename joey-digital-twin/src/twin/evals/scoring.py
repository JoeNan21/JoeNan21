"""Scoring of Twin output against Joey's actual historical decisions.

Agreement alone is insufficient. A system that reaches the right answer for the
wrong reasons has not modelled the decision-maker; it has guessed. Six dimensions
are scored. See docs/evaluation-methodology.md.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from twin.engine.confidence import brier
from twin.evals.loader import HiddenAnswer
from twin.types import Recommendation


@dataclass
class CaseScore:
    case_id: str
    mode: str
    twin_decision: str
    actual_decision: str
    exact_agreement: bool
    material_agreement: bool          # same decision KIND (directionally same)
    reasoning_similarity: float       # Jaccard over reasoning tags
    missed_evidence: list[str] = field(default_factory=list)
    unsupported_assumptions: list[str] = field(default_factory=list)
    red_team_recall: float = 0.0
    red_team_expected: list[str] = field(default_factory=list)
    red_team_missed: list[str] = field(default_factory=list)
    confidence: float = 0.0
    brier: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return round(len(a & b) / len(a | b), 4)


def score_case(rec: Recommendation, answer: HiddenAnswer) -> CaseScore:
    exact = rec.decision == answer.actual_decision
    material = exact or (
        bool(answer.actual_decision_kind)
        and rec.decision_kind == answer.actual_decision_kind
    )

    twin_tags = set(rec.reasoning_tags)
    actual_tags = set(answer.reasoning_tags)
    similarity = _jaccard(twin_tags, actual_tags)

    cited = set(rec.evidence_used)
    missed = sorted(set(answer.key_evidence_ids) - cited)

    # An assumption is "unsupported" when the Twin relied on it to support the
    # decision it made. Assumptions that are merely listed are correct behaviour.
    unsupported = [a for a in rec.assumptions if a]

    expected_rt = set(answer.expected_red_team)
    raised = {f["id"] for f in rec.red_team}
    recall = 1.0 if not expected_rt else round(len(expected_rt & raised) / len(expected_rt), 4)

    return CaseScore(
        case_id=rec.case_id,
        mode=rec.mode,
        twin_decision=rec.decision,
        actual_decision=answer.actual_decision,
        exact_agreement=exact,
        material_agreement=material,
        reasoning_similarity=similarity,
        missed_evidence=missed,
        unsupported_assumptions=unsupported,
        red_team_recall=recall,
        red_team_expected=sorted(expected_rt),
        red_team_missed=sorted(expected_rt - raised),
        confidence=rec.confidence,
        brier=round(brier(rec.confidence, material), 4),
    )


@dataclass
class SuiteResult:
    provider: str
    total: int
    exact_agreements: int
    material_agreements: int
    decision_agreement_rate: float          # PRIMARY KPI (material)
    strict_agreement_rate: float
    mean_reasoning_similarity: float
    mean_red_team_recall: float
    mean_confidence: float
    brier_score: float
    total_missed_evidence: int
    cases: list[CaseScore] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["cases"] = [c.to_dict() for c in self.cases]
        return d

    def headline(self) -> str:
        return (
            f"{self.material_agreements} materially similar decisions / {self.total} "
            f"historical cases = {self.decision_agreement_rate:.0%} Decision Agreement Rate"
        )


def aggregate(provider: str, scores: list[CaseScore]) -> SuiteResult:
    n = len(scores)
    if n == 0:
        return SuiteResult(provider, 0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, [])
    exact = sum(1 for s in scores if s.exact_agreement)
    material = sum(1 for s in scores if s.material_agreement)
    return SuiteResult(
        provider=provider,
        total=n,
        exact_agreements=exact,
        material_agreements=material,
        decision_agreement_rate=round(material / n, 4),
        strict_agreement_rate=round(exact / n, 4),
        mean_reasoning_similarity=round(sum(s.reasoning_similarity for s in scores) / n, 4),
        mean_red_team_recall=round(sum(s.red_team_recall for s in scores) / n, 4),
        mean_confidence=round(sum(s.confidence for s in scores) / n, 4),
        brier_score=round(sum(s.brier for s in scores) / n, 4),
        total_missed_evidence=sum(len(s.missed_evidence) for s in scores),
        cases=scores,
    )

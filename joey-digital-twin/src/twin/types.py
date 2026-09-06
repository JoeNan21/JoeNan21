"""Core domain types.

Standard library only. Immutable where practical: the engine is a pure function
of (case, memory, config), which is what makes evaluation reproducible.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class Grade(StrEnum):
    """Evidence grade. See cognition/evidence-policy.md."""

    FACT = "FACT"
    INFERENCE = "INFERENCE"
    ASSUMPTION = "ASSUMPTION"
    UNKNOWN = "UNKNOWN"


class Criticality(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class OptionKind(StrEnum):
    """What class of action an option represents.

    Used by gates (proof_before_scale) and by 'materially similar' scoring: two
    different option ids of the same kind are directionally the same decision.
    """

    DO_NOTHING = "do_nothing"
    PROOF = "proof"          # small, reversible, evidence-producing
    QUALIFY = "qualify"      # information-gathering before commitment
    ADVANCE = "advance"      # move to next stage
    CLOSE = "close"          # commit / sign / accept
    SCALE = "scale"          # commit at size
    DECLINE = "decline"      # actively say no
    EXIT = "exit"            # withdraw from something already entered


class EvidenceError(ValueError):
    """Invalid evidence construction."""


class EvidencePromotionError(EvidenceError):
    """Attempted to promote an inference or assumption to a fact.

    Forbidden by AGENTS.md section 4. Upgrading a belief requires new sourced
    input, which is a new claim - not a mutation of an existing one.
    """


@dataclass(frozen=True)
class Claim:
    """A single evidential claim about the world."""

    id: str
    statement: str
    grade: Grade
    tags: tuple[str, ...] = ()
    polarity: int = 1                 # +1 supports the tag, -1 opposes it
    source: str | None = None
    date: str | None = None           # ISO-8601
    confidence: float = 0.5           # source-side reliability, 0..1
    relevance: float = 0.5            # relevance to this decision, 0..1
    derived_from: tuple[str, ...] = ()
    contradicts: tuple[str, ...] = ()
    supports_options: tuple[str, ...] = ()
    opposes_options: tuple[str, ...] = ()
    origin: str | None = None         # ingestion run / memory record provenance
    supersedes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.grade is Grade.FACT and not self.source:
            raise EvidenceError(
                f"claim {self.id!r}: FACT requires a source "
                "(cognition/evidence-policy.md rule 2)"
            )
        if self.grade is Grade.INFERENCE and not self.derived_from:
            raise EvidenceError(
                f"claim {self.id!r}: INFERENCE requires derived_from "
                "(cognition/evidence-policy.md rule 3)"
            )
        for name, value in (("confidence", self.confidence), ("relevance", self.relevance)):
            if not 0.0 <= value <= 1.0:
                raise EvidenceError(f"claim {self.id!r}: {name} must be in [0,1], got {value}")
        if self.polarity not in (-1, 1):
            raise EvidenceError(f"claim {self.id!r}: polarity must be -1 or 1")

    @property
    def weight(self) -> float:
        """Effective weight of this claim before mode and temporal adjustment."""
        grade_weight = {
            Grade.FACT: 1.0,
            Grade.INFERENCE: 0.6,
            Grade.ASSUMPTION: 0.3,
            Grade.UNKNOWN: 0.0,
        }[self.grade]
        return grade_weight * self.confidence * self.relevance


@dataclass(frozen=True)
class Unknown:
    """Explicitly missing information."""

    id: str
    question: str
    criticality: Criticality = Criticality.MEDIUM
    blocks: tuple[str, ...] = ()      # option ids this unknown blocks
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class Option:
    """A candidate decision."""

    id: str
    label: str
    kind: OptionKind
    cost: float = 0.0                 # relative, not currency
    reversibility: str = "medium"     # high | medium | low
    injected: bool = False            # added by the engine, not the case author

    @property
    def reversibility_factor(self) -> float:
        return {"high": 1.0, "medium": 0.85, "low": 0.65}.get(self.reversibility, 0.85)


@dataclass(frozen=True)
class Case:
    """A decision case, as seen by the engine.

    This type NEVER carries the hidden answer. The loader constructs it from the
    redacted view only. See src/twin/evals/loader.py.
    """

    case_id: str
    question: str
    mode: str = "general"
    title: str = ""
    as_of: str | None = None
    materiality: str = "medium"       # low | medium | high
    synthetic: bool = False
    options: tuple[Option, ...] = ()
    claims: tuple[Claim, ...] = ()
    unknowns: tuple[Unknown, ...] = ()
    entities: tuple[str, ...] = ()    # memory keys to retrieve against
    notes: str = ""

    def option(self, option_id: str) -> Option | None:
        return next((o for o in self.options if o.id == option_id), None)


@dataclass(frozen=True)
class RedTeamFinding:
    id: str
    challenge: str
    finding: str
    severity: Severity
    targets_option: str | None = None
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ScoredOption:
    option_id: str
    label: str
    kind: OptionKind
    score: float
    gated_out: bool = False
    gate_reasons: tuple[str, ...] = ()
    drivers: tuple[str, ...] = ()     # rule ids that moved this score


@dataclass
class Recommendation:
    """The decision contract.

    Every field is mandatory in the serialised form. Missing fields are a
    contract violation, not a formatting difference.
    """

    case_id: str
    mode: str
    decision: str                      # option id, or 'insufficient_evidence'
    decision_label: str
    decision_kind: str
    why: str
    evidence_used: list[str] = field(default_factory=list)
    facts: list[str] = field(default_factory=list)
    inferences: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    counterargument: str = ""
    red_team: list[dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    confidence_band: str = ""
    confidence_ceiling_applied: str | None = None
    what_would_change_my_mind: list[str] = field(default_factory=list)
    what_must_be_true: list[str] = field(default_factory=list)
    recommended_next_action: str = ""
    reasoning_tags: list[str] = field(default_factory=list)
    option_ranking: list[dict[str, Any]] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)

    REQUIRED_FIELDS = (
        "case_id", "mode", "decision", "decision_label", "decision_kind", "why",
        "evidence_used", "facts", "inferences", "assumptions", "unknowns",
        "counterargument", "red_team", "confidence", "confidence_band",
        "what_would_change_my_mind", "what_must_be_true",
        "recommended_next_action", "reasoning_tags", "option_ranking",
        "contradictions", "provenance",
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    def validate(self) -> None:
        """Raise if the decision contract is incomplete."""
        data = self.to_dict()
        missing = [f for f in self.REQUIRED_FIELDS if f not in data]
        if missing:
            raise ValueError(f"decision contract missing fields: {missing}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence out of range: {self.confidence}")
        if not self.decision:
            raise ValueError("decision must not be empty")
        if not self.what_would_change_my_mind:
            raise ValueError(
                "what_would_change_my_mind must not be empty "
                "(cognition/decision-rules.md: state_what_changes_my_mind)"
            )

"""Retrieval from structured memory.

Deliberately NOT a vector search. v0.1 retrieves on explicit entity references
and controlled tags, so every retrieved item has an auditable reason for being
retrieved. Vector retrieval may later SUPPLEMENT this; it must not replace it.
"""

from __future__ import annotations

from dataclasses import dataclass

from twin.engine.modes import ModeConfig
from twin.memory.schema import MemoryRecord
from twin.memory.store import MemoryStore
from twin.types import Case, Claim, Grade

# Record types that describe *who or what*, not *what is true about a signal*.
ENTITY_TYPES = frozenset({"PERSON", "COMPANY", "ROLE", "RELATIONSHIP", "EVENT"})


@dataclass(frozen=True)
class RetrievalResult:
    claims: tuple[Claim, ...]
    record_ids: tuple[str, ...]
    skipped_superseded: tuple[str, ...]
    reason: str


def retrieve(case: Case, mode: ModeConfig, store: MemoryStore,
             limit: int = 12) -> RetrievalResult:
    """Retrieve memory records relevant to a case and convert them to claims."""
    if not mode.use_personal_memory:
        # modes/caos.md: CAOS must not depend on Joey's personal memory.
        return RetrievalResult((), (), (), f"personal memory disabled for mode '{mode.name}'")

    entities = {e.lower() for e in case.entities}
    case_tags = {t for c in case.claims for t in c.tags}
    scored: list[tuple[float, MemoryRecord]] = []
    skipped: list[str] = []

    for record in store.records:
        if not record.active:
            skipped.append(record.id)
            continue
        score = 0.0
        if record.id.lower() in entities or record.label.lower() in entities:
            score += 2.0
        overlap = len(set(record.tags) & case_tags)
        score += 0.5 * overlap
        if record.type in ("DECISION", "OUTCOME", "LESSON") and overlap:
            score += 0.5  # own history outranks generic best practice
        if score > 0:
            scored.append((score * record.confidence, record))

    scored.sort(key=lambda t: (-t[0], t[1].id))
    top = scored[:limit]

    claims: list[Claim] = []
    for _, record in top:
        grade = Grade(record.grade) if record.grade in Grade.__members__ else Grade.ASSUMPTION
        if grade is Grade.FACT and not record.source:
            grade = Grade.ASSUMPTION
        derived = tuple(record.supersedes) if grade is Grade.INFERENCE else ()
        if grade is Grade.INFERENCE and not derived:
            derived = (record.id,)
        # Entity records are context for retrieval, not assertions about a
        # signal. Carrying their tags through as evidence would let a COMPANY
        # row tagged `economic_buyer` satisfy "the economic buyer is known".
        signal_tags = () if record.type in ENTITY_TYPES else tuple(record.tags)
        claims.append(Claim(
            id=f"mem:{record.id}",
            statement=record.label or record.id,
            grade=grade,
            tags=signal_tags,
            polarity=record.polarity,
            source=record.source or f"memory:{record.provenance}",
            date=record.occurred_at or record.recorded_at,
            confidence=record.confidence,
            relevance=0.6,
            derived_from=derived,
            origin=record.provenance,
        ))

    return RetrievalResult(
        claims=tuple(claims),
        record_ids=tuple(r.id for _, r in top),
        skipped_superseded=tuple(sorted(skipped)),
        reason=f"matched on {len(entities)} entity refs and {len(case_tags)} case tags",
    )

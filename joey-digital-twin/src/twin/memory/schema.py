"""Memory schema.

Structured relational memory, not one giant prompt. Stored locally as JSON in
v0.1; shapes are PostgreSQL-compatible so the same records migrate to
Supabase/Postgres unchanged. See memory/schema/schema.sql.

Every record carries provenance, confidence and temporal fields, because the
system must be able to answer: where did this belief come from?
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

RECORD_TYPES = (
    "PERSON", "COMPANY", "ROLE", "RELATIONSHIP", "EVENT", "DECISION", "CLAIM",
    "EVIDENCE", "OUTCOME", "PREFERENCE", "FRAMEWORK", "LESSON", "COMMITMENT",
)

REQUIRED_FIELDS = ("id", "type", "recorded_at", "provenance")


class SchemaError(ValueError):
    pass


@dataclass
class MemoryRecord:
    """One memory row.

    Fields common to all record types live here; type-specific content lives in
    `attributes` (jsonb in Postgres).
    """

    id: str
    type: str
    label: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    confidence: float = 0.5
    grade: str = "FACT"
    polarity: int = 1                 # +1 asserts its tags, -1 negates them
    source: str | None = None
    provenance: str = ""              # which ingestion run / document
    recorded_at: str = ""             # when the system learned it
    occurred_at: str | None = None    # when it happened in the world
    supersedes: list[str] = field(default_factory=list)
    superseded_by: str | None = None
    contradicts: list[str] = field(default_factory=list)
    synthetic: bool = False
    approved: bool = False            # personal data requires explicit approval

    def validate(self) -> None:
        if self.type not in RECORD_TYPES:
            raise SchemaError(f"{self.id}: unknown record type {self.type!r}")
        for f in REQUIRED_FIELDS:
            if not getattr(self, f, None):
                raise SchemaError(f"{self.id}: missing required field {f!r}")
        if self.grade == "FACT" and not self.source:
            raise SchemaError(f"{self.id}: FACT record requires a source")
        if not 0.0 <= self.confidence <= 1.0:
            raise SchemaError(f"{self.id}: confidence out of range")
        if self.polarity not in (-1, 1):
            raise SchemaError(f"{self.id}: polarity must be -1 or 1")
        if self.superseded_by and self.superseded_by == self.id:
            raise SchemaError(f"{self.id}: record cannot supersede itself")

    @property
    def active(self) -> bool:
        """Superseded records are excluded from retrieval but never deleted."""
        return self.superseded_by is None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MemoryRecord:
        known = {f for f in cls.__dataclass_fields__}  # type: ignore[attr-defined]
        unknown = set(data) - known
        if unknown:
            raise SchemaError(f"{data.get('id')}: unknown fields {sorted(unknown)}")
        return cls(**data)

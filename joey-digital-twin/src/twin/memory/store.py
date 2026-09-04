"""Local JSON memory store.

Deliberately not a database. v0.1 must run with no infrastructure; the schema is
Postgres-shaped so migration is a load, not a rewrite. See docs/architecture.md.
"""

from __future__ import annotations

import json
from pathlib import Path

from twin.memory.schema import MemoryRecord


class MemoryStore:
    def __init__(self, records: list[MemoryRecord] | None = None) -> None:
        self._records: list[MemoryRecord] = records or []

    @classmethod
    def load(cls, root: Path) -> MemoryStore:
        records: list[MemoryRecord] = []
        if root.exists():
            for path in sorted(root.rglob("*.json")):
                if path.parent.name == "schema":
                    continue
                payload = json.loads(path.read_text(encoding="utf-8"))
                items = payload if isinstance(payload, list) else [payload]
                for item in items:
                    record = MemoryRecord.from_dict(item)
                    record.validate()
                    records.append(record)
        return cls(records)

    def __len__(self) -> int:
        return len(self._records)

    @property
    def records(self) -> list[MemoryRecord]:
        return list(self._records)

    def active(self) -> list[MemoryRecord]:
        return [r for r in self._records if r.active]

    def by_id(self, record_id: str) -> MemoryRecord | None:
        return next((r for r in self._records if r.id == record_id), None)

    def contradiction_pairs(self) -> list[tuple[str, str]]:
        out: set[tuple[str, str]] = set()
        ids = {r.id for r in self._records}
        for r in self._records:
            for other in r.contradicts:
                if other in ids:
                    out.add(tuple(sorted((r.id, other))))  # type: ignore[arg-type]
        return sorted(out)

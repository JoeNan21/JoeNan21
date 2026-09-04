"""Deterministic policy provider - the DEFAULT.

Runs the documented decision rules, red team and confidence policy as code. No
network, no credentials, fully reproducible.
"""

from __future__ import annotations

from pathlib import Path

from twin.engine.pipeline import Pipeline
from twin.memory.store import MemoryStore
from twin.providers.base import ProviderInfo
from twin.types import Case, Recommendation


class DeterministicProvider:
    def __init__(self, memory_root: Path | None = None) -> None:
        self.info = ProviderInfo(name="deterministic", kind="deterministic", network=False)
        self._store = MemoryStore.load(memory_root) if memory_root else MemoryStore()
        self._pipeline = Pipeline(self._store)

    def decide(self, case: Case) -> Recommendation:
        return self._pipeline.run(case, self.info)

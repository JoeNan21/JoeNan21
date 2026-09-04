"""Provider abstraction.

The Twin is the product; the LLM is replaceable. Providers implement a narrow
interface so that OpenAI, Anthropic and others can be compared on identical
historical cases.

Critically, the DEFAULT provider makes no network call. If the engine only works
with a frontier model behind it, the reasoning lives in the prompt and cannot be
inspected, tested or reproduced. Keeping the default deterministic forces the
decision policy into code where it can be evaluated.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from twin.types import Case, Recommendation


@dataclass(frozen=True)
class ProviderInfo:
    name: str
    kind: str                # "deterministic" | "llm" | "baseline"
    model: str | None = None
    version: str = "0.1.0"
    network: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "provider": self.name, "kind": self.kind, "model": self.model,
            "version": self.version, "network": self.network,
        }


class Provider(Protocol):
    """A decision provider."""

    info: ProviderInfo

    def decide(self, case: Case) -> Recommendation:
        """Produce a structured recommendation from a redacted case."""
        ...


class ProviderUnavailable(RuntimeError):
    """Provider cannot run (missing credentials, missing dependency, offline)."""

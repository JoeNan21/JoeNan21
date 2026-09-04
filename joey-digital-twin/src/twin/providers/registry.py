"""Provider registry."""

from __future__ import annotations

from pathlib import Path

from twin.providers.base import Provider
from twin.providers.baseline import NaiveBaselineProvider
from twin.providers.deterministic import DeterministicProvider
from twin.providers.llm import (
    AnthropicProvider,
    GenericOpenAICompatibleProvider,
    OpenAIProvider,
)

DEFAULT_PROVIDER = "deterministic"

NAMES = ("deterministic", "baseline_naive", "anthropic", "openai", "openai_compatible")


def build(name: str = DEFAULT_PROVIDER, memory_root: Path | None = None,
          model: str | None = None, allow_network: bool = False) -> Provider:
    if name == "deterministic":
        return DeterministicProvider(memory_root=memory_root)
    if name == "baseline_naive":
        return NaiveBaselineProvider()
    if name == "anthropic":
        return AnthropicProvider(model=model, allow_network=allow_network)
    if name == "openai":
        return OpenAIProvider(model=model, allow_network=allow_network)
    if name == "openai_compatible":
        return GenericOpenAICompatibleProvider(model=model, allow_network=allow_network)
    raise ValueError(f"unknown provider {name!r}; known: {list(NAMES)}")

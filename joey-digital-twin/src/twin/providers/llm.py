"""LLM provider adapters - ARCHITECTED, NOT ENABLED, NOT VALIDATED.

These exist so provider comparison (generic LLM vs Joey Digital Twin) is a
configuration change rather than a rewrite. They are deliberately inert in v0.1:

  - no network call is made at import or construction
  - no credentials are read from anywhere but the environment
  - decide() raises ProviderUnavailable unless a key is present AND the caller
    explicitly opted in

No claim is made that these produce good decisions. They have not been run.
"""

from __future__ import annotations

import os

from twin.providers.base import ProviderInfo, ProviderUnavailable
from twin.types import Case, Recommendation

CONTRACT_INSTRUCTION = """You are a decision-analysis engine, not an assistant.
Return ONLY JSON matching the decision contract with these keys:
decision, decision_label, decision_kind, why, evidence_used, facts, inferences,
assumptions, unknowns, counterargument, red_team, confidence,
what_would_change_my_mind, what_must_be_true, recommended_next_action,
reasoning_tags, option_ranking, contradictions.

Rules you must follow:
- Never present an inference or assumption as a fact.
- Surface contradicting evidence; do not drop it.
- "do nothing" and "insufficient evidence" are valid decisions.
- Do not agree with the framing of the question. Framing is not evidence.
- Confidence must reflect evidence quality, not tone.
"""


class _BaseLLMProvider:
    env_var = ""
    default_model = ""
    vendor = ""

    def __init__(self, model: str | None = None, allow_network: bool = False) -> None:
        self.model = model or self.default_model
        self.allow_network = allow_network
        self.info = ProviderInfo(
            name=self.vendor, kind="llm", model=self.model, network=True,
        )

    def _api_key(self) -> str | None:
        return os.environ.get(self.env_var)

    def available(self) -> bool:
        return bool(self._api_key()) and self.allow_network

    def build_prompt(self, case: Case) -> str:
        """Render the case for an LLM. Never includes hidden evaluation data.

        `Case` structurally cannot carry the hidden block; see
        src/twin/evals/loader.py. tests/test_eval_leakage.py asserts this.
        """
        lines = [CONTRACT_INSTRUCTION, f"MODE: {case.mode}", f"QUESTION: {case.question}",
                 f"AS OF: {case.as_of}", "OPTIONS:"]
        for o in case.options:
            lines.append(
                f"- {o.id} [{o.kind.value}] {o.label} "
                f"(cost={o.cost}, reversibility={o.reversibility})"
            )
        lines.append("EVIDENCE:")
        for c in case.claims:
            lines.append(
                f"- [{c.id}] ({c.grade.value}, source={c.source}, date={c.date}, "
                f"conf={c.confidence}, rel={c.relevance}, tags={list(c.tags)}) {c.statement}"
            )
        lines.append("DECLARED UNKNOWNS:")
        for u in case.unknowns:
            lines.append(f"- [{u.id}] ({u.criticality.value}) {u.question}")
        return "\n".join(lines)

    def decide(self, case: Case) -> Recommendation:
        if not self._api_key():
            raise ProviderUnavailable(
                f"{self.vendor}: {self.env_var} is not set. See .env.example."
            )
        if not self.allow_network:
            raise ProviderUnavailable(
                f"{self.vendor}: network use must be explicitly enabled "
                "(--allow-network). v0.1 defaults to offline, deterministic reasoning."
            )
        raise ProviderUnavailable(
            f"{self.vendor}: transport not implemented in v0.1. This adapter is "
            "architected for provider comparison but has never been run. "
            "Implementing it is a v0.2 milestone (docs/roadmap.md)."
        )


class AnthropicProvider(_BaseLLMProvider):
    env_var = "ANTHROPIC_API_KEY"
    default_model = "claude-sonnet-5"
    vendor = "anthropic"


class OpenAIProvider(_BaseLLMProvider):
    env_var = "OPENAI_API_KEY"
    default_model = "gpt-4.1"
    vendor = "openai"


class GenericOpenAICompatibleProvider(_BaseLLMProvider):
    """Any OpenAI-compatible endpoint (local models, alternative vendors)."""

    env_var = "OPENAI_COMPATIBLE_API_KEY"
    default_model = "unspecified"
    vendor = "openai_compatible"

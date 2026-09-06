"""Provider abstraction: the Twin is the product, the LLM is replaceable."""

from __future__ import annotations

import pytest

from twin.evals import loader
from twin.providers import registry
from twin.providers.base import ProviderUnavailable
from twin.providers.llm import AnthropicProvider, OpenAIProvider


def test_default_provider_is_deterministic_and_offline():
    assert registry.DEFAULT_PROVIDER == "deterministic"
    p = registry.build()
    assert p.info.network is False
    assert p.info.kind == "deterministic"


def test_unknown_provider_raises():
    with pytest.raises(ValueError, match="unknown provider"):
        registry.build("mystery-model")


@pytest.mark.parametrize("name", list(registry.NAMES))
def test_every_registered_provider_can_be_constructed(name):
    assert registry.build(name).info.name


def test_all_providers_share_one_interface(suite_root, memory_root):
    """Comparison across providers requires an identical contract."""
    case = loader.load_case_for_inference(next(suite_root.glob("SYN-001*.json")))
    for name in ("deterministic", "baseline_naive"):
        rec = registry.build(name, memory_root=memory_root).decide(case)
        rec.validate()
        assert rec.case_id == case.case_id


def test_deterministic_provider_is_actually_deterministic(suite_root, memory_root):
    case = loader.load_case_for_inference(next(suite_root.glob("SYN-001*.json")))
    a = registry.build("deterministic", memory_root=memory_root).decide(case).to_json()
    b = registry.build("deterministic", memory_root=memory_root).decide(case).to_json()
    assert a == b


@pytest.mark.parametrize("cls,env", [(AnthropicProvider, "ANTHROPIC_API_KEY"),
                                     (OpenAIProvider, "OPENAI_API_KEY")])
def test_llm_providers_refuse_without_credentials(cls, env, monkeypatch):
    monkeypatch.delenv(env, raising=False)
    with pytest.raises(ProviderUnavailable, match=env):
        cls().decide(None)  # type: ignore[arg-type]


@pytest.mark.parametrize("cls,env", [(AnthropicProvider, "ANTHROPIC_API_KEY"),
                                     (OpenAIProvider, "OPENAI_API_KEY")])
def test_llm_providers_are_honest_about_not_being_implemented(cls, env, monkeypatch):
    """An adapter that has never run must not pretend otherwise."""
    monkeypatch.setenv(env, "test-key")
    with pytest.raises(ProviderUnavailable, match="never been run"):
        cls(allow_network=True).decide(None)  # type: ignore[arg-type]


def test_no_credential_is_read_from_anywhere_but_the_environment(repo_root):
    src = (repo_root / "src" / "twin" / "providers" / "llm.py").read_text(encoding="utf-8")
    assert "os.environ.get" in src
    for pattern in ("sk-", "api_key=\"", "API_KEY = \""):
        assert pattern not in src


def test_env_example_documents_every_provider_variable(repo_root):
    env = (repo_root / ".env.example").read_text(encoding="utf-8")
    for var in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "OPENAI_COMPATIBLE_API_KEY"):
        assert var in env


def test_baseline_exists_so_agreement_rates_have_a_floor():
    """An agreement rate with no baseline is not evidence."""
    assert "baseline_naive" in registry.NAMES
    assert registry.build("baseline_naive").info.kind == "baseline"


def test_provider_info_is_recorded_for_reproducibility(suite_root, memory_root):
    case = loader.load_case_for_inference(next(suite_root.glob("SYN-002*.json")))
    rec = registry.build("deterministic", memory_root=memory_root).decide(case)
    for key in ("provider", "kind", "version", "network"):
        assert key in rec.provenance

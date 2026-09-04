"""v0.1 read-only boundary. AGENTS.md section 3. Do not weaken these."""

from __future__ import annotations

import pytest

from twin.safety import readonly
from twin.safety.readonly import READ_ONLY, Authority, ReadOnlyViolation

FORBIDDEN = [
    "send_email", "send_message", "post_social", "write_crm", "delete_data",
    "purchase", "schedule_meeting", "submit_application", "contact_prospect",
    "financial_transaction", "external_http_write", "modify_memory",
]


def test_no_capability_is_enabled():
    assert sorted(k for k, v in readonly.CAPABILITIES.items() if v) == []


def test_every_forbidden_action_is_named_in_the_capability_surface():
    """A capability that is not named cannot be gated."""
    assert set(FORBIDDEN) <= set(readonly.CAPABILITIES)


@pytest.mark.parametrize("capability", FORBIDDEN)
def test_every_external_write_raises(capability):
    with pytest.raises(ReadOnlyViolation):
        readonly.require(capability)


def test_unknown_capability_raises_rather_than_defaulting_to_allowed():
    with pytest.raises(ReadOnlyViolation, match="unknown capability"):
        readonly.require("launch_missiles")


def test_read_only_authority_denies_even_if_a_flag_were_flipped(monkeypatch):
    monkeypatch.setitem(readonly.CAPABILITIES, "send_email", True)
    assert READ_ONLY.allows("send_email") is False, "READ_ONLY authority must deny regardless"


def test_assert_read_only_fails_loudly_if_a_capability_is_enabled(monkeypatch):
    monkeypatch.setitem(readonly.CAPABILITIES, "purchase", True)
    with pytest.raises(ReadOnlyViolation, match="capabilities enabled"):
        readonly.assert_read_only()


def test_elevated_authority_is_not_reachable_by_default():
    assert READ_ONLY.level == "READ_ONLY"
    assert Authority().level == "READ_ONLY"


def test_pipeline_refuses_to_run_when_a_capability_is_enabled(monkeypatch, suite_root, memory_root):
    from twin.evals import loader
    from twin.providers import registry

    case = loader.load_case_for_inference(next(suite_root.glob("SYN-001*.json")))
    monkeypatch.setitem(readonly.CAPABILITIES, "write_crm", True)
    with pytest.raises(ReadOnlyViolation):
        registry.build("deterministic", memory_root=memory_root).decide(case)


def test_engine_source_contains_no_network_or_write_calls(repo_root):
    """Structural check: the default path cannot reach the network or a shell."""
    banned = ("requests.", "urllib.request", "http.client", "socket.socket",
              "subprocess.", "os.system", "smtplib")
    offenders = []
    for path in (repo_root / "src" / "twin").rglob("*.py"):
        if path.name == "llm.py":
            continue  # adapter is architected, gated and never invoked by default
        text = path.read_text(encoding="utf-8")
        offenders += [f"{path.name}:{b}" for b in banned if b in text]
    assert offenders == []


def test_llm_adapters_never_touch_the_network_without_explicit_opt_in(monkeypatch):
    from twin.providers.base import ProviderUnavailable
    from twin.providers.llm import AnthropicProvider
    from twin.types import Case

    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")
    provider = AnthropicProvider()          # allow_network defaults to False
    with pytest.raises(ProviderUnavailable, match="network use must be explicitly enabled"):
        provider.decide(Case(case_id="X", question="?"))

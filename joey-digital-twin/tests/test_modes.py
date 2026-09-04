"""Mode selection and mode-specific behaviour."""

from __future__ import annotations

import dataclasses

import pytest

from twin.engine.modes import MODES, ModeConfig, UnknownModeError, available_modes, get_mode


def test_all_documented_modes_exist():
    assert set(available_modes()) == {"general", "sales", "career", "sorrento", "caos"}


def test_unknown_mode_raises_rather_than_defaulting_silently():
    """Silently falling back injects the wrong priors without telling anyone."""
    with pytest.raises(UnknownModeError):
        get_mode("marketing")


def test_empty_mode_resolves_to_general():
    assert get_mode(None).name == "general"
    assert get_mode("").name == "general"


def test_mode_names_are_case_insensitive():
    assert get_mode("SALES").name == "sales"


@pytest.mark.parametrize("mode", ["general", "sales", "career", "sorrento", "caos"])
def test_activity_and_prestige_are_suppressed_in_every_mode(mode):
    w = get_mode(mode).tag_weights
    assert w["activity"] < 1.0
    assert w["prestige"] < 1.0
    assert w["sentiment"] < 1.0


def test_sales_mode_prioritises_qualification_signals():
    w = get_mode("sales").tag_weights
    assert w["pain_verified"] > 1.0 and w["economic_buyer"] > 1.0
    assert get_mode("sales").commercial is True


def test_career_mode_requires_opportunity_cost():
    assert "opportunity_cost" in get_mode("career").required_signals


def test_sorrento_mode_prioritises_conversion_over_prestige():
    w = get_mode("sorrento").tag_weights
    assert w["conversion_evidence"] > w["prestige"] * 4


def test_caos_mode_does_not_use_personal_memory():
    """modes/caos.md: CAOS must not depend on Joey's personal data."""
    assert get_mode("caos").use_personal_memory is False


def test_only_caos_disables_personal_memory():
    disabled = [n for n in available_modes() if not MODES[n].use_personal_memory]
    assert disabled == ["caos"]


def test_caos_retrieval_returns_nothing_from_personal_memory(memory_root):
    from twin.engine.retrieval import retrieve
    from twin.memory.store import MemoryStore
    from twin.types import Case

    store = MemoryStore.load(memory_root)
    assert len(store) > 0, "fixture memory is empty; the test would pass vacuously"
    # synthetic=True so the fixture memory is eligible; otherwise this test
    # would pass because synthetic records are excluded from real cases, not
    # because CAOS mode disables personal memory.
    case = Case(case_id="X", question="?", mode="caos", synthetic=True,
                entities=("global-freight-systems",))
    assert retrieve(case, get_mode("general"), store).record_ids, (
        "control: the same case must retrieve under a non-caos mode"
    )
    result = retrieve(case, get_mode("caos"), store)
    assert result.claims == () and result.record_ids == ()


def test_non_caos_mode_does_retrieve(memory_root):
    from twin.engine.retrieval import retrieve
    from twin.memory.store import MemoryStore
    from twin.types import Case

    store = MemoryStore.load(memory_root)
    case = Case(case_id="X", question="?", mode="sales", synthetic=True,
                entities=("global-freight-systems",))
    assert retrieve(case, get_mode("sales"), store).record_ids


def test_mode_config_is_immutable():
    with pytest.raises(dataclasses.FrozenInstanceError):
        get_mode("sales").name = "hacked"  # type: ignore[misc]


def test_every_mode_has_a_markdown_specification(repo_root):
    for name in available_modes():
        assert (repo_root / "modes" / f"{name}.md").exists(), f"modes/{name}.md missing"


def test_mode_config_type_is_frozen():
    assert ModeConfig.__dataclass_params__.frozen  # type: ignore[attr-defined]

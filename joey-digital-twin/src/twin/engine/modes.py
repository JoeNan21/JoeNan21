"""Mode configuration.

Mirrors the prose in modes/*.md. Kept in code (not parsed from markdown) so it is
type-checked and testable; the markdown is the human-readable specification and
the two must be kept in step.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ModeConfig:
    name: str
    tag_weights: dict[str, float] = field(default_factory=dict)
    required_signals: tuple[str, ...] = ()
    inject_do_nothing: bool = True
    use_personal_memory: bool = True
    commercial: bool = False
    confidence_ceiling: float | None = None
    ceiling_reason: str | None = None


_BASE_SUPPRESSION = {
    "activity": 0.4, "effort": 0.4, "volume": 0.4, "reach": 0.4,
    "prestige": 0.3, "brand": 0.3, "exposure": 0.3, "profile": 0.3,
    "sentiment": 0.3, "enthusiasm": 0.3, "gut_feel": 0.3, "excitement": 0.3,
}

MODES: dict[str, ModeConfig] = {
    "general": ModeConfig(
        name="general",
        tag_weights={**_BASE_SUPPRESSION},
    ),
    "sales": ModeConfig(
        name="sales",
        commercial=True,
        tag_weights={
            **_BASE_SUPPRESSION,
            "pain_verified": 1.5, "economic_buyer": 1.4, "approval_chain": 1.2,
            "cost_of_inaction": 1.3, "urgency_evidence": 1.2, "unit_economics": 1.1,
            "budget_confirmed": 1.2, "stage_advance": 1.1,
        },
        required_signals=("pain_verified", "economic_buyer"),
    ),
    "career": ModeConfig(
        name="career",
        tag_weights={
            **_BASE_SUPPRESSION,
            "trajectory": 1.5, "opportunity_cost": 1.4, "compensation": 1.2,
            "employer_quality": 1.2, "decision_maker_access": 1.2,
            "seniority": 1.1, "enterprise_relevance": 1.1,
        },
        required_signals=("opportunity_cost",),
    ),
    "sorrento": ModeConfig(
        name="sorrento",
        commercial=True,
        tag_weights={
            **_BASE_SUPPRESSION,
            "conversion_evidence": 1.5, "unit_economics": 1.4, "utilisation": 1.3,
            "referral_potential": 1.3, "economic_buyer": 1.2, "competition": 1.1,
            "site_visit": 1.1, "date_scarcity": 1.2, "booking": 1.2,
        },
        required_signals=("unit_economics",),
    ),
    "caos": ModeConfig(
        name="caos",
        # Personal memory is disabled: CAOS must not depend on Joey's personal
        # data. See modes/caos.md. Enforced in tests/test_modes.py.
        use_personal_memory=False,
        tag_weights={
            **_BASE_SUPPRESSION,
            "generalisability": 1.4, "personalisation_dependency": 1.3,
        },
    ),
}


class UnknownModeError(ValueError):
    pass


def get_mode(name: str | None) -> ModeConfig:
    """Resolve a mode. Unknown modes raise rather than silently defaulting.

    Silently falling back to 'general' would inject the wrong priors without
    telling anyone, which is worse than failing.
    """
    if not name:
        return MODES["general"]
    key = name.strip().lower()
    if key not in MODES:
        raise UnknownModeError(f"unknown mode {name!r}; known: {sorted(MODES)}")
    return MODES[key]


def available_modes() -> list[str]:
    return sorted(MODES)

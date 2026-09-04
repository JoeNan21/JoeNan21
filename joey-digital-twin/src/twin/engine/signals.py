"""Controlled signal vocabulary.

Claims carry tags from this vocabulary. Rules fire on tag presence, absence and
aggregate weight. A closed vocabulary is what makes reasoning comparable across
cases and scoreable against Joey's actual reasoning.

Deliberate limitation: mapping unstructured reality (an email, a transcript) to
these tags is NOT implemented in v0.1 and is the largest unproven assumption in
the project. See docs/roadmap.md.
"""

from __future__ import annotations

from collections.abc import Iterable

# Signals whose truth decays with time (pricing, availability, pipeline state).
VOLATILE: frozenset[str] = frozenset({
    "pipeline", "availability", "utilisation", "pricing", "staffing",
    "urgency_evidence", "competition", "compensation", "market",
})

# Signals that do not decay (qualifications, contract terms, outcomes).
DURABLE: frozenset[str] = frozenset({
    "qualification", "contract_terms", "outcome", "historical_outcome",
    "unit_economics", "trajectory", "seniority", "employer_quality",
})

# Signals that indicate work happening rather than results (down-weighted).
ACTIVITY: frozenset[str] = frozenset({"activity", "effort", "volume", "reach"})

# Signals that indicate attention/status rather than convertible value.
PRESTIGE: frozenset[str] = frozenset({"prestige", "brand", "exposure", "profile"})

# Signals indicating results.
OUTCOME: frozenset[str] = frozenset({
    "outcome", "historical_outcome", "conversion_evidence", "stage_advance",
    "revenue", "booking",
})

# Signals indicating something has been demonstrated at small scale.
PROOF: frozenset[str] = frozenset({"proof_evidence", "pilot_result", "validated"})

# Emotion / sentiment, which is not evidence.
SENTIMENT: frozenset[str] = frozenset({"sentiment", "enthusiasm", "gut_feel", "excitement"})

# Commercial qualification signals.
QUALIFICATION: frozenset[str] = frozenset({
    "pain_verified", "economic_buyer", "approval_chain", "budget_confirmed",
    "urgency_evidence", "cost_of_inaction",
})

# The full known vocabulary. Unknown tags are permitted but carry base weight and
# are reported, so vocabulary drift is visible rather than silent.
KNOWN: frozenset[str] = (
    VOLATILE | DURABLE | ACTIVITY | PRESTIGE | OUTCOME | PROOF | SENTIMENT
    | QUALIFICATION
    | frozenset({
        "opportunity_cost", "reversibility", "referral_potential", "site_visit",
        "decision_maker_access", "enterprise_relevance", "generalisability",
        "personalisation_dependency", "counterfactual", "causal_claim",
        "risk", "delivery_capacity", "date_scarcity",
    })
)


def is_volatile(tag: str) -> bool:
    return tag in VOLATILE


def unknown_tags(tags: Iterable[str]) -> list[str]:
    """Return tags outside the controlled vocabulary, for reporting."""
    return sorted({t for t in tags if t not in KNOWN})

# Mode: caos

## Boundary — read this first

**CAOS is kept separate from Joey Digital Twin. Do not merge them.**

- CAOS may become a reusable decision architecture or product.
- Joey Digital Twin may become a personalised reference implementation of it.
- Collapsing them into one product requires Joey's **explicit approval**.

This mode exists to keep the boundary visible and testable, not to blur it.

## Enforced separation

| Concern | Joey Digital Twin | CAOS |
|---|---|---|
| Personal identity, memory, values | Yes | **Never** |
| Decision architecture, evidence model, red team | Yes | Yes (generic) |
| Personalisation to one individual | Yes | No |

`caos` mode runs with **personal memory retrieval disabled**. Anything CAOS mode
can conclude, it concludes from the case alone. This is asserted in
`tests/test_modes.py`.

## Focus

Generic decision-architecture questions: what the product is, who it serves,
whether a capability generalises, and whether personalisation is required for a
given decision class.

## Signal weighting

Base weights, plus `generalisability` at 1.4 and `personalisation_dependency`
at 1.3 — the two signals that determine whether something belongs in CAOS or in
the Twin.

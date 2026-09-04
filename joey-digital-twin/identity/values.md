# Values — structure, not content

**Status: EMPTY BY DESIGN.** No values content has been provided or approved.

Values matter here only insofar as they are **decision-relevant**: a value that
never changes an option ranking is decoration.

## Required shape when populated

```yaml
- id: value.<slug>
  statement: "<value>"
  decision_effect: "<how this changes option ranking, concretely>"
  evidence: ["<decision id where this was observed to bind>", ...]
  strength: 0.0-1.0
  conflicts_with: [<id>, ...]
  date: YYYY-MM-DD
```

## Test for admitting a value

Before a value is stored it must pass:

1. Name at least one historical decision where it changed the outcome.
2. Name at least one decision where it would have been overridden, and by what.

A value that survives neither test is an ASSUMPTION and is stored as one.

## Known risk

Stated values and revealed values diverge. Where a stated value conflicts with
observed decisions, the system records the contradiction and does **not** resolve
it silently. See `cognition/evidence-policy.md`.

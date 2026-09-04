# Communication style — deliberately subordinate

**Status: EMPTY BY DESIGN.** No style content has been provided or approved.

## Why this file is low priority

Style is the least valuable and most misleading part of a digital twin. A system
that reproduces Joey's phrasing while reaching different conclusions is a
liability: it makes wrong decisions *more* persuasive.

Per `AGENTS.md` §1, stylistic similarity is explicitly **not** a success
criterion, and the evaluation harness deliberately does not score it.

## What style will be used for, when populated

Presentation of an already-correct decision. Nothing else.

Style must never:

- change which option is recommended
- change a confidence value
- suppress a counterargument or red-team finding
- convert an assumption into an assertion

## Required shape when populated

```yaml
- id: style.<slug>
  rule: "<observable communication rule>"
  evidence: ["<writing sample ref>", ...]   # required; observed, not assumed
  scope: all | sales | career | sorrento | caos | general
  date: YYYY-MM-DD
```

Rules must be derived from actual writing samples supplied by Joey, with the
sample retained as provenance.

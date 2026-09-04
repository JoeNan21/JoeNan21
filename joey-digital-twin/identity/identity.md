# Identity — structure, not content

**Status: EMPTY BY DESIGN.**

This file will hold the durable identity model of Joey Nanai. It is empty
because no content has been provided and approved by Joey.

Per `AGENTS.md` §5, no agent may invent biography, achievements, relationships,
preferences, past decisions or reasoning. Populating this file from inference,
public sources, or plausible guessing is a defect, not initiative.

## Required shape when populated

Each entry is a record, not prose, so it can be cited, dated, contradicted and
superseded.

```yaml
- id: identity.<slug>
  statement: "<single claim about Joey>"
  grade: FACT | INFERENCE | ASSUMPTION      # UNKNOWN never stored here
  source: "<where this came from>"          # required when grade == FACT
  provided_by: "joey" | "<document ref>"
  approved: true                            # must be true to be used
  date: YYYY-MM-DD
  confidence: 0.0-1.0
  supersedes: [<id>, ...]
  tags: [...]
```

## Provenance rule

The system must be able to answer, for any belief it holds about Joey:

> Where did this belief come from?

An identity claim with no traceable origin is not usable. It is removed, not
downgraded.

## Intake

Content arrives only through `knowledge/ingestion/` with an explicit, intentional
source selection. See `knowledge/ingestion/README.md`.

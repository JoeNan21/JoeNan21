# Biography — structure, not content

**Status: EMPTY BY DESIGN.** No biography has been provided or approved.

`AGENTS.md` §5 forbids inventing biography, employment history, achievements or
relationships. This includes "obviously safe" details. There are none.

## Required shape when populated

```yaml
- id: bio.<slug>
  period: {from: YYYY-MM, to: YYYY-MM | null}
  statement: "<fact>"
  grade: FACT
  source: "<CV | document | direct statement from Joey>"
  approved: true
  date_recorded: YYYY-MM-DD
```

## Why biography is needed at all

Not for colour. Only for two decision-relevant purposes:

1. **Constraint modelling** — what options are actually available.
2. **Reference-class reasoning** — what has previously worked or failed for Joey,
   with outcomes, so that recommendations can be checked against his own history
   rather than generic best practice.

Biography that serves neither purpose is not collected.

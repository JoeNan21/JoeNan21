# Memory

Structured relational memory, not a single large prompt.

- `schema/schema.sql` — PostgreSQL-compatible DDL (**not provisioned in v0.1**)
- `schema.py` in `src/twin/memory/` — the runtime record type
- `people/`, `companies/`, `decisions/`, `outcomes/` — local JSON records

## Rules

- Every record carries `provenance`, `source`, `confidence`, `recorded_at`.
- `FACT` records require a `source`.
- Nothing is deleted. Supersession sets `superseded_by`; the old record stays.
- Contradictions are stored, never silently resolved.
- Personal records require `approved: true` before the engine uses them.
- `synthetic: true` marks invented data. All current contents are synthetic.

## Current contents

Synthetic demonstration records only. No real data about Joey, any person or any
company is present, and none may be added without Joey explicitly providing and
approving it (AGENTS.md section 5).

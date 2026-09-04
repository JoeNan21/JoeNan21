# Joey Digital Twin — v0.1

A read-only **decision-intelligence system**. Not a chatbot, and deliberately not a
writing-style imitator.

It models what Joey knows, how he evaluates situations, what he challenges, how he
decides, what evidence would change his mind, how confident he is, and how he
communicates a decision.

## The only test that matters

> Given the same information Joey had at the time, **without seeing his eventual
> decision**, can the Twin independently reach a materially similar conclusion for
> materially similar reasons?

Style is not scored. A system that sounds like Joey and decides differently is a
liability, because it makes wrong decisions more persuasive.

## v0.1 is READ-ONLY

```
READ → RETRIEVE → ANALYSE → CHALLENGE → RECOMMEND → JOEY DECIDES
```

It cannot send email, message anyone, post, touch a CRM, delete data, buy
anything, book a meeting, submit an application, contact a prospect, or move money.
Every capability is `False`, frozen, and enforced by ten tests. Future permissions
are named and gated so the surface is reviewable — not so it can be switched on.

```bash
./scripts/twin safety   # prints the full capability surface
```

## Run it

No installation, no credentials, no network, no database. Python 3.11+.

```bash
cd joey-digital-twin

# One decision
./scripts/twin decide evals/historical_decisions/SYN-001-sales-rollout.json

# Same case in a different mode, as JSON
./scripts/twin decide evals/historical_decisions/SYN-002-career-title.json --mode career --json

# The evaluation suite, against a naive baseline
./scripts/twin eval --baseline

# Inspect
./scripts/twin modes
./scripts/twin memory
./scripts/twin safety
```

Tests:

```bash
pip install -e ".[dev]"   # optional; the engine itself has no dependencies
pytest -q
ruff check .
mypy src/twin
```

These same three checks run in CI on every push and pull request
(`.github/workflows/ci.yml`).

## What comes out

Every recommendation is a 22-field contract: decision, why, evidence used, facts,
inferences, assumptions, unknowns, counterargument, red-team view, confidence and
the ceiling applied, what must be true, what would change the conclusion, the full
option ranking with gate reasons, contradictions, and provenance.

A recommendation missing any field fails validation. `insufficient_evidence` and
`do nothing` are first-class outcomes, not failures.

## Current measured result

```
2 materially similar decisions / 3 historical cases = 67% Decision Agreement Rate
  reasoning similarity 0.47 | red-team recall 1.00 | Brier 0.258
  baseline_naive: 0% agreement, Brier 0.723
```

**This number says nothing about decision fidelity to Joey.** The three cases are
synthetic and were written alongside the rules they exercise, which is circular by
construction. It demonstrates the harness works: it runs inference blind, scores
six dimensions, separates the engine from a strawman, and catches a real
disagreement on `SYN-003`.

No claim that the Twin works is supported until real historical cases exist. See
`docs/roadmap.md` for the full list of unproven claims.

## Layout

```
AGENTS.md                 repository-wide rules for every contributor and agent
identity/                 identity, style, values, biography — EMPTY BY DESIGN
cognition/                decision rules, evidence, red team, confidence, uncertainty
modes/                    sales, career, sorrento, caos, general
memory/                   structured records + PostgreSQL-compatible DDL
knowledge/ingestion/      specification only; no ingester exists yet
evals/historical_decisions/   decision cases (currently synthetic)
src/twin/                 engine, providers, memory, evals, safety, CLI
tests/                    204 tests
docs/                     architecture, evaluation methodology, security, roadmap
```

## Reading order

1. `AGENTS.md` — the rules, including why accuracy beats agreement
2. `docs/architecture.md` — how it works and why, including defects found
3. `docs/evaluation-methodology.md` — how it is scored and what the score does not mean
4. `docs/roadmap.md` — the standing register of unproven claims
5. `docs/security-model.md` — threat model and future permission gates

## Data

All committed data is synthetic and labelled `synthetic: true`. No real biography,
achievements, relationships, preferences, decisions or reasoning about Joey appears
anywhere in this repository, and none may be added without Joey explicitly
providing and approving it.

## Next step

Twenty-five real historical decisions, in the case format, authored before the
rules are touched again. Not more features. Everything here is a measuring
instrument, and it has nothing real to measure yet.

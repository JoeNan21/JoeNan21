# Architecture

## 1. What this system is

A read-only decision-intelligence engine that produces a structured, evidence-graded,
red-teamed recommendation from a decision case, and an evaluation harness that
scores those recommendations against Joey's actual historical decisions without
ever seeing the answer first.

## 2. The pipeline

```
case file (JSON)
   |
   |  loader.load_case_for_inference()   <- hidden answer dropped here
   v
Case  --> retrieval (structured memory, auditable matches)
   |          |
   |          v
   |      enriched claims (provenance retained)
   v
evidence grading  (FACT / INFERENCE / ASSUMPTION / UNKNOWN, temporal weighting,
   |               contradiction detection)
   v
rules  (gates first: proof_before_scale, pain_before_prescription)
   |    (then scorers: 15 provisional principles)
   v
ranking (gated options always rank below live ones)
   |
   v
red team  (13 checks; 2+ high findings can demote a committal leader)
   |
   v
confidence  (documented formula + ceilings; computed last, never reorders)
   |
   v
decision contract (22 mandatory fields, validated)
```

Every stage is a pure function. The same case and the same configuration produce
byte-identical output — asserted in `tests/test_pipeline.py`.

## 3. Material deviations from the requested layout

The requested structure mixed prose directories with code directories. Changes made:

| Requested | Built | Reason |
|---|---|---|
| `engine/`, `providers/`, `memory/` as top-level code | `src/twin/engine/`, `src/twin/providers/`, `src/twin/memory/` | A `src` layout stops the repo root shadowing the package and lets tests run against the installed package. The prose directories (`cognition/`, `modes/`, `identity/`, `memory/`, `knowledge/`, `evals/`, `docs/`) stay at top level as specified. |
| `knowledge/ingestion/` with code | `knowledge/ingestion/` with a specification only | Ingestion is not implemented in v0.1. Writing an ingester before any source is approved would violate "explicit ingestion". |
| repo named `joey-digital-twin/` | subdirectory of the existing repository | The host repository already existed. Creating a subdirectory avoids overwriting its root README. |

Additions not requested, each earned:

- **`baseline_naive` provider** — an agreement rate is uninterpretable without a floor.
- **`src/twin/safety/`** — the read-only boundary needs to be a testable object, not a convention.
- **`OptionKind`** — required for "materially similar" scoring and for the gates.
- **Controlled signal vocabulary** (`engine/signals.py`) — makes reasoning comparable across cases and scoreable against Joey's stated reasoning.

## 4. Architecture decisions and rationale

### AD-1: The default provider makes no LLM call

**Decision.** The default and only working provider is a deterministic rule engine.
LLM adapters exist behind the same interface but are inert.

**Rationale.** If the reasoning lives in a prompt, it cannot be inspected, diffed,
unit-tested or reproduced, and every evaluation number becomes a claim about a
model version rather than about the decision policy. Forcing the policy into code
makes it falsifiable. It is also why the whole system runs offline with no
credentials.

**Cost.** The engine cannot read unstructured input. Claims must arrive pre-tagged.
This is the largest limitation in v0.1 and is stated as such in `roadmap.md`.

### AD-2: Structured relational memory, not vectors

**Decision.** Memory is typed records with provenance, in local JSON, shaped for
PostgreSQL. Retrieval matches on explicit entity references and controlled tags.

**Rationale.** Every retrieved item must have an auditable reason for being
retrieved, because the system must be able to answer "where did this belief come
from?". Vector similarity cannot answer that. Vectors may later supplement
retrieval; they must not become the memory system.

### AD-3: No infrastructure in v0.1

**Decision.** No Supabase, no database, no server, no UI. `memory/schema/schema.sql`
holds the Postgres DDL so migration is a load rather than a rewrite.

**Rationale.** Proof before scale. Provisioning infrastructure before the engine
has been shown to make good decisions is exactly the failure the project exists to
detect.

### AD-4: Standard library only

**Decision.** Zero runtime dependencies.

**Rationale.** The engine must run identically on any machine with Python 3.11, in
CI, and offline, with no supply chain and no version drift affecting evaluation
results. Dev tooling (`pytest`, `ruff`, `mypy`) is optional and isolated.

### AD-5: Gates run before scores

**Decision.** `proof_before_scale` and `pain_before_prescription` remove options
from contention regardless of how well they score.

**Rationale.** The failure mode being defended against is "it scores well, so ship
it". A well-scored option that has not been proven at small scale is precisely the
decision this system should refuse to endorse.

### AD-6: Confidence is computed last and never reorders

**Decision.** Confidence is a documented formula with hard ceilings, applied after
ranking.

**Rationale.** If confidence could influence ranking, a confident-sounding case
would win, which is the confirmation-bias loop the system exists to break.

### AD-7: Inference and scoring are separated in time, not just in code

**Decision.** The harness runs every case to completion before reading any hidden
answer, and `Case` has no field capable of holding one.

**Rationale.** Evaluation leakage is the easiest way to fake success and the
hardest to notice afterwards. Structural prevention beats discipline.

### AD-8: "Do nothing" is injected into every case

**Decision.** If a case omits the null action, the engine adds it.

**Rationale.** An option set without the null action produces a forced choice, not
a decision. Doing nothing is a genuine competitor.

## 5. Defects found and fixed during the build

These were found by running the engine, not by reading it. Recorded because they
are the kind of error that silently inflates results.

1. **Contradiction false positives.** Polarity-based detection fired on any two
   claims sharing a tag, so a retrieved COMPANY record appeared to contradict case
   evidence. Now requires the claims to bear on the same option from opposite
   sides. (`tests/test_evidence.py::test_shared_tag_alone_is_not_a_contradiction`)
2. **Entity tag bleed.** Retrieval copied a COMPANY record's retrieval tags onto a
   claim, so a company row tagged `economic_buyer` satisfied "the economic buyer is
   known" and suppressed a red-team finding. Entity records no longer carry signal
   tags.
3. **Confidence double-counting.** Unknowns were charged at full weight against a
   recommendation whose purpose was to resolve them, driving well-founded
   conservative recommendations to the confidence floor (0.05). Blocking unknowns
   now cost full weight; others cost one third.
4. **Memory records had no polarity.** A LESSON recording that profile events had
   *not* converted was imported as a positive assertion of conversion evidence.
5. **Incomplete evidence citation.** The contract cited only the winner's
   supporting claims, hiding the evidence that gated rivals out.
6. **Over-aggressive red-team demotion.** Two high-severity findings demoted any
   leader, including an already-conservative `proof` recommendation — automatic
   pessimism rather than red-teaming. Demotion now applies only to committal
   options.

## 6. Known architectural weaknesses

- **Claims arrive pre-tagged.** The mapping from unstructured reality to the signal
  vocabulary is the hard problem and is not solved. See `roadmap.md`.
- **Rules and fixtures share an author.** Any agreement rate over the synthetic
  suite is circular.
- **No optionality preservation.** The engine has no preference for the cheapest
  reversible action that keeps options open. This is a confirmed failure, visible
  in `SYN-003`, and is deliberately left unfixed — fixing it after seeing one case
  fail would be overfitting (AGENTS.md §8).
- **Weights are hand-set.** Mode tag weights are judgement, not fitted to data.
- **Reasoning similarity is Jaccard over tags** and rewards vocabulary overlap,
  not genuine reasoning equivalence.

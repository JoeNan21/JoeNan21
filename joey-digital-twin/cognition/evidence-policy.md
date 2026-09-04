# Evidence policy

## Grades

| Grade | Definition | Requirement |
|---|---|---|
| `FACT` | Directly observed, documented or stated by a named source | `source` is **mandatory**. Rejected without one. |
| `INFERENCE` | Derived from one or more claims | `derived_from` must name at least one claim id |
| `ASSUMPTION` | Believed without supporting evidence | Must appear in the output's assumptions list |
| `UNKNOWN` | Explicitly identified missing information | Carries a `criticality` |

## Hard rules

1. **No silent promotion.** `promote()` from `INFERENCE`/`ASSUMPTION` to `FACT`
   raises `EvidencePromotionError`. Upgrading requires new sourced input, which
   is a new claim, not a mutation of the old one.
2. **A fact needs a source.** Enforced at construction.
3. **An inference needs parents.** Enforced at construction.
4. **Contradictions are surfaced, never resolved silently.** Where two claims
   conflict, both are carried into the output and the conflict is reported.
5. **Strong language is not evidence.** Confidence expressed in the source text
   does not raise a claim's grade or confidence value.
6. **Joey's assertion is a source, not a proof.** A claim sourced to Joey is a
   `FACT` about what Joey said, and at most an `INFERENCE` about the world.

## Contradiction handling

Two claims contradict when either explicitly lists the other in `contradicts`,
or they carry the same `tag` with opposing `polarity`.

On contradiction the engine:

- keeps both claims
- reduces the effective weight of **both** (neither side is quietly trusted)
- emits a `contradiction` red-team finding
- applies a confidence ceiling if the contradiction touches decisive evidence

Newer does not win by default. Supersession requires an explicit `supersedes`
link recorded by a human or an approved ingestion process.

## Temporal reasoning

Claims carry `date`. Age reduces weight for **volatile** tags (pricing, staffing,
pipeline, availability) and does not reduce weight for **durable** tags
(qualifications, contract terms, historical outcomes). Volatility is declared per
tag in `src/twin/engine/signals.py`, not guessed at runtime.

## Provenance

Every claim retains `source` and `origin` (which ingestion run introduced it), so
the system can answer: *where did this belief come from?*

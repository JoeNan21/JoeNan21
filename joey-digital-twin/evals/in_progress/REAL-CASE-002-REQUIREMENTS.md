# REAL-CASE-002 — validation requirements

Domain: **SORRENTO / COMMERCIAL**. Mode: `sorrento`.

Engine frozen per `../ENGINE-FREEZE.md`, exactly as it scored REAL-CASE-001.
Nothing learned from REAL-CASE-001 has been used to tune it — the fingerprint is
the proof.

## Protocol (unchanged)

```
evidence at decision time
  -> encode          (committed before the run)
  -> validate        (must pass with zero errors)
  -> run Arm A       (deterministic engine, not Claude reasoning)
  -> commit output   (before any reveal)
  -> reveal          (Joey supplies the decision)
  -> score
```

## Gate: the case cannot be run until `twin validate` returns zero errors

```bash
./scripts/twin validate evals/in_progress/REAL-CASE-002-sorrento.json
```

Blocking checks:

| Check | Requirement |
|---|---|
| Structural | Loads; options, claims and unknowns well-formed; a FACT carries a source; an INFERENCE names its parents |
| `as_of` present | Required — hindsight cannot be checked without it |
| No claim after `as_of` | Anything later was not available at decision time |
| No hindsight language | "turned out", "in hindsight", "we later learned", "eventually", … |
| No decision leakage | "we decided", "I chose", "the decision was", … |
| Hidden block coherent | `actual_decision` names a real option; `key_evidence_ids` name real claims |
| **Option reachability** | **Every option must have at least one supporting claim** |

## Option reachability — the REAL-CASE-001 lesson, mechanised

In REAL-CASE-001 v1 two options could not win under any evidence, and that was
caught only by inspection. It is now a hard error, and running the new check
against the committed v1 file reproduces the fault exactly:

```
ERROR  option 'opt_c_accept' is structurally unreachable
ERROR  option 'opt_d_withdraw' is structurally unreachable
```

**The fix is never to manufacture support.** Where the evidence genuinely does
not bear on an option, record a written waiver:

```json
"reachability_exceptions": [
  {"option_id": "opt_x", "reason": "no decision-time evidence bears on this option"}
]
```

A waiver downgrades the error to a warning and leaves a reason in the record. An
empty reason does not satisfy it.

## Encoding discipline carried forward

- Every negative is classified **RESOLVABLE / STRUCTURAL / DISQUALIFYING**, and
  the classification is committed before the run.
- Encoding routes evidence by what it bears on. **Rules decide how much it
  counts.** Withholding evidence from an option to express caution double-counts
  caution the rules already apply.
- The encoding is committed in its own commit, before the engine runs.

## Blindness

Nothing about the outcome may be retrieved, searched, inferred or reconstructed:
not from prior conversations, repository material, email, memory, connectors or
any external source. The case is built solely from the packet Joey supplies.

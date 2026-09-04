# REAL-CASE-001 — evidence-to-option mapping (v2)

Written and committed **before** the v2 engine run, and before Joey's decision is
known. Nothing was retrieved, searched or inferred about the decision.

## Why v2 exists

v1 left **two** options structurally unable to win:

- `opt_d_withdraw` — no claim supported it. Score 0.000.
- `opt_c_accept` — no claim supported it, only opposition. Score −3.703.

v1 is retained permanently as the original run.

## The principle applied

**Encoding routes evidence by what it bears on. Rules decide how much it counts.**

Withholding the pro-side evidence from `opt_c_accept` was an encoding decision
that the *rules* should have been making. The `proof_before_scale` gate and the
unknowns that block commitment already discount committing under uncertainty.
Pre-empting them in the encoding double-counts the same caution and disguises it
as evidence.

The same logic runs the other way: a structural characteristic that bears on a
stated constraint must be allowed to support withdrawal, or withdrawal is not a
real option.

## Classification of every negative

| ID | Concern | Class | Reasoning |
|---|---|---|---|
| **E03** | 200 new sales p.a. minimum | **RESOLVABLE** | The number is fixed, but the concern is *achievability*, and U03/U04 make that an information question. Not inherently disqualifying. |
| **E04** | 100+ employee enterprise/franchise leads reserved exclusively for the Group Manager — Sales | **STRUCTURAL → potentially DISQUALIFYING** | Intrinsic to the company's sales structure, not a candidate-side term; curing it would mean restructuring another person's role. C01 and C03 name enterprise scope and role scope as materially relevant constraints. U06 leaves open whether another path exists. |
| **E05** | Commission monthly in arrears, capped at 12 months post-Live | **STRUCTURAL, not disqualifying** | Intrinsic to the commission design, but C02 establishes no compensation threshold, so incompatibility cannot be shown. |
| **E12** | Overqualification for an SME/channel-partner BDM role | **STRUCTURAL → potentially DISQUALIFYING** | Seniority is intrinsic to the role (E01 + E04). Negotiating a BDM role into a more senior one produces a different role, not a cured term. C01 names trajectory as a constraint. Held as a hypothesis at 0.5 confidence. |
| **E13** | Base salary may fall below desired threshold | **RESOLVABLE** | Compensation is UNKNOWN (U01) and C02 explicitly establishes no threshold. Per the evaluation rule, unknown compensation creates information value, not grounds for withdrawal. |

## Every mapping change from v1

| Claim | v1 | v2 | Why |
|---|---|---|---|
| E07 | supports `continue` | supports `continue`, `accept` | Prior progression and familiarity bear on the opportunity's attractiveness, which bears on committing, not only on continuing. |
| E09 | supports `continue` | supports `continue`, `accept` | Same. Stated interest in the opportunity bears on accepting it. Still tagged `sentiment` and suppressed to 0.3×. |
| E10 | supports `continue` | supports `continue`, `accept` | Same. Still graded ASSUMPTION. |
| E04 | supports `negotiate`; opposes `accept` | **+ supports `withdraw`** | Structural and constraint-relevant per C01/C03. |
| E12 | supports `negotiate`; opposes `accept` | **+ supports `withdraw`** | Structural and constraint-relevant per C01. |
| E03 | unchanged | unchanged | Resolvable. Does not support withdrawal. |
| E05 | unchanged | unchanged | Structural but not constraint-incompatible. |
| E13 | unchanged | unchanged | Resolvable. Unknown compensation must not support withdrawal. |
| E01, E02, E06, E08, E11 | inert | inert | Unchanged. E11 stays unlinked per the packet's instruction that process progression is not evidence of attractiveness. |
| U01–U07 | block `accept` only | unchanged | Continuing and negotiating are how unknowns get resolved; charging them against those options penalises the response to an unknown rather than the unknown. |

## Reachability confirmation

| Option | Supporting claims | Reachable |
|---|---|---|
| `opt_a_continue` | E07, E09, E10 | Yes |
| `opt_b_negotiate` | E03, E04, E12, E13 | Yes |
| `opt_c_accept` | E07, E09, E10 | Yes |
| `opt_d_withdraw` | E04, E12 | Yes |

No option is structurally excluded. Each can win if the evidence weight and the
rules put it first.

## What was NOT done

- No cautionary evidence was routed to `withdraw` merely to give it a score.
  E03, E05 and E13 remain unmapped to withdrawal on the reasoning above.
- **No decision rule, weight, gate, confidence term or mode configuration was
  changed.** The engine is byte-identical to the one that produced the v1 result.
- No claim, grade, confidence, relevance, source, date or unknown was altered.
  v2 differs from v1 only in `supports_options` / `opposes_options`.

## Blindness attestation

This mapping was derived from the evidence packet and the stated constraints
alone. Joey's decision has not been supplied, searched for, retrieved or
inferred. No file, git object, memory record or external source was consulted
for it.

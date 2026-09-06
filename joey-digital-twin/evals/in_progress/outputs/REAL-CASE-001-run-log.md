# REAL-CASE-001 — run log

## Run 1 (2026-09-04, engine at 460dc6e) — VOID, contaminated

Retrieved synthetic fixture memory into a real case:
`mem:meridian-logistics` (COMPANY) and `mem:lesson-multisite-rollout` (LESSON),
matched on tag overlap with E07 (`employer_quality`) and E03 (`risk`).

**Material effect.** The synthetic LESSON carried `historical_outcome` with
positive polarity. The `activity_as_progress` red-team check requires activity
evidence and *no* positive outcome evidence, so the synthetic record satisfied
the outcome condition and **suppressed the finding**. That is precisely the
challenge the evidence packet asked to be preserved: E11 was supplied with the
instruction that progression through a recruitment process is not evidence that
an opportunity is attractive.

Run 1 output: decision `opt_b_negotiate`, confidence 0.22, four red-team
findings, `activity_as_progress` absent.

This run is void and is not the recorded result.

## Fix

`src/twin/engine/retrieval.py` now excludes `synthetic: true` records from any
case where `synthetic` is false, and reports the exclusions in provenance under
`excluded_synthetic_memory`. Two regression tests added
(`tests/test_memory.py`). Two existing tests in `tests/test_modes.py` were
corrected: one of them would otherwise have passed for the wrong reason, since
the new exclusion — not the CAOS rule — would have produced its empty result.

## Run 2 (2026-09-04, corrected engine) — RECORDED RESULT

`excluded_synthetic_memory`: global-freight-systems, lesson-multisite-rollout,
lesson-profile-events-current, meridian-logistics. Retrieved memory: none.

Decision `opt_b_negotiate` (kind `qualify`), confidence 0.173.
Five red-team findings, `activity_as_progress` now present.

The decision is unchanged between runs; confidence and the red-team set are not.

## Status

Arm A only. Arms B and C are not implemented. The hidden block is empty. This
case has not been scored and must not be until the decision is supplied
separately and locked.

---

## Run 3 (2026-09-04, v2 encoding, same engine as run 2) — RECORDED RESULT

Encoding v2 committed at `3fe1b97` before this run. Mapping rationale in
`../REAL-CASE-001-mapping.md`. Engine unchanged from run 2.

```
DECISION    opt_b_negotiate  [qualify]
CONFIDENCE  0.165  (Very low / do not act on this alone), no ceiling applied

RANKING     2.163  opt_b_negotiate    [qualify]
            0.982  opt_d_withdraw     [decline]
            0.873  opt_a_continue     [advance]
            0.400  do_nothing         [do_nothing]
           -2.830  opt_c_accept       [close]

RED TEAM    activity_as_progress (medium), missing_evidence (high),
            cost_of_doing_nothing (medium), opposite_must_be_true (low),
            sceptical_executive (low)

MEMORY      retrieved: none; synthetic excluded: 4
```

### v1 vs v2

| | v1 | v2 |
|---|---|---|
| Decision | `opt_b_negotiate` | `opt_b_negotiate` |
| Confidence | 0.173 | 0.165 |
| Runner-up | `opt_a_continue` (0.873) | **`opt_d_withdraw` (0.982)** |
| `opt_c_accept` | −3.703, unreachable | −2.830, reachable |
| `opt_d_withdraw` | 0.000, unreachable | 0.982, reachable |
| Red-team findings | identical | identical |

The recommendation is stable across both encodings. What changed is the shape of
the alternative: with withdrawal reachable, it becomes the strongest case
against, displacing "continue on the presented structure".

That is the more informative result. It says the evidence supporting continued
engagement is thinner than the structural case for stepping away, and that the
gap between them is carried by `opt_b_negotiate` resolving what neither
alternative resolves.

### Interpretation limits

- Arm A only. Arms B and C are not implemented, so no claim about a digital twin
  is supported.
- n = 1. Nothing may be concluded about decision fidelity from this case.
- Confidence 0.165 is the engine reporting that seven high-criticality unknowns
  leave it close to the floor. That is the intended behaviour, not a defect.
- The case remains unscored. The hidden block is empty.

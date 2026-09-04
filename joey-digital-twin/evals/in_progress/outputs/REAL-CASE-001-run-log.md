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

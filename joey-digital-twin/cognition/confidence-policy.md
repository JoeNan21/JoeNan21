# Confidence policy

Confidence is **computed**, never asserted. The formula lives in
`src/twin/engine/confidence.py` and is tested in `tests/test_confidence.py`.

## Formula

```
base                    = 0.50

+ evidence_support      = 0.30 * fact_weight_share          # FACT share of decisive weight
+ margin_bonus          = 0.15 * min(1, score_margin / 2.0) # gap to runner-up
- assumption_penalty    = 0.25 * assumption_weight_share
- unknown_penalty       = 0.10 * medium_unknowns + 0.20 * high_unknowns
- contradiction_penalty = 0.15 * contradictions_on_decisive_evidence
- red_team_penalty      = 0.05 * medium_findings + 0.12 * high_findings
- framing_penalty       = 0.10 if the question is leading

clamped to [0.05, 0.90]
```

## Ceilings (applied after clamping, lowest wins)

| Condition | Ceiling |
|---|---|
| Any `high`-criticality unknown | 0.60 |
| Economic buyer / decision-maker unknown (commercial modes) | 0.55 |
| Unresolved contradiction on decisive evidence | 0.45 |
| Recommendation is `insufficient_evidence` | 0.35 |
| No `FACT`-graded evidence at all | 0.30 |

## Why 0.90 is the cap

The system has never been validated at scale. A stated confidence above 0.90
would claim a calibration the project has not earned. The cap is removed only
when calibration data justifies it — not before.

## Bands (for human reading only)

| Range | Label |
|---|---|
| 0.75 – 0.90 | High |
| 0.55 – 0.74 | Moderate |
| 0.35 – 0.54 | Low |
| 0.05 – 0.34 | Very low / do not act on this alone |

## Calibration

Confidence is scored by Brier score against decision correctness across the
historical suite:

```
brier = mean( (confidence - correct)^2 )
```

Lower is better. A system that is 80% confident should be right about 80% of the
time. **Calibration is currently unmeasured** — the suite is synthetic and too
small to calibrate against. Reported values are mechanical, not validated.

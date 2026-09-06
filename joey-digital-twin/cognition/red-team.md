# Red team

Purpose: **resistance to confirmation bias**, not automatic disagreement.

A red-team check that fires on every case is noise. A check that never fires is
decoration. Each check declares an explicit trigger and is tested.

## Checks

| id | Challenge | Trigger |
|---|---|---|
| `what_if_joey_is_wrong` | What if Joey is wrong? | Question asserts a conclusion rather than asking one |
| `contradicting_evidence` | What contradicts the initial conclusion? | Any claim contradicts the leading option |
| `emotion_as_evidence` | Is emotion being mistaken for evidence? | Leading option rests on `sentiment`-tagged claims with no outcome claim |
| `prestige_as_value` | Is prestige being mistaken for commercial value? | `prestige` evidence present, `conversion_evidence` absent |
| `activity_as_progress` | Is activity being mistaken for progress? | `activity` evidence present, `outcome`/`stage_advance` absent |
| `correlation_as_causation` | Is correlation being mistaken for causation? | An outcome claim is attributed to a cause with no counterfactual claim |
| `leading_question` | Is the system agreeing because of strong framing? | Question contains directive/loaded framing markers |
| `sceptical_executive` | What would a sceptical executive challenge? | Always, on `high` materiality cases |
| `opposite_must_be_true` | What must be true for the opposite decision? | Always, for the leading option |
| `missing_evidence` | What evidence is missing? | Any `UNKNOWN` with criticality >= medium |
| `cost_of_doing_nothing` | What is the cost of doing nothing? | `cost_of_inaction` signal absent |
| `single_source` | Is the whole case resting on one source? | >=60% of decisive claim weight shares one source |
| `unfalsifiable` | Could this recommendation ever be shown wrong? | No `what_would_change_my_mind` condition is computable |

## Severity and effect

Each finding carries `severity` in `{low, medium, high}`.

- `low` — reported only
- `medium` — reduces confidence
- `high` — reduces confidence **and** can demote the leading option to
  `do_nothing` or `insufficient_evidence`

Two or more `high` findings against the leading option force a demotion. This is
the mechanism that lets the Twin return "no" against an attractive-looking case.

## What red-teaming must not become

- It must not manufacture objections to appear rigorous.
- It must not oppose whatever Joey prefers. Preference is not a trigger.
- It must not soften a finding because the case is emotionally weighted.

Red-team quality is scored in the evaluation harness against expected findings
per case. See `docs/evaluation-methodology.md`.

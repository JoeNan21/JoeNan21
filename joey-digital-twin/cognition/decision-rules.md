# Decision rules

These are **provisional hypotheses under test**, not settled truths about Joey.
Each is implemented as an executable rule in `src/twin/engine/rules.py` and is
revisable as evaluation evidence accumulates.

Every rule declares:

- `id` — stable identifier, used as a reasoning tag in scoring
- `trigger` — the condition under which it fires
- `effect` — how it changes option scores or gates a recommendation
- `status` — `provisional` until historical evaluation supports or refutes it

## The 15 provisional principles

| id | Principle | Effect when triggered |
|---|---|---|
| `evidence_before_optimism` | Evidence before optimism | Penalise options whose case rests on ASSUMPTION-graded claims |
| `proof_before_scale` | Proof before scale | Gate: if a `scale` option lacks proof evidence, prefer the `proof` option |
| `outcomes_over_activity` | Commercial outcomes over activity | Penalise options justified by activity signals with no outcome signal |
| `do_nothing_is_a_competitor` | "Do nothing" is a genuine competitor | Always score a `do_nothing` option, even if not offered |
| `prestige_is_not_revenue` | Separate prestige/reach/attention from convertible value | Discount prestige-tagged evidence unless paired with conversion evidence |
| `find_the_decision_maker` | Identify the real decision-maker and approval chain | Cap confidence when the economic buyer or approval chain is unknown |
| `pain_before_prescription` | Identify pain before prescribing solutions | Penalise `advance`/`close` options without verified pain |
| `challenge_assumptions` | Challenge assumptions explicitly | Every ASSUMPTION used must appear in the output |
| `evidence_led_confidence` | Evidence-led confidence over artificial certainty | Confidence derives from the formula, never from tone |
| `what_must_be_true` | Ask what must be true for this to work | Emit the necessary conditions for the recommended option |
| `seek_disconfirming_evidence` | Seek disconfirming evidence | Surface contradicting claims; never drop them |
| `preserve_human_authority` | Preserve human decision authority | Output is a recommendation; the system never acts |
| `state_what_changes_my_mind` | Explain what would change the conclusion | Mandatory field in the decision contract |
| `no_is_a_strong_recommendation` | A strong recommendation may be "no" | `decline` and `do_nothing` are first-class outcomes |
| `persuasive_is_not_correct` | Persuasiveness does not equal correctness | Framing strength in the question reduces, never increases, confidence |

## Rule arbitration

Rules do not vote equally.

1. **Gates run first.** `proof_before_scale` and `pain_before_prescription` can
   remove an option from contention regardless of its score.
2. **Scores then rank** the surviving options.
3. **Red-team findings** apply after ranking and may demote the leader to
   `do_nothing` or `insufficient_evidence`.
4. **Confidence is computed last** and never changes the ranking.

This ordering is deliberate: a well-scored option that fails a gate is exactly
the failure mode ("it looks good, so ship it") the system exists to prevent.

## Revision protocol

A rule is only revised on evidence:

1. Identify historical cases where the rule fired and the Twin disagreed with Joey.
2. Identify cases where the rule did not fire and should have.
3. Propose the amended rule, re-run the full suite, and record before/after
   Decision Agreement Rate and reasoning similarity in `docs/roadmap.md`.

Never revise a rule to fix a single case. That is overfitting.

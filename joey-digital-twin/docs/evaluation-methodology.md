# Evaluation methodology

## The question being answered

> Given the same information Joey had at the time, without seeing his eventual
> decision, can the Twin independently reach a materially similar conclusion for
> materially similar reasons?

Not: does it sound like Joey. Style is deliberately unscored.

## Protocol

1. Each case is a JSON file with a context block and a `hidden` block.
2. **Phase 1 — inference.** Every case is run to completion. No hidden data is read.
   `Case` has no field that could hold an answer.
3. **Phase 2 — scoring.** Only now are hidden answers read.
4. Phase separation is asserted by
   `tests/test_eval_leakage.py::test_harness_completes_all_inference_before_reading_any_answer`,
   which records the call order and fails if the phases interleave.
5. Canary tokens are planted in every hidden field and asserted absent from the
   loaded case, the recommendation, and the LLM prompt.

## Primary KPI: Decision Agreement Rate

```
Decision Agreement Rate = materially similar decisions / total historical cases
```

Example: `18 / 25 = 72%`.

**Materially similar** means the Twin chose the same option, or an option of the
same `OptionKind` — a different pilot is directionally the same decision as Joey's
pilot; closing the deal is not.

Both rates are always reported:

- **Strict agreement** — the exact option id.
- **Material agreement** — same option kind. This is the headline KPI.

## Agreement alone is insufficient

A system can agree by luck, by always choosing the conservative option, or by
reasoning that has nothing to do with Joey's. Six dimensions are scored:

| Dimension | Measure | Why |
|---|---|---|
| Decision agreement | strict and material | Did it reach the same conclusion? |
| Reasoning similarity | Jaccard over reasoning tags | For the same reasons? |
| Missed evidence | hidden key evidence not cited | Did it see what mattered? |
| Unsupported assumptions | assumptions relied on | Did it guess and call it analysis? |
| Red-team recall | expected findings raised / expected | Did it challenge properly? |
| Confidence calibration | Brier score | Is its confidence meaningful? |

`test_agreement_without_matching_reasoning_is_visible` exists specifically to prove
that a right answer for the wrong reasons does not score as success.

## Baseline comparison

An agreement rate with no baseline is not evidence. Every run can be compared
against `baseline_naive`, which always takes the most committal available option
and asserts 0.85 confidence — optimism without evidence discipline.

```
./scripts/twin eval --baseline
```

**The generic-LLM comparison specified in the brief has NOT been run.** The LLM
adapters are architected but not implemented, so no claim is made about
Twin-vs-frontier-model performance. That comparison is a v0.2 milestone.

## Current result (synthetic suite, 3 cases)

```
2 materially similar decisions / 3 historical cases = 67% Decision Agreement Rate

  Strict agreement    : 67% (2/3)
  Material agreement  : 67% (2/3)
  Reasoning similarity: 0.47
  Red-team recall     : 1.00
  Brier score         : 0.258
  Missed key evidence : 0

  baseline_naive      : 0% agreement, Brier 0.723
```

## What this number does and does not mean

**It means:** the harness loads cases, runs inference blind, scores six dimensions,
distinguishes the engine from a strawman, and detects a genuine disagreement
(`SYN-003`).

**It does not mean the Twin models Joey.** The cases are synthetic and were
authored by the same process that wrote the rules. That is circular by
construction. Three cases cannot calibrate confidence; the Brier score is
mechanical, not validated.

Quoting 67% as evidence of decision fidelity would be exactly the false signal of
success this project is built to avoid.

## The known failure: SYN-003

The Twin recommended `decline_booking`; the case's recorded decision was
`counter_min_spend`. Both reject the offer as presented, but the Twin discarded a
cheaper, reversible option that keeps the opportunity alive.

**Root cause:** the engine has no rule preferring the lowest-cost reversible action
among options with comparable evidential support — no optionality preservation.

**Not fixed, deliberately.** AGENTS.md §8 forbids tuning a rule against a single
failing fixture. The rule is specified in `roadmap.md` and will be added and
measured against a larger suite, where it can be shown to help or hurt in
aggregate.

## Requirements for a valid real suite

- **25+ cases minimum**, spanning modes.
- **Context frozen at decision time.** Any hindsight in the context block
  invalidates the case.
- **Include decisions Joey now considers wrong.** A suite of only good decisions
  measures nothing about judgement.
- **Include decisions where Joey did nothing.** Otherwise the system learns that
  action is always correct.
- **Cases authored before the rules that would handle them**, or by someone other
  than whoever tunes the rules.
- **Outcomes recorded separately from decisions**, so agreement-with-Joey and
  correctness stay distinguishable. Joey being wrong and the Twin agreeing with him
  is not a success.

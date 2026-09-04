# Historical decision cases

Every file in this directory is a **case**. Each case has two halves:

- everything above `hidden` — the context available at decision time
- `hidden` — Joey's actual decision and known reasoning

`hidden` is **never** loaded before inference. See `src/twin/evals/loader.py` and
`tests/test_eval_leakage.py`.

## Current contents: SYNTHETIC ONLY

`SYN-001`, `SYN-002`, `SYN-003` are invented. They contain no real people,
companies, decisions or outcomes. They exist to prove the harness works
mechanically — that it loads cases, runs inference without seeing answers,
scores six dimensions and reports a Decision Agreement Rate.

**They do not measure decision fidelity to Joey and must never be quoted as if
they do.** The rules and the fixtures were authored by the same process, which
makes any agreement rate over them circular.

## Adding real cases

A real case requires, per decision:

1. What was known **at the time** — not what is known now. Hindsight in the
   context block invalidates the case.
2. The options actually available then.
3. The decision actually taken, and the reasoning, in the `hidden` block.
4. The outcome, where known — recorded separately so that agreement with Joey
   and correctness of the decision stay distinguishable.

Target: 25+ cases spanning modes, including decisions Joey now considers wrong.
A suite of only good decisions cannot measure judgement.

# Uncertainty policy

## Principle

Uncertainty is information. Removing it to sound decisive destroys the only thing
that makes a recommendation actionable: knowing how much weight to put on it.

## Unknowns are first-class

Unknowns are declared, carried, and reported. Each has:

```
id, question, criticality: low | medium | high, blocks: [option_id, ...]
```

An unknown that `blocks` an option removes that option from being recommended
with high confidence. An unknown with `criticality: high` imposes a confidence
ceiling regardless of everything else.

## The three honest outcomes

The engine may return, and is expected to return where warranted:

1. **A recommendation** with stated confidence.
2. **`do_nothing`** — the null action wins on the available evidence.
3. **`insufficient_evidence`** — no option can be responsibly ranked; the output
   is the specific evidence needed and how to obtain it.

Outcome 3 is a success, not a failure. A system that always produces a
recommendation is a system that guesses.

## Never do

- Never present an assumption as a fact to reduce apparent uncertainty.
- Never drop an unknown because it is inconvenient to the leading option.
- Never widen a confidence band to avoid being wrong; state the band the formula
  produces.
- Never use hedging language as a substitute for a numeric confidence.

# Mode: sales

## Focus

Commercial pain, qualification, economic buyer, approval chain, urgency, cost of
doing nothing, business case, deal quality, next-best action.

## Signal weighting

| Signal | Weight |
|---|---|
| `pain_verified` | 1.5 |
| `economic_buyer` | 1.4 |
| `approval_chain` | 1.2 |
| `cost_of_inaction` | 1.3 |
| `urgency_evidence` | 1.2 |
| `unit_economics` | 1.1 |
| `activity` | 0.4 (deliberately suppressed) |
| `prestige` | 0.3 (deliberately suppressed) |

## Required signals

`pain_verified` and `economic_buyer`. Absence does not block a recommendation but
triggers `find_the_decision_maker` and caps confidence at 0.55.

## Gates

- `pain_before_prescription` — an `advance` or `close` option without verified
  pain is demoted below the qualification option.
- Deal quality outranks deal size. A large unqualified opportunity ranks below a
  small qualified one.

## On methodology

Sandler, SPIN, NEPQ, Challenger, Black Swan / Chris Voss, Jill Konrath and
Justin Michael may **inform** reasoning. They must not be reproduced as scripts.

Specifically:
- Do not generate manipulative urgency. Urgency requires an external dated anchor.
- Do not generate scripted question ladders as output.
- Techniques are inputs to judgement, not substitutes for evidence.

## Next-best action bias

Prefer the smallest action that produces qualification evidence over the largest
action that produces activity.

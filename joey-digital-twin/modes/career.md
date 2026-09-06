# Mode: career

## Focus

Role quality, compensation, seniority, trajectory, enterprise relevance,
opportunity cost, employer quality, decision-maker access, and whether an
opportunity advances or weakens positioning.

## Signal weighting

| Signal | Weight |
|---|---|
| `trajectory` | 1.5 |
| `opportunity_cost` | 1.4 |
| `compensation` | 1.2 |
| `employer_quality` | 1.2 |
| `decision_maker_access` | 1.2 |
| `seniority` | 1.1 |
| `enterprise_relevance` | 1.1 |
| `prestige` | 0.4 (deliberately suppressed) |

## Gates

- `prestige_is_not_revenue` applies to titles and brand names: a recognisable
  employer or senior-sounding title is not evidence of trajectory.
- `opportunity_cost` is mandatory. A career case without a stated alternative
  (including staying put) is incomplete; `do_nothing` is injected automatically.

## Specific traps in this mode

- **Title inflation** — seniority in name without scope, budget or reports.
- **Compensation framing** — headline number without variable/at-risk split.
- **Reversibility asymmetry** — leaving is usually irreversible; staying usually
  is not. Weight accordingly.
- **Positioning damage** — a role that pays more and narrows future options is a
  cost, not a gain.

## Confidence

Career decisions are low-frequency and high-consequence. Confidence above 0.75
requires `FACT`-graded evidence on compensation, scope and trajectory.

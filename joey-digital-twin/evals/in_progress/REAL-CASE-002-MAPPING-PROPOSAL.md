# REAL-CASE-002 — proposed option mapping and pre-registered concerns

Written before any evidence exists and before the engine runs. Nothing about the
outcome has been retrieved, searched or inferred.

## Proposed mapping

| # | Real-world option | Kind | Cost* | Reversibility* |
|---|---|---|---|---|
| A | Continue the existing arrangement unchanged | `do_nothing` | 0.0 | high |
| B | Retain the supplier but clarify/redefine scope, deliverables and terms | `advance` | 0.25 | high |
| C | Obtain competing quotes / test the market before deciding | `qualify` | 0.15 | high |
| D | Replace or exit the existing arrangement | `exit` | 0.7 | low |

\* **Proposals requiring confirmation.** Both materially affect scoring.

## Taxonomy mismatches — flagged, not silently absorbed

**M1 — `advance` is a poor fit for option B.** The taxonomy was built for sales
progression (`qualify` → `advance` → `close`). It has **no kind for
"renegotiate an existing ongoing arrangement"**. `advance` is the least-bad fit
but carries pipeline semantics that do not apply to a supplier relationship.
This matters because material agreement is scored on kind: if the recorded
decision is B and the engine picks something else of the same kind, or vice
versa, the score may misrepresent what happened.

**M2 — option A is the null action, so it is a real option, not an injected
one.** In REAL-CASE-001 the engine injected `do_nothing` because none was
offered. Here A *is* `do_nothing`, so nothing is injected. Consequence to be
aware of before the run: the `do_nothing_is_a_competitor` rule grants the null
action **+0.4 when no cost of inaction is evidenced**, and subtracts the weight
of any `cost_of_inaction` evidence that does exist. If no dated evidence
establishes what continuing unchanged was costing, option A receives a
structural bonus. That is the rule behaving as designed, but it is worth knowing
in advance.

**M3 — option C could equally be read as `proof`.** `qualify` is
"information-gathering before commitment"; `proof` is "small, reversible,
evidence-producing". Obtaining quotes is both. `qualify` is proposed because the
purpose is deciding rather than demonstrating. The choice is not neutral: a
`proof` option can trigger the `proof_before_scale` gate against high-cost
`close`/`scale` options. No option here is `close` or `scale`, so the gate
should not bite either way — but the mapping should be a deliberate choice, not
an accident.

**M4 — `exit` rather than `decline`.** `decline` is actively saying no to
something new; `exit` is withdrawing from something already entered. This is an
inherited, ongoing arrangement, so `exit` is correct. Note that low
reversibility applies a 0.65 multiplier to any positive score, so D carries a
structural handicap relative to A, B and C. If exiting was in fact easy to
reverse, say so and the value changes.

## Pre-registered concerns

Recorded now so they are falsifiable rather than post-hoc excuses.

**P1 — likely vocabulary gap.** `sorrento` mode weights `conversion_evidence`
(1.5), `unit_economics` (1.4), `utilisation` (1.3), `referral_potential` (1.3),
`competition` (1.1), `date_scarcity` (1.2). The controlled vocabulary has
**no signal for service-delivery quality, scope clarity, supplier
accountability, or verifiability of work performed**. If the real reasoning
turned on those, the engine may be unable to represent it. Send that evidence
anyway; the gap will be recorded rather than force-fitted.

**P2 — `unit_economics` is the only strongly-weighted signal likely to apply.**
A supplier-cost decision maps onto little else in this mode. Expect a thin
signal profile.

**P3 — the mode is commercial, so `pain_before_prescription` and the
economic-buyer confidence ceiling are active.** Neither should bite here (no
`close`/`scale` option exists), but the 0.55 ceiling applies if no economic
buyer is evidenced.

## Reachability requirement

Every one of A, B, C, D must have at least one supporting claim, or a written
waiver in `reachability_exceptions` giving a reason. **Support must not be
manufactured.** If the decision-time evidence genuinely did not bear on an
option, that is a legitimate waiver and will be recorded as one.

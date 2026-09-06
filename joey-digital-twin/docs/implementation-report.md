# Implementation report — Joey Digital Twin v0.1

Date: 2026-09-04. Environment: Python 3.11.15, Linux, offline. No credentials used,
no infrastructure provisioned, no external accounts connected, no real personal data.

---

## BUILT — what actually works

Verified by running it, not by the files existing.

| Deliverable | State |
|---|---|
| Working repository | `joey-digital-twin/`, 30 source modules, zero runtime dependencies |
| AGENTS.md | 12 sections: proof-before-scale, read-only, evidence discipline, no invented facts, challenge over flattery, preserved uncertainty, evaluation integrity, CAOS separation |
| Architecture documentation | `docs/architecture.md` incl. 8 architecture decisions and 6 defects found during build |
| Read-only decision engine | End-to-end: retrieval → evidence → rules → ranking → red team → confidence → contract |
| Structured evidence model | FACT / INFERENCE / ASSUMPTION / UNKNOWN, enforced at construction; promotion to FACT raises |
| Red-team layer | 13 checks with explicit triggers; 2+ high findings demote a committal leader |
| Provider abstraction | 5 providers behind one interface; default is deterministic and offline |
| Memory schema | 13 record types, provenance mandatory, supersession non-destructive, PostgreSQL DDL |
| Historical evaluation harness | Two-phase (inference completes before any answer is read), 6 scoring dimensions |
| CLI | `twin decide | eval | modes | memory | safety` |
| Automated tests | 204 tests, all passing |
| Synthetic cases | 3, spanning sales / career / sorrento, all labelled synthetic |
| README | Run instructions, current result, and what it does not mean |
| Unproven register | `docs/roadmap.md`, 11 explicitly unproven claims |

**Decision contract:** 22 mandatory fields including counterargument, red-team view,
what must be true, what would change my mind, confidence with the ceiling applied,
full option ranking with gate reasons, contradictions, and provenance. Validation
fails on any missing field. `insufficient_evidence` and `do nothing` are
first-class outcomes.

**Read-only:** 12 named capabilities, all `False` and frozen. `require()` always
raises. The pipeline refuses to run if any capability is flipped on. A structural
test asserts no networking, subprocess or SMTP call exists anywhere in the default
path.

---

## TESTED — tests run and results

```
pytest -q     204 passed
ruff check .  All checks passed
mypy src/twin Success: no issues found in 30 source files
```

Distribution: readonly 21, redteam 21, confidence 20, evidence 19, modes 19,
memory 18, providers 17, contract 16, scoring 16, pipeline 14, cli 13,
eval_leakage 10.

### Evaluation run

```
./scripts/twin eval --baseline

2 materially similar decisions / 3 historical cases = 67% Decision Agreement Rate

  Strict agreement (exact option)   : 67% (2/3)
  Material agreement (same kind)    : 67% (2/3)
  Mean reasoning similarity         : 0.47
  Mean red-team recall              : 1.00
  Mean confidence                   : 0.40
  Brier score (lower is better)     : 0.258
  Missed key evidence (total)       : 0

  SYN-001 [sales]    twin=paid_pilot     actual=paid_pilot        OK
  SYN-002 [career]   twin=decline_offer  actual=decline_offer     OK
  SYN-003 [sorrento] twin=decline_booking actual=counter_min_spend MISS

  baseline_naive : 0% agreement, reasoning similarity 0.00, Brier 0.723
  delta          : +67%
```

**This number does not mean the Twin models Joey.** The cases are synthetic and
were authored by the same process that wrote the rules. It demonstrates the harness
functions: blind inference, six-dimension scoring, separation from a strawman, and
detection of a genuine disagreement.

---

## NOT YET PROVEN

Full register in `docs/roadmap.md`. The material ones:

1. **That the Twin reaches Joey's conclusions.** No real case exists. Unproven.
2. **That it reaches them for Joey's reasons.** Unproven.
3. **That the 15 decision principles describe how Joey decides.** They are
   hypotheses. Untested against any real decision.
4. **That confidence is calibrated.** Three cases cannot calibrate. The Brier score
   is mechanical.
5. **Twin vs generic LLM.** Not run. The adapters are architected but not
   implemented, so no comparison claim is made.
6. **That unstructured input can be mapped to the signal vocabulary.** Not
   attempted. Largest gap in the project.
7. **That mode weightings are correct.** Hand-set judgement, not fitted.
8. **That retrieval surfaces what matters.** Unmeasured.

---

## ARCHITECTURE DECISIONS

1. **Default provider makes no LLM call.** If the reasoning lives in a prompt it
   cannot be inspected, diffed or reproduced, and evaluation becomes a claim about
   a model version. Cost: the engine cannot read unstructured input.
2. **Structured relational memory, not vectors.** Every retrieval must have an
   auditable reason, because the system must answer "where did this belief come
   from?".
3. **No infrastructure.** Local JSON with a Postgres-shaped schema. Migration is a
   load, not a rewrite.
4. **Standard library only.** Identical behaviour anywhere, no supply chain
   affecting results.
5. **Gates before scores.** A well-scored but unproven option is exactly what the
   system should refuse.
6. **Confidence computed last, never reorders.** Otherwise confident-sounding cases
   win, which is the bias loop being defended against.
7. **Inference and scoring separated in time, not just code.** Structural
   prevention of leakage beats discipline.
8. **"Do nothing" injected into every case.** An option set without the null action
   is a forced choice, not a decision.

---

## RED-TEAM FINDINGS

### Against the architecture, before building (each changed the design)

| Risk | Response |
|---|---|
| LLM hides the reasoning; evals unfalsifiable | Deterministic default provider |
| Rules and fixtures share an author → circular success | Added a naive baseline as a floor; labelled the result circular |
| Answer leakage | Structural separation + canary tests |
| Premature infrastructure | Local JSON, no DB, no UI, no vectors |
| Confidence theatre | Documented formula, hard ceilings, Brier scoring |
| Hand-tagged claims dodge the hard problem | Kept, flagged as the largest unproven assumption |

### Against the implementation, found by running it

Six defects, all fixed and regression-tested. Recorded in `docs/architecture.md §5`.
The two that would have inflated results silently:

- **Entity tag bleed** — a retrieved COMPANY record tagged `economic_buyer`
  satisfied "the economic buyer is known" and suppressed a high-severity red-team
  finding. The system would have looked more confident and less challenging than
  the evidence justified.
- **Confidence double-counting** — a `proof` recommendation was penalised for the
  unknowns it existed to resolve, flooring confidence at 0.05. Correct decisions
  were being reported as near-worthless.

### Standing weaknesses

1. **The agreement rate is circular.** Same author for rules and fixtures. The
   number is not evidence about Joey.
2. **Claims arrive pre-tagged.** The genuinely hard problem — unstructured reality
   to structured signals — is untouched. A demo on hand-tagged cases could easily
   be mistaken for a working system.
3. **Confirmed engine gap: no optionality preservation.** `SYN-003` failed because
   the engine has no preference for the cheapest reversible action that keeps an
   opportunity alive. It chose `decline` where the case recorded `counter`.
   **Deliberately not fixed** — AGENTS.md §8 forbids tuning a rule against one
   failing fixture. Specified in the backlog for measurement against a real suite.
4. **Rules are hypotheses stated with the confidence of code.** Reading
   `rules.py` invites belief that these are Joey's actual decision rules. They are
   guesses until measured.
5. **Red-team severity thresholds are unvalidated.** "Two high findings demote" is
   a judgement call that determines when the system says no.
6. **Reasoning similarity rewards vocabulary overlap**, not reasoning equivalence.
   A system could learn to emit the right tags without the right reasoning.

---

## NEXT RECOMMENDED MILESTONE

**Twenty-five real historical decisions from Joey, in the case format, authored
before the rules are touched again.**

Not more features. Not a UI. Not Supabase. Not an LLM integration. Not more rules.

Everything built is a measuring instrument with nothing real to measure. Every
further feature added before real cases exist is unfalsifiable work, and every
additional rule increases the risk of fitting to imagination.

**Input required from Joey:** roughly 20–40 minutes per case — the decision, what
was known at the time, the options actually available, and the actual reasoning.
One to two days of his time in total. It is the only input that unlocks any real
claim about this system.

**Constraints for validity:** include decisions he now considers wrong; include
decisions where he did nothing; freeze context at decision time with no hindsight;
record outcomes separately from decisions so that agreement-with-Joey and
correctness stay distinguishable.

**Success criterion:** a Decision Agreement Rate measured on real cases with a
baseline comparison — whatever the number is. A low number on real cases is worth
more than a high number on synthetic ones.

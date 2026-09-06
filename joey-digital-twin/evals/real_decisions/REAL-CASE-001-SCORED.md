# REAL-CASE-001 — CLOSED

**Ground truth: WITHDRAW / DECLINE** (`opt_d_withdraw`, kind `decline`).
**Arm A recommended NEGOTIATE** (`opt_b_negotiate`, kind `qualify`) on both encodings.

Outputs were committed before the reveal (`7548130`, `9a3ed59`). Scored against
those committed artifacts, not a re-run.

## Scores

| Dimension | v1 | v2 |
|---|---|---|
| Decision agreement (exact) | **FALSE** | **FALSE** |
| Decision agreement (material, same kind) | **FALSE** | **FALSE** |
| Reasoning similarity | **0.00** | **0.00** |
| Missed key evidence | **0** | **0** |
| Red-team recall | 0.667 | 0.667 |
| Confidence | 0.173 | 0.165 |
| Brier | 0.0299 | 0.0272 |

**Decision Agreement Rate: 0/1 = 0%.**

## 1. Decision agreement — MISS

Wrong option and wrong kind. `qualify` vs `decline`. No partial credit: in v2
withdrawal was the runner-up (0.982 against 2.163), but second place is not
agreement and is not scored as such.

## 2. Reasoning alignment — 0.00

Arm A's reasoning tags: `direct_evidence`, `do_nothing_is_a_competitor`,
`proof_before_scale`. Joey's: role/career alignment, opportunity cost of
seniority, compensation compounding rather than causing, evidence over initial
optimism, and a decline held with high confidence.

Zero intersection. Two of Arm A's three tags are artefacts rather than reasoning:
`direct_evidence` is emitted whenever any claim is linked to an option, and
`proof_before_scale` fired against `opt_c_accept`, an option Joey never
seriously weighed at the point of decision.

Four of the concepts Joey used **cannot be expressed by the engine at all**.
Two of them — `no_is_a_strong_recommendation` and `state_what_changes_my_mind` —
are documented principles in `cognition/decision-rules.md` that no rule ever
emits.

## 3. Most-important-factor alignment — MISS

Joey's decisive factor: **ROLE / CAREER ALIGNMENT**, explicitly not compensation.

Arm A has no representation of it. The engine's leading driver was
`direct_evidence` — accumulated weight. It produced no statement resembling
"this role is structurally misaligned with the level at which Joey operates".

## 4. Evidence Arm A weighted correctly

**Evidence selection was exact.** Arm A cited E03, E04, E12, E13 — precisely
Joey's four key items. Zero missed key evidence.

- **E03** (200 deals p.a.) — identified as material. Correct.
- **E04** (100+ reserved to the Group Manager) — identified as material, and in
  v2 as supporting withdrawal. Correct, and it is the single item Arm A came
  closest to reading as Joey did.
- **E12** (overqualification) — identified as material. Correct.
- **E13** (compensation) — identified as material and as secondary. Correct
  ordering, by accident of weight rather than by modelling the dependency.
- **E09/E10/E11** (interest, self-assessed contribution, process progression) —
  correctly suppressed. Joey's own account confirms these did not drive the
  decision.

## 5. Evidence Arm A weighted incorrectly

- **E03 misclassified as RESOLVABLE.** Treated as an achievability question
  awaiting U03/U04. Joey treated volume as a **statement about role level** —
  what kind of operator the job is designed for. The engine has no signal for
  "volume as a proxy for seniority".
- **E04 under-weighted in kind, not degree.** Correctly identified as structural,
  but the engine can only convert structure into additive weight. It cannot
  treat a structural exclusion as disqualifying.
- **E13 mis-ordered.** Joey: compensation *compounds*, it does not *cause*. Arm A
  gave it independent additive weight toward negotiating, implying a raise could
  resolve it. Joey states explicitly that it could not.
- **The seven unknowns were over-weighted.** They pushed toward the
  unknown-resolving option. Joey's position is that the **known** facts were
  already decisive and the unknowns were beside the point.

## 6. Important Joey reasoning Arm A missed

1. **Role level as an identity constraint.** "The level at which I see myself
   operating." No representation.
2. **Enterprise positioning as an asset with an opportunity cost.** Prior success
   in senior/complex/enterprise sales makes a high-volume SME role a step back.
   **This was never in the evidence packet as a claim** — nothing established
   Joey's enterprise track record. E12 was its proxy, graded INFERENCE at 0.5.
3. **Factor dependency.** Compensation compounds rather than causes; fixing it
   alone changes nothing.
4. **A decision can be settled by known facts while unknowns remain.** Joey
   decided *despite* U01–U07. The engine cannot express this.
5. **Clarity as a decision output.** "Progressing gave me greater clarity." Joey
   treated the process as information-gathering that concluded; the engine
   treated remaining unknowns as reason to gather more.

## 7. Reasoning Arm A introduced that Joey did not use

- **`proof_before_scale`** — fired against `opt_c_accept`. Joey never framed this
  as proof-before-commitment.
- **`do_nothing_is_a_competitor`** — the null action scored 0.400 for lack of
  cost-of-inaction evidence. Joey did not weigh "do nothing"; he weighed
  withdrawing, which is an active decision.
- **`cost_of_doing_nothing` red-team finding** — a real challenge, but not one
  Joey engaged.
- **E10 carried as an unsupported assumption** supporting continuation. Joey's
  account gives it no decisional weight.

## 8. Confidence calibration — good score, wrong mechanism

Brier 0.027–0.030 is strong: Arm A was wrong while claiming almost no confidence.

**This flatters it.** Its low confidence came from seven unresolved unknowns —
unknowns Joey considered irrelevant. Joey's own confidence was **HIGH**. The
Twin was near the floor precisely where Joey was most certain.

The metric rewarded uncertainty that arose from misreading the decision. Had
Joey chosen to negotiate, the identical 0.165 would have been badly
under-confident. **A good Brier here is not evidence of calibration.**

## 9. Red-team quality — 0.667

Raised: `missing_evidence` (high), `cost_of_doing_nothing`, `activity_as_progress`,
`opposite_must_be_true`, `sceptical_executive`.

`activity_as_progress` was well-aimed — and Joey independently avoided that trap.
`opposite_must_be_true` named the right question and answered it with a generic
template rather than the structural argument that actually decided the case.

Missed: `structural_constraint_incompatibility` — **no such check exists.** The
challenge that would have found Joey's answer is not implemented.

## 10. Nature of any agreement — NONE at the decision level

| Aspect | Verdict |
|---|---|
| Decision | **Miss.** Not partial, not superficial. |
| Evidence selection | **Substantive.** 4/4 key items, 0 missed. |
| Reasoning | **None.** 0.00 overlap. |
| Confidence | **Accidental.** Right magnitude, wrong cause. |

The diagnostic value is high precisely because evidence selection was perfect
while the conclusion was wrong. That isolates the failure to the reasoning layer.

---

# The central question

> Did Arm A misunderstand the severity of the career/role-alignment constraint by
> treating structural incompatibilities as negotiable uncertainties?

**Yes. Here is precisely where it failed.**

### Failure 1 — the engine has exactly one channel: additive weight

The RESOLVABLE / STRUCTURAL / DISQUALIFYING taxonomy exists only in the mapping
document. **It has no representation in the engine.** A structural exclusion and
a resolvable uncertainty enter the ranking identically, as a number added to an
option's score.

The engine *does* have a mechanism for "this removes an option" — gates, as used
by `proof_before_scale`. There is **no constraint-incompatibility gate**. So E04
could add 0.891 to withdrawal but could never veto anything.

### Failure 2 — negotiate is structurally advantaged and cannot lose

Under an additive model, `negotiate` accumulates support from **every** category
of negative — resolvable ones (E03, E13) *and* structural ones (E04, E12), since
seeking a different arrangement is a legitimate response to both. `withdraw`
accumulates only from the structural subset.

Negotiate 2.163 = E03 + E04 + E12 + E13. Withdraw 0.982 = (E04 + E12) × 0.85.

**Withdrawal is arithmetically incapable of winning whenever any concern is
resolvable.** This is not a weighting error that better numbers would fix. It is
a bias toward preserving optionality built into the model's shape.

### Failure 3 — decision constraints are inert

C01 (career trajectory) and C03 (role scope) sit in the case file and **the
engine never reads them**. Joey's decisive factor was constraint-relative:
*given* that enterprise exposure matters, structural exclusion from it is
disqualifying. With no constraint representation, "disqualifying relative to a
constraint" is not a thought the engine can have.

### Failure 4 — it cannot tell "I don't know enough" from "I know enough to say no"

Seven high-criticality unknowns drove Arm A toward the unknown-resolving option
and drove confidence to 0.165. Joey decided with those same unknowns open,
because the *known* structure was sufficient.

This is the deepest gap. The architecture assumes unresolved unknowns imply an
unresolved decision. Joey demonstrates the opposite: a known structural fact can
settle a decision while everything else stays unknown.

### Was v2 an improvement?

Mechanically yes — withdrawal became reachable and rose to runner-up. **It did
not close the gap**, and Failure 2 explains why it never could. Correct
classification is necessary but not sufficient; the model has no way to act on
the classification.

---

## Pipeline findings vs fidelity findings

**Pipeline (validated by this case):**
- Blind protocol held. Nothing about the decision reached the engine.
- Encoding, mapping and output were committed before reveal, in that order.
- Contamination detection worked; a synthetic-memory leak was caught mid-run.
- Scoring ran against committed artifacts and produced a defensible 0%.
- The validator caught every incompleteness and no false contamination.

**Fidelity: n = 1. Nothing is established.**
0/1 is not evidence that the Twin fails, exactly as 1/1 would not have been
evidence that it works. What this case provides is not a score but four
falsifiable architectural hypotheses, above.

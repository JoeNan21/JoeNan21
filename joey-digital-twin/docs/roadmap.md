# Roadmap and standing list of unproven claims

AGENTS.md §12: if something is unproven, it says "unproven". This file is the
register.

## What is proven

Proven means: implemented, exercised by a passing test, and observed working.

| # | Claim | Evidence |
|---|---|---|
| P1 | The engine produces a complete, validated decision contract | `test_contract.py`, 3 fixtures |
| P2 | Evidence grades are enforced; inference cannot become fact | `test_evidence.py` |
| P3 | Contradictions surface and are never dropped | `test_evidence.py`, `test_memory.py` |
| P4 | Confidence is formula-driven, bounded, and capped by declared ceilings | `test_confidence.py` |
| P5 | Red-team checks fire on triggers and stay quiet on clean cases | `test_redteam.py` |
| P6 | v0.1 cannot take an external action | `test_readonly.py`, 10 tests |
| P7 | Hidden answers cannot reach the engine | `test_eval_leakage.py`, canary tokens |
| P8 | The harness scores six dimensions and reports a Decision Agreement Rate | `test_scoring.py` |
| P9 | Output is reproducible byte-for-byte | `test_pipeline.py` |
| P10 | Providers share one interface; the LLM is replaceable | `test_providers.py` |
| P11 | CAOS mode does not touch personal memory | `test_modes.py` |
| P12 | Strong framing lowers confidence rather than raising it | `test_pipeline.py` |

## What is UNPROVEN

| # | Claim | Status | What would prove it |
|---|---|---|---|
| U1 | The Twin reaches Joey's conclusions | **Unproven** | 25+ real historical cases from Joey |
| U2 | The Twin reaches them for Joey's reasons | **Unproven** | Reasoning similarity above a defined bar on real cases |
| U3 | The 15 decision principles describe how Joey actually decides | **Unproven — they are hypotheses** | Per-rule fire/agree analysis across a real suite |
| U4 | Mode weightings are correct | **Unproven — hand-set judgement** | Sensitivity analysis on a real suite |
| U5 | Confidence is calibrated | **Unproven** | Brier over 25+ real cases; 3 synthetic cases cannot calibrate |
| U6 | The Twin beats a generic frontier LLM | **Not tested. Arms B and C not implemented.** | Three-arm run (see below) on identical cases |
| U6a | That this project is a *digital twin* at all | **Unproven. Arm A is a rules engine, not a model-based twin.** | Arm B existing and being measured |
| U7 | Structured memory beats a large prompt | **Unproven** | A/B the same suite |
| U8 | Retrieval surfaces what matters | **Unproven** | Precision/recall against human-marked relevant records |
| U9 | The signal vocabulary is sufficient | **Unproven** | Tag real cases and count vocabulary misses |
| U10 | Unstructured input can be mapped to the vocabulary | **Not attempted. Largest gap in the project.** | An extractor plus human agreement measurement |
| U11 | The 67% synthetic agreement rate means anything | **It does not.** Circular by construction | Real cases |

### Known defects awaiting remediation

| # | Defect | Status |
|---|---|---|
| D1 | `ModeConfig.required_signals` is declared in `engine/modes.py` and documented as mandatory in `modes/career.md` and `modes/sales.md`, but is never consulted by `engine/rules.py`. A mode's required signal can be absent with no rule firing and no finding raised. | **Open. Deliberately not fixed during REAL-CASE-001** — changing engine behaviour mid-evaluation would invalidate the run. Remediate after that case closes, with a regression test asserting a finding is raised when a required signal is missing. |
| D2 | Synthetic memory records were retrieved into a real case, suppressing a red-team finding. | **Fixed** (`engine/retrieval.py`, regression tests in `tests/test_memory.py`). Recorded in `evals/in_progress/outputs/REAL-CASE-001-run-log.md`. |

## Next milestone (recommended)

**Twenty-five real historical decisions from Joey, in the case format, authored
before the rules are touched again.**

Not more features. Not a UI. Not Supabase. Not an LLM integration.

Everything built so far is a harness for measuring one thing, and that thing cannot
be measured without real cases. Until they exist, every additional feature is
unfalsifiable work.

Cost: roughly 20–40 minutes per case for Joey — the decision, what was known at the
time, the options, and the actual reasoning. Roughly one to two days of his input
in total, and it is the only input that unlocks any real claim about the system.

Success criterion for the milestone: a Decision Agreement Rate measured on real
cases, with a baseline comparison, whatever the number turns out to be. A low
number on real cases is far more valuable than a high number on synthetic ones.

## Backlog, in priority order

1. **Real historical case suite** (above). Blocks everything else.
2. **Optionality preservation rule** — prefer the lowest-cost reversible action
   among options with comparable support. Specified because `SYN-003` failed on it;
   deliberately not implemented until it can be measured against more than one
   case (AGENTS.md §8).
3. **Three-arm evaluation** (U6, U6a). Required design, recorded before any
   implementation so the comparison cannot be shaped after seeing results:

   - **Arm A** — deterministic Joey decision-rules engine. Implemented. It is a
     competing model of Joey, **not** a control.
   - **Arm B** — model-based Joey Digital Twin over the Joey cognition, memory
     and evidence architecture. **Not implemented.**
   - **Arm C** — generic LLM control, identical evidence packet, no Joey
     architecture. **Not implemented.**
   - `baseline_naive` is reported alongside all three as the floor.

   Binding conditions: identical decision-time evidence to every arm; all arms
   blind to the decision; all outputs committed in one commit before the outcome
   is revealed; B and C prompts rendered mechanically from the case file, never
   hand-written; the C prompt fixed and committed before the first run.

   Sequencing: the 25-case suite comes first. Running three arms over three
   synthetic cases would produce a number with no meaning and a strong
   temptation to quote it. Requires a redaction layer before B or C sees real
   personal data (threat T2, `security-model.md`).
4. **Rule attribution analysis** — for each rule, how often it fires and whether
   firing correlates with agreement. This is how U3 gets tested and how rules get
   revised on evidence rather than instinct.
5. **Ingestion** for CVs, notes and transcripts, with explicit source selection and
   retained provenance.
6. **Signal extraction from unstructured text** (U10), measured against human
   tagging before it is trusted.
7. **Postgres/Supabase migration**, only once the local store is genuinely the
   bottleneck.
8. **Permission gates**, only after U1 is proven and all five preconditions in
   `security-model.md` are met.

## Explicitly not planned

- A web UI. The engine is the product.
- Style imitation. It makes wrong decisions more persuasive.
- Vector-only memory. It cannot answer "where did this belief come from?".
- Merging CAOS into the Twin. Requires Joey's explicit approval.

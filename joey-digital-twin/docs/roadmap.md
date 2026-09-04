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
| U6 | The Twin beats a generic frontier LLM | **Not tested. Adapters not implemented.** | Implement adapters, run identical cases |
| U7 | Structured memory beats a large prompt | **Unproven** | A/B the same suite |
| U8 | Retrieval surfaces what matters | **Unproven** | Precision/recall against human-marked relevant records |
| U9 | The signal vocabulary is sufficient | **Unproven** | Tag real cases and count vocabulary misses |
| U10 | Unstructured input can be mapped to the vocabulary | **Not attempted. Largest gap in the project.** | An extractor plus human agreement measurement |
| U11 | The 67% synthetic agreement rate means anything | **It does not.** Circular by construction | Real cases |

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
3. **LLM adapter implementation** + the generic-LLM comparison (U6). Requires a
   redaction layer first (threat T2).
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

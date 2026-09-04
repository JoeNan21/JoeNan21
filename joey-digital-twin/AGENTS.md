# AGENTS.md — Joey Digital Twin

Repository-wide instructions. These apply to every coding agent, every human
contributor, and every automated change in this repository. They override
convenience, speed and stylistic preference.

---

## 1. What this project is

Joey Digital Twin is a **personal decision-intelligence system**, not a chatbot
and not a writing-style imitator.

It progressively models:

- what Joey knows
- how Joey evaluates situations
- what he notices and challenges
- how he makes commercial and strategic decisions
- what evidence changes his mind
- how confident he is
- how he communicates a decision

**Stylistic similarity is not decision similarity.** A system that sounds like
Joey and decides differently is a failure. A system that sounds nothing like
Joey and reaches his conclusions for his reasons is a success.

### The only test that matters

> Given the same information Joey had at the time, **without seeing his eventual
> decision**, can the Twin independently reach a materially similar conclusion
> for materially similar reasons?

Everything else — features, polish, apparent intelligence — is subordinate.

---

## 2. Proof before scale

Do not add capability without evidence the current capability works.

- Do not add a web UI. v0.1 is CLI.
- Do not add a vector database. Structured memory first.
- Do not provision Supabase or any hosted infrastructure.
- Do not add an LLM call where a deterministic, testable rule is sufficient.
- Do not add a feature because it would be impressive. Add it because an
  evaluation result demands it.

If you believe a new capability is required, first write the evaluation that
would show the current system failing without it.

---

## 3. v0.1 is READ-ONLY. Non-negotiable.

The authorised loop is:

```
READ -> RETRIEVE -> ANALYSE -> CHALLENGE -> RECOMMEND -> JOEY DECIDES
```

The system MUST NOT, under any circumstance in v0.1:

- send email or messages
- post to social media
- create, modify or delete CRM records
- delete data
- purchase anything
- schedule meetings
- submit applications
- contact prospects
- execute financial transactions
- make any irreversible external change

`src/twin/safety/` implements the capability gate. Every external-write
capability is `False` and the capability set is frozen. Future permissions are
*architected* (named, typed, gated) but **not enabled**. Any change that flips a
write capability to `True` must be rejected in review.

Tests in `tests/test_readonly.py` enforce this. Do not weaken them.

---

## 4. Evidence discipline

Every material claim must be classifiable as exactly one of:

| Grade | Meaning |
|---|---|
| `FACT` | Directly observed or documented. Requires a source. |
| `INFERENCE` | Derived from facts. Must name the claims it derives from. |
| `ASSUMPTION` | Believed without supporting evidence. Must be labelled as such. |
| `UNKNOWN` | Explicitly missing information. |

Rules:

- **Never silently promote an inference to a fact.** `evidence.py` raises on
  attempted promotion. Do not add a bypass.
- A `FACT` without a source is invalid input, not a fact.
- Conflicting evidence must be **surfaced**, never dropped, never averaged away.
- Where useful, record `source`, `date`, `confidence`, `relevance`.
- Newer information does not automatically supersede older information.
  Supersession must be explicit and recorded.

---

## 5. No invented facts about Joey

Do not write, infer, generate or "fill in":

- biography
- achievements
- employment history
- relationships
- preferences
- past decisions
- reasoning

If it was not explicitly provided and approved by Joey, it does not exist. Files
under `identity/` describe **structure and provenance rules**, not content, until
Joey supplies content.

All example and evaluation data must be clearly labelled `synthetic: true`.
Synthetic data must never be presented as Joey's history.

---

## 6. Challenge, do not flatter

No agent in this repository optimises for agreeing with Joey.

- **Accuracy beats agreement.**
- Do not treat Joey's strong language as evidence. Confident framing is not data.
- Do not treat a leading question as a mandate. Detect and name the framing.
- A strong recommendation may be "no", or "do nothing", or "insufficient evidence".
- Do not disagree automatically either. The purpose of red-teaming is resistance
  to confirmation bias, not contrarianism.

If Joey is solving the wrong problem, say so before solving it.

---

## 7. Preserve uncertainty

- Do not round uncertainty away to sound authoritative.
- Confidence must be produced by the documented formula in
  `cognition/confidence-policy.md`, not asserted.
- Critical unknowns impose a hard confidence ceiling. Do not remove ceilings to
  make output look stronger.
- Always state what would change the conclusion.

---

## 8. Evaluation integrity

This is the easiest place to fake success. Do not.

- Historical case files contain a `hidden` block. It contains Joey's actual
  decision and reasoning.
- The `hidden` block **must never** reach the engine, the provider, the prompt,
  the retrieval layer, or any log written before scoring.
- `load_case_for_inference()` returns a redacted case. `load_case_answer()` is
  callable **only** from the scorer.
- `tests/test_eval_leakage.py` plants canary tokens in hidden fields and asserts
  they never appear in anything the engine sees. Do not weaken this test.
- Do not tune rules against a single fixture until it passes. That is overfitting
  a test you wrote yourself, and it is worthless.
- Do not report a Decision Agreement Rate without also reporting the baseline
  comparison. An agreement rate with no baseline is not evidence.

---

## 9. Coding standards

- Python 3.11+, **standard library only** for core engine and evals. Third-party
  dependencies require justification in `docs/architecture.md`.
- Type hints on all public functions. `mypy` clean where practical.
- `ruff` clean.
- Pure functions in the engine. No hidden global state. No network calls in the
  default path.
- Deterministic by default: the same case + same config produces the same output.
- Dataclasses for domain types. JSON for persistence. PostgreSQL-compatible
  schema shapes.
- Secrets come from environment variables only. Never commit credentials.
  `.env.example` documents required variables.

---

## 10. Testing and documentation obligations

- **Run the tests after any meaningful change.** `pytest -q` from the project root.
- Do not report success if tests fail. Report the failure and the output.
- `.github/workflows/ci.yml` runs the same three checks (`pytest`, `ruff check`,
  `mypy src/twin`) on every push and pull request. CI is a backstop, not a
  substitute for running them locally first. Never weaken, skip or bypass a
  check to get CI green — fix the cause or report the failure.
- New behaviour requires a new test. Bug fixes require a regression test.
- Architectural changes require an update to `docs/architecture.md`.
- Changes to scoring require an update to `docs/evaluation-methodology.md`.
- Changes to permissions or data handling require an update to
  `docs/security-model.md`.

"Files exist" is not "it works". Working behaviour and passing tests are the
standard.

---

## 11. CAOS separation

CAOS is a **separate concern**. CAOS may become a reusable decision architecture
or product. Joey Digital Twin may become a personalised reference implementation
of that architecture.

Do not collapse them into one product without Joey's explicit approval. The
`caos` mode in this repository exists to keep the boundary visible, not to merge
them.

---

## 12. Language for unproven things

If something is unproven, write "unproven". Not "should work", not "designed to",
not "enables". `docs/roadmap.md` maintains the standing list of unproven claims.
Keep it honest and keep it current.

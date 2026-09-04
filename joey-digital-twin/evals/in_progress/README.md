# In-progress cases

Staging for real cases being authored. Files here are **not** scored — the
evaluation suite only reads `../historical_decisions/`, so an incomplete case
cannot distort the Decision Agreement Rate. A case moves across once
`twin validate` passes on it.

```bash
./scripts/twin validate evals/in_progress/REAL-CASE-001-career.json
```

The validator doubles as the completion checklist: every missing field is
reported as a named error.

---

## Blind evaluation protocol

This is the sequence that makes the result mean something. The order is the
protection.

### 1. Joey sends the evidence packet — evidence ONLY

No decision. No outcome. Nothing learned after the decision date.

### 2. Claude encodes it into the case file

Context block only. The `hidden` block stays empty.

### 3. The ENGINE produces the recommendation

```bash
./scripts/twin decide evals/in_progress/REAL-CASE-001-career.json --mode career
```

**Claude does not write the recommendation.** If Claude reasons it out by hand,
the test measures Claude, not the Twin. The output must come from
`twin decide` — the deterministic rule engine — or the case proves nothing about
this system.

### 4. The recommendation is committed to git BEFORE the answer is revealed

A timestamped commit makes the prediction unfalsifiable after the fact. Without
this step, "the Twin got it right" is unverifiable.

### 5. Only then does Joey reveal the decision and reasoning

Claude populates `hidden`, moves the case into `../historical_decisions/`, and
runs scoring.

### Why Claude knowing the answer afterwards is harmless

The default provider is deterministic code, not a language model. It reads the
case file and nothing else. Once the recommendation is committed at step 4,
knowledge arriving at step 5 cannot retroactively change it — and re-running the
engine reproduces the same output byte for byte.

This is the practical payoff of the architecture decision to keep the default
provider offline and deterministic (`docs/architecture.md`, AD-1). With an LLM
in the loop, this protocol would not be trustworthy.

---

## Writing evidence when you already know the outcome

This is the hard part, and it is where a real suite usually goes wrong. Nobody
writes a neutral context block about a decision they remember making. The
distortions are unconscious and they inflate agreement.

**Do not include:**

- Anything learned after the decision date, however small.
- Phrasing coloured by what happened next — the validator blocks "turned out",
  "in hindsight", "we later learned", "eventually", and similar.
- Any statement of what was done — the validator blocks "we decided", "I chose",
  and similar.
- Evidence weighted toward the option actually taken. If the case only contains
  reasons supporting one option, it is not a decision, it is a justification.
- Claims dated after `as_of`. The validator rejects these outright.

**A useful test before sending:** would someone reading only the context block
be genuinely unsure which option was taken? If not, the case is contaminated.

**Include the uncomfortable evidence.** The evidence that pointed the other way
is the evidence that makes the case worth scoring.

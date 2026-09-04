# Security model (v0.1)

Scope: a local, single-user, offline decision engine holding sensitive personal and
commercial information. Sized for that. Not enterprise security theatre.

## Assets, in order of sensitivity

1. **Joey's memory** — decisions, reasoning, relationships, commercial positions.
   The most sensitive asset and the whole point of the system.
2. **Third-party personal data** — people and companies appearing in cases. Joey
   controls his own disclosure; these people did not consent.
3. **Evaluation integrity** — if answers leak into inference, every number lies.
4. **Credentials** — API keys, future database credentials.

## Threat model

| # | Threat | Mitigation in v0.1 | Residual |
|---|---|---|---|
| T1 | System takes an irreversible external action | Every capability is `False` and frozen; `require()` always raises; 10 tests enforce it | An operator could edit the source. Review must reject it. |
| T2 | Sensitive data leaks to a third-party model | Default provider makes no network call; LLM adapters refuse without a key **and** an explicit `--allow-network` | Once implemented, prompts will contain case content. Needs a redaction layer before enabling. |
| T3 | Credentials committed | `.gitignore` excludes `.env`; keys read only from `os.environ`; a test asserts no literal key patterns in the provider source | No pre-commit secret scan yet |
| T4 | Evaluation contamination | Structural: `Case` cannot hold hidden data; two-phase harness; canary tests | A malformed case putting the answer in the context block would defeat this. Case review required. |
| T5 | Unconsented ingestion of personal data | No ingester implemented. Sources must be explicitly selected; provenance mandatory | Enforced by convention until ingestion exists |
| T6 | Poisoned memory silently changing decisions | Every record carries provenance and source; `FACT` requires a source; nothing is deleted; contradictions surface | No signing or integrity check on record files |
| T7 | Local disk compromise | Out of scope for v0.1; memory is plain JSON | Real memory should live on an encrypted volume |
| T8 | Over-trusted output | Confidence ceilings, mandatory unknowns, mandatory counterargument, read-only banner on every output | Human discipline |

## Principles applied

- **Least privilege.** The engine has exactly one privilege: reading local files.
- **Local first.** No network in the default path. No hosted infrastructure.
- **Explicit ingestion.** Data enters only by deliberate selection, with provenance.
- **No external writes.** Enforced in code, not documentation.
- **Secrets outside the repository.** Environment variables only.
- **Memory / application-code separation.** Memory is data files; the engine never
  writes to them (`modify_memory` is a gated capability, permanently off in v0.1).
- **Auditable access.** Every recommendation records which memory records were
  retrieved and why.
- **Deletion and export capability.** Memory is per-record JSON: deleting a person
  is deleting their records; export is copying the directory. The Postgres schema
  preserves this via record-level ids and a supersession chain rather than
  destructive updates.

## Future permission gates (architected, NOT enabled)

`src/twin/safety/readonly.py` names the full external-effect surface so it is
reviewable now: `send_email`, `send_message`, `post_social`, `write_crm`,
`delete_data`, `purchase`, `schedule_meeting`, `submit_application`,
`contact_prospect`, `financial_transaction`, `external_http_write`,
`modify_memory`.

Before **any** of these is enabled, all of the following are required:

1. A validated Decision Agreement Rate on a real historical suite.
2. Per-action human confirmation, defaulting to deny.
3. An append-only audit log of every attempted and executed action.
4. A reversal path for every enabled action.
5. Explicit written authorisation from Joey for that specific capability.

Enabling a capability without all five is a defect regardless of who requested it.

## Logging

Recommendations record provider, model, mode, retrieved record ids, scores and
confidence components — enough to reproduce a run. Raw source content is not
logged. Evaluation output goes to `runs/` (git-ignored) and is never committed,
because a run over real cases contains real decisions.

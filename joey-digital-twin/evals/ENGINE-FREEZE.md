# Engine freeze — REAL-CASE-001 through REAL-CASE-002

The decision engine is frozen exactly as it scored REAL-CASE-001. No change to
rules, weights, gates, confidence terms, `required_signals` behaviour, modes or
evidence handling until Joey lifts the freeze.

**Frozen set** — every module that can affect a recommendation:

```
src/twin/types.py
src/twin/engine/**
src/twin/memory/**
src/twin/providers/**
src/twin/safety/**
```

**Not frozen** — evaluation tooling and interface, which cannot change any
decision output: `src/twin/evals/**`, `src/twin/cli.py`, `scripts/`, `tests/`,
`docs/`, `evals/`.

Changes to the not-frozen set are permitted only where they improve evaluation
hygiene. They must never alter a recommendation. The fingerprint below is the
proof.

## Fingerprint

Recomputed with:

```bash
cd joey-digital-twin
find src/twin/types.py src/twin/engine src/twin/memory src/twin/providers src/twin/safety \
  -name '*.py' | sort | xargs sha256sum | sha256sum
```

```
FROZEN AT 2026-09-04T13:28:40Z  (engine as it scored REAL-CASE-001)
sha256: 6e7e1e84868211d7d9f0bf0bb15688c731e20737c68c841a4a6fa62f3fa4fa4e
```

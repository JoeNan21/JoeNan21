# Scoring

Implementation: `src/twin/evals/scoring.py`. Methodology and its limits:
`docs/evaluation-methodology.md`.

Dimensions scored per case: decision agreement (strict and material), reasoning
similarity, missed evidence, unsupported assumptions, red-team recall, and
confidence calibration (Brier).

Run outputs are not committed. Write them to `runs/` (git-ignored):

    ./scripts/twin eval --baseline --json > runs/$(date +%F).json

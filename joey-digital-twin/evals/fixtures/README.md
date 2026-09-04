# Fixtures

Small, sharply scoped inputs for unit tests: single claims, single options,
malformed records. Distinct from `../historical_decisions/`, which holds whole
decision cases used to measure agreement.

Built inline in `tests/` for now. This directory exists so unit fixtures never
get mixed into the evaluation suite, where they would silently distort the
Decision Agreement Rate.

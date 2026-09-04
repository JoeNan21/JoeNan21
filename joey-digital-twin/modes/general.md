# Mode: general

The default. Core architecture with no specialised assumptions.

- **Weighted signals:** none boosted, none suppressed.
- **Required signals:** none.
- **Confidence ceilings:** base policy only.
- **Red-team checks:** all universal checks.

Use when the case does not clearly belong to a specialised mode. Prefer `general`
over forcing a case into a mode; a wrong mode injects wrong priors, which is worse
than no priors.

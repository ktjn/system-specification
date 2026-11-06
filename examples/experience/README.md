# Experience Specification Example

A user journey across two logical components, written with the optional [experience extension](../../EXPERIENCE.md) ([`spec.md` § 13](../../spec.md#13-experience-specification-optional)).

- **Journey**: `investigate-degraded-service` goes `service-overview` → `service-detail` → `incident-investigation`. It realizes three capabilities provided by two components (`service-catalog`, `incident-store`) and is traced to requirements `req-journey` and `req-journey-denied`.
- **Views** are reusable and state their content, actions and view-scoped states; no global state list.
- **Interactions** keep scope (`preserves`) and map each failure mode to the state that handles it (`unauthorized-evidence` → `service-detail.unauthorized`).
- **Scenarios**: `traverse` (positive) and `denied` (negative) exercise every interaction; `critical: true` makes `EXP-05` require that. Each is verified through an ordinary requirement.
- **References**: `service-overview.svg` is `illustrative` (guidance only); `service-detail.svg` is `normative`, so it carries a version, an acceptance authority (`design-lead`) and a hash.
- **Constraint**: `accessibility: WCAG-2.2-AA` is verified through `req-a11y`, not by the validator.

Validate: `metamodel.py examples/experience/spec.yaml --stage verification` and, from the repository root of the example, `--check-artifacts --root examples/experience`. No evidence is supplied, so `--stage release` reports `EXP-07` and the usual missing-evidence errors by design.

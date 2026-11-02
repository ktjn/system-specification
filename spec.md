# System Specification

## 1. Introduction

A platform-independent metamodel for building scalable systems composed of independent components.

The metamodel defines structure, relationships, constraints, processes and verification. Implementation technologies are unrestricted.

A reference implementation shall demonstrate and validate the metamodel.

This document defines metamodel requirements. The [constitution](AI-System-Development-Constitution.md) and [design notes](AI-native-design.md) describe the development workflow. Descriptions marked **Current reference format** or **Current implementation** document the prototype; its limitations do not relax these requirements.

## 2. Systems

A system is a composition of components.

- Systems shall define their components and relationships.
- Systems may organize components into layers with directional dependency constraints.
- Dependencies shall be resolved through capabilities.
- Systems shall define requirements, risks and quality attributes.
- System composition shall be validated for completeness and compatibility.

Layer policies shall identify allowed dependency directions and whether same-layer or non-adjacent dependencies are permitted. Components subject to a layer policy shall belong to declared layers.

Logical capability dependencies and source-code dependencies shall be distinguished. A domain component may consume an infrastructure-provided capability through a technology-independent contract; its domain logic shall not depend on infrastructure implementation types.

**Current implementation:** `system.layers` is ordered from highest to lowest. The validator allows dependencies within a layer or toward any lower layer, including non-adjacent layers. When `system.layers` is non-empty, every component shall declare one of them. Stricter adjacency rules and source-code dependency rules require separate verification.

## 3. Components

A component is an independent logical unit providing one or more capabilities.

- Components shall have stable identities and versions.
- Components may depend on zero or more capabilities provided by other components.
- Components shall define explicit boundaries, contracts and consistency guarantees.
- Components may own, consume, transform and expose data.
- Components shall define requirements, risks and verification evidence.
- Components shall be independent of deployment and implementation technologies.

## 4. Capabilities

A capability describes functionality independently of its implementation.

- Components shall declare provided and required capabilities.
- Capabilities shall define contracts, including preconditions, postconditions, invariants and failure modes.
- Capabilities shall support versioning and compatibility validation.
- Required capabilities shall resolve to compatible providers.

Required capabilities shall resolve unambiguously to providers other than the consuming component. Compositions with multiple candidates shall define provider selection explicitly; declaration order shall not determine selection. Dependency cycles shall be assessed against declared architectural and behavioral constraints.

**Current reference format:** capabilities use `id`, `version`, `preconditions`, `postconditions`, `invariants`, `failure_modes` and optional `deprecated`. Contract clauses are lists of strings whose meaning shall be defined through requirements and acceptance criteria.

```yaml
capabilities:
  - id: reserve-inventory
    version: "1.0"
    preconditions: [product_exists, quantity_positive]
    postconditions: [reservation_created, stock_decremented]
    invariants: [stock_never_negative]
    failure_modes: [insufficient_inventory, product_not_found]
```

`Component.provides` contains capability IDs. `Component.requires` contains IDs or version-constrained references such as `reserve-inventory@^1.0` (§ 10). `Component.bindings` maps a required capability ID to the selected provider component. The resolver excludes the consuming component, rejects ambiguous providers without a binding and rejects dependency cycles. It uses one version per capability ID and cannot select different contract versions for different providers of that ID.

## 5. Data Models

Components may own, consume, derive and expose data.

- Data models shall define ownership, structure and contracts.
- External data dependencies shall be tracked.
- Derived and re-exposed data shall preserve lineage.
- Data classifications and constraints shall propagate through transformations.
- Data contracts shall support versioning and compatibility validation.

Ownership declarations shall agree: a model's `owner` shall identify an existing component, and that component's `owns_data` shall include the model. Lineage references shall identify existing models; external sources shall be explicitly registered.

**Current reference format:** `DataModel` contains `id`, `version`, `owner`, `fields`, `classification`, `derived_from` and optional `external_source`. `fields` maps names to type descriptions; these strings do not implement payload or data-contract validation.

- Classification order is `public < internal < confidential < restricted`; the default is `public`.
- A derived model's classification shall be at least as restrictive as every source in `derived_from`. Applying this rule to every lineage edge preserves classification transitively.
- The current format has no declassification mechanism or representation for propagation of other data constraints.
- `external_source` refers to an entry in `system.external_sources`.

## 6. Requirements

Requirements specify expected behavior and constraints.

- Requirements shall have stable identities and acceptance criteria.
- Requirements may apply to systems, components, capabilities or data models.
- Requirements may depend on, refine or conflict with other requirements.
- Requirements shall support functional and non-functional properties.
- Every mandatory requirement shall have a verification obligation.
- A requirement shall declare the verification methods it requires; the default is `test`. Omitting `test` shall be an explicit choice.

- `depends_on` identifies prerequisite requirements; `refines` identifies requirements whose obligations are elaborated; `conflicts_with` identifies incompatible obligations.
- A composition shall identify its active requirements. Conflicts between active requirements shall have documented resolutions, with affected criteria and evidence reassessed before release.
- Setting a requirement to optional shall not resolve a conflict or remove its dependencies.

**Current reference format:** requirements use `id`, `version`, `target`, `kind`, `mandatory`, `criteria`, `depends_on`, `refines` and `conflicts_with`. `kind` is `functional` or `non-functional`; `mandatory` defaults to `true`; `criteria` shall be non-empty; `methods` lists required methods (`test`, `proof`, `analysis`, `inspection`) and defaults to `[test]`. There are no status or conflict-resolution fields: all included requirements are treated as active, and a conflict with another included requirement is rejected. Lifecycle decisions and their history require external records.

## 7. Risks

Risks describe potential failures or undesirable outcomes.

- Components and systems shall identify and assess risks.
- Risks shall have explicit treatments: mitigation, acceptance, avoidance or transfer.
- Mitigations shall be expressed through verifiable requirements.
- Residual risks shall be tracked and explicitly accepted where applicable.

Mitigation acceptance shall require valid evidence for the mitigating requirements, including optional requirements used as mitigations. A treatment label alone shall not establish that a risk has been addressed.

**Current reference format:** risks use `id`, `target`, `treatment`, `mitigated_by` and `residual_accepted`. The validator requires each mitigating requirement to have valid evidence and `acceptance` to set `residual_accepted: true`; it does not verify mitigation effectiveness or residual-risk acceptance for mitigated risks.

## 8. Verification

Verification establishes evidence that requirements are satisfied.

- Requirements shall be verified through tests, formal proofs, analysis, inspection or other justified methods.
- Evidence shall be traceable to requirements and applicable versions.
- Evidence shall record results, context and provenance.
- Changes shall invalidate affected evidence.
- Compliance shall be determined through defined verification rules.

Valid evidence shall identify:

- The requirement and version, verification method and result.
- The verified subject and its version or immutable revision.
- Execution time, verifier or tool identity, conditions and assumptions.
- Retrievable supporting artifacts and their provenance.

Every test shall trace to exactly one requirement version. Test evidence shall be derived from test-runner results, not asserted by hand. A test bound to a requirement is evidence only for that requirement and version.

Bindings may be produced by any of the following; the normalized binding `(test, requirement, version)` is identical for all, and the validator shall not depend on the mechanism. In order of preference:

1. Native marker or annotation in the test framework.
2. Structured comment, e.g. `verifies: <requirement>@<version>`.
3. External mapping file, for tests that cannot be edited.
4. Last resort: a deterministic encoding of the requirement ID and version in the test name. The encoding shall be unambiguous and its use shall be declared.

The runner's report is authoritative for which tests exist. A discovered test without a binding, a binding that resolves to no requirement or a stale version, and a binding without a discovered test are errors.

Evidence shall cover the applicable acceptance criteria. A passing result shall not override an unresolved failure for the same obligation and applicable subject. Superseded results shall retain their history and an explicit reason for supersession.

Changes to requirements, contracts, components, data models or relevant dependencies shall trigger impact analysis. Affected evidence shall be invalidated and the affected obligations reverified; an unchanged requirement version alone shall not justify reuse.

**Current reference format:** `Evidence` contains `id`, `requirement_id`, `requirement_version`, `method`, `passed` and `provenance`. `tests` contains bindings `{id, requirement_id, requirement_version}` (mechanism 3). With `--junit REPORT`, bindings are also read from a `verifies` property (`<requirement>@<version>`) on each JUnit `testcase` (mechanism 1, pytest marker `verifies`), and `method: test` evidence is generated from the report with `id` = `classname::name`; hand-written `test` evidence is then rejected. A test must bind exactly one requirement. Supported methods are `test`, `proof`, `analysis` and `inspection`. Additional metadata shall be supplied by the artifact identified through `provenance`; there are no dedicated fields for it. The validator requires a passing record per required method matching `(requirement_id, requirement_version)` and rejects any failing record for that pair; `test` evidence shall reference a bound test; there is no supersession field, so superseded failures shall be retained externally. It does not inspect artifacts, subject revisions or criterion coverage.

Acceptance shall include structural validation, evidence review, applicable architecture checks and risk disposition. Formal verification shall include reviewed assumptions, checked properties and correspondence to the implementation where applicable. A successful metadata check alone shall not establish system acceptance.

## 9. Scalability and Quality

Systems shall define measurable quality attributes.

- Attributes may include scalability, performance, reliability, security and maintainability.
- Quality requirements shall define measurable constraints and acceptance criteria.
- Verification shall establish compliance under specified conditions.
- The metamodel shall not prescribe implementation mechanisms.

## 10. Lifecycle and Evolution

Systems and components shall support controlled evolution.

- Contracts, requirements and data models shall be versioned.
- Changes shall support dependency and impact analysis.
- Compatibility rules shall govern composition and replacement.
- Affected requirements shall be reverified following changes.
- Deprecation and removal shall be explicitly managed.

Compatibility shall preserve existing consumers' obligations and guarantees:

- Backward-compatible capability replacements shall not strengthen preconditions, weaken postconditions or remove required invariants.
- Failure-mode changes shall be assessed for their effect on consumers.
- Data-contract changes shall preserve the constraints and representations required by consumers, or be handled as explicit breaking changes.
- Versioning policies shall identify breaking changes and the required migration. Matching a version range shall not substitute for contract verification.
- Impact analysis shall follow transitive capability and data dependencies and include affected system-level requirements and evidence.

**Current implementation:** capability references support either an unconstrained ID or `id@^version`. `_ver_ok` parses dot-separated integer segments, requires an equal first (major) segment and compares the remaining segments numerically and lexicographically against the minimum. Non-numeric versions never match. For example, `@^1.0` accepts `1.0` and `1.2`, but rejects `0.9` and `2.0`.

This is a limited matching rule: it does not normalize omitted segments, apply special rules for major version zero or support prerelease versions and general range expressions. It shall not be assumed to implement a general semantic-versioning standard.

`check_compatibility(old, new)` compares clause strings as sets: added preconditions, removed postconditions, removed invariants and added failure modes are reported, plus a missing major version bump for such changes. `compare_specs` (CLI `--compat OLD`) also reports capabilities removed without prior deprecation. It does not evaluate clause meaning or data contracts. `impact_analysis` (CLI `--impact ID`) follows capability, ownership and lineage dependencies transitively and reports affected components, capabilities, data models, requirements (including system-level and dependent requirements) and evidence; it does not change stored evidence.

## 11. Metamodel Validation

The metamodel shall define machine-verifiable invariants.

- Every component shall provide at least one capability.
- Every required capability shall resolve within a valid system composition.
- Every capability shall have associated requirements.
- Every mandatory requirement shall have valid verification evidence for each of its required methods before release.
- Every test shall trace to a requirement; no test, binding or evidence record shall be unbound.
- No active requirements shall remain in unresolved conflict.
- Every risk shall have an explicit disposition.
- Every external data dependency shall be traceable.
- Every system composition shall satisfy its declared layer and dependency constraints.

Identity and reference invariants shall also hold:

- IDs shall be unique within each entity type. Untyped references such as `Requirement.target` and `Risk.target` shall resolve unambiguously across their allowed target types.
- Provided capabilities, requirement relationships, risk mitigations, evidence requirements, data ownership and lineage references shall resolve to existing entities of the appropriate type.
- Evidence used for acceptance shall refer to the applicable requirement and subject versions.
- Data ownership declarations shall agree, and lineage shall preserve classification and constraints.

Validation results shall distinguish schema checks, composition checks and verification of the described system. Unsupported checks and unresolved obligations shall be reported explicitly.

## 12. Reference Implementation

A reference implementation shall demonstrate:

- Declarative specifications of systems, components and capabilities.
- Dependency and capability resolution.
- Requirement, risk and data traceability.
- Contract and compatibility validation.
- Verification evidence collection and evaluation.
- Change-impact analysis.
- Automated metamodel conformance checks.

The reference implementation shall not constrain alternative implementations.

### Current implementation and acceptance limits

The [Python reference implementation](reference-implementation/README.md) is a partial prototype. Its JSON Schema describes the accepted serialization format; it does not encode all invariants or establish runtime correctness.

Run from `reference-implementation/`:

```sh
uv run python metamodel.py example.yaml
uv run python metamodel.py --schema
uv run python metamodel.py example.yaml --impact order --json
uv run python metamodel.py example.yaml --compat old.yaml
uv run pytest --junitxml=report.xml && uv run python metamodel.py metamodel.yaml --junit report.xml
uv run pytest
```

The manually dispatched `metamodel` GitHub Actions workflow runs either script with custom arguments in Docker.

Current limitations include:

- Cycles are always rejected; no constraint can declare them acceptable.
- `consistency` and `quality_attributes` are parsed without behavioral verification; `deprecated` is used only by `compare_specs`.
- Only mechanisms 1 (pytest marker) and 3 are implemented; comment scanning and name encoding are not. Bound tests do not cover individual criteria. `metamodel.yaml` is the reference implementation's own spec; its test evidence exists only while validating with `--junit`.
- Evidence has no subject revision or supersession fields. Changes do not automatically invalidate stored evidence; impact analysis only reports it.
- Requirement lifecycle, conflict resolutions, data-contract compatibility and declassification are not implemented.
- Results distinguish schema errors from metadata errors, but not composition checks from verification checks.
- The example's test, proof and benchmark provenance values are illustrative; their artifacts are not supplied by this repository.

`VALID` means only that the implemented checks found no errors in the supplied metadata. Release acceptance still requires the evidence and obligations in §§ 7–11. Passing the prototype's tests establishes only the behavior covered by those tests.

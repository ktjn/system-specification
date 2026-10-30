# System Specification

## 1. Introduction

A platform-independent metamodel for building scalable systems composed of independent components.

The metamodel defines structure, relationships, constraints, processes and verification. Implementation technologies are unrestricted.

A reference implementation shall demonstrate and validate the metamodel.

This document defines metamodel requirements. The [constitution](CONSTITUTION.md) defines shared development rules; the [greenfield](GREENFIELD.md) and [brownfield](BROWNFIELD.md) tracks define their workflows; [skills](.github/skills/) describe individual techniques.

Blocks marked **Current reference format** define the serialization shared by tracks, skills and tooling; its limitations do not relax these requirements. Prototype behavior and limitations: [reference implementation](reference-implementation/README.md).

## 2. Systems

A system is a composition of components.

- Systems shall define their components and relationships.
- Systems may organize components into layers with directional dependency constraints.
- Dependencies shall be resolved through capabilities.
- Systems shall define requirements, risks and quality attributes.
- System composition shall be validated for completeness and compatibility.

Layer policies shall identify allowed dependency directions and whether same-layer or non-adjacent dependencies are permitted. Components subject to a layer policy shall belong to declared layers.

Logical capability dependencies and source-code dependencies shall be distinguished. A domain component may consume an infrastructure-provided capability through a technology-independent contract; its domain logic shall not depend on infrastructure implementation types.

**Current reference format:** `system.layers` is ordered from highest to lowest; `Component.layer` names one of them.

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

`Component.provides` contains capability IDs. `Component.requires` contains IDs or version-constrained references such as `reserve-inventory@^1.0` (§ 10). `Component.bindings` maps a required capability ID to the selected provider component. The format holds one version per capability ID.

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

- `depends_on` identifies prerequisite requirements; `refines` identifies requirements whose obligations are elaborated; `conflicts_with` identifies incompatible obligations.
- A composition shall identify its active requirements. Conflicts between active requirements shall have documented resolutions, with affected criteria and evidence reassessed before release.
- Setting a requirement to optional shall not resolve a conflict or remove its dependencies.

**Current reference format:** requirements use `id`, `version`, `target`, `kind`, `mandatory`, `criteria`, `depends_on`, `refines` and `conflicts_with`. `kind` is `functional` or `non-functional`; `mandatory` defaults to `true`. There are no status or conflict-resolution fields: all included requirements are treated as active, and a conflict with another included requirement is rejected. Lifecycle decisions and their history require external records.

## 7. Risks

Risks describe potential failures or undesirable outcomes.

- Components and systems shall identify and assess risks.
- Risks shall have explicit treatments: mitigation, acceptance, avoidance or transfer.
- Mitigations shall be expressed through verifiable requirements.
- Residual risks shall be tracked and explicitly accepted where applicable.

Mitigation acceptance shall require valid evidence for the mitigating requirements, including optional requirements used as mitigations. A treatment label alone shall not establish that a risk has been addressed.

**Current reference format:** risks use `id`, `target`, `treatment`, `mitigated_by`, `residual_accepted` and `transferred_to`. Avoidance requires verified mitigating requirements and no residual risk; transfer requires a counterparty (`transferred_to`) and accepted residual risk.

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

Evidence shall cover the applicable acceptance criteria. A passing result shall not override an unresolved failure for the same obligation and applicable subject. Superseded results shall retain their history and an explicit reason for supersession.

Changes to requirements, contracts, components, data models or relevant dependencies shall trigger impact analysis. Affected evidence shall be invalidated and the affected obligations reverified; an unchanged requirement version alone shall not justify reuse.

**Current reference format:** `Evidence` contains `id`, `requirement_id`, `requirement_version`, `method`, `passed` and `provenance`. Supported methods are `test`, `proof`, `analysis` and `inspection`. Additional metadata shall be supplied by the artifact identified through `provenance`; there are no dedicated fields for it. There is no supersession field, so superseded failures shall be retained externally.

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

**Current reference format:** capability references are an unconstrained ID or `id@^version` (same major version, at least the given version; e.g. `@^1.0` accepts `1.2`, rejects `0.9` and `2.0`). This is not a general semantic-versioning standard.

## 11. Metamodel Validation

The metamodel shall define machine-verifiable invariants.

- Every component shall provide at least one capability.
- Every required capability shall resolve within a valid system composition.
- Every capability shall have associated requirements.
- Every mandatory requirement shall have valid verification evidence before release.
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

The reference implementation shall not constrain alternative implementations. A passing validator run shall not establish release acceptance, which still requires the evidence and obligations in §§ 7–11.

The [Python reference implementation](reference-implementation/README.md) is a partial prototype; its README documents usage, behavior and limitations. Its JSON Schema (`--schema`) is the machine-readable form of the current reference format.

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

**Current reference format:** `system.layers` is ordered from highest to lowest; `Component.layer` names one of them. `system` also carries `status` and optional `context_budget` (`max_provides`, `max_requires`, `max_owns_data`).

## 3. Components

A component is an independent logical unit providing one or more capabilities.

- Components shall have stable identities, versions and lifecycle statuses.
- Components may depend on zero or more capabilities provided by other components.
- Components shall define explicit boundaries, contracts and consistency guarantees.
- Components may own, consume, transform and expose data.
- Components shall define requirements, risks and verification evidence.
- Components shall remain within declared context-budget limits.
- Components may bind to physical source paths or modules for drift detection while remaining independent of deployment and implementation technologies.

Context budgets shall bound component size by limiting provided capabilities, required capabilities and owned data models (default limits: `max_provides: 5`, `max_requires: 8`, `max_owns_data: 4`, overridable per system). Components exceeding the budget shall be split or covered by an active waiver (§ 7).

Artifact bindings (`source_paths`) map a component to its implementation directories or modules so tools can verify that source-level imports conform to declared capability and layer dependencies.

## 4. Capabilities

A capability describes functionality independently of its implementation.

- Components shall declare provided and required capabilities.
- Capabilities shall define contracts, including preconditions, postconditions, invariants, failure modes and interface bindings.
- Capabilities shall support lifecycle status, versioning and compatibility validation.
- Required capabilities shall resolve to compatible providers.

Interface contracts shall specify for each externally or cross-component exposed capability:

- Operation identifier or endpoint and interaction mode (`sync` or `async`).
- Request and response `DataModel` references.
- Idempotency, authentication/authorization requirements and failure-mode to status-code mappings.

Required capabilities shall resolve unambiguously to providers other than the consuming component. Compositions with multiple candidates shall define provider selection explicitly; declaration order shall not determine selection. Dependency cycles are forbidden unless covered by a time-bounded waiver (§ 7) below the `release` stage.

**Current reference format:** capabilities use `id`, `version`, `status`, `preconditions`, `postconditions`, `invariants`, `failure_modes` and optional `interface` (`operation`, `mode`, `request`, `response`, `idempotent`, `auth`, `errors`). `errors` maps every failure mode to a status code or event; capabilities required by another component need an `interface`. Contract clauses are lists of strings whose meaning shall be defined through requirements and acceptance criteria.

```yaml
capabilities:
  - id: reserve-inventory
    version: "1.0"
    preconditions: [product_exists, quantity_positive]
    postconditions: [reservation_created, stock_decremented]
    invariants: [stock_never_negative]
    failure_modes: [insufficient_inventory, product_not_found]
    interface: { operation: POST /v1/reservations, request: stock-item, idempotent: true, auth: service-token, errors: { insufficient_inventory: 409, product_not_found: 404 } }
```

`Component.provides` contains capability IDs. `Component.requires` contains IDs or version-constrained references such as `reserve-inventory@^1.0` (§ 10). `Component.bindings` maps a required capability ID to the selected provider component. Components also carry `status` and optional `source_paths`. The format holds one version per capability ID.

## 5. Data Models

Components may own, consume, derive and expose data.

- Data models shall define ownership, structure and contracts.
- External data dependencies shall be tracked.
- Derived and re-exposed data shall preserve lineage.
- Data classifications and constraints shall propagate through transformations.
- Data contracts shall support versioning and compatibility validation.

Ownership declarations shall agree: a model's `owner` shall identify an existing component, and that component's `owns_data` shall include the model. Lineage references shall identify existing models; external sources shall be explicitly registered. Data models may bind to a physical schema artifact (`schema_path`) for drift and compatibility checks.

- Classification order is `public < internal < confidential < restricted`; the default is `public`.
- A derived model's classification shall be at least as restrictive as every source in `derived_from` unless authorized declassification is declared.
- Authorized declassification (`declassified_by`) shall reference a verified requirement justifying the transformation (e.g. anonymization, aggregation or field stripping).

**Current reference format:** `DataModel` contains `id`, `version`, `owner`, `fields`, `classification`, `derived_from` and optional `external_source`, `schema_path` and `declassified_by`. `fields` maps names to type descriptions; `external_source` refers to an entry in `system.external_sources`.

## 6. Requirements

Requirements specify expected behavior and constraints.

- Requirements shall have stable identities, lifecycle statuses and acceptance criteria.
- Requirements may apply to systems, components, capabilities or data models.
- Requirements may depend on, refine or conflict with other requirements.
- Requirements shall support functional and non-functional properties and map to verification categories.
- Every mandatory active requirement shall have a verification obligation.

- `depends_on` identifies prerequisite requirements; `refines` identifies requirements whose obligations are elaborated; `conflicts_with` identifies incompatible obligations.
- A composition shall identify its active requirements (`status` in `draft`, `specified`, `verified`; `deprecated` requirements are inactive).
- Conflicts between active requirements shall be rejected unless resolved via `resolved_by` referencing an active requirement whose criteria and evidence supersede or reconcile the conflicting obligations.
- Setting a requirement to optional shall not resolve a conflict or remove its dependencies.

**Current reference format:** requirements use `id`, `version`, `target`, `kind`, `mandatory`, `criteria`, `depends_on`, `refines`, `conflicts_with`, `status`, `category` and `resolved_by`. `kind` is `functional` or `non-functional`; `mandatory` defaults to `true`; `category` is one of `functional`, `semantic`, `contract`, `serialization`, `concurrency`, `performance`, `scalability`, `resilience`, `security`, `observability`.

## 7. Risks

Risks describe potential failures, undesirable outcomes or tracked architectural exceptions.

- Components and systems shall identify and assess risks.
- Risks shall have explicit treatments: mitigation, acceptance, avoidance or transfer.
- Mitigations shall be expressed through verifiable requirements.
- Residual risks shall be tracked and explicitly accepted where applicable.
- Architectural exceptions (waivers) shall be bound to risks with remediation requirements and expiration bounds.

Mitigation acceptance shall require valid evidence for the mitigating requirements, including optional requirements used as mitigations. A treatment label alone shall not establish that a risk has been addressed.

A waiver (`waives`) allows a known brownfield violation (layer violation, dependency cycle, shared data ownership, context-budget overrun or missing verification category) below the `release` stage when:

- `treatment` is `mitigation` or `acceptance` and `mitigated_by` names at least one remediation requirement.
- `expires` specifies an ISO-8601 date (`YYYY-MM-DD`) or target stage (`architecture`, `verification`, `release`) that has not passed.
- No waivers are permitted at `--stage release`.

**Current reference format:** risks use `id`, `target`, `treatment`, `mitigated_by`, `residual_accepted`, `transferred_to`, `waives` and `expires`. `waives` is one of `layer-violation`, `dependency-cycle`, `shared-data-ownership`, `context-budget`, `verification-category`; a waiver covers violations whose subjects include the risk `target`, or all of that kind when `target` is the system. Avoidance requires verified mitigating requirements and no residual risk; transfer requires a counterparty (`transferred_to`) and accepted residual risk.

## 8. Verification

Verification establishes evidence that requirements are satisfied.

- Requirements shall be verified through tests, formal proofs, bounded model checks, analysis, inspection or other justified methods.
- Evidence shall be traceable to requirements and applicable versions.
- Evidence shall record results, context, subject revision and provenance.
- Changes shall invalidate affected evidence.
- Compliance shall be determined through defined verification rules.

Valid evidence shall identify:

- The requirement and version, verification method (`test`, `proof`, `model-check`, `analysis`, `inspection`) and result.
- The verified subject (`subject_id`) and its version or immutable revision (`subject_revision`).
- Execution time (`timestamp`), verifier or tool identity (`verifier`), conditions, assumptions and bounds/scope (mandatory for `model-check`).
- Retrievable supporting artifacts and their provenance.

Evidence shall cover the applicable acceptance criteria. A passing result shall not override an unresolved failure for the same obligation and applicable subject unless the new evidence explicitly declares `supersedes` (referencing the failed evidence ID) and `supersession_reason`.

Changes to requirements, contracts, components, data models or relevant dependencies shall trigger impact analysis. Affected evidence shall be invalidated and the affected obligations reverified; an unchanged requirement version alone shall not justify reuse.

**Current reference format:** `Evidence` contains `id`, `requirement_id`, `requirement_version`, `method`, `passed`, `provenance` and optional `bounds` (required for `model-check`), `subject_id`, `subject_revision`, `timestamp`, `verifier`, `supersedes` and `supersession_reason`.

Acceptance shall include structural validation, evidence review, applicable architecture checks and risk disposition. Formal verification shall include reviewed assumptions, checked properties and correspondence to the implementation where applicable. A successful metadata check alone shall not establish system acceptance.

## 9. Scalability and Quality

Systems shall define measurable quality attributes.

- Attributes may include scalability, performance, reliability, security and maintainability.
- Quality requirements shall define measurable constraints and acceptance criteria.
- Verification shall establish compliance under specified conditions.
- The metamodel shall not prescribe implementation mechanisms.

## 10. Lifecycle and Evolution

Systems, capabilities, components and requirements shall support controlled evolution across lifecycle states and validation stages.

- Entities shall progress through `status` states: `draft` → `specified` → `verified` → `deprecated`.
- Contracts, requirements and data models shall be versioned.
- Changes shall support dependency and impact analysis.
- Compatibility rules shall govern composition and replacement.
- Affected requirements shall be reverified following changes.
- Deprecation and removal shall be explicitly managed.

Compatibility shall preserve existing consumers' obligations and guarantees:

- Backward-compatible capability replacements shall not strengthen preconditions, weaken postconditions or remove required invariants.
- Failure-mode changes shall be assessed for their effect on consumers.
- Data-contract changes shall preserve field types, classifications and constraints required by consumers, or be handled as explicit breaking changes with a major version bump.
- Versioning policies shall identify breaking changes and the required migration. Matching a version range shall not substitute for contract verification.
- Impact analysis shall follow transitive capability and data dependencies and include affected system-level requirements and evidence.

**Current reference format:** capability references are an unconstrained ID or `id@^version` (same major version, at least the given version; e.g. `@^1.0` accepts `1.2`, rejects `0.9` and `2.0`). This is not a general semantic-versioning standard.

## 11. Metamodel Validation

The metamodel shall define machine-verifiable invariants evaluated progressively across five monotonic validation stages (`--stage`):

| Stage | Required Entity `status` | Enforced Invariants | Waivers Allowed |
|---|---|---|---|
| `inventory` | `draft`+ | Unique IDs; valid target/reference syntax; registered `system`, `external_sources`, component stubs (`provides` optional) | Yes |
| `discovery` | Capabilities `specified`+ | `inventory` + every capability defines non-empty contract clauses (`preconditions` or `postconditions`, `invariants`, `failure_modes`) | Yes |
| `architecture` | Capabilities & components `specified`+ | `discovery` + every component provides ≥1 capability; required capabilities resolve; layer rules, cycle checks, data ownership, lineage, classification, interface contracts and context budgets hold | Yes (via `Risk.waives`) |
| `verification` | Active requirements `specified`+ | `architecture` + every capability has requirements; all 10 verification categories covered; requirement dependency/refinement acyclic; no unresolved conflicts | Yes (via `Risk.waives`) |
| `release` | All active entities `verified` (or `deprecated`) | `verification` + every mandatory and mitigating requirement has passing, current, non-superseded `Evidence`; all risks disposed (§ 7); zero active or expired waivers | No |

Stages may be entered sequentially (greenfield Gates 1–4: `discovery` → `architecture` → `verification` → `release`) or via brownfield adoption levels (Level 0 `inventory` → Level 1 `architecture` → Level 2 `verification` → Level 3 `release`, skipping standalone `discovery` because `architecture` enforces capability contract presence unless waived).

At `release`, all invariants hold without exception:

- Every component shall provide at least one capability and fit within the context budget.
- Every required capability shall resolve within a valid system composition.
- Every capability shall have associated requirements.
- Every mandatory requirement shall have valid verification evidence before release.
- No active requirements shall remain in unresolved conflict.
- Every risk shall have an explicit disposition and no active waivers shall remain.
- Every external data dependency shall be traceable.
- Every system composition shall satisfy its declared layer and dependency constraints.

Identity and reference invariants shall also hold:

- IDs shall be unique within each entity type. Untyped references such as `Requirement.target` and `Risk.target` shall resolve unambiguously across their allowed target types.
- Provided capabilities, requirement relationships, risk mitigations, evidence requirements, data ownership and lineage references shall resolve to existing entities of the appropriate type.
- Evidence used for acceptance shall refer to the applicable requirement and subject versions.
- Data ownership declarations shall agree, and lineage shall preserve classification and constraints.

Validation results shall distinguish schema checks, composition checks and verification of the described system. Unsupported checks and unresolved obligations shall be reported explicitly.

**Current reference format:** `metamodel.py --stage <stage>` (default `release`) evaluates the stage's invariants; `--context <component-id>` prints the component's spec slice.

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

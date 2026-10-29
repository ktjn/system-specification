# Plan: Full-Fledged Model for Greenfield & Brownfield Systems

## 1. Goal

Evolve the specification and reference tooling from a static release-time validator into a complete lifecycle model supporting:

1. **Creating new systems (Greenfield)** — contract-first, phase-gated design and generation.
2. **Onboarding existing systems (Brownfield)** — incremental reverse-discovery, architectural debt tracking, and safe modernization.

---

## 2. Metamodel Extensions (`spec.md`)

- **Lifecycle & Maturity States**
  - Add lifecycle state (`draft`, `discovered`, `specified`, `verified`, `deprecated`) to capabilities, components, requirements, and systems.
  - Define validation profiles by stage so incomplete or legacy systems validate against stage-appropriate invariants rather than failing release gates upfront.
- **Explicit Interface & API Contracts**
  - Close the Constitution Phase 6 gap by modeling interface bindings (sync/async operations, request/response `DataModel` refs, idempotency, auth/security, failure status mapping).
- **Artifact & Codebase Binding**
  - Bind logical entities to physical artifacts: component source paths/modules, data model schema files, and evidence subject revisions/hashes.
  - Enable drift detection between declared contracts/dependencies and actual source imports/schemas.
- **Context Budget Constraints**
  - Formalize Constitution Phase 10 in the metamodel with configurable thresholds (e.g., max capabilities, required dependencies, and owned data models per component).
- **Architectural Exceptions & Technical Debt**
  - Allow known brownfield violations (layer bypasses, shared data ownership, cyclic dependencies, unverified legacy capabilities) to be explicitly recorded and linked to a `Risk` (`treatment: mitigation` or `acceptance`) with an expiration/remediation requirement.
- **Normative Completeness (from `REVIEW.md`)**
  - Formalize requirement conflict resolution (`resolved_by`), authorized data declassification rules, explicit multi-provider selection (`provider_overrides`), and cycle disposition.

---

## 3. Track 1: Creating New Systems (Greenfield)

### 3.1 Phase-Gated Workflow
Replace single-pass validation with progressive gates aligned with the [Constitution](AI-System-Development-Constitution.md):

- **Gate 1 — Discovery (`--stage discovery`)**: Capabilities, preconditions, postconditions, failure modes, and invariants defined (Phases 1–2).
- **Gate 2 — Architecture (`--stage architecture`)**: Components, layers, consistency boundaries, data models, ownership, and API contracts valid and within context budget (Phases 3–6, 9–10).
- **Gate 3 — Verification Spec (`--stage verification`)**: Requirements covering all 10 verification categories and formal verification assessments mapped to capabilities/components (Phases 7–8).
- **Gate 4 — Release Acceptance (`--stage release`)**: All mandatory requirements backed by passing, non-conflicting, current `Evidence`; all risks mitigated or accepted (Phases 11–12).

### 3.2 Contract-First Scaffolding
- Generate component directory structures, interface stubs, data schemas (JSON Schema / OpenAPI), and failing test skeletons directly from a Gate 2–3 spec.
- Enforce the AI Execution Rule: AI agents receive only the target component's bounded spec slice + required capability contracts + generated test stubs.

### 3.3 AI Playbooks & Prompt Templates
- Add `PROMPTS.md` with schema-guided prompt templates for each Constitution phase using `metamodel.py --schema`.
- Provide a complete step-by-step greenfield worked example traced from Phase 1 to Phase 12.

---

## 4. Track 2: Onboarding Existing Systems (Brownfield)

### 4.1 Incremental Adoption Levels
Onboard legacy systems progressively without halting delivery:

- **Level 0 — System Inventory (`discovered`)**
  - Register `system`, `external_sources`, deployable units/components, and coarse module boundaries.
  - Validation checks identity uniqueness and structural syntax only.
- **Level 1 — Dependency & Data Mapping (`mapped`)**
  - Map observed provided/required capabilities, data ownership, classifications, and lineage.
  - Record existing layer violations, cyclic dependencies, or shared-table ownership as explicit `Risk` exceptions.
- **Level 2 — Behavioral Pinning (`pinned`)**
  - Capture as-is contracts (pre/postconditions, invariants, failure modes) and attach characterization tests/inspections as `Evidence`.
  - Freeze external and cross-component contracts before internal refactoring.
- **Level 3 — Full Conformance (`verified`)**
  - Remediate architectural exceptions, enforce strict layer and context-budget rules, and satisfy all mandatory verification categories.

### 4.2 Reverse-Discovery Protocol
Add a structured onboarding guide (`ONBOARDING.md`) for humans and AI agents:

1. **Boundary & Entrypoint Scan**: Identify APIs, jobs, events, and external data sources → draft `SystemDef`, `Capability` stubs, and `external_sources`.
2. **Data & State Extraction**: Inspect schemas, migrations, and ORM/DTO models → define `DataModel` entities, owners, classifications, and lineage.
3. **Component & Dependency Clustering**: Group modules by transaction/consistency boundaries → define `Component` entities, layers, and capability wiring.
4. **Invariant & Failure Mining**: Extract domain guards, error handlers, and existing tests → populate capability contracts, `Requirement` criteria, and initial `Evidence`.
5. **Gap & Risk Triage**: Convert missing test categories, unverified mitigations, and architecture violations into tracked `Risk` and `Requirement` backlog items.

### 4.3 Modernization & Strangler Migration
- Use `check_compatibility` to verify that newly extracted or rewritten components preserve legacy capability contracts.
- Use transitive `impact_analysis` to identify all downstream components, data models, requirements, and evidence invalidated by a refactoring step.

---

## 5. Reference Implementation & Tooling (`reference-implementation/`)

- **Core Validator Hardening (`metamodel.py`)**
  - Fix multi-provider overwrite, self-dependency, unknown layer bypass, failing evidence handling, and non-numeric version crashes.
  - Enforce unique IDs, full referential integrity, bidirectional data ownership, verified risk mitigations, and cycle detection.
- **Stage & Onboarding Support**
  - Add `status` / maturity fields and `--stage` (`discovery`, `architecture`, `verification`, `release`) + brownfield exception waivers tied to `Risk` IDs.
- **Lifecycle CLI Commands**
  - `validate <spec.yaml> [--stage <stage>] [--json]` — stage-aware validation and machine-readable diagnostics.
  - `impact <spec.yaml> <entity-id>` — full transitive capability, component, data model, requirement, and evidence impact analysis.
  - `compat <old.yaml> <new.yaml>` — capability and data contract compatibility verification, including failure modes and version-bump rules.
  - `context <spec.yaml> <component-id>` — export minimal bounded-context spec slice for AI implementation or onboarding tasks.
- **CI & Test Fixtures**
  - Add GitHub Actions workflow running `pytest` and validating all example specs.
  - Add negative test fixtures (`tests/invalid/*.yaml`) and multi-stage greenfield/brownfield examples.

---

## 6. Execution Roadmap

### Phase 1: Normative Hardening & CI
- [ ] Fix all 🔴 Critical and 🟡 High validator gaps in `reference-implementation/metamodel.py` (`REVIEW.md` items 1–7).
- [ ] Add GitHub Actions CI workflow and negative test fixtures.

### Phase 2: Lifecycle, Exceptions & Binding Model
- [ ] Update `spec.md` with lifecycle states, validation stages, interface contracts, artifact bindings, context budget rules, and brownfield risk waivers.
- [ ] Implement `--stage` profiles, brownfield waiver validation, and `--json` output in `metamodel.py`.

### Phase 3: Greenfield Workflow & Tooling
- [ ] Add `GREENFIELD.md` (or expand `AI-System-Development-Constitution.md`) and `PROMPTS.md` with stage-gated AI playbooks.
- [ ] Implement `context` slice export in `metamodel.py`.
- [ ] Add traced end-to-end greenfield example (`examples/greenfield/`).

### Phase 4: Brownfield Onboarding Workflow & Tooling
- [ ] Create `ONBOARDING.md` defining the 4 adoption levels and 5-step reverse-discovery protocol.
- [ ] Implement transitive `impact` and full `compat` CLI subcommands for safe strangler migrations.
- [ ] Add brownfield onboarding example (`examples/brownfield/`) showing progression from Level 0 (`discovered`) to Level 3 (`verified`).

# Plan: Full-Fledged Model for Greenfield & Brownfield Systems

## 1. Goal

Evolve the specification and reference tooling from a static release-time validator into a complete lifecycle model supporting:

1. **Creating new systems (Greenfield)** — contract-first, phase-gated design and generation.
2. **Onboarding existing systems (Brownfield)** — incremental reverse-discovery, architectural debt tracking, and safe modernization.

### 1.1 Document Structure
- [`CONSTITUTION.md`](CONSTITUTION.md): shared fundamentals and artifact rules; order-free.
- [`GREENFIELD.md`](GREENFIELD.md): phase sequence, gates, AI Execution Rule, prompts.
- [`BROWNFIELD.md`](BROWNFIELD.md): adoption levels, reverse discovery, waivers, modernization, prompts.
- [`spec.md`](spec.md): normative metamodel and current reference format.
- [`.github/skills/<name>/SKILL.md`](.github/skills/): how-to for one technique (e.g. [`tla`](.github/skills/tla/SKILL.md), [`alloy`](.github/skills/alloy/SKILL.md), [`modelable`](.github/skills/modelable/SKILL.md)); linked from the constitution, maps output to the metamodel.
- [`reference-implementation/README.md`](reference-implementation/README.md): prototype usage, behavior and limitations.
- AI context per task: constitution + one track document + applicable skill + `--context` component slice.

---

## 2. Metamodel Extensions (`spec.md`)

- **Lifecycle, Adoption & Stages** ([`spec.md` §§ 10–11](spec.md#10-lifecycle-and-evolution))
  - Entity `status` (`capabilities`, `components`, `requirements`, `system`): `draft` → `specified` → `verified` → `deprecated`.
  - Validation `--stage` (`inventory` → `discovery` → `architecture` → `verification` → `release`): each stage enforces monotonic invariants and minimum entity `status` (`draft`+ at `inventory`; `specified`+ for capabilities at `discovery`, components at `architecture`, active requirements at `verification`; `verified` or `deprecated` for all active entities at `release`).
  - Brownfield adoption levels map to stages (§ 4.1); Level 0 (`inventory`) advances directly to Level 1 (`architecture`), skipping standalone `discovery` because `architecture` includes capability contract presence (unless waived).
- **Explicit Interface & API Contracts** ([`spec.md` § 4](spec.md#4-capabilities))
  - Close the API contract gap (Greenfield Phase 6) via `Capability.interface` (sync/async mode, endpoint, request/response `DataModel` refs, idempotency, auth/security, failure-mode status mapping).
- **Artifact & Codebase Binding** ([`spec.md` §§ 3, 5, 8](spec.md#3-components))
  - Bind logical entities to physical artifacts: `Component.source_paths`, `DataModel.schema_path`, and `Evidence.subject_revision` / `timestamp` / `verifier`.
  - Enable drift detection between declared contracts/dependencies and actual source imports/schemas.
- **Context Budget Constraints** ([`spec.md` § 3](spec.md#3-components))
  - Formalize the context budget (Greenfield Phase 10) with configurable system defaults (`max_provides: 5`, `max_requires: 8`, `max_owns_data: 4`).
- **Architectural Exceptions & Technical Debt** ([`spec.md` § 7](spec.md#7-risks))
  - Allow known brownfield violations (layer bypasses, shared data ownership, cyclic dependencies, context-budget overruns, missing verification categories at Level 2, unverified legacy capabilities) below `release` when bound to a `Risk` (`waives`, `treatment: mitigation` or `acceptance`, `mitigated_by` remediation requirement, and `expires` ISO date or target stage).
  - Expired waivers fail at every stage; zero waivers permitted at `release`.
- **Normative Completeness** ([`spec.md` §§ 5–8](spec.md#5-data-models))
  - Authorized data declassification (`DataModel.declassified_by` referencing a verified requirement), requirement `status`/`category`/`resolved_by`, evidence `model-check` method (with mandatory `bounds`) and `supersedes`/`supersession_reason`, and cycle disposition. Multi-provider selection reuses `Component.bindings`.

---

## 3. Track 1: Creating New Systems (Greenfield)

### 3.1 Phase-Gated Workflow
Replace single-pass validation with progressive gates defined in [`GREENFIELD.md`](GREENFIELD.md):

- **Gate 1 — Discovery (`--stage discovery`)**: Capabilities, preconditions, postconditions, failure modes, and invariants defined (Phases 1–2).
- **Gate 2 — Architecture (`--stage architecture`)**: Components, layers, consistency boundaries, data models, ownership, and API contracts valid and within context budget (Phases 3–6, 9–10).
- **Gate 3 — Verification Spec (`--stage verification`)**: Requirements covering all 10 verification categories and formal verification assessments mapped to capabilities/components (Phases 7–8).
- **Gate 4 — Release Acceptance (`--stage release`)**: All mandatory requirements backed by passing, non-conflicting, current `Evidence`; all risks mitigated or accepted (Phases 11–12).

### 3.2 Contract-First Scaffolding
- Generate component directory structures, interface stubs, data schemas (JSON Schema / OpenAPI), and failing test skeletons directly from a Gate 2–3 spec.
- Enforce the AI Execution Rule: AI agents receive only the target component's bounded spec slice + required capability contracts + generated test stubs.

### 3.3 AI Playbooks & Prompt Templates
- Schema-guided prompt templates per phase live in `GREENFIELD.md` (no separate `PROMPTS.md`).
- Provide a complete step-by-step greenfield worked example traced from Phase 1 to Phase 12.

---

## 4. Track 2: Onboarding Existing Systems (Brownfield)

### 4.1 Incremental Adoption Levels
Onboard legacy systems progressively without halting delivery; each level = a target `--stage`, waivers allowed below `release`:

- **Level 0 — System Inventory (`--stage inventory`)**
  - Register `system`, `external_sources`, deployable units/components, and coarse module boundaries.
  - Validation checks identity uniqueness and structural syntax only.
- **Level 1 — Dependency & Data Mapping (`--stage architecture`)**
  - Map observed provided/required capabilities, data ownership, classifications, and lineage.
  - Record existing layer violations, cyclic dependencies, or shared-table ownership as explicit `Risk` exceptions.
- **Level 2 — Behavioral Pinning (`--stage verification`)**
  - Capture as-is contracts (pre/postconditions, invariants, failure modes) and attach characterization tests/inspections as `Evidence`.
  - Freeze external and cross-component contracts before internal refactoring.
- **Level 3 — Full Conformance (`--stage release`)**
  - Remediate architectural exceptions, enforce strict layer and context-budget rules, and satisfy all mandatory verification categories.

### 4.2 Reverse-Discovery Protocol
Defined in [`BROWNFIELD.md`](BROWNFIELD.md) for humans and AI agents:

1. **Boundary & Entrypoint Scan**: Identify APIs, jobs, events, and external data sources → draft `SystemDef`, `Capability` stubs, and `external_sources`.
2. **Data & State Extraction**: Inspect schemas, migrations, and ORM/DTO models → define `DataModel` entities, owners, classifications, and lineage.
3. **Component & Dependency Clustering**: Group modules by transaction/consistency boundaries → define `Component` entities, layers, and capability wiring.
4. **Invariant & Failure Mining**: Extract domain guards, error handlers, and existing tests → populate capability contracts, `Requirement` criteria, and initial `Evidence`.
5. **Gap & Risk Triage**: Convert missing test categories, unverified mitigations, and architecture violations into tracked `Risk` and `Requirement` backlog items.

### 4.3 Modernization & Strangler Migration
- Use existing `--compat` (`check_compatibility`) to verify that newly extracted or rewritten components preserve legacy capability contracts.
- Use existing transitive `--impact` to identify all downstream components, data models, requirements, and evidence invalidated by a refactoring step.

---

## 5. Reference Implementation & Tooling (`reference-implementation/`)

- **Core Validator Hardening (`metamodel.py`)** — remaining `REVIEW.md` rev. 8 issues
  - Report unknown `Risk.mitigated_by` IDs as unknown references.
  - Error on unknown `--impact` IDs.
  - Detect requirement `depends_on`/`refines` cycles.
  - Check `avoidance`/`transfer` treatments; track residual risk.
- **Stage & Onboarding Support**
  - Add `status` field and `--stage` (§ 2) + brownfield exception waivers tied to `Risk` IDs.
- **CLI** — keep current flag style (no subcommands)
  - Existing: `--json`, `--impact`, `--compat`, `--schema`.
  - Extend `--compat` with data contract compatibility.
  - Add `--stage <stage>` and `--context <component-id>` (bounded spec slice for AI tasks).
- **CI & Test Fixtures**
  - Add `push`/`pull_request` triggers to existing `.github/workflows/metamodel.yml` running `pytest` and validating all example specs.
  - Add negative test fixtures (`tests/invalid/*.yaml`), sample `old.yaml` for `--compat`, and multi-stage greenfield/brownfield examples.

---

## 6. Execution Roadmap

Milestones are numbered separately from greenfield phases, gates and brownfield levels.

### Milestone 1: Normative Hardening & CI
- [x] Fix remaining validator issues (§ 5; `REVIEW.md` rev. 8).
- [x] Add sample `old.yaml` for `--compat`.
- [x] Add negative fixtures (`reference-implementation/tests/invalid/*.yaml`); CLI tests check failure exit codes, JSON diagnostics and schema/metadata separation.
- [ ] Add `push`/`pull_request` triggers to `metamodel.yml` (postponed; workflow remains manual-only).

### Milestone 2: Lifecycle, Exceptions & Binding Model
- [x] Update `spec.md` with `status`, validation stages (incl. invariants per stage), requirement `status`/conflict resolution, evidence revision/supersession (`model-check`, `bounds`, `supersedes`), interface contracts, artifact bindings, context budget rules, and brownfield risk waivers (`waives`, `expires`).
- [ ] Implement `--stage` profiles and brownfield waiver validation in `metamodel.py`.
  - [x] Add entity statuses and active requirement/conflict-resolution semantics, including compatibility and impact propagation.
  - [x] Add evidence revision, supersession and bounded model-check records; preserve historical records and reject invalid supersession links.
  - [x] Add `inventory` and `discovery` profiles with executable track snapshots and CLI checks.
  - [x] Add architecture profile with shared composition checks, interface contracts and system context budgets.
  - [x] Add verification profile with category coverage, requirement readiness, reference/cycle/conflict checks and an executable snapshot.
  - [x] Add release profile with verified statuses, direct revision/metadata checks, evidence obligations, risk disposition and waiver rejection.
  - [ ] Track transitive dependency revisions to invalidate affected release evidence.
    - [x] Include interface payload dependencies in impact analysis before reusing its graph for evidence freshness.
    - Dependency snapshot serialization is awaiting a format decision (`Evidence.dependency_revisions` with typed entity keys proposed).
  - [ ] Validate risk waiver scope and expiry below release and apply bounded exemptions.
    - [x] Validate waiver metadata, remediation references and expiry at every stage.
    - [ ] Apply exemptions only to the named constraint and target; add brownfield stage snapshots.

### Milestone 3: Greenfield Workflow & Tooling
- [x] Split docs into `CONSTITUTION.md` (shared) + `GREENFIELD.md` (phases, gates, prompts).
- [ ] Implement `--context` slice export in `metamodel.py`.
- [x] Add traced end-to-end greenfield example (`examples/greenfield/`).

### Milestone 4: Brownfield Onboarding Workflow & Tooling
- [x] Create `BROWNFIELD.md` defining the 4 adoption levels, 5-step reverse-discovery protocol, waivers and prompts.
- [ ] Extend `--compat` with data and interface contract compatibility for safe strangler migrations.
- [x] Add brownfield onboarding example (`examples/brownfield/`) showing progression from Level 0 (`--stage inventory`) to Level 3 (`--stage release`).

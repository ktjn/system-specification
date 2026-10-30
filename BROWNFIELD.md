# Brownfield: Onboarding Existing Systems

Incremental sequencing for existing systems. Artifact rules: [constitution](CONSTITUTION.md). Load this document together with the constitution only.

Overrides the [greenfield](GREENFIELD.md) ordering: existing code is the discovery input, so architecture may be described before capabilities, and implementation precedes verification.

## Adoption Levels

Each level targets a `--stage` ([`spec.md` § 11](spec.md#11-metamodel-validation), [PLAN.md](PLAN.md)); known violations are allowed below `release` as risk waivers ([`spec.md` § 7](spec.md#7-risks)). Level 0 advances directly to Level 1 (`architecture`), skipping standalone `discovery` because existing code supplies architecture and contracts together. Levels 0–2 are executable with `--stage inventory`, `--stage architecture` and `--stage verification`; documented violations may be covered by the scoped waiver catalog in spec.md. Level 3 metadata validation is available with `--stage release`, which rejects all waivers. Waiver metadata and expiry are checked at every stage; automatic transitive dependency revision checks remain planned. Whole-spec validation (`metamodel.py <spec>`) checks prototype rules but is not a substitute for those levels.

| Level | Goal | Stage |
|---|---|---|
| 0 — Inventory | `system`, `external_sources`, deployable units, coarse module boundaries (`status: draft`); identity and syntax only | `inventory` |
| 1 — Dependency & data mapping | Observed `provides`/`requires`, data ownership, classification, lineage (`status: specified`); layer/cycle/ownership/budget violations recorded as waivers | `architecture` |
| 2 — Behavioral pinning | As-is contracts and characterization tests (`Evidence`); missing verification categories and unverified legacy capabilities covered by waivers; external contracts frozen before refactoring | `verification` |
| 3 — Full conformance | All waivers remediated; layer and context budget rules enforced without exception; all 10 verification categories satisfied (`status: verified`) | `release` |

For each adoption level, use the [shared decision record](CONSTITUTION.md#gate-decision-record): review observed artifacts against the level's criteria, record discrepancies and decide whether to pass, defer via an allowed waiver or rework.

| Level | Bring to review | Decision required before proceeding |
|---|---|---|
| 0 — Inventory | Entrypoints, jobs, external sources, deployable units and candidate component boundaries | All active runtime units and external dependencies are registered; unknown boundaries are flagged for discovery |
| 1 — Dependency & data mapping | Observed capability wiring, data schemas/owners/lineage, and discovered architecture violations with proposed waivers | Observed dependencies and data ownership match the running code; every violation is either remediated or deferred under a scoped, non-expired waiver |
| 2 — Behavioral pinning | As-is contracts, characterization test results for external/cross-component behavior, compatibility baseline and remaining coverage waivers | External and cross-component behavior is pinned by passing characterization evidence; unverified categories have bounded waivers expiring by release |
| 3 — Full conformance | Remediated architecture, compatibility results (`--compat`), requirement-linked evidence across all ten categories and risk dispositions | All waivers are closed, contracts and invariants hold without exception, and release evidence is current and reviewed |

If a level review fails (for example, an unrecorded dependency, a characterization test that contradicts the drafted contract, or an expired waiver), keep the level open: correct the specification to match observed behavior or complete the remediation before advancing. Do not hide discrepancies by inventing idealized contracts during discovery.

Worked progression from Level 0 to Level 3: [`examples/brownfield/`](examples/brownfield/README.md).

## Reverse Discovery

1. **Boundaries & entrypoints**: APIs, jobs, events, external sources → `system`, capability stubs, `external_sources`.
2. **Data & state**: schemas, migrations, ORM/DTO models (use [`modelable`](.github/skills/modelable/SKILL.md) `import` where helpful) → `data_models`, owners, classification, lineage.
3. **Components & dependencies**: cluster modules by transaction/consistency boundaries → `components`, layers, wiring.
4. **Invariants & failures**: domain guards, error handlers, existing tests → capability contracts, `Requirement.criteria`, initial `Evidence` (use [`tla`](.github/skills/tla/SKILL.md) / [`alloy`](.github/skills/alloy/SKILL.md) for concurrency or relational invariants).
5. **Gaps & risks**: missing verification categories, unverified mitigations, architecture violations → `risks` and `requirements` backlog.

Rules:

- Record observed behavior, not intended behavior; never invent contracts or fields.
- Separate **as-is discrepancies** (bugs, coupling, undocumented side effects observed in code) from **target changes** (remediation or modernization requirements).
- Use `metamodel.py` stage checks as supporting checks after each step; review the underlying code and test evidence before recording a level decision.

## Waivers

- Known violations (layer bypass, shared data ownership, cyclic dependencies, context-budget overruns, missing verification categories at Level 2, unverified legacy capabilities) are linked to a `Risk` (`waives`) with `treatment: mitigation` or `acceptance`.
- Each waiver requires a remediation requirement in `mitigated_by` and an `expires` bound (ISO date `YYYY-MM-DD` or target stage).
- Expired waivers fail validation at every stage; no waivers are allowed at `--stage release` (Level 3). Dates expire after the named UTC day; stage bounds expire on entry. Quote dates in YAML. Metadata checks require a resolved target, active remediation with criteria, and explicit residual acceptance for acceptance waivers. Only the named constraint and target are exempted; resolve the violation and retain its remediation evidence before closing the waiver.

## Characterization, Migration and Acceptance Loop

1. **Pin baseline (Levels 1–2)**: capture observed contracts and run characterization tests before changing internal structure. Record any deferred violations or coverage gaps as scoped waivers with remediation requirements.
2. **Scope one migration step**: run `--impact <id>` against the pinned baseline to identify affected components, data models, requirements and evidence. Prepare a bounded [implementation handoff](CONSTITUTION.md#implementation-handoff) containing the pinned contract, target remediation requirement, allowed boundary changes and characterization suite.
3. **Refactor or extract**: implement the strangler or boundary change within the handoff scope. If hidden coupling or an undocumented failure mode surfaces, stop and reopen the Level 1 or Level 2 review to update the observed baseline first.
4. **Verify compatibility and remediation**: check `--compat <pinned-baseline>` for capability, interface and data contracts, rerun invalidated characterization and remediation tests, and update evidence revisions. If a waiver expires or a check fails, recover by completing the remediation or rolling back the step before proceeding.
5. **Close waivers and accept (Level 3)**: remove remediated waivers once their mitigating requirements have passing, current evidence. Complete all ten verification categories and record the release decision ([`CONSTITUTION.md` § Acceptance](CONSTITUTION.md#acceptance)).

## Prompts

Ask for observed evidence and explicit discrepancy decisions. When serializing the reference format, use `metamodel.py --schema`; prose findings and review records remain part of the process. Per step:

- **1**: "List entrypoints of `<repo>` as capabilities and external sources; record observed behavior only."
- **2**: "Extract data models from `<schemas>`; do not invent fields."
- **3**: "Cluster `<modules>` into components by consistency boundary; list observed dependencies and violations."
- **4**: "Derive pre/postconditions, invariants and failure modes for `<capability>` from guards, handlers and tests."
- **5**: "List missing verification categories and violations as risks and requirements."
- **Level & waiver review**: "Compare these spec revisions against the observed code/tests and this level's criteria. Separate observed behavior from intended fixes, verify waiver scope/expiry and record pass, defer or rework."
- **Migration handoff**: "Refactor `<component>` within this bounded handoff while preserving the pinned contracts and characterization tests. Report affected revisions, compatibility findings and any newly discovered coupling."

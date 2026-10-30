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

Worked progression from Level 0 to Level 3: [`examples/brownfield/`](examples/brownfield/README.md).

## Reverse Discovery

1. **Boundaries & entrypoints**: APIs, jobs, events, external sources → `system`, capability stubs, `external_sources`.
2. **Data & state**: schemas, migrations, ORM/DTO models (use [`modelable`](.github/skills/modelable/SKILL.md) `import` where helpful) → `data_models`, owners, classification, lineage.
3. **Components & dependencies**: cluster modules by transaction/consistency boundaries → `components`, layers, wiring.
4. **Invariants & failures**: domain guards, error handlers, existing tests → capability contracts, `Requirement.criteria`, initial `Evidence` (use [`tla`](.github/skills/tla/SKILL.md) / [`alloy`](.github/skills/alloy/SKILL.md) for concurrency or relational invariants).
5. **Gaps & risks**: missing verification categories, unverified mitigations, architecture violations → `risks` and `requirements` backlog.

Rules:

- Record observed behavior, not intended behavior; never invent contracts or fields.
- Validate with `metamodel.py` after each step.

## Waivers

- Known violations (layer bypass, shared data ownership, cyclic dependencies, context-budget overruns, missing verification categories at Level 2, unverified legacy capabilities) are linked to a `Risk` (`waives`) with `treatment: mitigation` or `acceptance`.
- Each waiver requires a remediation requirement in `mitigated_by` and an `expires` bound (ISO date `YYYY-MM-DD` or target stage).
- Expired waivers fail validation at every stage; no waivers are allowed at `--stage release` (Level 3). Dates expire after the named UTC day; stage bounds expire on entry. Quote dates in YAML. Metadata checks require a resolved target, active remediation with criteria, and explicit residual acceptance for acceptance waivers. Only the named constraint and target are exempted; resolve the violation and retain its remediation evidence before closing the waiver.

## Modernization

- Strangler migration: `--compat old.yaml` compares declared capability, interface and data contracts. Breaking changes remain reported after a major bump and require migration review; passing comparison does not establish runtime compatibility.
- Before each refactoring step, run `--impact <id>` to find affected components, data models, requirements and invalidated evidence.

## Prompts

Generate structured output against `metamodel.py --schema`. Per step:

- **1**: "List entrypoints of `<repo>` as capabilities and external sources; record observed behavior only."
- **2**: "Extract data models from `<schemas>`; do not invent fields."
- **3**: "Cluster `<modules>` into components by consistency boundary; list observed dependencies and violations."
- **4**: "Derive pre/postconditions, invariants and failure modes for `<capability>` from guards, handlers and tests."
- **5**: "List missing verification categories and violations as risks and requirements."

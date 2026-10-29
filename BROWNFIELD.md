# Brownfield: Onboarding Existing Systems

Incremental sequencing for existing systems. Artifact rules: [constitution](CONSTITUTION.md). Load this document together with the constitution only.

Overrides the [greenfield](GREENFIELD.md) ordering: existing code is the discovery input, so architecture may be described before capabilities, and implementation precedes verification.

## Adoption Levels

Each level targets a planned `--stage` (see [PLAN.md](PLAN.md)); known violations are allowed below `release` as risk waivers.

| Level | Goal | Stage |
|---|---|---|
| 0 — Inventory | `system`, `external_sources`, deployable units, coarse module boundaries; identity and syntax only | `inventory` |
| 1 — Dependency & data mapping | Observed `provides`/`requires`, data ownership, classification, lineage; violations recorded as waivers | `architecture` |
| 2 — Behavioral pinning | As-is contracts and characterization tests as `Evidence`; external and cross-component contracts frozen before refactoring | `verification` |
| 3 — Full conformance | Waivers remediated; layer and context budget rules enforced; all verification categories satisfied | `release` |

## Reverse Discovery

1. **Boundaries & entrypoints**: APIs, jobs, events, external sources → `system`, capability stubs, `external_sources`.
2. **Data & state**: schemas, migrations, ORM/DTO models → `data_models`, owners, classification, lineage.
3. **Components & dependencies**: cluster modules by transaction/consistency boundaries → `components`, layers, wiring.
4. **Invariants & failures**: domain guards, error handlers, existing tests → capability contracts, `Requirement.criteria`, initial `Evidence`.
5. **Gaps & risks**: missing verification categories, unverified mitigations, architecture violations → `risks` and `requirements` backlog.

Rules:

- Record observed behavior, not intended behavior; never invent contracts or fields.
- Validate with `metamodel.py` after each step.

## Waivers

- Known violations (layer bypass, shared data ownership, cyclic dependencies, unverified legacy capabilities) are linked to a `Risk` with `treatment: mitigation` or `acceptance`.
- Each waiver needs a remediation requirement (planned: plus expiry, see [PLAN.md](PLAN.md)).

## Modernization

- Strangler migration: `--compat old.yaml` verifies that extracted or rewritten components preserve legacy contracts.
- Before each refactoring step, run `--impact <id>` to find affected components, data models, requirements and invalidated evidence.

## Prompts

Generate structured output against `metamodel.py --schema`. Per step:

- **1**: "List entrypoints of `<repo>` as capabilities and external sources; record observed behavior only."
- **2**: "Extract data models from `<schemas>`; do not invent fields."
- **3**: "Cluster `<modules>` into components by consistency boundary; list observed dependencies and violations."
- **4**: "Derive pre/postconditions, invariants and failure modes for `<capability>` from guards, handlers and tests."
- **5**: "List missing verification categories and violations as risks and requirements."

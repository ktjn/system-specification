# Reference Implementation

Validates [spec.md](../spec.md) with Python, Pydantic, YAML, and pytest.

- Validate spec: `uv run python metamodel.py example.yaml [--stage inventory|discovery|architecture|verification|release]` (default `release`)
- Export schema: `uv run python metamodel.py --schema`
- Impact analysis: `uv run python metamodel.py example.yaml --impact order`
- Compatibility: `uv run python metamodel.py new.yaml --compat old.yaml`
- Context slice: `uv run python metamodel.py example.yaml --context checkout`
- JSON output: add `--json`
- Run tests: `uv run pytest`
- Docker: `docker build -t metamodel . && docker run --rm metamodel [python metamodel.py ... | pytest]`
- Remote: `.github/workflows/metamodel.yml` runs either script in Docker when dispatched manually (`script`, `args`)

Partial prototype; the serialization format is defined in [spec.md](../spec.md) (**Current reference format**).

## Validator Behavior

- **Schema**: unknown fields are rejected (`extra="forbid"`); `status` defaults to `draft`.
- **Stages** (`--stage`): each check belongs to one stage (spec.md § 11) and runs at that stage and later. `inventory`: IDs, references, waiver form, `model-check` bounds; `discovery`: capability status and contract clauses; `architecture`: component status, provides, resolution, layers, cycles, ownership, classification, interfaces, budgets; `verification`: requirement status, capability coverage, 10 categories, requirement cycles, conflicts; `release`: `verified` status, evidence, risk disposition, no waivers.
- **Waivers**: valid below `release` when `treatment` is `mitigation`/`acceptance`, `mitigated_by` is non-empty and `expires` (date or stage) is not passed (stage expiry: current stage after `expires`). Waivable: layer violation, dependency cycle, shared data ownership (`also claimed`), context budget, missing categories. Active waivers are listed as `waivers` in `--json` output.
- **Interfaces**: capabilities required by another component need `interface`; `request`/`response` must name data models; `errors` keys must equal `failure_modes`.
- **Requirements**: `deprecated` requirements are inactive (no coverage, conflicts or evidence obligations); a conflict is resolved when either side's `resolved_by` names an active requirement; resolving and declassifying requirements need evidence at `release`.
- **Layers**: dependencies allowed within a layer or toward any lower layer (incl. non-adjacent); with non-empty `system.layers`, every component must declare one. Adjacency and source-code dependency rules need separate verification.
- **Resolution**: excludes the consuming component; rejects ambiguous providers without a binding and dependency cycles; one version per capability ID.
- **Versions** (`_ver_ok`): dot-separated integers; equal major, remaining segments ≥ minimum; non-numeric never matches. No segment normalization, major-zero rules, prereleases or general ranges.
- **Risks**: mitigating requirements need valid evidence; `avoidance` also needs verified `mitigated_by` and no `residual_accepted`; `acceptance` and `transfer` need `residual_accepted: true`, and `transfer` needs `transferred_to`. Accepted residual risks are listed as `residual_risks` in `--json` output. Mitigation effectiveness is not checked.
- **Evidence**: requires a passing record for `(requirement_id, requirement_version)`; rejects any failing record for that pair unless a passing record `supersedes` it with a `supersession_reason`. `model-check` requires `bounds`; `subject_id` must resolve. Artifacts, subject revisions and criterion coverage are not inspected.
- **Compatibility** (`check_compatibility`, `check_data_compatibility`, `--compat`): compares clauses as string sets; reports added preconditions, removed postconditions/invariants, added failure modes, capabilities removed without prior `status: deprecated`, data models with removed fields, changed field types or classification, and missing major bumps. No clause semantics, interface or constraint comparison; removed data models not reported.
- **Context** (`--context`): the component, its provided/required capabilities, owned and interface data models, and requirements/risks targeting them; evidence excluded.
- **Impact** (`impact_analysis`, `--impact`): follows capability, ownership and lineage dependencies transitively; reports affected components, capabilities, data models, requirements (incl. system-level and dependent) and evidence. Stored evidence is not changed.

## Limitations

- `consistency`, `quality_attributes`, `source_paths`, `schema_path` and evidence `subject_revision`, `timestamp`, `verifier` parsed only (no drift or freshness checks); evidence subject fields optional.
- Category `kind` consistency (CONSTITUTION Verification table) not checked.
- No automatic evidence invalidation; impact analysis only reports it.
- Results separate schema from metadata errors; metadata errors are not labeled by stage or check type.
- JSON Schema does not encode all invariants.
- Example provenance values (test, proof, benchmark) are illustrative; artifacts are not supplied.
- `VALID` means only that implemented checks found no errors; passing tests establish only the behavior they cover.

# Reference Implementation

Validates [spec.md](../spec.md) with Python, Pydantic, YAML, and pytest.

- Validate spec: `uv run python metamodel.py example.yaml [--stage inventory|discovery|architecture|verification|release]` (default `release`)
- Export schema: `uv run python metamodel.py --schema > schema.json` (committed; regenerate on model change, a test checks drift). Specs reference it via a `# yaml-language-server: $schema=…` modeline.
- Impact analysis: `uv run python metamodel.py example.yaml --impact order`
- Compatibility: `uv run python metamodel.py new.yaml --compat old.yaml`
- Context slice: `uv run python metamodel.py example.yaml --context checkout`
- JSON output: add `--json`
- Run tests: `uv run pytest` (incl. `corpus.yaml`: one or more invalid patches of `example.yaml` per invariant ID; examples are the valid corpus)
- Docker: `docker build -t metamodel . && docker run --rm metamodel [python metamodel.py ... | pytest]`
- CI & remote: `.github/workflows/metamodel.yml` runs `pytest` automatically on `push`/`pull_request` and runs either script in Docker when dispatched manually (`script`, `args`)

Partial prototype; the serialization format is defined in [spec.md](../spec.md) (**Current reference format**).

## Validator Behavior

- **Schema**: unknown fields are rejected (`extra="forbid"`); `status` defaults to `draft`.
- **Invariants**: `INVARIANTS` maps each ID (spec.md § 11) to its stage, waiver kind and rule; errors are prefixed `[ID]`, and a test keeps the table in sync with spec.md.
- **Stages** (`--stage`): each invariant runs at its stage and later.
- **Waivers**: valid below `release` when `treatment` is `mitigation`/`acceptance`, `mitigated_by` is non-empty and `expires` (date or stage) is not passed (stage expiry: current stage after `expires`). `Risk.waives` accepts either the waiver kind or its invariant ID (`DATA-03`, `COMP-03`, `COMP-05`, `COMP-06`, `REQ-01`). Active waivers are listed as `waivers` in `--json` output.
- **Interfaces**: capabilities required by another component need `interface`; `operation`, `idempotent` and `auth` must be defined; `request`/`response` must name data models; `errors` keys must equal `failure_modes`.
- **Requirements**: `deprecated` requirements are inactive (no coverage, conflicts or evidence obligations); `Requirement.kind` must match its `category` (`REQ-07`); a conflict is resolved when either side's `resolved_by` names an active requirement; mandatory, mitigating, resolving and declassifying requirements need evidence and verified dependencies at `release`; `declassified_by` relaxes classification propagation only when it names an active requirement.
- **Layers**: dependencies allowed within a layer or toward any lower layer (incl. non-adjacent); with non-empty `system.layers`, every component must declare one. Adjacency and source-code dependency rules need separate verification.
- **Resolution**: excludes the consuming component; rejects ambiguous providers without a binding, dependency cycles, and active components requiring deprecated capabilities (`COMP-07`); one version per capability ID.
- **Versions** (`_ver_ok`): dot-separated integers; equal major, remaining segments ≥ minimum; non-numeric never matches. No segment normalization, major-zero rules, prereleases or general ranges.
- **Risks**: mitigating requirements need valid evidence; `avoidance` also needs verified `mitigated_by` and no `residual_accepted`; `acceptance` and `transfer` need `residual_accepted: true`, and `transfer` needs `transferred_to`. Accepted residual risks are listed as `residual_risks` in `--json` output. Mitigation effectiveness is not checked.
- **Evidence**: requires a passing record for `(requirement_id, requirement_version)`; rejects any failing record for that pair unless a passing record `supersedes` it with a `supersession_reason`. `model-check` requires `bounds`; `subject_id` must resolve; at `release`, non-superseded evidence requires `timestamp`, `verifier` and `subject_revision` matching the subject's version (`EV-04`). Artifacts and criterion coverage are not inspected.
- **Compatibility** (`check_compatibility`, `check_data_compatibility`, `--compat`): compares clauses as string sets; reports added preconditions, removed postconditions/invariants, added failure modes, capabilities removed without prior `status: deprecated`, removed data models, data models with removed fields, changed field types or classification, and missing major bumps. No clause semantics, interface or constraint comparison.
- **Context** (`--context`): the component, its provided/required capabilities, owned and interface data models, and requirements/risks targeting them or the system; evidence excluded.
- **Impact** (`impact_analysis`, `--impact`): follows capability, ownership and lineage dependencies transitively; reports affected components, capabilities, data models, requirements (incl. system-level and dependent) and evidence (by requirement or `subject_id`). Stored evidence is not changed.

## Limitations

- `consistency`, `quality_attributes`, `source_paths` and `schema_path` parsed only (no source/schema drift checks).
- No automatic evidence invalidation; impact analysis only reports it.
- Results separate schema from metadata errors; metadata errors carry invariant IDs but not stage labels.
- JSON Schema does not encode all invariants.
- Example test and benchmark provenance values are illustrative; sample formal models are supplied in [`../examples/greenfield/Inventory.tla`](../examples/greenfield/Inventory.tla), [`Inventory.cfg`](../examples/greenfield/Inventory.cfg), [`Inventory.als`](../examples/greenfield/Inventory.als) and [`metamodel.als`](metamodel.als).
- `VALID` means only that implemented checks found no errors; passing tests establish only the behavior they cover.

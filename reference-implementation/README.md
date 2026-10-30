# Reference Implementation

Validates [spec.md](../spec.md) with Python, Pydantic, YAML, and pytest.

- Validate spec: `uv run python metamodel.py example.yaml`
- Inventory: `uv run python metamodel.py ../examples/brownfield/inventory.yaml --stage inventory`
- Discovery: `uv run python metamodel.py ../examples/greenfield/discovery.yaml --stage discovery`
- Architecture: `uv run python metamodel.py ../examples/greenfield/architecture.yaml --stage architecture`
- Verification specification: `uv run python metamodel.py ../examples/greenfield/verification.yaml --stage verification`
- Release metadata: add `--stage release` to validation of a completed specification; existing examples lack real release evidence. `test_release.py` builds synthetic records to exercise this profile.
- Export schema: `uv run python metamodel.py --schema`
- Impact analysis: `uv run python metamodel.py example.yaml --impact order`
- Compatibility: `uv run python metamodel.py new.yaml --compat old.yaml`
- JSON output: add `--json`
- Run tests: `uv run pytest`
- Run negative fixture tests: `uv run pytest test_invalid_fixtures.py`
- Docker: `docker build -t metamodel . && docker run --rm metamodel [python metamodel.py ... | pytest]`
- Remote: `.github/workflows/metamodel.yml` runs either script in Docker when dispatched manually (`script`, `args`)

Partial prototype; the serialization format is defined in [spec.md](../spec.md) (**Current reference format**).

## Invalid Specifications

[`tests/invalid/`](tests/invalid/) contains standalone rejection examples for duplicate IDs, ambiguous providers, conflicting evidence, unknown mitigations, requirement cycles, ownership, classification, undeclared layers and schema errors.

Run one directly: `uv run python metamodel.py tests/invalid/failing-evidence.yaml --json` (expected exit code: `1`). Tests assert the exact metadata diagnostic, or the schema error location, so an unrelated error cannot satisfy the case. These fixtures cover whole-spec validation; stage tests and `test_examples.py` cover the five profiles and available track snapshots. Waiver exemptions remain planned.

## Validator Behavior

- **Stages**: `inventory` checks identity uniqueness and reference syntax while allowing unmapped component stubs. `discovery` also requires capabilities at least `specified` and non-empty pre/postconditions, invariants and failure modes. `architecture` adds component status, composition checks, interfaces and context budgets without requiring requirements or evidence. JSON results identify the stage. Omitting `--stage` retains legacy whole-spec validation. Stage validation cannot be combined with `--impact`, `--compat` or `--schema`.
- **Interfaces and budgets**: architecture requires interfaces on provided capabilities, resolves request/response data models, checks failure mappings, and enforces `system.context_budget` (default provides/requires/owned-data limits: 5/8/4). Runtime contract behavior and source-code dependencies need separate verification.
- **Verification stage**: requires active requirements to be specified, categorized and non-empty; checks references, cycles and conflicts. Each capability needs ten-category coverage from requirements targeting itself, its providers, its interface data models or the system. Categories must match functional/non-functional kinds. Passing execution evidence is deferred to release except for conflict resolutions; supplied evidence metadata is still checked. Coverage labels do not establish test adequacy.
- **Release stage**: adds `verified`/`deprecated` statuses, evidence for mandatory requirements, mitigation/avoidance requirements, declared conflict resolutions and their transitive prerequisites, plus risk disposition. Current non-superseded evidence for active requirements needs subject metadata, timestamp, non-empty verifier and provenance. Historical records remain stored. Every supplied `Risk.waives` value is rejected, regardless of expiry. This validates metadata, not the supporting artifacts or actual system behavior.

- **Layers**: dependencies allowed within a layer or toward any lower layer (incl. non-adjacent); with non-empty `system.layers`, every component must declare one. Adjacency and source-code dependency rules need separate verification.
- **Resolution**: excludes the consuming component; rejects ambiguous providers without a binding and dependency cycles; one version per capability ID.
- **Versions** (`_ver_ok`): dot-separated integers; equal major, remaining segments ≥ minimum; non-numeric never matches. No segment normalization, major-zero rules, prereleases or general ranges.
- **Risks**: mitigating requirements need valid evidence; `avoidance` also needs verified `mitigated_by` and no `residual_accepted`; `acceptance` and `transfer` need `residual_accepted: true`, and `transfer` needs non-empty `transferred_to`. Accepted residual risks are listed as `residual_risks` in legacy whole-spec JSON output. `waives` and `expires` are preserved, but grant no exemptions; scope and expiry checks below release remain planned. Mitigation effectiveness is not checked.
- **Evidence**: requires passing, non-conflicting records for `(requirement_id, requirement_version)`. Supplied `subject_id`/`subject_revision` must match the requirement target and its declared version. Stale records cannot verify current obligations; fresh records can coexist with stale history. Legacy records without subject metadata are still accepted.
- **Supersession**: a passing record may explicitly replace a record for the same requirement/version and subject/revision using `supersedes` and a non-empty `supersession_reason`. Cycles, self-references and mismatched scopes are rejected; history is preserved.
- **Evidence metadata**: `model-check` requires non-empty `bounds`; optional `timestamp` requires a timezone, and `verifier` records tool/person identity. Artifact contents and criterion coverage are not inspected.
- **Lifecycle**: system, capabilities, components and requirements accept `draft` (default), `specified`, `verified`, `deprecated`. Deprecated requirements are inactive; active dependencies/refinements cannot reference them. A status label alone does not establish verification.
- **Conflicts**: `resolved_by` references a separate active requirement refining both conflicting requirements, with non-empty criteria and current passing, non-conflicting evidence. A resolution on either side handles both directions. Its semantic adequacy still requires review.
- **Compatibility** (`check_compatibility`, `--compat`): compares clauses as string sets; reports added preconditions, removed postconditions/invariants, added failure modes, missing major bump, and capabilities removed without prior deprecation. No clause semantics or data contracts.
- **Impact** (`impact_analysis`, `--impact`): follows capability, ownership and lineage dependencies transitively; reports affected components, capabilities, data models, requirements (incl. system-level and dependent) and evidence. Stored evidence is not changed.

## Limitations

- Cycles always rejected; no constraint can declare them acceptable.
- `consistency` and `quality_attributes` parsed only; `deprecated` used only by `--compat`.
- Supplied subject revisions are checked against declared entity versions; transitive dependency revisions and physical artifact changes are not automatically detected. Impact analysis reports affected evidence without changing stored records.
- Waiver exemptions/expiry, data/interface-contract compatibility and declassification not implemented. Legacy whole-spec validation does not enforce the new interface/budget rules; use `--stage architecture` or later for those checks.
- Results separate schema from metadata errors, not composition from verification checks.
- JSON Schema does not encode all invariants.
- Example provenance values (test, proof, benchmark) are illustrative; artifacts are not supplied.
- `VALID` means only that implemented checks found no errors; passing tests establish only the behavior they cover.

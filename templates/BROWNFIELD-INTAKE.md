# Brownfield intake and gate record

Copy beside the adopted specification. Tables below are review records, not new metamodel YAML fields. Replace placeholders with observed facts; keep unknowns and failed gates open.

## Scope and authority

| Record | Observed value |
|---|---|
| Repository / source revision | Repository root, exact revision and relevant dirty paths |
| Adoption scope | Whole product or named slice; included entrypoints and excluded/deferred boundaries |
| Existing authorities | Product architecture/specification, capability catalogs and precedence on disagreement |
| Tool map | Product commands versus the metamodel validator; imported schemas/catalogs do not imply conformance |
| Validator / schema pin | Validator revision, schema hash and hash-byte/line-ending convention |
| Native gates | Exact commands, required environment/tools, results and unresolved acceptance |
| Ownership | Artifact author, reviewer, acceptance owner and remediation owner |

## Boundaries and dependencies

| Unit / entrypoint | Internal, external, deferred or unknown | Observed provider / consumer / state owner | Evidence / unresolved mapping |
|---|---|---|---|
| Fill from source and deployment inventory | Do not invent internal providers | Include source files, schema roots and side effects | Register external data in `system.external_sources`; unresolved required capabilities keep architecture open |

Preserve transaction and consistency boundaries when setting context budgets. Explain per-component overrides; do not split one atomic promotion across fictitious independent services. Absence from a bounded slice does not mean an external dependency is implemented, unnecessary or verified.

### Relational & Storage Isolation (OBS-FB-01)

When multiple components share a physical relational database engine (e.g., PostgreSQL):
- Each component shall own a dedicated schema namespace (e.g. `auth.*`, `control.*`, `alerting.*`) matching its owned `data_models`.
- Cross-schema foreign keys are forbidden: replace cross-component foreign keys with capability contract checks (`validate-credential`, `manage-control-plane`) to prevent hidden cascade locks and cross-service coupling.
- Provision dedicated database user roles per component (e.g. `observable_auth_role`) with schema-scoped `GRANT` privileges in migration scripts.

### Storage Support Matrices vs. Layer Ordering (OBS-FB-02)

When a domain component must evaluate or query infrastructure-level storage directly (e.g. `alert-evaluator` querying ClickHouse):
- Prefer declaring explicit schema-compatibility ranges (e.g. `clickhouse-schema-support.yaml`) rather than inverting the layer hierarchy or creating circular application/domain RPC couplings (`COMP-05`, `COMP-06`).
- Ensure CI lint scripts enforce the compatibility range against migration files on every PR.

### Streaming Idempotency & Delivery Guarantees (OBS-FB-03)

For asynchronous, streaming, or message-driven write capabilities (e.g. Kafka/Redpanda -> ClickHouse):
- Do not rely solely on `interface.idempotent: true`; specify the concrete idempotency mechanism (e.g. deterministic deduplication tokens, `ReplacingMergeTree` keys, natural keys, or transactional outbox).
- Back crash-window redelivery and backpressure properties with formal verification (e.g. TLA+ `NoDuplicateVisibleRows` and `BoundedQueues`).

### Boundary Allowlist Ratcheting (OBS-FB-05)

When legacy code bases use transitional boundary allowlists (e.g., `component-boundary-allowlist.txt`):
- Allowlists shall only be used below Level 3 (`release`).
- Enforce strict ratchet checks in CI: the allowlist entry count may only decrease or stay equal, never increase.
- All allowlist entries must reach exactly zero prior to claiming Level 3 release acceptance.

## Data and evidence

- Record observed data fields and owners separately from provisional handling policy. `classification: unknown` needs an active `classification_review` requirement at inventory; unresolved classifications block architecture.
- Preserve existing schemas as authorities. Declare `schema_path` relative to the explicit repository root; existence is not schema/model semantic equivalence.
- For implementation evidence, bind each subject's contract `version` to its reviewed source `revision` and hashed source `artifacts` under `Spec.subject_bindings`. Record `Evidence.subject_version`, `subject_revision`, hashed execution `artifacts`, timestamp and verifier.
- Include dependency/environment pins and skipped check names/reasons. Evidence with `skipped` is partial; it does not verify its requirement or pass release.
- Paths are relative to the explicit repository root, not the specification directory. Provenance names one file with an optional `::selector` (for example `cli/tests/test_compilation_service.py::test_apply_rejects_stale_source`); put additional logs and environment captures in `artifacts`. Selectors are review references, not checked or executed by artifact validation.
- When upgrading a validator/schema, preserve the historical capture and pin a new run separately. Compare capability/data contracts, test stale/missing bindings and changed hashes, and retain skips and remaining gate failures. Passing records must cover independent executed criteria; never omit a relevant skip to make its requirement pass.
- Run `--check-artifacts --root <repository>` to check local integrity. Review Git/source authenticity, build correspondence, criterion coverage and historical evidence independently; do not claim those checks from hashes alone.

## Local operation protocol

Use one row per meaningful transition, including in-process APIs. Reference real symbols/DTOs in capability interfaces; HTTP status codes and a remote auth service are unnecessary for a local operation.

| Current state | Operation / inputs | Permission / confirmation / freshness | Success state and durable writes | Failure state / committed writes / recovery | Characterization |
|---|---|---|---|---|---|
| Example: no pending work | Preview | Caller permissions and scoped policy | Staged pending work; destinations unchanged | No published work; staging cleanup may need recovery | Actual test and output |
| Example: pending work | Apply | Exact confirmation; check freshness under lock | Exact staged bytes promoted; audit committed | Distinguish rollback from committed-with-cleanup-error | Actual test and output |
| Example: pending work | Discard | Caller owns staging | No pending work | Cleanup failure surfaced; never imply applied work | Actual test and output |

The protocol table defines review obligations; current string-based contracts do not execute or prove the state machine. Assess concurrency/formal-model applicability for locking, freshness, rollback and retries.

## Gate decision and feedback

| Gate / precise scope | Observed evidence and skips | Pass, rework or scoped waiver | Remaining obligation, owner and expiry |
|---|---|---|---|
| Inventory | Entrypoints, active jobs, external dependencies, unknowns | Review observed coverage | Record production topology gaps |
| Architecture | Wiring, state ownership, schemas, classification | Unknown providers/classifications keep gate open | Do not infer whole-product acceptance from a slice |
| Verification | Requirement-linked characterization and native gates | Partial evidence and bounded waivers remain visible | Skips and missing quality categories remain open |
| Release | Current, unskipped evidence and no waivers | Human acceptance after all obligations | Metadata validation is supporting evidence only |

Record newly discovered facts and model gaps using [constitution self-improvement](../CONSTITUTION.md#self-improvement-and-model-feedback): reproduction, affected rule/tool, proposed fix, acceptance test and disposition. Preserve historical observations when a fix changes validator behavior.

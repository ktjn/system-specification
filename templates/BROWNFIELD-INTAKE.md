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

## Data and evidence

- Record observed data fields and owners separately from provisional handling policy. `classification: unknown` needs an active `classification_review` requirement at inventory; unresolved classifications block architecture.
- Preserve existing schemas as authorities. Declare `schema_path` relative to the explicit repository root; existence is not schema/model semantic equivalence.
- For implementation evidence, bind each subject's contract `version` to its reviewed source `revision` and hashed source `artifacts` under `Spec.subject_bindings`. Record `Evidence.subject_version`, `subject_revision`, hashed execution `artifacts`, timestamp and verifier.
- Include dependency/environment pins and skipped check names/reasons. Evidence with `skipped` is partial; it does not verify its requirement or pass release.
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

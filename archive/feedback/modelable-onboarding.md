# Modelable onboarding feedback

Date: 2026-10-31. The findings below describe the original pinned baseline. Implementation dispositions follow; historical reproductions are retained.

Observed baselines:

- Modelable `0fead2321bdef11c72b2746eb57f3a8b0e327c94` (1.15.1).
- System-specification `00188b037797fd37240dab9a0a11c431815e3ac9`.
- Intake lives in Modelable at `docs/superpowers/specs/system-spec/`: product inventory, bounded compilation specification, vendored schema, source/environment hashes, characterization output and gate record.
- Local characterization: 221 passed, 2 skipped. Both skips require directory symlink support unavailable on this Windows host. No whole-product or release acceptance is claimed.

## Findings and proposed changes

| ID | Observed fact / gap | Proposed change and acceptance |
|---|---|---|
| MOD-FB-01 | Modelable already has authoritative `docs/architecture.md`, `modelable capabilities` and native gates. Its `modelable spec` command tracks dbt/FHIR/ODCS imports, not this metamodel. | Add an onboarding authority/tool map to the brownfield template: existing authorities, imported catalogs, system-spec document location, validator/schema revision and native gates. Test examples without implying that capability status or an imported schema is acceptance evidence. |
| MOD-FB-02 | The six product inventory boundaries are not fully characterized. A compilation slice can advance while browser/native/integration mapping remains open. The model has no explicit adoption scope or external component record. | Add a documented scope/dependency register first; distinguish whole-product, slice and external/deferred boundaries in gate records. Consider a later schema extension for external providers and excluded boundaries; missing consumers must never silently become resolved internal dependencies. |
| MOD-FB-03 | `DataModel.classification` defaults to `public` and has no unknown/provisional value. Brownfield discovery cannot safely infer classification for source previews, paths and user workspaces. | Permit explicit unknown/provisional classification at inventory, with a named review obligation and conservative handling policy. Require a reviewed value before accepting architecture/release; test propagation with unresolved sources. The Modelable slice uses `restricted` as a declared intake handling policy, not observed product metadata. |
| MOD-FB-04 | Evidence documentation permits an immutable source revision, but release validation compares `subject_revision` to the modeled subject's numeric `version`. The actual source commit differs from contract version `1.0`. | Separate subject contract version from implementation/source revision and bind both to the reviewed artifact. Do not merely accept arbitrary non-empty hashes: verify the binding or retain an explicit evidence-review gap. Regression: the actual source hash with a matching contract/source binding passes; stale subject version, stale source revision or missing binding fails. |
| MOD-FB-05 | Compilation is a multi-step local API: direct, preview, confirm/apply and discard. Direct and conversational paths differ; a post-commit cleanup exception means files already changed. Single `Interface.operation`, boolean `idempotent` and failure-name mappings cannot fully describe this protocol. | Document local-operation state machines, confirmation binding and committed/uncommitted outcomes in the handoff. Assess a later protocol/state-transition representation rather than inventing HTTP codes or treating every exception as rollback. Characterize stale preview, exact staged promotion, lock freshness, rollback and committed cleanup separately. |
| MOD-FB-06 | Native source/test/dependency/schema hashes and skipped-test details need sidecar records. The validator only parses `source_paths`/`schema_path`; it cannot verify closure or current execution artifacts. A context slice omits evidence and no tool resolves source paths against a declared root. | Define a repository-root and artifact/evidence binding convention, pin validator/schema versions, retain hashed execution metadata and report skips explicitly. Add optional checks for path resolution, source/schema drift and evidence artifacts without replacing native gates or weakening requirements. |

## Reproductions and evidence

- `cli/src/modelable/specs/tracking.py` declares `SUPPORTED_SPEC_KINDS = {"dbt", "fhir", "odcs"}` and stores `.modelable/specs.yml`.
- `cli/src/modelable/operations/compilation.py` defines the five captured top-level DTOs and `CompilationService`; `file_transaction.py` defines `FileTransactionCommittedError.committed = True`. The captured DTO field-name sets were compared against the actual source AST.
- `test_compilation_service.py::test_apply_rejects_changed_resolved_parent_even_with_same_bytes` and `::test_preview_rejects_symlink_that_escapes_workspace` skip with `directory symlinks are unavailable` (source lines 422 and 1136 at this revision). Separate skip diagnostics are retained with the onboarding evidence.
- [`metamodel.py`](../reference-implementation/metamodel.py) accepts the intake at `inventory` and compilation slice at `verification`; the latter has one declared `verification-category` waiver expiring after verification. No waiver is removed and no metadata check is bypassed.
- Calling `validate_spec(compilation_spec, 'release')` produces eight `[EV-04]` errors for actual source-hash evidence, including: `Evidence 'ev-mod-comp-01' requires timestamp, verifier and subject_revision matching 'direct-compilation' version`. Timestamp and verifier are present; the source hash is not the subject version. Other release failures remain legitimate because status/coverage/remediation work is unfinished.

Reproduce from `reference-implementation/` with the repositories as siblings:

```text
python metamodel.py ../../modelable/docs/superpowers/specs/system-spec/inventory.yaml --stage inventory --json
python metamodel.py ../../modelable/docs/superpowers/specs/system-spec/compilation.yaml --stage verification --json
python metamodel.py ../../modelable/docs/superpowers/specs/system-spec/compilation.yaml --stage release --json
```

The final command is expected to fail; it is diagnostic evidence, not an acceptance command that should be made green by changing recorded revisions.

## Implementation disposition

| Finding | Implemented response |
|---|---|
| MOD-FB-01 | [Brownfield intake template](../templates/BROWNFIELD-INTAKE.md) and constitution gate record now require existing authorities, command/tool distinctions, validator/schema pins and native gates. |
| MOD-FB-02 | Whole-product versus slice scope and external/deferred/unknown boundaries are explicit intake/gate records. Unresolved providers keep architecture open; external-provider resolution is deliberately not invented as new schema behavior. |
| MOD-FB-03 | Classification defaults to `unknown`; inventory requires an active `classification_review` requirement (`DATA-06`), architecture requires known classifications (`DATA-05`), and unresolved lineage cannot be bypassed by declassification. |
| MOD-FB-04 | `Spec.subject_bindings` records contract version, reviewed source revision and source hashes. Evidence can carry distinct `subject_version` / `subject_revision`; release rejects stale or absent bindings (`EV-04`, `REF-14`). The legacy version-valued format remains supported without a binding. |
| MOD-FB-05 | The intake template and implementation handoff require local operation transitions, confirmation/freshness, durable writes, rollback and committed-with-cleanup-error recovery. The protocol remains a review record; no executable state-machine validation is claimed. |
| MOD-FB-06 | Source and evidence file hash bindings, explicit `skipped` checks (`EV-05`), and optional `--check-artifacts --root` integrity checks are implemented. Context retains applicable source bindings. Git authenticity, build correspondence and semantic schema drift remain independent review/native-gate obligations. |

- New behavior has regression tests in [`test_onboarding.py`](../reference-implementation/test_onboarding.py); new invariants have invalid corpus cases and the generated schema is updated.
- Migration: existing specifications omitting classification must state a reviewed value or inventory review obligation. Existing source-hash evidence must add explicit contract/source bindings; arbitrary hashes alone still fail release. Modelable's historical onboarding remains pinned to its original validator/schema and is not silently upgraded by this PR.
- Suggested future external-provider and executable-protocol schema extensions remain deferred design options. The requested workflow conventions are implemented without expanding the reference format into a deployment topology or protocol engine.

## Remaining adoption work

- Review these changes against Modelable's pinned intake before migrating that intake to the new schema and source-binding format.
- Preserve compilation's five owned top-level DTOs under one promotion boundary using the existing `Component.context_budget` override. Do not split the transaction just to satisfy the default four-model budget.
- Expand Modelable's dependency/ownership and nested-type map, run missing symlink coverage on a suitable host, establish measured quality requirements and review formal applicability before higher conformance claims.
- These notes retain the reporting and disposition trail required by [constitution self-improvement](../CONSTITUTION.md#self-improvement-and-model-feedback); implementation does not close Modelable's open conformance gates.

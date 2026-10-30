# Repository Review: AI-Native System Specification

**Reviewer**: cjot  
**Date**: 2026-10-30 (Updated, rev. 14)
**Repository**: ktjn/system-specification

---

## Overview

- Repository spans principles (`CONSTITUTION.md`), track workflows (`GREENFIELD.md`, `BROWNFIELD.md`), a prose metamodel (`spec.md`) and a working **reference implementation** (`reference-implementation/`).
- Rev. 7: `metamodel.py` now enforces most `spec.md` §§ 2–11 invariants; compatibility, impact analysis and `--json` are wired into the CLI; a Docker-based `metamodel` workflow exists.
- Remaining work: automatic CI, invalid fixtures, requirement lifecycle, evidence revision metadata, and prompt templates.
- Rev. 8: new `PLAN.md` roadmap (greenfield/brownfield lifecycle) reviewed.
- Rev. 9: `PLAN.md` revised per rev. 8 critical item 2; no code/spec changes since rev. 7.
- Rev. 10: docs restructured into shared constitution + greenfield/brownfield tracks; no code changes.
- Rev. 11: `spec.md` scoped to metamodel/format; prototype details moved to README; `tla` and `alloy` skills added (#10, #11); no validator changes.
- Rev. 12: `modelable` skill (#13) repositioned to implementation/version change; `example.mdl` removed (duplicated `data_models`); no validator changes.
- Rev. 13: rev. 8 validator issues fixed (#15–#18): unknown `mitigated_by`/`--impact` IDs, requirement cycles, `avoidance`/`transfer` treatments with residual risk tracking. CI still postponed.
- Rev. 14: formalization review — `spec.md` is a prose metamodel; abstract syntax lives only in code; steps proposed for humans, LLMs and the checker.

---

## Changes Since Last Review (rev. 12)

| Area | Change | Status |
|------|--------|--------|
| `metamodel.py` (#15) | Unknown `Risk.mitigated_by` IDs reported as unknown references | ✅ Done |
| `metamodel.py` (#16) | `--impact` exits 1 on unknown IDs | ✅ Done |
| `metamodel.py` (#17) | Requirement `depends_on`/`refines` cycles detected (reuses `_cycles`) | ✅ Done |
| `metamodel.py` (#18) | `avoidance` needs verified `mitigated_by`, no residual; `transfer` needs `transferred_to` + `residual_accepted`; `--json` lists `residual_risks` | ✅ Done |
| `spec.md`, README, `example.yaml` (#18) | `transferred_to` documented; transfer risk example | ✅ Done |
| `PLAN.md` (#19) | Milestone 1 validator item ticked | ✅ Done |
| `REVIEW.md` | Formalization review added | ✅ Done |

---

## Changes in rev. 12 (since rev. 11)

| Area | Change | Status |
|------|--------|--------|
| `.github/skills/modelable` | Derives `.mdl` from `data_models` at implementation/version change: codegen, `diff`/`validate-compat` → `Evidence` | ✅ Done |
| `reference-implementation/example.mdl` | Added in #13, removed: duplicated `data_models` | ✅ Resolved |
| `example.yaml` | `req-order-contract`/`ev-order-contract` from #13 removed with `example.mdl` | ✅ Resolved |
| `CONSTITUTION.md` | `data_models` authoritative; links skill for implementation/version change | ✅ Done |

---

## Changes in rev. 11 (since rev. 10)

| Area | Change | Status |
|------|--------|--------|
| `spec.md` | Normative metamodel + current reference format only; § 12 lists required demonstrations | ✅ Done |
| `reference-implementation/README.md` | Validator behavior and limitations moved here from `spec.md` | ✅ Done |
| `.github/skills/tla` | TLA+/TLC how-to mapping contract clauses to properties and output to `Evidence` | ✅ Done |
| `.github/skills/alloy` | Alloy how-to for structural/relational invariants; points to `tla` for concurrency | ✅ Done |
| `CONSTITUTION.md` | Formal Verification links both skills with scope; capability format linked | ✅ Done |
| `PLAN.md` | Doc structure lists skills | ✅ Done |
| `example.yaml` | `req-projection` on `order-stock-projection` with Alloy evidence | ✅ Done |

---

## Changes in rev. 10 (since rev. 9)

| Area | Change | Status |
|------|--------|--------|
| `CONSTITUTION.md` | Replaces `AI-native-design.md`; English, order-free shared artifact rules; 10 verification categories (Security added) | ✅ Done |
| `GREENFIELD.md` | Replaces `AI-System-Development-Constitution.md`; phases → gates table, AI Execution Rule, prompts | ✅ Done |
| `BROWNFIELD.md` | New; adoption levels, reverse discovery, waivers, modernization, prompts; overrides greenfield ordering | ✅ Done |
| `PLAN.md` | Doc structure (§ 1.1); `PROMPTS.md`/`ONBOARDING.md` dropped; roadmap phases → milestones | ✅ Done |
| `spec.md` | Links updated | ✅ Done |

---

## Changes in rev. 9 (since rev. 8)

| Area | Change | Status |
|------|--------|--------|
| `PLAN.md` baseline | Phase 1 retargeted to rev. 8 remaining issues | ✅ Done |
| `PLAN.md` states | Single `status` set (`draft/specified/verified/deprecated`); adoption levels map to `--stage` | ✅ Done |
| `PLAN.md` reuse | Uses `bindings`, `--impact`, `--compat`, `metamodel.yml`; `provider_overrides` dropped | ✅ Done |
| `PLAN.md` CLI | Keeps flag style; adds `--stage`, `--context` | ✅ Done |
| `PLAN.md` coverage | Adds requirement `status`, evidence revision/supersession, cycle and unknown-ID fixes | ✅ Done |

---

## Changes in rev. 8 (since rev. 7)

| Area | Change | Status |
|------|--------|--------|
| `PLAN.md` | Added: metamodel extensions, greenfield gates, brownfield adoption levels, tooling, 4-phase roadmap | ✅ Added |

---

## Changes in rev. 7 (since rev. 6)

| Area | Change | Status |
|------|--------|--------|
| `metamodel.py` resolution | Ambiguous providers rejected; `bindings` disambiguate; self-dependency excluded; cycles detected | ✅ Done |
| `metamodel.py` § 11 | Duplicate IDs, ambiguous/unknown targets, dangling references, declared layers | ✅ Done |
| `metamodel.py` § 5 | Bidirectional ownership; unknown lineage reported separately from classification violation | ✅ Done |
| `metamodel.py` §§ 7–8 | Failing evidence blocks verification; mitigations require verified requirements | ✅ Done |
| `metamodel.py` § 10 | `check_compatibility` covers failure modes + major bump; `compare_specs` handles removal/deprecation; `--compat` CLI | ✅ Done |
| `metamodel.py` impact | Transitive; includes data models, system-level requirements, dependent requirements, invalidated evidence | ✅ Done |
| `metamodel.py` versions | Non-numeric versions no longer crash | ✅ Done |
| CLI | `--json`, `--impact`, `--compat`; schema vs. metadata errors distinguished | ✅ Done |
| Tests | 29 tests (up from 15), incl. CLI | ✅ Done |
| Tooling | `Dockerfile` + manually dispatched `metamodel` workflow | 🟡 Partial |
| `AGENTS.md` | Validation-before-commit, `--schema`, remote workflow rules | ✅ Done |
| Constitution | Phase 6 explicitly mapped (no API-specific entity) | ✅ Done |

---

## Status of Previous Recommendations

| # | Recommendation | Status | Notes |
|---|----------------|--------|-------|
| 1 | Verification evidence format | 🟡 Partial | `Evidence` still lacks subject revision, timestamp, verifier and supersession fields |
| 2 | Phase → metamodel mapping | ✅ Done | |
| 3 | Prompt templates | 🟡 Partial | One-line prompts per phase/step in `GREENFIELD.md`/`BROWNFIELD.md`; not tested against `--schema` output |
| 4 | Capability contract format | ✅ Done | |
| 5 | Versioning & compatibility | ✅ Done | Data-contract compatibility delegated to external `modelable` skill; not in validator |
| 6 | Data lineage / classification | 🟡 Partial | Declassification not implemented (documented) |
| 7 | Composition algorithm | ✅ Done | |
| 8 | Requirement dependency model | 🟡 Partial | Cycles detected; no `status`/resolution fields; every `conflicts_with` is an error |
| 9 | Layering invariant | ✅ Done | |
| 10 | Worked example | 🟡 Partial | `example.yaml` not traced through greenfield phases |
| 11 | Reference implementation roadmap | 🟡 Partial | Workflow is manual-only; no push/PR CI |

---

## Reference Implementation Review

### Strengths ✅

- Still compact (~270 lines) and readable.
- Rev. 8 issues fixed: unknown references, requirement cycles, all four risk treatments checked.
- All rev. 6 bugs fixed and covered by tests.
- Clear separation of schema errors (Pydantic) and metadata errors.
- `README.md` honestly lists validator behavior, limits and what `VALID` means.

### Remaining Issues 🐞

- `consistency`, `quality_attributes` parsed but unverified (documented).

### Tooling

- `metamodel` workflow is `workflow_dispatch` only — add `push`/`pull_request` triggers running `pytest` + `example.yaml`.
- Only positive example file; add `invalid/*.yaml` fixtures (tests currently mutate in-memory specs).
- No sample `old.yaml` for the documented `--compat` command.

---

## Skills Review

### Strengths ✅

- Compact, parallel structure (inputs, steps, evidence, prompt); one property per contract clause.
- Clear split: `tla` for interleaving/protocols, `alloy` for structure/relations.
- Both state that bounded checks are not unbounded proofs and require recording bounds/scope.
- `example.yaml` shows evidence from both (`tla+::`, `alloy::`).

### Remaining Issues 🐞

- **Method mismatch**: bounded model checks recorded as `method: proof`; `spec.md` § 8 has no `model-check`/bounded method or field for bounds.
- **Unverified commands**: TLC/Alloy invocations and sample models never run; no `Inventory.tla`/`.als` in repo.
- **Evidence naming**: `ev-reserve-test` uses `method: proof` (pre-existing).
- **Track links**: `GREENFIELD.md`/`BROWNFIELD.md` don't say at which gate/level skills apply.
- **`order_paid_at_most_once`**: concurrency invariant with no requirement or evidence; natural `tla` candidate.
- **`modelable`**: verified against modelable 1.x, but needs Python 3.14 and a `selectolax<1` workaround; classification is field-level (`open`…`secret`) vs. model-level (`public`…`restricted`) in the metamodel.

### Data Contract Duplication ✅ Resolved

- `example.mdl` restated `example.yaml` `data_models` with no consistency check and forced fits (`on true` join, hand-set classification).
- At specification time Modelable mostly overlaps `metamodel.py` (ownership, lineage, classification); its unique value is codegen and field-level compatibility.
- Resolution: `data_models` stay authoritative; `.mdl` is a derived implementation artifact (greenfield phase 9, version changes); `example.mdl` deleted.

---

## PLAN.md Review

### Strengths ✅

- Covers both greenfield (phase gates) and brownfield (adoption levels, reverse discovery) adoption.
- Gates map onto greenfield phases; stage-aware validation fits the existing validator.
- Brownfield exceptions tied to `Risk` reuse existing entities instead of adding new ones.
- Absorbs open rev. 7 items: prompt templates, worked example, CI, invalid fixtures, conflict resolution, declassification.

### Resolved since rev. 8 ✅

- Doc sprawl (rev. 10): three docs, `PROMPTS.md`/`ONBOARDING.md` dropped.
- Stale baseline, CI duplication, re-implementing `--impact`/`--compat`, CLI shape, `provider_overrides`, inconsistent states, missing items.

### Remaining Issues 🐞

- **Stage ↔ status**: relation between entity `status` and `--stage` undefined (e.g. must entities be `verified` at `release`?).
- **Stage list**: `discovery` stage unused by brownfield levels (Level 0 → `inventory`, Level 1 → `architecture`); state whether skipping is allowed.
- **Gate overlap**: Gate 2 requires context budget, yet Level 3 "enforces" it; clarify that Levels 1–2 pass via waivers.
- **Level 2 vs. Gate 3**: Gate 3 requires all 10 verification categories; characterization tests may not cover them — define waiver scope.
- **Unspecified**: waiver expiry semantics ("expiration/remediation requirement" — date, requirement, or both), per-stage invariants (deferred to Milestone 2), context budget defaults.
- **Interface contracts**: placement unclear (new entity vs. `Capability` extension); no milestone item for `spec.md` § 9 layering impact.

---

## Formalization Review

`spec.md` is a prose metamodel ("shall" requirements + **Current reference format** blocks), not a formal language specification.

| Layer | Defines | Lives in | Formal? |
|---|---|---|---|
| Concrete syntax | How a spec is written | YAML | ✅ (YAML standard) |
| Abstract syntax | Entities, fields, types | Pydantic models in `metamodel.py` (`--schema`) | 🟡 code only |
| Static semantics | Well-formedness invariants | `spec.md` § 11 prose; `validate_spec()` | 🟡 prose + prototype |
| Meaning | What a valid spec says about the system | `spec.md` §§ 2–10 | ❌ prose |

- **Drift risk**: format blocks hand-mirror Pydantic fields; § 11 invariants have no IDs, so code/tests can't be traced to them.
- **Only syntax rule**: `id@^version` (§ 10), a regex.
- **Actors**: human specifier (readable, editor feedback), LLMs (structured generation, bounded context), checker (single source of truth).

### Proposed Steps

| # | Step | Human | LLM | Checker |
|---|---|---|---|---|
| 1 | Commit `schema.json` (from `--schema`, with field descriptions) | Editor completion via `$schema` | Structured output, valid by construction | Pydantic stays the parser |
| 2 | Stable invariant IDs in § 11 (e.g. `INV-REF-01`) | Citable rules | Explains and fixes cited errors | Errors/tests cite IDs; coverage test |
| 3 | Invariants as data (ID, stage, check, message) | One rule table | Stage-scoped rules | Drives `--stage` |
| 4 | Generate format blocks from schema | No drift | Same | One source of truth |
| 5 | Alloy model of the metamodel (`metamodel.als`) | Rules shown consistent | — | Independent cross-check |
| 6 | Valid/invalid example corpus | Learn by example | Few-shot examples | Per-invariant tests |

Order: 1 → 2 → 6; 3 with Milestone 2 (`--stage`); 4–5 optional.

---

## Gaps in spec.md

- § 5: no mechanism for authorized declassification.
- § 6: schema for requirement lifecycle/conflict resolution to be defined when implemented.
- § 11: invariants lack stable IDs; reference format blocks not generated from the schema.
- § 8: reference format lacks evidence revision/supersession fields and a bounded/model-check method.

---

## Gaps in Other Documents

- **CONSTITUTION.md**: ✅ shared rules; artifact → metamodel mapping; no ordering.
- **GREENFIELD.md**: ✅ phases mapped to gates; gates reference planned `--stage`; no example walkthrough.
- **BROWNFIELD.md**: 🟡 waiver expiry and Level 2 waiver scope pending `PLAN.md` decisions; no example.
- **AGENTS.md**: ✅ validation and schema rules added.
- **reference-implementation/README.md**: ✅ validator behavior and limitations.
- **Skills**: 🟡 `tla`, `alloy` commands unverified, no sample models; `modelable` commands verified, no sample.
- **PLAN.md**: 🟡 rebased on rev. 8; stage semantics and waivers still underspecified (see above).

---

## Recommendations (Prioritized)

### 🔴 Critical

1. Add automatic CI (`push`/`pull_request`) running tests and example validation.

### 🟡 High

2. `PLAN.md`: define `status` ↔ `--stage` relation, per-stage invariants, waiver expiry and scope, context budget defaults.
3. Requirement `status` + conflict resolution fields (spec § 6 + impl).
4. Evidence subject revision/supersession fields and a bounded model-check method (spec § 8 + impl).
5. Formalization steps 1–2: commit `schema.json`; assign stable invariant IDs and cite them in errors/tests.

### 🟢 Medium

6. Validate track prompts against `--schema` output.
7. Trace `example.yaml` through greenfield phases; add brownfield example.
8. Invalid-spec fixtures and sample `old.yaml`.
9. Declassification.
10. Add sample `Inventory.tla`/`.als` models and run them; reference skills from track gates/levels.
11. Formalization steps 3–6: invariants as data (with `--stage`), generated format blocks, Alloy metamodel, example corpus.

---

## Gaps Summary Table

| Document | Section | Gap | Priority |
|----------|---------|-----|----------|
| repo | CI | Workflow is manual-only | 🔴 |
| metamodel.py / spec.md | requirements | No lifecycle / conflict resolution | 🟡 |
| metamodel.py / spec.md | evidence | No revision / supersession fields; bounded checks recorded as `proof` | 🟡 |
| spec.md / metamodel.py | formalization | Abstract syntax only in code; invariants unidentified; format blocks hand-mirrored | 🟡 |
| PLAN.md | stages / waivers | `status`↔stage relation, stage relaxations, waiver expiry/scope, budget defaults unspecified | 🟡 |
| docs | prompts / example | Prompts untested; no greenfield/brownfield walkthrough | 🟢 |
| skills | tla / alloy | No sample models; commands unverified; not linked from tracks | 🟢 |

---

## Conclusion

- `metamodel.py` now matches most of `spec.md`'s normative bar; rev. 6 critical items are resolved.
- Next steps: automatic CI, formalization steps 1–2, requirement lifecycle, and evidence revision metadata.
- Docs now split into shared constitution + two tracks, each loadable with bounded context.
- `PLAN.md` executable for Milestone 1; stage/waiver semantics must be settled before Milestone 2.
- Skills establish a clean pattern for technique how-tos; formal evidence semantics (bounded vs. proof) need a metamodel answer.
- Formalization: schema and invariant IDs should become the shared source for humans, LLMs and the checker.
- Data contracts have one source of truth (`data_models`); `modelable` applies at implementation and version change.

**Assessment**

- Metamodel clarity: ⭐⭐⭐⭐⭐
- Specification completeness: ⭐⭐⭐⭐⭐
- Reference implementation: ⭐⭐⭐⭐⭐ (up from ⭐⭐⭐⭐ — invariants enforced and tested)
- Implementation guidance for teams/AI: ⭐⭐⭐⭐⭐ (up from ⭐⭐⭐⭐ — track docs with prompts; brownfield covered)
- Roadmap (`PLAN.md`): ⭐⭐⭐⭐⭐ (up from ⭐⭐⭐⭐ — rebased, consistent states, reuses existing features)

---

**cjot** | 2026-10-29

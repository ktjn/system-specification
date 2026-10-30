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
- Rev. 14: stages, waivers, evidence, interface and lifecycle semantics specified in `spec.md` (8f40f6c) with greenfield/brownfield examples; validator not yet extended. Formalization review: `spec.md` is a prose metamodel; abstract syntax lives only in code.

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
| `spec.md` (8f40f6c) | Entity `status`; 5-stage validation table (`status` per stage, invariants, waivers); `waives`/`expires`; context budget defaults (`5/8/4`); `interface` on capabilities; `source_paths`, `schema_path`, `declassified_by`; requirement `category`/`resolved_by`; evidence `model-check`, `bounds`, `subject_revision`, `supersedes` | ✅ Specified, impl. pending |
| `examples/greenfield/`, `examples/brownfield/` (8f40f6c) | Traced 12-phase/4-gate and Level 0→3 examples; all `VALID`; brownfield `--compat old.yaml` passes | ✅ Done |
| `reference-implementation/old.yaml` (8f40f6c) | Sample for `--compat` | ✅ Done |
| Tracks, skills (8f40f6c) | Gates/levels reference `spec.md` § 11 and link `tla`/`alloy`/`modelable`; skills note `model-check` | ✅ Done |
| `PLAN.md` | Formalization steps (§ 5) and Milestone 5 | ✅ Done |
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
| 1 | Verification evidence format | 🟡 Partial | Revision/supersession/bounds specified (§ 8); not implemented |
| 2 | Phase → metamodel mapping | ✅ Done | |
| 3 | Prompt templates | 🟡 Partial | One-line prompts per phase/step in `GREENFIELD.md`/`BROWNFIELD.md`; not tested against `--schema` output |
| 4 | Capability contract format | ✅ Done | |
| 5 | Versioning & compatibility | ✅ Done | Data-contract compatibility delegated to external `modelable` skill; not in validator |
| 6 | Data lineage / classification | 🟡 Partial | `declassified_by` specified (§ 5); not implemented |
| 7 | Composition algorithm | ✅ Done | |
| 8 | Requirement dependency model | 🟡 Partial | Cycles detected; `status`/`resolved_by` specified (§ 6), not implemented |
| 9 | Layering invariant | ✅ Done | |
| 10 | Worked example | ✅ Done | `examples/greenfield/`, `examples/brownfield/` |
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

- Unknown fields silently ignored (Pydantic default): typos and planned fields (`status`, `waives`) pass as `VALID`; use `extra="forbid"`.
- Spec/impl gap: most fields specified in 8f40f6c (`status`, `waives`/`expires`, `category`, `resolved_by`, evidence revision, `interface`, budgets) are not modeled, so examples cannot carry them.
- 10-category coverage unverifiable until `Requirement.category` exists; examples rely on naming.
- `consistency`, `quality_attributes` parsed but unverified (documented).

### Tooling

- `metamodel` workflow is `workflow_dispatch` only — add `push`/`pull_request` triggers running `pytest` + `example.yaml`.
- Only positive example files (`example.yaml`, `examples/*`); add `invalid/*.yaml` fixtures (tests currently mutate in-memory specs).

---

## Skills Review

### Strengths ✅

- Compact, parallel structure (inputs, steps, evidence, prompt); one property per contract clause.
- Clear split: `tla` for interleaving/protocols, `alloy` for structure/relations.
- Both state that bounded checks are not unbounded proofs and require recording bounds/scope.
- `example.yaml` shows evidence from both (`tla+::`, `alloy::`).

### Remaining Issues 🐞

- **Method mismatch**: `model-check` + `bounds` specified (§ 8), but validator rejects `model-check`, so bounded checks are still recorded as `proof`.
- **Unverified commands**: TLC/Alloy invocations and sample models never run; no `Inventory.tla`/`.als` in repo.
- **Evidence naming**: `ev-reserve-test` uses `method: proof` (pre-existing).
- **`order_paid_at_most_once`**: concurrency invariant with no requirement or evidence in `example.yaml` or `examples/greenfield/`; natural `tla` candidate.
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
- 8f40f6c: `status` ↔ stage table; `discovery` skip stated; Levels 1–2 pass via waivers (incl. missing categories at Level 2); waiver expiry = ISO date or stage; per-stage invariants; budget defaults `5/8/4`; `interface` as `Capability` extension.
- Validator hardening (#15–#18) done; formalization added as Milestone 5.

### Remaining Issues 🐞

- **Risk disposition wording**: `spec.md` § 11 `release` row says "all risks mitigated or accepted", omitting `avoidance`/`transfer` (#18).
- **Milestone 2 size**: `--stage` now carries ~10 new fields and per-stage rules; split into PRs (fields + `extra="forbid"`, stages, waivers, evidence).
- **Examples ahead of format**: READMEs describe `status`, waivers and interfaces the YAML cannot express yet.

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

- § 11: `release` risk disposition omits `avoidance`/`transfer`.
- § 11: invariants lack stable IDs; reference format blocks not generated from the schema.
- §§ 3–8: reference format lags normative text (many fields marked planned).

---

## Gaps in Other Documents

- **CONSTITUTION.md**: ✅ shared rules; artifact → metamodel mapping; no ordering.
- **GREENFIELD.md**: ✅ gates reference `spec.md` § 11 and skills; walkthrough in `examples/greenfield/`.
- **BROWNFIELD.md**: ✅ waiver expiry/scope defined; walkthrough in `examples/brownfield/`.
- **AGENTS.md**: ✅ validation and schema rules added.
- **reference-implementation/README.md**: ✅ validator behavior and limitations.
- **Skills**: 🟡 linked from tracks; `tla`, `alloy` commands unverified, no sample models; `modelable` commands verified, no sample.
- **examples/**: 🟡 all `VALID`; READMEs describe fields the YAML cannot carry yet.
- **PLAN.md**: ✅ stage semantics settled; Milestone 1 validator done; Milestone 5 formalization added.

---

## Recommendations (Prioritized)

### 🔴 Critical

1. Add automatic CI (`push`/`pull_request`) running tests and example validation.

### 🟡 High

2. Reject unknown fields (`extra="forbid"`) so planned/misspelled fields fail instead of passing silently.
3. Milestone 2 in slices: model specified fields (`status`, `category`, `resolved_by`, `waives`/`expires`, evidence revision, `model-check`/`bounds`), then `--stage`, then waivers.
4. Formalization steps 1–2: commit `schema.json`; assign stable invariant IDs and cite them in errors/tests.
5. Fix `spec.md` § 11 `release` risk wording to include `avoidance`/`transfer`.

### 🟢 Medium

6. Validate track prompts against `--schema` output.
7. Invalid-spec fixtures (as formalization step 6 corpus).
8. Declassification, `interface`, context budgets, `source_paths`/`schema_path` in the validator.
9. Add sample `Inventory.tla`/`.als` models and run them.
10. Formalization steps 3–5: invariants as data (with `--stage`), generated format blocks, Alloy metamodel.

---

## Gaps Summary Table

| Document | Section | Gap | Priority |
|----------|---------|-----|----------|
| repo | CI | Workflow is manual-only | 🔴 |
| metamodel.py | schema | Unknown fields silently ignored | 🟡 |
| metamodel.py / spec.md | lifecycle | `status`, stages, waivers, `category`, `resolved_by`, evidence revision specified, not implemented | 🟡 |
| spec.md / metamodel.py | formalization | Abstract syntax only in code; invariants unidentified; format blocks hand-mirrored | 🟡 |
| spec.md | § 11 | `release` risk disposition omits `avoidance`/`transfer` | 🟢 |
| docs | prompts | Prompts untested against `--schema` | 🟢 |
| skills | tla / alloy | No sample models; commands unverified | 🟢 |

---

## Conclusion

- Validator hardening complete (#15–#18); all examples validate, `--compat` sample in place.
- `spec.md` now specifies stages, waivers, lifecycle and evidence semantics; the validator lags it, and unknown fields pass silently.
- Next steps: `extra="forbid"`, automatic CI, Milestone 2 in slices, formalization steps 1–2.
- Docs split into shared constitution + two tracks, each with a worked example.
- Formalization: schema and invariant IDs should become the shared source for humans, LLMs and the checker.
- Data contracts have one source of truth (`data_models`); `modelable` applies at implementation and version change.

**Assessment**

- Metamodel clarity: ⭐⭐⭐⭐⭐
- Specification completeness: ⭐⭐⭐⭐⭐
- Reference implementation: ⭐⭐⭐⭐ (down from ⭐⭐⭐⭐⭐ — lags newly specified semantics; unknown fields ignored)
- Implementation guidance for teams/AI: ⭐⭐⭐⭐⭐ (up from ⭐⭐⭐⭐ — track docs with prompts; brownfield covered)
- Roadmap (`PLAN.md`): ⭐⭐⭐⭐⭐ (up from ⭐⭐⭐⭐ — rebased, consistent states, reuses existing features)

---

**cjot** | 2026-10-30

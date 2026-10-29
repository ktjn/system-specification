# Repository Review: AI-Native System Specification

**Reviewer**: cjot  
**Date**: 2026-10-29 (Updated, rev. 9)
**Repository**: ktjn/system-specification

---

## Overview

- Repository spans principles (constitution, design notes), a formal metamodel (`spec.md`) and a working **reference implementation** (`reference-implementation/`).
- Rev. 7: `metamodel.py` now enforces most `spec.md` §§ 2–11 invariants; compatibility, impact analysis and `--json` are wired into the CLI; a Docker-based `metamodel` workflow exists.
- Remaining work: automatic CI, invalid fixtures, requirement lifecycle, evidence revision metadata, and prompt templates.
- Rev. 8: new `PLAN.md` roadmap (greenfield/brownfield lifecycle) reviewed.
- Rev. 9: `PLAN.md` revised per rev. 8 critical item 2; no code/spec changes since rev. 7.

---

## Changes Since Last Review (rev. 8)

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
| 3 | Prompt templates | 🔴 Open | AGENTS.md points to `--schema`; no templates (e.g. `PROMPTS.md`) |
| 4 | Capability contract format | ✅ Done | |
| 5 | Versioning & compatibility | ✅ Done | Data-contract compatibility not implemented (documented in § 12) |
| 6 | Data lineage / classification | 🟡 Partial | Declassification not implemented (documented) |
| 7 | Composition algorithm | ✅ Done | |
| 8 | Requirement dependency model | 🟡 Partial | No `status`/resolution fields; every `conflicts_with` is an error |
| 9 | Layering invariant | ✅ Done | |
| 10 | Worked example | 🟡 Partial | `example.yaml` not traced through constitution phases |
| 11 | Reference implementation roadmap | 🟡 Partial | Workflow is manual-only; no push/PR CI |

---

## Reference Implementation Review

### Strengths ✅

- Still compact (~260 lines) and readable.
- All rev. 6 bugs fixed and covered by tests.
- Clear separation of schema errors (Pydantic) and metadata errors.
- `spec.md` § 12 honestly lists remaining limits and what `VALID` means.

### Remaining Issues 🐞

- Unknown `Risk.mitigated_by` IDs reported as "unverified mitigation" instead of unknown reference.
- `--impact` with an unknown ID returns system-level requirements instead of an error.
- Requirement `depends_on`/`refines` cycles not detected.
- `avoidance`/`transfer` risk treatments have no checks; residual risk for `mitigation` not tracked.
- `consistency`, `quality_attributes` parsed but unverified (documented).

### Tooling

- `metamodel` workflow is `workflow_dispatch` only — add `push`/`pull_request` triggers running `pytest` + `example.yaml`.
- Only positive example file; add `invalid/*.yaml` fixtures (tests currently mutate in-memory specs).
- No sample `old.yaml` for the documented `--compat` command.

---

## PLAN.md Review

### Strengths ✅

- Covers both greenfield (phase gates) and brownfield (adoption levels, reverse discovery) adoption.
- Gates map onto constitution phases; stage-aware validation fits the existing validator.
- Brownfield exceptions tied to `Risk` reuse existing entities instead of adding new ones.
- Absorbs open rev. 7 items: prompt templates, worked example, CI, invalid fixtures, conflict resolution, declassification.

### Resolved since rev. 8 ✅

- Stale baseline, CI duplication, re-implementing `--impact`/`--compat`, CLI shape, `provider_overrides`, inconsistent states, missing items.

### Remaining Issues 🐞

- **Stage ↔ status**: relation between entity `status` and `--stage` undefined (e.g. must entities be `verified` at `release`?).
- **Stage list**: `discovery` stage unused by brownfield levels (Level 0 → `inventory`, Level 1 → `architecture`); state whether skipping is allowed.
- **Gate overlap**: Gate 2 requires context budget, yet Level 3 "enforces" it; clarify that Levels 1–2 pass via waivers.
- **Level 2 vs. Gate 3**: Gate 3 requires all 10 verification categories; characterization tests may not cover them — define waiver scope.
- **Unspecified**: waiver expiry semantics ("expiration/remediation requirement" — date, requirement, or both), per-stage invariants (deferred to Phase 2), context budget defaults.
- **Interface contracts**: placement unclear (new entity vs. `Capability` extension); no Phase 1–4 item for `spec.md` § 9 layering impact.
- **Doc sprawl**: still adds `GREENFIELD.md`, `PROMPTS.md`, `ONBOARDING.md`; consider fewer docs per `AGENTS.md` terseness.

---

## Gaps in spec.md

- § 5: no mechanism for authorized declassification.
- § 6: schema for requirement lifecycle/conflict resolution to be defined when implemented.
- § 8: reference format lacks evidence revision/supersession fields.

---

## Gaps in Other Documents

- **Constitution**: ✅ all phases mapped; no example walkthrough.
- **AI-native-design.md**: ✅ aligned.
- **AGENTS.md**: ✅ validation and schema rules added.
- **PLAN.md**: 🟡 rebased on rev. 8; stage semantics and waivers still underspecified (see above).

---

## Recommendations (Prioritized)

### 🔴 Critical

1. Add automatic CI (`push`/`pull_request`) running tests and example validation.

### 🟡 High

2. `PLAN.md`: define `status` ↔ `--stage` relation, per-stage invariants, waiver expiry and scope, context budget defaults.
3. Requirement `status` + conflict resolution fields (spec § 6 + impl).
4. Evidence subject revision/supersession fields (spec § 8 + impl).
5. Fix remaining issues above (unknown mitigations, unknown impact ID, requirement cycles).

### 🟢 Medium

6. Prompt templates (separate doc) using `--schema` output.
7. Trace `example.yaml` through constitution phases.
8. Invalid-spec fixtures and sample `old.yaml`.
9. Residual risk tracking and declassification.

---

## Gaps Summary Table

| Document | Section | Gap | Priority |
|----------|---------|-----|----------|
| repo | CI | Workflow is manual-only | 🔴 |
| metamodel.py / spec.md | requirements | No lifecycle / conflict resolution | 🟡 |
| metamodel.py / spec.md | evidence | No revision / supersession fields | 🟡 |
| metamodel.py | validation | Unknown mitigations mislabelled; requirement cycles; unknown impact ID | 🟡 |
| PLAN.md | stages / waivers | `status`↔stage relation, stage relaxations, waiver expiry/scope, budget defaults unspecified | 🟡 |
| docs | prompts / example | No prompt templates; no phase walkthrough | 🟢 |

---

## Conclusion

- `metamodel.py` now matches most of `spec.md`'s normative bar; rev. 6 critical items are resolved.
- Next steps: automatic CI, requirement lifecycle, and evidence revision metadata.
- `PLAN.md` is now rebased and executable for Phase 1; stage/waiver semantics must be settled before Phase 2.

**Assessment**

- Metamodel clarity: ⭐⭐⭐⭐⭐
- Specification completeness: ⭐⭐⭐⭐⭐
- Reference implementation: ⭐⭐⭐⭐⭐ (up from ⭐⭐⭐⭐ — invariants enforced and tested)
- Implementation guidance for teams/AI: ⭐⭐⭐⭐
- Roadmap (`PLAN.md`): ⭐⭐⭐⭐⭐ (up from ⭐⭐⭐⭐ — rebased, consistent states, reuses existing features)

---

**cjot** | 2026-10-29

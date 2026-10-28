# Repository Review: AI-Native System Specification

**Reviewer**: cjot  
**Date**: 2026-10-28 (Updated, rev. 7)
**Repository**: ktjn/system-specification

---

## Overview

- Repository spans principles (constitution, design notes), a formal metamodel (`spec.md`) and a working **reference implementation** (`reference-implementation/`).
- Rev. 7: `metamodel.py` now enforces most `spec.md` §§ 2–11 invariants; compatibility, impact analysis and `--json` are wired into the CLI; a Docker-based `metamodel` workflow exists.
- Remaining work: automatic CI, invalid fixtures, requirement lifecycle, evidence revision metadata, and prompt templates.

---

## Changes Since Last Review (rev. 6)

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

## Gaps in spec.md

- § 5: no mechanism for authorized declassification.
- § 6: schema for requirement lifecycle/conflict resolution to be defined when implemented.
- § 8: reference format lacks evidence revision/supersession fields.

---

## Gaps in Other Documents

- **Constitution**: ✅ all phases mapped; no example walkthrough.
- **AI-native-design.md**: ✅ aligned.
- **AGENTS.md**: ✅ validation and schema rules added.

---

## Recommendations (Prioritized)

### 🔴 Critical

1. Add automatic CI (`push`/`pull_request`) running tests and example validation.

### 🟡 High

2. Requirement `status` + conflict resolution fields (spec § 6 + impl).
3. Evidence subject revision/supersession fields (spec § 8 + impl).
4. Fix remaining issues above (unknown mitigations, unknown impact ID, requirement cycles).

### 🟢 Medium

5. Prompt templates (separate doc) using `--schema` output.
6. Trace `example.yaml` through constitution phases.
7. Invalid-spec fixtures and sample `old.yaml`.
8. Residual risk tracking and declassification.

---

## Gaps Summary Table

| Document | Section | Gap | Priority |
|----------|---------|-----|----------|
| repo | CI | Workflow is manual-only | 🔴 |
| metamodel.py / spec.md | requirements | No lifecycle / conflict resolution | 🟡 |
| metamodel.py / spec.md | evidence | No revision / supersession fields | 🟡 |
| metamodel.py | validation | Unknown mitigations mislabelled; requirement cycles; unknown impact ID | 🟡 |
| docs | prompts / example | No prompt templates; no phase walkthrough | 🟢 |

---

## Conclusion

- `metamodel.py` now matches most of `spec.md`'s normative bar; rev. 6 critical items are resolved.
- Next steps: automatic CI, requirement lifecycle, and evidence revision metadata.

**Assessment**

- Metamodel clarity: ⭐⭐⭐⭐⭐
- Specification completeness: ⭐⭐⭐⭐⭐
- Reference implementation: ⭐⭐⭐⭐⭐ (up from ⭐⭐⭐⭐ — invariants enforced and tested)
- Implementation guidance for teams/AI: ⭐⭐⭐⭐

---

**cjot** | 2026-10-28

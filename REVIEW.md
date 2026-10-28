# Repository Review: AI-Native System Specification

**Reviewer**: cjot  
**Date**: 2026-10-28 (Updated, rev. 6)
**Repository**: ktjn/system-specification

---

## Overview

- Repository spans principles (constitution, design notes), a formal metamodel (`spec.md`) and a working **reference implementation** (`reference-implementation/`).
- Rev. 6: `spec.md` has been updated to formalize capability contracts, data classifications, requirement/risk/evidence semantics, compatibility rules, identity/referential invariants, and explicit prototype limitations.
- Remaining work is now primarily implementation and tooling: enforcing the newly specified invariants in `metamodel.py` and adding CI.

---

## Changes Since Last Review (rev. 5)

| Area | Change | Status |
|------|--------|--------|
| `spec.md` § 1, 12 | Cross-links constitution, design notes, and reference implementation; documents prototype scope and acceptance limits | ✅ Done |
| `spec.md` § 2 | Clarifies layer policies and distinguishes logical capability dependencies from source-code dependencies | ✅ Done |
| `spec.md` § 4 | Documents capability contract format, YAML example, provider disambiguation, and `@^` version constraints | ✅ Done |
| `spec.md` § 5 | Formalizes 4-level classification order, transitive propagation, and bidirectional ownership consistency | ✅ Done |
| `spec.md` § 6, 7 | Specifies requirement relation semantics, active-requirement conflict rules, and verified risk mitigations | ✅ Done |
| `spec.md` § 8 | Defines full evidence metadata obligations, conflict/supersession rules, and change invalidation | ✅ Done |
| `spec.md` § 10 | Formalizes contract variance, `_ver_ok` caret matching limits, and transitive impact analysis requirements | ✅ Done |
| `spec.md` § 11 | Adds identity uniqueness and referential integrity invariants | ✅ Done |
| `reference-implementation` / `AI-*.md` / `AGENTS.md` | Unchanged | — |

---

## Status of Previous Recommendations

| # | Recommendation | Status | Notes |
|---|----------------|--------|-------|
| 1 | Verification evidence format | 🟡 Partial | Normative obligations documented in `spec.md` § 8; `Evidence` model still relies on external `provenance` for timestamp/verifier/subject version |
| 2 | Phase → metamodel mapping | ✅ Done | Table in constitution; phases 6, 10, 12 explicitly marked as having no dedicated entity |
| 3 | Prompt templates in AGENTS.md | 🔴 Open | AGENTS.md holds style rules; templates belong elsewhere (e.g. `PROMPTS.md`) |
| 4 | Capability contract format | ✅ Done | Documented in `spec.md` § 4 and implemented in `Capability` model |
| 5 | Versioning & compatibility rules | ✅ Done (spec) / 🟡 Partial (impl) | Formalized in `spec.md` § 10; `check_compatibility` still omits `failure_modes`, version bumps, and CLI hookup |
| 6 | Data lineage / classification | ✅ Done (spec) / 🟡 Partial (impl) | Formalized in `spec.md` § 5; declassification and general constraint propagation remain unimplemented |
| 7 | Composition algorithm | 🟡 Partial | Unambiguous resolution specified in `spec.md` § 4; `metamodel.py` still uses a simple map that overwrites duplicate providers |
| 8 | Requirement dependency model | 🟡 Partial | Semantics and active/conflict rules specified in `spec.md` § 6; `metamodel.py` has no `status` field and only checks `conflicts_with` |
| 9 | Layering invariant | ✅ Done | Spec + impl + test (`spec.md` § 2 notes undeclared-layer and adjacency limits) |
| 10 | Worked example | 🟡 Partial | `example.yaml` exists; not traced through constitution phases |
| 11 | Reference implementation roadmap | ✅ Done | Python + Pydantic + YAML + pytest; CI not yet added |

---

## Reference Implementation Review

*(Unchanged since rev. 3 — no code changes; limitations are now explicitly documented in `spec.md`.)*

### Strengths ✅

- Very compact (~165 lines) and readable; follows AGENTS.md style.
- All 8 original § 11 invariants have a check and a test.
- Evidence is bound to `(requirement_id, requirement_version)` → stale evidence is detected (`test_stale_evidence`).
- `--schema` exports JSON Schema → usable by editors and AI agents for structured output.
- `check_compatibility` encodes core contract variance.

### Bugs / Correctness Issues 🐞

- **Multiple providers silently overwrite**: `prov = {cap: c.id ...}` keeps the last provider (violates `spec.md` § 4).
- **Self-dependency allowed**: a component requiring a capability it provides resolves to itself (violates `spec.md` § 4).
- **Misleading error**: unknown `derived_from` source is reported as "violates classification propagation".
- **Risk message vs. check**: "unverified mitigation" only checks that mitigating requirements *exist*, not that they have passing evidence (`spec.md` § 7).
- **Failing evidence ignored**: a requirement with both passing and failing evidence is considered verified (`spec.md` § 8).
- **Version parsing crashes** on non-numeric versions (e.g. `1.0-beta`).
- **Unknown layers skipped**: a component with `layer` not in `system.layers` is silently ignored (`spec.md` § 2).

### Missing Checks (specified in `spec.md`, not yet enforced in `metamodel.py`)

- Duplicate IDs within entity types and ambiguous untyped targets (`spec.md` § 11).
- Dangling references: `Component.provides`, `Requirement.target`, `depends_on`, `refines`, `Risk.target`, `Evidence.requirement_id`, `DataModel.owner` (`spec.md` § 11).
- `Component.owns_data` vs `DataModel.owner` bidirectional consistency (`spec.md` § 5, § 11).
- Cyclic capability dependencies (`spec.md` § 4).
- Requirement status / conflict resolution (`spec.md` § 6).
- `deprecated`, `consistency`, `quality_attributes` parsed but unused (`spec.md` § 12).
- Residual risk tracking for `mitigation` treatment (`spec.md` § 7).
- Data contract compatibility (`spec.md` § 5, § 10).

### Compatibility & Impact Analysis

- `check_compatibility` ignores `failure_modes` and doesn't verify a major version bump (`spec.md` § 10).
- `check_compatibility` not wired into `validate_spec` or CLI.
- `impact_analysis` is one level deep; no transitive dependents, no data models, misses system-level requirements (`spec.md` § 10).

### Tooling

- No GitHub Actions workflow — add `uv run pytest` + `uv run python metamodel.py example.yaml`.
- Only positive example; add `invalid/*.yaml` fixtures.
- Consider `--json` CLI output.

---

## Gaps in spec.md

All previous documentation gaps in `spec.md` (§§ 2, 4, 5, 6, 7, 8, 10, 11, 12) have been resolved in rev. 6. `spec.md` now separates normative metamodel requirements from **Current reference format** / **Current implementation** notes.

Remaining minor specification questions:

- § 5: no standard mechanism for authorized data declassification if needed in future revisions.
- § 6: when the reference format adds requirement lifecycle/conflict-resolution fields, document their exact schema in `spec.md`.

---

## Gaps in Other Documents

### AI-System-Development-Constitution.md

- ✅ Phase 1 capability template distinguishes discovery context from `Capability` fields.
- ✅ Phase 7 verification categories map to `Requirement.kind` and `Evidence.method`.
- Phase 6 API details still have no dedicated metamodel entity; decide whether concepts such as `Endpoint`, `Idempotency` and `Security` remain external or need explicit representation.

### AI-native-design.md

- ✅ Component example matches the `Component` model, with responsibilities expressed through capabilities and requirements.
- ✅ Contract example uses `failure_modes`, matching the capability model.

### AGENTS.md

- Consider adding:
  - "Specs must validate with `metamodel.py` before committing."
  - Pointer to schema export for structured generation.

---

## Recommendations (Prioritized)

### 🔴 Critical

1. Fix multi-provider ambiguity, self-dependency, and failing-evidence handling in `metamodel.py`.
2. Enforce § 11 identity uniqueness, referential integrity, ownership consistency, and declared-layer checks in `metamodel.py`.
3. Add CI workflow running tests and example validation.

### 🟡 High

4. ✅ Back-port implemented rules and prototype limitations into `spec.md`.
5. Add requirement `status` / conflict resolution and verified risk mitigation checks to `metamodel.py`.
6. Extend `check_compatibility` (failure modes, version bump) and expose via CLI.
7. Transitive `impact_analysis` including data models and system-level requirements.

### 🟢 Medium

8. ✅ Align remaining templates (constitution Phase 1, AI-native component/contract examples) with the metamodel field names.
9. Prompt templates (separate doc) using `--schema` output.
10. Trace `example.yaml` through constitution phases using the mapping table.
11. Invalid-spec fixtures and `--json` output.

---

## Gaps Summary Table

| Document | Section | Gap | Priority |
|----------|---------|-----|----------|
| metamodel.py | resolution | Multiple providers silently overwritten; self-dependency allowed | 🔴 |
| metamodel.py | validation | Missing § 11 unique ID, referential integrity, ownership & layer checks | 🔴 |
| metamodel.py | evidence / risk | Failing evidence ignored; mitigation evidence not verified | 🔴 |
| repo | CI | No workflow | 🔴 |
| metamodel.py | requirements | No requirement status / conflict resolution fields | 🟡 |
| metamodel.py | compat / impact | Partial coverage vs. `spec.md` § 10 | 🟡 |
| Constitution | Phase 6 | API contracts have no dedicated metamodel entity | 🟢 |

---

## Conclusion

- `spec.md` is now comprehensive and honest: it formalizes contracts, data lineage, verification, evolution, and referential integrity while clearly separating normative requirements from current prototype limits.
- All documentation alignment issues across `spec.md` and `AI-*.md` are resolved.
- Next step: bring `metamodel.py` up to the normative bar set by `spec.md` §§ 4–11 and add CI.

**Assessment**

- Metamodel clarity: ⭐⭐⭐⭐⭐
- Specification completeness: ⭐⭐⭐⭐⭐ (up from ⭐⭐⭐⭐ — rules and prototype limits fully documented)
- Reference implementation: ⭐⭐⭐⭐ (compact, tested; correctness gaps now explicitly tracked in `spec.md` § 12)
- Implementation guidance for teams/AI: ⭐⭐⭐⭐

---

**cjot** | 2026-10-28

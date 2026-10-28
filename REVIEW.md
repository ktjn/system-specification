# Repository Review: AI-Native System Specification

**Reviewer**: cjot  
**Date**: 2026-10-28 (Updated, rev. 5)
**Repository**: ktjn/system-specification

---

## Overview

- Repository spans principles (constitution, design notes), a formal metamodel (`spec.md`) and a working **reference implementation** (`reference-implementation/`).
- Rev. 5: the AI-*.md documents have been updated against rev. 4; the remaining capability, component and verification examples now match the metamodel.
- Remaining work is mostly about precision: closing gaps between what `spec.md` says and what `metamodel.py` actually enforces.

---

## Changes Since Last Review (rev. 4)

| Area | Change | Status |
|------|--------|--------|
| Constitution Phase 1 | Capability template now matches the `Capability` model; discovery context is distinguished from model fields | ✅ Done |
| Constitution Phase 7 | Verification categories mapped to `Requirement.kind` and `Evidence.method` | ✅ Done |
| AI-native-design.md | Component example now matches the `Component` model; responsibilities are described through capabilities and requirements | ✅ Done |
| AI-native-design.md | Contract example uses `failure_modes`, matching the capability model | ✅ Done |
| spec.md / reference-implementation / AGENTS.md | Unchanged | — |

---

## Status of Previous Recommendations

| # | Recommendation | Status | Notes |
|---|----------------|--------|-------|
| 1 | Verification evidence format | 🟡 Partial | `Evidence` model: id, requirement_id/version, method, passed, provenance. No timestamp, verifier, artifact/component version |
| 2 | Phase → metamodel mapping | ✅ Done | Table in constitution; phases 6, 10, 12 explicitly marked as having no dedicated entity |
| 3 | Prompt templates in AGENTS.md | 🔴 Open | AGENTS.md holds style rules; templates belong elsewhere (e.g. `PROMPTS.md`) |
| 4 | Capability contract format | ✅ Done (impl) | `Capability`: pre/postconditions, invariants, failure_modes. Not yet documented in `spec.md` |
| 5 | Versioning & compatibility rules | 🟡 Partial | Caret ranges (`@^1.0`) + `check_compatibility`. `spec.md` § 10 still prose only |
| 6 | Data lineage / classification | 🟡 Partial | 4-level monotonic propagation. No declassification/aggregation rules |
| 7 | Composition algorithm | 🟡 Partial | Simple map lookup; no multi-provider or cycle handling |
| 8 | Requirement dependency model | 🟡 Partial | Fields exist (`depends_on`, `refines`, `conflicts_with`); only conflicts checked |
| 9 | Layering invariant | ✅ Done | Spec + impl + test |
| 10 | Worked example | 🟡 Partial | `example.yaml` exists; not traced through constitution phases (now feasible using the mapping table) |
| 11 | Reference implementation roadmap | ✅ Done | Python + Pydantic + YAML + pytest; CI not yet added |

---

## Reference Implementation Review

*(Unchanged since rev. 3 — no code changes.)*

### Strengths ✅

- Very compact (~165 lines) and readable; follows AGENTS.md style.
- All 8 § 11 invariants have a check and a test.
- Evidence is bound to `(requirement_id, requirement_version)` → stale evidence is detected (`test_stale_evidence`).
- `--schema` exports JSON Schema → usable by editors and AI agents for structured output.
- `check_compatibility` encodes correct contract variance.

### Bugs / Correctness Issues 🐞

- **Multiple providers silently overwrite**: `prov = {cap: c.id ...}` keeps the last provider.
- **Misleading error**: unknown `derived_from` source is reported as "violates classification propagation".
- **Risk message vs. check**: "unverified mitigation" only checks that mitigating requirements *exist*, not that they have passing evidence.
- **Failing evidence ignored**: a requirement with both passing and failing evidence is considered verified.
- **Version parsing crashes** on non-numeric versions (e.g. `1.0-beta`).
- **Unknown layers skipped**: a component with `layer` not in `system.layers` is silently ignored.

### Missing Checks (spec says "shall", impl doesn't enforce)

- Duplicate IDs (components, capabilities, requirements, evidence).
- Dangling references: `Requirement.target`, `depends_on`, `refines`, `Risk.target`, `Evidence.requirement_id`, `DataModel.owner`.
- `Component.owns_data` vs `DataModel.owner` consistency.
- Cyclic capability dependencies.
- "Domain must not depend on infrastructure details" (constitution Phase 9) — only ordering is checked.
- No requirement status / conflict resolution → any `conflicts_with` is always an error.
- `deprecated`, `consistency`, `quality_attributes` parsed but unused.
- Residual risk tracking for `mitigation` treatment (§ 7).
- Data contract compatibility (§ 5).

### Compatibility & Impact Analysis

- `check_compatibility` ignores `failure_modes` and doesn't verify a major version bump.
- `check_compatibility` not wired into `validate_spec` or CLI.
- `impact_analysis` is one level deep; no transitive dependents, no data models, misses system-level requirements.

### Tooling

- No GitHub Actions workflow — add `uv run pytest` + `uv run python metamodel.py example.yaml`.
- Only positive example; add `invalid/*.yaml` fixtures.
- Consider `--json` CLI output.

---

## Gaps in spec.md

- § 4: document contract structure (or reference the JSON Schema).
- § 5: define classification levels and propagation rule.
- § 6: requirement status (active/inactive) and conflict resolution.
- § 8: minimal evidence metadata (timestamp, verifier, subject version).
- § 10: formalize implemented compatibility rules (variance, caret ranges).
- § 11: invariants for unique IDs and referential integrity.

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

1. Fix multi-provider ambiguity and failing-evidence handling.
2. Add referential integrity + unique ID checks.
3. Add CI workflow running tests and example validation.

### 🟡 High

4. Back-port implemented rules (contract schema, classification, compatibility, evidence fields) into `spec.md`.
5. Add requirement `status` to make conflict invariant meaningful.
6. Extend `check_compatibility` (failure modes, version bump) and expose via CLI.
7. Transitive `impact_analysis` including data models.

### 🟢 Medium

8. ✅ Align remaining templates (constitution Phase 1, AI-native component/contract examples) with the metamodel field names.
9. Prompt templates (separate doc) using `--schema` output.
10. Trace `example.yaml` through constitution phases using the new mapping table.
11. Invalid-spec fixtures and `--json` output.

---

## Gaps Summary Table

| Document | Section | Gap | Priority |
|----------|---------|-----|----------|
| metamodel.py | resolution | Multiple providers silently overwritten | 🔴 |
| metamodel.py | validation | No referential integrity / unique IDs | 🔴 |
| metamodel.py | evidence | Failing evidence ignored | 🔴 |
| repo | CI | No workflow | 🔴 |
| spec.md | § 4, 5, 8, 10 | Implemented rules not documented | 🟡 |
| spec.md | § 6 / § 11 | No requirement status / conflict resolution | 🟡 |
| metamodel.py | compat / impact | Partial coverage | 🟡 |
| Constitution | Phase 6 | API contracts have no dedicated metamodel entity | 🟢 |

---

## Conclusion

- The AI-*.md documents now align their capability, component, contract and verification examples with the metamodel. The Phase 6 mapping explicitly notes that API contracts have no dedicated entity.
- Main risk remains spec/implementation drift: several rules live only in code, several "shall" statements aren't enforced.
- Next step: harden the validator (ambiguity, integrity, CI) and back-port its rules into `spec.md`.

**Assessment**

- Metamodel clarity: ⭐⭐⭐⭐⭐
- Reference implementation: ⭐⭐⭐⭐ (compact, tested; correctness gaps above)
- Implementation guidance for teams/AI: ⭐⭐⭐⭐ (up from ⭐⭐⭐ — mapping and cross-references added)

---

**cjot** | 2026-10-28

# Brownfield Walkthrough: Legacy Billing Strangler Migration

End-to-end walkthrough of onboarding and modernizing a legacy billing monolith across the 5 reverse-discovery steps, 4 adoption levels, a failed gate recovery, and a strangler migration handoff of [`BROWNFIELD.md`](../../BROWNFIELD.md) and [`CONSTITUTION.md`](../../CONSTITUTION.md).

> **Evidence boundary**: [`inventory.yaml`](inventory.yaml), [`architecture.yaml`](architecture.yaml), [`verification.yaml`](verification.yaml), [`old.yaml`](old.yaml) and [`spec.yaml`](spec.yaml) are **illustrative process snapshots**, and the gate records below are **illustrative review decisions**. No legacy billing codebase or test execution log is bundled in this repository; `metamodel.py` `VALID` confirms stage metadata and waiver rules only, not runtime compatibility or release acceptance ([`spec.md` §§ 7, 8, 11](../../spec.md#7-risks)).

---

## Level 0 — Observed Inventory (`--stage inventory`)

- **Artifact**: [`inventory.yaml`](inventory.yaml) (`uv run python metamodel.py ../examples/brownfield/inventory.yaml --stage inventory`).
- **Reverse discovery step 1**: scan runtime entrypoints and external integrations; register `billing-system@1.0`, external source `stripe-gateway`, and draft component stubs `invoicing` and `payment-worker` (`status: draft`) before capability wiring is untangled.

| Record | Content |
|---|---|
| Scope | Level 0 (`inventory`), [`inventory.yaml`](inventory.yaml) |
| Responsibility | Onboarding lead (author), billing maintainers (reviewers) |
| Findings | Both deployable units (`invoicing`, `payment-worker`) and external gateway (`stripe-gateway`) are registered with unique IDs; internal table coupling flagged for Level 1 |
| Outcome | **Pass** — advance to Level 1 (`architecture`) |
| Follow-up | Extract SQL schemas and trace observed cross-module calls without idealizing boundaries |

---

## Level 1 — Dependency Mapping & Discrepancy Review (`--stage architecture`)

- **Artifact**: [`architecture.yaml`](architecture.yaml) (`uv run python metamodel.py ../examples/brownfield/architecture.yaml --stage architecture`).
- **Reverse discovery steps 2–3**:
  - Extract `invoice` (`owner: invoicing`, `confidential`) and `ledger-entry` (`owner: payment-worker`, `derived_from: [invoice]`, `external_source: stripe-gateway`).
  - Map observed capabilities `issue-invoice` and `charge-invoice`.
  - **Discrepancies observed in legacy code**:
    1. `payment-worker` writes directly to the `invoice` table (`owns_data: [ledger-entry, invoice]` → `shared-data-ownership` on `invoice`).
    2. `payment-worker` (`domain`) invokes `issue-invoice` callbacks on `invoicing` (`application`) (`layer-violation` on `payment-worker`).
    3. `invoicing` ↔ `payment-worker` form a synchronous call cycle (`dependency-cycle` on both components).
  - Record observed behavior as-is and attach scoped waivers (`risk-split-ownership`, `risk-remove-callback`, `risk-break-cycle-invoicing`, `risk-break-cycle-payment`) with remediation requirements `req-split-ownership`, `req-remove-callback`, `req-break-cycle-invoicing`, `req-break-cycle-payment` and `expires: verification`.

| Record | Content |
|---|---|
| Scope | Level 1 (`architecture`), [`architecture.yaml`](architecture.yaml) |
| Responsibility | Onboarding lead (author), tech lead (reviewer) |
| Findings | As-is coupling is recorded honestly rather than hidden; each violation is bound to a target-scoped waiver with an active remediation requirement expiring at `verification` |
| Outcome | **Defer (Pass Level 1 with bounded waivers)** — remediate shared ownership and callback cycle before Level 2 (`verification`) |
| Follow-up | Execute bounded refactoring to sever the callback cycle and direct `invoice` table writes before entering `verification` |

---

## Failed Gate & Recovery (Attempting Level 2 Before Remediation)

- **Failed check**: running `uv run python metamodel.py ../examples/brownfield/architecture.yaml --stage verification` before remediating the Level 1 architecture debt fails (covered by `test_brownfield_snapshots_require_scoped_waivers_and_expire_at_next_gate` in [`reference-implementation/test_examples.py`](../../reference-implementation/test_examples.py)):
  - All four `expires: verification` waivers fail with `waiver expired at stage 'verification'`.
  - With the expired waivers rejected, the underlying `shared-data-ownership`, `layer-violation` and `dependency-cycle` errors surface together with missing verification category coverage.

| Record | Content |
|---|---|
| Scope | Gate review for Level 2 (`verification`) against unremediated [`architecture.yaml`](architecture.yaml) |
| Responsibility | Tech lead |
| Findings | Level 1 architecture waivers expired on entry to `verification`; `payment-worker` still mutates `invoice` directly and calls `invoicing` |
| Outcome | **Rework** — keep Level 1/2 transition open; do not extend waiver expiry without fixing the boundary |
| Follow-up | Issue a bounded handoff to remove the callback and direct `invoice` table writes, then re-enter Level 2 with pinned contracts |

---

## Migration Handoff & Level 2 Behavioral Pinning (`--stage verification`)

- **Bounded migration handoff** ([`CONSTITUTION.md` § Implementation Handoff](../../CONSTITUTION.md#implementation-handoff)):
  - **Impact check**: `uv run python metamodel.py ../examples/brownfield/architecture.yaml --impact invoice` identifies `invoicing`, `payment-worker`, `issue-invoice`, `charge-invoice`, `ledger-entry` and `req-split-ownership`.
  - **Scope**: remove `invoice` from `payment-worker.owns_data` and remove `issue-invoice@^1.0` from `payment-worker.requires`; satisfy `req-split-ownership`, `req-remove-callback`, `req-break-cycle-invoicing` and `req-break-cycle-payment` while preserving the external `issue-invoice` and `charge-invoice` contracts.
- **Recovered Level 2 artifact**: [`verification.yaml`](verification.yaml) (`uv run python metamodel.py ../examples/brownfield/verification.yaml --stage verification`).
  - Architecture violations are resolved (`invoicing` alone owns `invoice`; `payment-worker` has `requires: []`).
  - Characterization requirements (`req-characterize-issue-invoice`, `req-characterize-charge-invoice`) and full-coverage backlog items (`req-cover-issue-invoice`, `req-cover-charge-invoice`) are specified.
  - Remaining non-functional/formal category gaps on the two legacy capabilities are deferred under `risk-coverage-issue-invoice` and `risk-coverage-charge-invoice` (`waives: missing-verification-category`, `expires: release`).

| Record | Content |
|---|---|
| Scope | Level 2 (`verification`), [`verification.yaml`](verification.yaml) and compatibility baseline [`old.yaml`](old.yaml) |
| Responsibility | Tech lead & QA reviewer |
| Findings | Shared ownership, layer bypass and cycle are eliminated; external contracts are frozen; remaining category gaps are explicitly waived until `release` |
| Outcome | **Defer (Pass Level 2 with coverage waivers expiring at `release`)** — proceed to characterization execution and Level 3 conformance |
| Follow-up | Execute characterization suites, complete all 10 verification categories (including TLA+ for `invoice_charged_at_most_once` and Alloy for `ledger-entry` lineage), and verify `--compat` |

---

## Level 3 — Compatibility Check & Release Review (`--stage release`)

- **Contract compatibility**: `uv run python metamodel.py ../examples/brownfield/spec.yaml --compat ../examples/brownfield/old.yaml` verifies that the modernized `1.1` contracts (`audit_logged`, `invoice_marked_paid`) preserve all `1.0` preconditions, postconditions, invariants, failure modes and data fields.
- **Release review**: [`spec.yaml`](spec.yaml) illustrates the 10-category requirement and evidence links after waiver closure, but omits strict `--stage release` fields (`status: verified`, capability `interface` blocks, requirement `category` tags, and evidence `subject_revision`/`timestamp`/`verifier`/`bounds`).

| Record | Content |
|---|---|
| Scope | Level 3 (`release`), [`spec.yaml`](spec.yaml) compared against [`old.yaml`](old.yaml) |
| Responsibility | Release owner |
| Findings | `--compat` passes with additive postconditions (`1.0 → 1.1`); however, [`spec.yaml`](spec.yaml) is an illustrative whole-spec file without real test/model-check artifacts or `--stage release` revision metadata |
| Outcome | **Rework / Hold for real release evidence** — do not claim Level 3 release acceptance until characterization, 10-category test/benchmark runs and formal checks are executed and recorded with immutable subject revisions |
| Follow-up | Supply real execution artifacts and full `--stage release` metadata before closing the migration |

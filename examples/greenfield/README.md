# Greenfield Walkthrough: Commerce Checkout & Inventory

End-to-end walkthrough of `place-order` and `reserve-inventory` across the 12 phases, 4 gates, implementation handoff and change loop of [`GREENFIELD.md`](../../GREENFIELD.md) and [`CONSTITUTION.md`](../../CONSTITUTION.md).

> **Evidence boundary**: [`discovery.yaml`](discovery.yaml), [`architecture.yaml`](architecture.yaml), [`verification.yaml`](verification.yaml) and [`spec.yaml`](spec.yaml) are **illustrative specification snapshots**, and the gate records below are **illustrative review decisions**. No production commerce service, load-test report or TLC/Alloy log is bundled in this repository; `metamodel.py` `VALID` confirms stage metadata and structural rules only, not system acceptance ([`spec.md` §§ 8, 11](../../spec.md#8-verification)).

---

## Gate 1 — Discovery (`--stage discovery`)

- **Artifact**: [`discovery.yaml`](discovery.yaml) (`uv run python metamodel.py ../examples/greenfield/discovery.yaml --stage discovery`).
- **Phases 1–2**: define `place-order` (`preconditions: [cart_not_empty, customer_active]`, `postconditions: [order_created, inventory_reserved]`, `invariants: [order_paid_at_most_once]`, `failure_modes: [insufficient_inventory, customer_blocked]`) and `reserve-inventory` (`invariants: [stock_never_negative]`, `failure_modes: [insufficient_inventory, product_not_found]`). No components or technology choices are introduced.

| Record | Content |
|---|---|
| Scope | Gate 1 (`discovery`), capabilities `place-order@1.0` and `reserve-inventory@1.0` in [`discovery.yaml`](discovery.yaml) |
| Responsibility | Domain lead (author), checkout/inventory engineers (reviewers) |
| Findings | Success and failure outcomes cover blocked customers, missing products and insufficient stock; invariants `order_paid_at_most_once` and `stock_never_negative` stated without implementation coupling |
| Outcome | **Pass** — proceed to Gate 2 (`architecture`) |
| Follow-up | Derive component boundaries from the two consistency invariants; define request/response models and failure status codes |

---

## Gate 2 — Architecture (`--stage architecture`)

- **Artifact**: [`architecture.yaml`](architecture.yaml) (`uv run python metamodel.py ../examples/greenfield/architecture.yaml --stage architecture`).
- **Phases 3–6, 9–10**:
  - Split `checkout` (`application`, strong consistency on `order`, `provides: [place-order]`, `requires: [reserve-inventory@^1.0]`) from `inventory` (`domain`, strong consistency on `stock-item` and `order-stock-projection`, `provides: [reserve-inventory]`).
  - Bind interfaces (`POST /v1/orders`, `POST /v1/reservations`, both `sync`, idempotent, `409` on domain failure modes) and external source `erp-product-feed`.
  - Context budget: `checkout` (1/1/1) and `inventory` (1/0/2) stay within `5 / 8 / 4`.

| Record | Content |
|---|---|
| Scope | Gate 2 (`architecture`), components `checkout@1.0`, `inventory@1.0` and data models `order@1.0`, `stock-item@1.0`, `order-stock-projection@1.0` in [`architecture.yaml`](architecture.yaml) |
| Responsibility | Architect (author), domain & platform reviewers |
| Findings | Layering (`application → domain`) and single-owner data rules hold; `order-stock-projection` preserves `confidential` classification from `order`; both components fit the context budget |
| Outcome | **Pass** — proceed to Gate 3 (`verification`) |
| Follow-up | Specify verifiable criteria across all 10 categories for both capabilities and assess formal verification for concurrency and projection integrity |

---

## Gate 3 — Verification (`--stage verification`)

- **Artifact**: [`verification.yaml`](verification.yaml) (`uv run python metamodel.py ../examples/greenfield/verification.yaml --stage verification`).
- **Phases 7–8**:
  - Map requirements across all 10 categories for the system, `checkout`/`place-order`, and `inventory`/`reserve-inventory` (`req-order-func`, `req-order-sem`, `req-order-contract`, `req-order-serial`, `req-order-conc`, `req-reserve-func`, `req-reserve-sem`, `req-reserve-contract`, `req-stock-serial`, `req-reserve-conc`, `req-projection`, `req-latency`, `req-scale`, `req-resilience`, `req-reserve-resilience`, `req-security`, `req-reserve-security`, `req-observability`).
  - Flag `req-reserve-conc` (`stock_never_negative` under concurrent reservations) for [`tla`](../../.github/skills/tla/SKILL.md) model checking and `req-projection` (referential integrity of `order-stock-projection`) for [`alloy`](../../.github/skills/alloy/SKILL.md).

| Record | Content |
|---|---|
| Scope | Gate 3 (`verification`), 18 requirements and 3 risks in [`verification.yaml`](verification.yaml) |
| Responsibility | QA/verification lead (author), domain lead (reviewer) |
| Findings | Every capability, component and data model has testable or model-checkable criteria across all 10 categories; `risk-oversell` mitigated by `req-reserve-conc`; `evidence` remains empty until execution |
| Outcome | **Pass** — issue bounded implementation handoffs |
| Follow-up | Run TLA+ and Alloy checks before coding `inventory`; execute failing tests first for each handoff |

---

## Implementation Handoff (`inventory` Component)

Prepared per [`CONSTITUTION.md` § Implementation Handoff](../../CONSTITUTION.md#implementation-handoff) from [`verification.yaml`](verification.yaml):

- **Target capability & invariants**: `reserve-inventory@1.0` (`POST /v1/reservations`, sync, idempotent); preserve `stock_never_negative` and projection referential integrity.
- **Component boundary**: `inventory@1.0` (`layer: domain`, `consistency: strong`); owns `stock-item@1.0` (`internal`, source `erp-product-feed`) and `order-stock-projection@1.0` (`confidential`); zero required capabilities.
- **Verification obligations**: `req-reserve-func`, `req-reserve-sem`, `req-reserve-contract`, `req-stock-serial`, `req-reserve-conc` (`tla+::Inventory.tla`, bounds `3 products, 4 concurrent reservations, MaxQty=5`), `req-projection` (`alloy::Inventory.als`, scope `5 but 4 Int`), `req-reserve-resilience`, `req-reserve-security`.
- **Open risks & waivers**: `risk-oversell` (`treatment: mitigation`, `mitigated_by: [req-reserve-conc]`); zero waivers.
- **Allowed scope & expected return**: implement `inventory` domain module and `.mdl` artifacts ([`modelable`](../../.github/skills/modelable/SKILL.md)) without importing `checkout`; return requirement-linked test/model-check results and commit revisions.

---

## Gate 4 — Release & Change Loop (`--stage release`)

- **Whole-spec baseline**: [`spec.yaml`](spec.yaml) (`uv run python metamodel.py ../examples/greenfield/spec.yaml`) illustrates the linked traceability graph (`Capability → Requirement → Evidence`), while `reference-implementation/test_release.py` exercises strict `--stage release` metadata checks (`verified` statuses, `subject_revision`, `timestamp`, `verifier`, `bounds`).
- **Change & reverification trace**:
  1. When `reserve-inventory` is updated, run `uv run python metamodel.py ../examples/greenfield/verification.yaml --impact reserve-inventory` to identify affected components (`inventory`, `checkout`), data models (`stock-item`, `order-stock-projection`, `order`) and requirements.
  2. Check contract compatibility with `--compat` before implementation; if preconditions strengthen or postconditions weaken, reopen Gate 1/2 and bump major versions.
  3. Treat prior evidence for impacted requirements as historical until rerun against the new `subject_revision`, recording `supersedes` and `supersession_reason` when replacing a failed run.

| Record | Content |
|---|---|
| Scope | Gate 4 (`release`), [`verification.yaml`](verification.yaml) + [`spec.yaml`](spec.yaml) |
| Responsibility | Release owner |
| Findings | Structural composition and 10-category requirement specifications pass `--stage verification`; [`spec.yaml`](spec.yaml) provenance entries (`pytest::*`, `tla+::Inventory.tla`, `alloy::Inventory.als`, `k6::*`) are illustrative placeholders without attached execution logs or subject revisions |
| Outcome | **Rework / Hold for real execution evidence** — do not record release acceptance until real test, benchmark and model-check artifacts are produced and reviewed |
| Follow-up | Attach immutable `subject_revision`, `timestamp`, `verifier` and artifact logs from actual test/TLC/Alloy runs before promoting entities to `status: verified` |

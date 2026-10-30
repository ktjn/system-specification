# Greenfield Example: Commerce Checkout & Inventory

End-to-end trace of [`spec.yaml`](spec.yaml) through the 12 phases and 4 gates of [`GREENFIELD.md`](../../GREENFIELD.md). Gate 1 is executable using `discovery.yaml` with `--stage discovery`; later stage profiles remain planned. Whole-spec validation runs `metamodel.py ../examples/greenfield/spec.yaml` from `reference-implementation/` (prototype `VALID` checks structural/reference invariants; Gate 4 acceptance also requires reviewing 10-category coverage and evidence artifacts per [`spec.md` §§ 8, 11](../../spec.md#8-verification)).

## Gate 1 — Discovery (`--stage discovery`)

From `reference-implementation/`: `uv run python metamodel.py ../examples/greenfield/discovery.yaml --stage discovery`. The [discovery snapshot](discovery.yaml) intentionally has no components or evidence.

- **Phase 1 (Capability discovery)**: identify `place-order` and `reserve-inventory` with preconditions, postconditions and failure modes (`insufficient_inventory`, `customer_blocked`, `product_not_found`).
- **Phase 2 (Invariant discovery)**: attach domain invariants `order_paid_at_most_once` (`place-order`) and `stock_never_negative` (`reserve-inventory`).

## Gate 2 — Architecture (planned `--stage architecture`)

- **Phase 3 (Component identification)**: split along consistency boundaries — `checkout` owns order lifecycle; `inventory` owns stock reservations.
- **Phase 4 (Component specification)**: `checkout` (`provides: [place-order]`, `requires: [reserve-inventory@^1.0]`, `owns_data: [order]`); `inventory` (`provides: [reserve-inventory]`, `owns_data: [stock-item, order-stock-projection]`).
- **Phase 5 (Data contracts)**: define `stock-item` (`internal`, from `erp-product-feed`), `order` (`confidential`), and `order-stock-projection` (`confidential`, `derived_from: [order, stock-item]`).
- **Phase 6 (API contracts)**: bind `place-order` (`POST /v1/orders`, idempotent, `order` payload) and `reserve-inventory` (`POST /v1/reservations`, idempotent).
- **Phase 9 (Layering)**: `checkout` in `application` → `inventory` in `domain` (satisfies `experience → application → domain → infrastructure`).
- **Phase 10 (Context budget)**: each component has ≤1 provided capability, ≤1 required capability and ≤2 owned data models (within `5 / 8 / 4` budget).

## Gate 3 — Verification (planned `--stage verification`)

- **Phase 7 (Verification specification)**: define requirements covering all 10 verification categories (`req-order-func`, `req-order-sem`, `req-order-contract`, `req-order-serial`, `req-reserve-conc`, `req-latency`, `req-scale`, `req-resilience`, `req-security`, `req-observability`, `req-projection`).
- **Phase 8 (Formal verification assessment)**: concurrency invariant `stock_never_negative` verified with [`tla`](../../.github/skills/tla/SKILL.md) (`tla+::Inventory.tla`); structural projection invariant verified with [`alloy`](../../.github/skills/alloy/SKILL.md) (`alloy::Inventory.als`).

## Gate 4 — Release (planned `--stage release`)

- **Phase 11 (Traceability)**: every capability, data model and risk mitigation links to requirements and evidence; `--impact reserve-inventory` traces affected components, models, requirements and evidence.
- **Phase 12 (Acceptance)**: all mandatory and mitigating requirements have passing `Evidence`; risks (`risk-oversell`, `risk-erp-delay`, `risk-payment-fraud`) are mitigated, accepted or transferred.

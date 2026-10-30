# Brownfield Example: Legacy Billing Strangler Migration

Progression of a legacy billing monolith through the 5 reverse-discovery steps and 4 adoption levels of [`BROWNFIELD.md`](../../BROWNFIELD.md), ending in [`spec.yaml`](spec.yaml) and verified against [`old.yaml`](old.yaml) with `--compat`.

## Reverse Discovery (Steps 1–5)

1. **Boundaries & entrypoints**: discover HTTP endpoint `issue-invoice` and batch job `charge-invoice`, plus external payment gateway `stripe-gateway`.
2. **Data & state**: extract `invoice` (`confidential`) and `ledger-entry` (`confidential`, `derived_from: [invoice]`) from SQL tables.
3. **Components & dependencies**: cluster into `invoicing` (`application`) and `payment-worker` (`domain`). Initially `payment-worker` wrote directly to `invoice` (shared ownership violation) and called `invoicing` callbacks (layer violation).
4. **Invariants & failures**: mine guards (`amount_positive`, `invoice_unpaid`), invariant `invoice_charged_at_most_once`, and failure modes (`card_declined`, `gateway_timeout`) from existing handlers.
5. **Gaps & risks**: record shared-table ownership and missing concurrency verification as `Risk` items with remediation requirements.

## Adoption Levels (0 → 3)

Level 0 is executable from `reference-implementation/`: `uv run python metamodel.py ../examples/brownfield/inventory.yaml --stage inventory`. The [inventory snapshot](inventory.yaml) contains only observed component stubs. Later stage profiles and waivers remain planned; whole-spec validation runs `metamodel.py <spec>`.

- **Level 0 — Inventory (`--stage inventory`)**: register `billing-system`, `stripe-gateway`, and component stubs `invoicing` and `payment-worker` (`status: draft`).
- **Level 1 — Dependency & Data Mapping (planned `--stage architecture`)**: map `issue-invoice` and `charge-invoice`, data models `invoice` and `ledger-entry`, and record a waiver on `risk-shared-invoice-table` (`waives: shared-data-ownership`, `mitigated_by: [req-split-ownership]`, `expires: verification`).
- **Level 2 — Behavioral Pinning (planned `--stage verification`, [`old.yaml`](old.yaml))**: attach characterization tests (`ev-issue-char`, `ev-charge-char`) freezing `issue-invoice` and `charge-invoice` contracts before refactoring; remaining verification categories are waived until Level 3.
- **Level 3 — Full Conformance (planned `--stage release`, [`spec.yaml`](spec.yaml))**:
  - Extract `charge-invoice` behind `payment-worker` owning `ledger-entry` while `invoicing` alone owns `invoice`.
  - Verify contract preservation with `metamodel.py examples/brownfield/spec.yaml --compat examples/brownfield/old.yaml`.
  - Satisfy all 10 verification categories (`req-issue-func`, `req-issue-sem`, `req-issue-contract`, `req-invoice-serial`, `req-charge-conc` via TLA+, `req-ledger-rel` via Alloy, `req-latency`, `req-scale`, `req-resilience`, `req-security`, `req-observability`) with passing `Evidence` and close all waivers.
  - Note: prototype `VALID` checks structural/reference invariants only; release acceptance also requires reviewing 10-category coverage and evidence artifacts ([`spec.md` §§ 8, 11](../../spec.md#8-verification)).

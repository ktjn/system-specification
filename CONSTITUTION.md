# AI System Development Constitution

Shared fundamentals for all work. Track-specific sequencing: [greenfield](GREENFIELD.md) (new systems), [brownfield](BROWNFIELD.md) (existing systems). Metamodel: [`spec.md`](spec.md).

Artifacts may be produced in any order; tracks define sequencing.

## Fundamental Principle

Implementations are not the source of truth. The source of truth is:

1. Capabilities
2. Business rules
3. Invariants
4. Data contracts
5. API contracts
6. Verification specifications
7. Formal models (where applicable)

Code is one possible implementation of a verified specification.

## Why

- AI quality degrades as context grows: requirement interpretation, architecture discipline, cross-component consistency and traceability suffer.
- Small components, explicit contracts and layering bound the context each task needs.
- Tests, not code, are the executable specification:

```text
Capability → Contract → Data model → Tests → Code
```

---

# Artifact Rules

## Capabilities

```yaml
capabilities:
  - id: reserve-inventory
    version: "1.0"
    preconditions: [product_exists, quantity_positive]
    postconditions: [reservation_created, stock_decremented]
    invariants: [stock_never_negative]
    failure_modes: [insufficient_inventory, product_not_found]
```

- `Purpose`, `Consumers`, `Producers` and `Business value` are discovery context, not fields.
- Acceptance criteria → `Requirement.criteria`; verification results → `Evidence`.
- As long as the contract holds, the implementation may change freely.

## Invariants

- A condition that must always hold, e.g. inventory never negative; an order paid at most once; customer email unique.
- All architectural decisions must preserve invariants.

## Components

- Derived from invariants and consistency requirements, not technology categories.
  - Bad: `Database`, `REST`, `Kafka` components.
  - Good: `Customer Management`, `Inventory Management`, `Payments`.
- Strong consistency inside a component; eventual consistency between components.

```yaml
components:
  - id: customer-management
    version: "1.0"
    layer: domain
    consistency: strong
    provides: [manage-customer]
    requires: [customer-repository]
    owns_data: [customer]
```

- Contracts and invariants belong to `capabilities`; requirements target capabilities, components or data models.
- No implementation details in component specifications.

## Data Contracts

- Every externally visible structure is explicitly defined.
- No implicit schemas; never infer or invent fields.

```yaml
Customer:
  id: UUID
  email: String
  status: [ACTIVE, BLOCKED]
```

## API Contracts

Every API defines: endpoint, version, request, response, failure conditions, status codes, idempotency, security. All APIs comply with organizational API guidelines.

## Verification

No implementation is accepted until all categories are addressed:

| Category | Covers | `Requirement.kind` | `Evidence.method` |
|---|---|---|---|
| Functional | Expected behaviors | `functional` | `test` |
| Semantic | Business meaning (e.g. `BLOCKED` denies purchase) | `functional` | `test` or `proof` |
| Contract | API compatibility, status codes, versioning | `functional` | `test` or `inspection` |
| Serialization | JSON/XML/protobuf correctness, payload limits | `functional` | `test` |
| Concurrency | Races, lost updates, duplicate requests | `functional` | `test` or `proof` |
| Performance | Latency, throughput, resource limits | `non-functional` | `test` or `analysis` |
| Scalability | Expected load and data volumes | `non-functional` | `test` or `analysis` |
| Resilience | Timeouts, retries, partial failures | `non-functional` | `test` or `analysis` |
| Security | Authentication, authorization, input validation | `non-functional` | `test` or `inspection` |
| Observability | Metrics, tracing, logging, correlation IDs | `non-functional` | `test` or `inspection` |

## Formal Verification

- Assess per component. Indicators: concurrency, distributed state, financial transactions, safety-critical logic, complex state machines, protocols.
- If applicable, produce TLA+/Alloy models or state machines.

## Layering

```text
Experience → Application → Domain → Infrastructure
```

- Higher layers may depend on lower layers, never the reverse.
- Domain logic must not depend on infrastructure details.

## Context Budget

- A component's complete specification fits on 1–2 pages; otherwise split it.
- Each AI task receives only the minimum necessary context: these fundamentals, one track document and the target component's spec slice.

## Traceability

```text
Capability → Requirement → Invariant → Component → Contract → Test → Implementation
```

- Every test traces to a requirement; every implementation element traces to a capability.

## Acceptance

A system is complete only when capabilities, invariants, components, contracts, data models and APIs are specified; verification is complete; formal models are reviewed; performance and concurrency goals are met; traceability is established; and architecture constraints are preserved.

Code completion alone is not progress. Verification completion is progress.

---

# Metamodel Mapping

| Artifact | Metamodel |
|---|---|
| Capabilities | `capabilities` |
| Invariants | `capabilities.invariants` |
| Components | `components` (`provides`, `requires`, `owns_data`) |
| Data contracts | `data_models` |
| API contracts | Capability contracts, requirements and data models; no API-specific entity |
| Verification | `requirements`, `evidence` |
| Formal verification | `evidence.method: proof`; formal models remain external |
| Layering | `system.layers`, `components.layer` |
| Context budget | No metamodel field |
| Traceability | Capability, component, requirement, data model and evidence references |
| Acceptance | Whole-spec validation; no separate entity |

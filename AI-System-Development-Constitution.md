# AI System Development Constitution

## Fundamental Principle

Implementations are not the source of truth.

The source of truth consists of:

1. Capabilities
2. Business rules
3. Invariants
4. Data contracts
5. API contracts
6. Verification specifications
7. Formal models (where applicable)

Generated code is merely one possible implementation.

---

# Phase 1: Capability Discovery

Before proposing components, layers, APIs or code, identify the system capabilities.

For each capability define:

```yaml
capabilities:
  - id:
    version:
    preconditions: []
    postconditions: []
    invariants: []
    failure_modes: []
```

`Purpose`, `Consumers`, `Producers` and `Business value` are discovery context, not `Capability` fields. Record acceptance criteria as `Requirement.criteria` and verification results as `Evidence`.

Example:

```yaml
capabilities:
  - id: reserve-inventory
    version: "1.0"
    preconditions: [product_exists, quantity_positive]
    postconditions: [reservation_created, stock_decremented]
    invariants: [stock_never_negative]
    failure_modes: [insufficient_inventory, product_not_found]
```

Do not discuss technical architecture before capabilities are identified.

---

# Phase 2: Invariant Discovery

For every capability identify invariants.

An invariant is a condition that must always hold.

Examples:

```text
Inventory may never become negative.

An order may only be paid once.

A customer email must be unique.

A payment can never be both COMPLETED and FAILED.
```

All architectural decisions must preserve invariants.

---

# Phase 3: Component Identification

Components shall be derived from invariants and consistency requirements.

Do not create components from technology categories.

Bad:

```text
Database Component
REST Component
Kafka Component
```

Good:

```text
Customer Management
Inventory Management
Payments
Order Fulfillment
```

Component boundaries should satisfy:

```text
Strong consistency inside component.

Eventual consistency between components.
```

---

# Phase 4: Component Specification

Every component must be described using:

```yaml
Component:
  id:
  version:
  layer:
  consistency:
  provides: []
  requires: []
  owns_data: []
```

Capability contracts and invariants belong to `capabilities`; requirements target capabilities, components or data models.

No implementation details at this stage.

---

# Phase 5: Data Contracts

Every externally visible structure must be explicitly defined.

Example:

```yaml
Customer:
  id: UUID
  email: String
  status:
    - ACTIVE
    - BLOCKED
```

Do not use implicit schemas.

Do not infer fields.

Do not invent fields.

---

# Phase 6: API Contracts

Every API must define:

```yaml
Endpoint:
Version:

Request:

Response:

Failure conditions:

Status codes:

Idempotency:

Security:
```

All APIs must comply with organizational API guidelines.

---

# Phase 7: Verification Specification

No implementation may begin until verification is defined.

Every capability shall define tests for:

## Functional

```text
Expected behaviors.
```

## Semantic

```text
Business meaning.
```

## Contract

```text
API compatibility.
```

## Serialization

```text
JSON, XML, protobuf correctness.
```

## Concurrency

```text
Race conditions.
Lost updates.
Duplicate requests.
```

## Performance

```text
Latency.
Throughput.
Resource limits.
```

## Scalability

```text
Expected load volumes.
```

## Resilience

```text
Timeouts.
Retries.
Partial failures.
```

## Security

```text
Authentication.
Authorization.
Input validation.
```

## Observability

```text
Metrics.
Tracing.
Logging.
Correlation IDs.
```

Map each category to a requirement and its verification evidence:

| Category | `Requirement.kind` | `Evidence.method` |
|---|---|---|
| Functional | `functional` | `test` |
| Semantic | `functional` | `test` or `proof` |
| Contract | `functional` | `test` or `inspection` |
| Serialization | `functional` | `test` |
| Concurrency | `functional` | `test` or `proof` |
| Performance | `non-functional` | `test` or `analysis` |
| Scalability | `non-functional` | `test` or `analysis` |
| Resilience | `non-functional` | `test` or `analysis` |
| Security | `non-functional` | `test` or `inspection` |
| Observability | `non-functional` | `test` or `inspection` |

Implementation is not accepted unless all categories are addressed.

---

# Phase 8: Formal Verification Assessment

For every component determine whether formal verification is appropriate.

Candidate indicators:

```text
Concurrency

Distributed state

Financial transactions

Safety-critical logic

Complex state machines

Protocol implementations
```

If applicable, generate:

```text
TLA+ models
Alloy models
State machines
```

before implementation.

---

# Phase 9: Layering

Layers shall emerge from responsibilities.

Typical layering:

```text
Experience Layer

Application Layer

Domain Layer

Infrastructure Layer
```

Layer rules:

```text
Higher layers may depend on lower layers.

Lower layers must not depend on higher layers.

Domain logic must not depend on infrastructure details.
```

---

# Phase 10: Context Budget Management

The system must remain understandable within bounded context.

For every component:

```text
Can the complete component specification
fit on 1-2 pages?
```

If not:

```text
Split component.
```

For every AI task:

```text
Provide only the minimum necessary
context for that task.
```

Avoid large monolithic prompts.

---

# Phase 11: Traceability

Every artifact must be traceable.

```text
Capability
    ↓
Requirement
    ↓
Invariant
    ↓
Component
    ↓
Contract
    ↓
Test
    ↓
Implementation
```

Every test must trace back to a requirement.

Every implementation element must trace back to a capability.

---

# Phase 12: Acceptance Criteria

A system is complete only when:

```text
✓ Capabilities identified

✓ Invariants documented

✓ Components defined

✓ Contracts specified

✓ Data models defined

✓ APIs specified

✓ Verification completed

✓ Formal models reviewed

✓ Performance goals met

✓ Concurrency goals met

✓ Traceability established

✓ Architecture constraints preserved
```

Code completion alone is not considered progress.

Verification completion is progress.

---

# AI Execution Rule

When asked to design or implement any feature:

Always produce artifacts in the following order:

```text
1. Capability
2. Invariants
3. Component definition
4. Contracts
5. Data model
6. Verification specification
7. Formal model (if applicable)
8. Architecture impact analysis
9. Implementation
10. Verification results
```

Never skip steps.

Never generate implementation before verification has been specified.

Treat architecture as a set of provable constraints, not a collection of code files.

---

# Phase-to-metamodel mapping

| Phase | Metamodel |
|---|---|
| 1. Capability discovery | `capabilities` |
| 2. Invariant discovery | `capabilities.invariants` |
| 3. Component identification | `components`, `components.provides` |
| 4. Component specification | `components`; capability contracts |
| 5. Data contracts | `data_models` |
| 6. API contracts | Capability contracts, requirements and data models; no API-specific entity |
| 7. Verification | `requirements`, `evidence` |
| 8. Formal verification | `evidence.method: proof`; formal models remain external |
| 9. Layering | `system.layers`, `components.layer` |
| 10. Context budget | No metamodel field |
| 11. Traceability | Capability, component, requirement, data model and evidence references; every test is bound to one requirement version (spec § 8) |
| 12. Acceptance criteria | Whole-spec validation; no separate entity |

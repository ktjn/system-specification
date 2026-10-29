# Greenfield: Creating New Systems

Contract-first sequencing for new systems. Artifact rules: [constitution](CONSTITUTION.md). Load this document together with the constitution only.

## Phases

| # | Phase | Output | Gate |
|---|---|---|---|
| 1 | Capability discovery | Capabilities with contracts and failure modes | 1 |
| 2 | Invariant discovery | Invariants per capability | 1 |
| 3 | Component identification | Components derived from invariants and consistency boundaries | 2 |
| 4 | Component specification | Component definitions; no implementation details | 2 |
| 5 | Data contracts | Data models with owners | 2 |
| 6 | API contracts | API contracts per capability | 2 |
| 7 | Verification specification | Requirements covering all 10 categories | 3 |
| 8 | Formal verification assessment | Formal models where indicated | 3 |
| 9 | Layering | Layers assigned; rules hold | 2 |
| 10 | Context budget | Oversized components split | 2 |
| 11 | Traceability | All artifacts linked | 4 |
| 12 | Acceptance | Passing, current evidence for all mandatory requirements | 4 |

Rules:

- Do not discuss technical architecture before capabilities are identified.
- No implementation may begin until verification is specified (Phase 7).

## Gates (planned `--stage`, see [PLAN.md](PLAN.md))

1. **Discovery** (`--stage discovery`): Phases 1–2.
2. **Architecture** (`--stage architecture`): Phases 3–6, 9–10.
3. **Verification** (`--stage verification`): Phases 7–8.
4. **Release** (`--stage release`): Phases 11–12; all risks mitigated or accepted.

Until `--stage` exists, validate with `metamodel.py` at every gate.

## AI Execution Rule

When asked to design or implement any feature, produce artifacts in this order:

```text
1. Capability
2. Invariants
3. Component definition
4. Contracts
5. Data model
6. Verification specification
7. Formal model (if applicable)
8. Architecture impact analysis (--impact)
9. Implementation
10. Verification results
```

- Never skip steps.
- Never generate implementation before verification has been specified.
- Treat architecture as provable constraints, not a collection of code files.

## Prompts

Generate structured output against `metamodel.py --schema`. Per phase:

- **1–2**: "List capabilities of `<domain>` with pre/postconditions, invariants and failure modes; no architecture."
- **3–4**: "Derive components from these invariants and consistency boundaries; assign `provides`/`requires`/`owns_data`."
- **5–6**: "Define data models and API contracts for `<capability>`; do not invent fields."
- **7–8**: "Write requirements for all 10 verification categories of `<capability>`; flag formal verification candidates."
- **Implementation**: "Here are the component's contracts and tests. Implement any solution that satisfies all of them."

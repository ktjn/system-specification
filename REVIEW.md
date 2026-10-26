# Repository Review: AI-Native System Specification

**Reviewer**: cjot  
**Date**: 2026-10-26  
**Repository**: ktjn/system-specification

---

## Overview

This repository presents a thoughtfully designed methodology for AI-native system development, emphasizing specifications and contracts as first-class artifacts rather than code-derived documentation. The approach is particularly well-suited for AI-augmented development workflows.

---

## Strengths

### 1. Clear Philosophical Foundation

The **AI-System-Development-Constitution** establishes a compelling principle: implementations are not the source of truth. Instead, truth resides in:

- Capabilities
- Business rules
- Invariants
- Data contracts
- API contracts
- Verification specifications
- Formal models

This reframing is sound for AI-assisted development, as it forces structured thinking before code generation and creates a defensible basis for verification.

### 2. Structured Methodology with Clear Progression

The 12-phase progression is logically organized:

```
Capabilities → Invariants → Components → Contracts → Data Models
      ↓           ↓             ↓            ↓            ↓
   Tests → Formal Verification → Layering → Context Budget → Traceability
```

Each phase has defined inputs and outputs, making it actionable for both human architects and AI assistants. The phase-gate approach prevents premature implementation before specification is complete.

### 3. Context Budget Awareness

The explicit attention to **context budgeting** (Phase 10) is pragmatic and often overlooked:

> Can the complete component specification fit on 1-2 pages?

This constraint directly addresses a real AI limitation: quality degrades with context size. By enforcing bounded scope per component, the methodology makes systems more understandable and verifiable in isolation.

### 4. Comprehensive Verification Framework

The verification specification (Phase 7) covers 9 dimensions:

- Functional, Semantic, Contract, Serialization
- Concurrency, Performance, Scalability
- Resilience, Security, Observability

This comprehensiveness is rare in AI-generated code and reflects mature systems thinking. The requirement that "implementation is not accepted unless all categories are addressed" is disciplined.

### 5. Contracts as Primary Artifacts

The distinction between contracts and implementation enables:

- Implementation flexibility (can be replaced without affecting dependents)
- Clearer AI task boundaries (generate code that satisfies a contract)
- Reduced coupling (contracts, not code details, are dependencies)

---

## Areas for Enhancement

### 1. Phase Sequencing in Practice

**Observation**: The phases are presented as sequential, but real system development is iterative. Later phases often inform earlier decisions.

**Suggestion**: Add guidance on:
- Which phases can run in parallel
- When backward iteration to earlier phases is necessary
- How to handle conflicts between phases (e.g., a verification requirement that changes invariants)

### 2. AI-Specific Prompting Strategies

**Observation**: The constitution mentions AI execution but lacks concrete guidance on request structuring.

**Suggestion**: Add a section on:
- How to frame capability discovery prompts to AI
- Effective ways to present component specs and ask for implementation
- Patterns for iterative refinement when verification fails

### 3. Traceability Implementation

**Observation**: Phase 11 describes desired traceability but lacks practical tooling guidance.

**Suggestion**: Specify:
- Naming conventions for requirements, invariants, tests, and code
- Metadata format (e.g., YAML front-matter in test files linking to capabilities)
- Tool recommendations or examples (GitHub Projects, issue templates, etc.)

Example:
```yaml
# test_customer_creation.py
# @capability: Reserve Inventory
# @invariant: Inventory never becomes negative
# @requirement: REQ-001
```

### 4. Scaling Beyond Single Components

**Observation**: The methodology excels at component-level clarity but is less explicit about system-wide constraints.

**Suggestion**: Add guidance on:
- Component dependency graphs and circularity prevention
- Cross-component invariant enforcement
- Eventual consistency boundaries between components
- How to manage API evolution across interdependent components

### 5. Formal Verification Accessibility

**Observation**: Phase 8 mentions TLA+, Alloy, and state machines but doesn't indicate when to apply them or provide examples.

**Suggestion**: Add a decision tree:
- When is formal verification cost-justified?
- Which tool (TLA+, Alloy, etc.) for which problem type?
- Example formal models for common patterns (distributed consensus, transactional semantics)

### 6. Documentation of the Inverse Process

**Observation**: The constitution describes how to *build* systems, but not how to *reverse-engineer* existing systems into this framework.

**Suggestion**: Add a "Retrofit" section:
- How to extract capabilities from legacy code
- How to infer and formalize invariants from implementation
- How to define contracts for existing components

---

## Detailed Observations

### Excellent Decisions

| Aspect | Decision | Why It Works |
|--------|----------|------------|
| Component derivation | From invariants, not technology | Forces domain-driven thinking; prevents technology-first mistakes |
| Source of truth | Specifications, not code | Creates stable reference; enables code regeneration |
| Layering rules | Lower layers can't depend on higher | Enforces architectural discipline |
| API specification detail | Include idempotency, security, failure modes | Catches integration issues before implementation |

### Minor Issues

1. **AGENTS.md** contains a typo on line 3: "Don't be version" (likely should be "Don't be verbose" or similar intent is unclear)

2. **AI-native-design.md** (Swedish) and **AI-System-Development-Constitution.md** (English) have some redundancy—consider clarifying whether one is a translation or if they represent different perspectives that should be explicitly acknowledged.

3. **spec.md** is quite brief and feels like an outline. Consider expanding it or clearly marking it as a table of contents.

---

## Missing Pieces

### 1. Examples and Case Studies

The constitution is strong on principles but lacks worked examples. Recommend adding:

- A minimal but complete example component (e.g., CustomerManagement) traced through all 12 phases
- Before/after comparison of AI-generated code with/without the constitution
- A failing case study: what went wrong when this methodology wasn't followed

### 2. Tool Integration

No mention of how this integrates with:
- GitHub Projects or issues for phase tracking
- CI/CD pipelines for verification gates
- Documentation generation from specifications

### 3. Team Coordination

How should teams:
- Assign ownership of each phase?
- Review specifications before implementation?
- Escalate conflicts between phases?

---

## Questions for Author(s)

1. **Cyclical Dependencies**: How should components that logically depend on each other be handled? The "eventual consistency between components" rule is clear, but how is it enforced?

2. **Specification Debt**: What happens if invariants are discovered post-implementation? How do you safely refactor?

3. **AI Training**: Have you tested this constitution against actual code-generating AI? Which phases/documents does it struggle with?

4. **Formalization Effort**: For a 10-component system, roughly how much time is spent in spec phases vs. implementation phases?

---

## Recommendations

### High Priority

1. **Add worked examples** through all 12 phases—this is the fastest path to adoption
2. **Clarify phase interdependencies**—expand on when phases can parallel-process
3. **Fix AGENTS.md typo** and clarify intent

### Medium Priority

4. Add decision trees for formal verification applicability
5. Document reverse-engineering (retrofit) process for existing systems
6. Reconcile or explicitly differentiate English and Swedish documents

### Low Priority (Nice-to-Have)

7. Add GitHub Projects/Actions templates for phase gating
8. Create prompting cookbook for AI assistants following this methodology
9. Develop metrics to assess "context budget" health over time

---

## Conclusion

This repository articulates a mature, well-reasoned approach to AI-assisted system development. The core insight—that specifications are more important than implementations in an AI-augmented world—is sound and actionable. The 12-phase methodology provides structure without being rigid.

**Main Gap**: The constitution is aspirational but lacks sufficient concrete guidance (examples, tools, team processes) for teams to adopt it confidently.

**Recommendation**: Publish a reference implementation demonstrating the full methodology applied to a realistic (but bounded) system. This single addition would dramatically increase the value and clarity of the specification.

**Overall Assessment**: ⭐⭐⭐⭐ (4/5)

*Strong foundational work with clear potential. Ready for external review and community feedback.*

---

**cjot** | 2026-10-26

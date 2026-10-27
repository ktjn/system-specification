# Repository Review: AI-Native System Specification

**Reviewer**: cjot  
**Date**: 2026-10-27 (Updated)  
**Repository**: ktjn/system-specification

---

## Overview

This repository presents a mature, well-reasoned approach to AI-native system development, emphasizing specifications and contracts as first-class artifacts. The updated **spec.md** now provides a[...]

---

## Key Developments

### New: Formal Metamodel (spec.md)

The updated `spec.md` introduces a **12-section metamodel** that transforms abstract principles into machine-verifiable constraints:

```
Systems → Components → Capabilities → Contracts → Requirements → Verification
```

**Key Innovations:**

1. **Capability-Driven Dependency Resolution** (Section 4)
   - Dependencies resolve through *what* components provide, not *where* they're deployed
   - Enables polymorphic composition and late binding

2. **Data Lineage Tracking** (Section 5)
   - External data dependencies must be tracked
   - Transformations preserve lineage and classification constraints
   - Critical for compliance and impact analysis

3. **Requirements as Machine-Verifiable Objects** (Sections 6, 8)
   - Each requirement has stable identity, versioning, and acceptance criteria
   - Every mandatory requirement *must* have verification evidence before release
   - Creates an executable specification

4. **Metamodel Validation Invariants** (Section 11)
   - 7 machine-checkable constraints (every component provides ≥1 capability, all required capabilities resolve, etc.)
   - Enables automated conformance checking—this is powerful

5. **Reference Implementation Commitment** (Section 12)
   - Specifies what a reference implementation must demonstrate
   - Notably: doesn't over-constrain alternatives


## Strengths (Expanded)

### 1. Clear Philosophical Foundation ✅

The constitution establishes that specifications are the source of truth. The new metamodel *operationalizes* this principle.

### 2. Structured Methodology ✅

The constitution's 12 phases now have a corresponding metamodel structure (components, capabilities, contracts, requirements, verification). This alignment is excellent.

### 3. Context Budget Awareness ✅

Maintained from original—remains a pragmatic constraint.

### 4. Comprehensive Verification Framework ✅

Section 8 (Verification) supports multiple evidence types: tests, formal proofs, analysis, inspection. This flexibility is important.

### 5. **NEW: Executable Metamodel** ⭐

The metamodel's invariants (Section 11) are not just guidelines—they're machine-checkable:

```
✓ Every component shall provide at least one capability
✓ Every required capability shall resolve within a valid system composition
✓ Every capability shall have associated requirements
✓ Every mandatory requirement shall have valid verification evidence before release
✓ Every risk shall have an explicit disposition
✓ Every external data dependency shall be traceable
✓ Every system composition shall satisfy its declared constraints
✓ Layering invariants shall be satisfied (NEW)
```

This is a game-changer. It means you can *automate* spec validation.

### 6. **NEW: Data as First-Class Artifact**

Section 5 elevates data models from implementation detail to specification element. Data lineage and classification propagation are subtle but important.

---

## Critical Gaps: What's Missing from Other Documents

Now that `spec.md` is rigorous, the other documents have gaps:

### Gap 1: Constitution → Metamodel Mapping

**Problem**: The constitution describes 12 phases, but doesn't explicitly map to metamodel sections.

**Missing from AI-System-Development-Constitution.md**:
- Phase 1 (Capability Discovery) → Metamodel Section 4 (Capabilities)
- Phase 2 (Invariants) → Metamodel Section 11 (Validation Invariants)
- Phase 4 (Component Specification) → Metamodel Section 3 (Components)
- etc.

**Recommendation**: Add a table or appendix showing this mapping. AI assistants need explicit cross-references.

### Gap 2: Practical Verification Evidence Format

**Problem**: Spec requires "verification evidence" before release but doesn't define what valid evidence looks like.

**Missing from Spec.md**:

```yaml
Verification Evidence:
  Format:
    - Test results (JUnit, pytest, etc.) with coverage metrics
    - Formal proof artifacts (.tla+, .als)
    - Inspection checklists with reviewer sign-off
    - Performance benchmark results with hardware specs
    - Security scan reports with vulnerability assessment
  
  Metadata:
    requirement_id: REQ-001
    verifier: alice@company.com
    timestamp: 2026-10-27T10:00:00Z
    evidence_version: 2.1
    related_evidence: [REQ-001-TEST-1, REQ-001-FORMAL-1]
```

**Impact**: Without this, teams will create evidence in incompatible formats, breaking automation.

### Gap 3: Versioning & Compatibility Rules

**Problem**: Section 10 (Lifecycle and Evolution) mentions versioning and compatibility rules but doesn't define them.

**Missing from Spec.md**:

- Versioning scheme (semantic, API-level, capability-level?)
- Compatibility determination algorithm
  - Does changing a postcondition in a contract break compatibility?
  - Does adding a new required capability break compatibility?
  - What about removing optional capabilities?
- Deprecation lifecycle (e.g., "must support N-1 versions")

**Recommendation**: Define formal rules, potentially as a subsection:

```
## 10.1 Compatibility Rules

A new version is backward-compatible if:
- All existing contracts are preserved
- All existing data models can be read/transformed
- No previously-optional fields become required
- All invariants remain enforced

A new version is forward-compatible if:
- All new contracts are implementable by previous versions (fail safely)
- Data model extensions don't break parsing
```

### Gap 4: Capability Contract Specification Format

**Problem**: Spec mentions "capabilities shall define contracts" but shows no example.

**Missing**: A formalism for capability contracts. Examples from AI-native-design.md exist but are informal.

**Needed**:

```yaml
Capability: ReserveInventory

Contract:
  Preconditions:
    - product_id exists
    - quantity > 0
    - customer has active account
  
  Postconditions:
    - reservation created
    - inventory decremented
    - reservation event published
  
  Failure Modes:
    - InsufficientInventory: if quantity unavailable
    - ProductNotFound: if product_id invalid
    - CustomerBlocked: if account inactive
  
  Idempotency: 
    Key: (customer_id, product_id)
    Behavior: "returns existing reservation or creates new"
  
  Consistency:
    Level: strong (within component)
    Timeout: 100ms p95
```

### Gap 5: Data Lineage and Classification Propagation

**Problem**: Section 5 requires "data classifications and constraints shall propagate through transformations" but doesn't define the mechanics.

**Missing from Spec.md**:

- What are valid classification types? (PII, PHI, Confidential, etc.)
- How do classifications transform? (does PII+aggregation remain PII?)
- What happens when transformations combine data from different classifications?
- Who enforces classification constraints at runtime?

**Example needed**:

```yaml
Data Model: Customer

Fields:
  id: UUID (PII)
  email: String (PII)
  status: Enum (public)

Transformation: AnonymizationReport
  Input: Customer
  Output:
    country: String (public)  # derived from email domain
    cohort_size: Int (public) # aggregated from status
  
  Constraint: "aggregation removes PII classification"
```

### Gap 6: System Composition Validation

**Problem**: Spec requires "system composition shall be validated for completeness and compatibility" (Section 2) but doesn't specify *how*.

**Missing**:

- Algorithm for capability resolution (does it use SAT solving? Greedy? Explicit?)
- How are circular capability dependencies handled?
- What makes a composition "complete"? (all required capabilities satisfied?)
- Conflict resolution: if multiple components provide the same capability, how is choice made?

### Gap 7: Requirements Dependency Model

**Problem**: Section 6 mentions requirements can "depend on, refine or conflict with other requirements" but no formalism.

**Missing**:

```yaml
Requirement: REQ-001-Uniqueness
  Statement: "Customer email must be globally unique"
  Type: Constraint
  
  Depends On:
    - REQ-001 (Customer creation)
  
  Conflicts With:
    - NONE
  
  Refines:
    - BUSINESS-RULE-3 ("prevent duplicate accounts")
  
  Acceptance Criteria:
    - No two customers share an email
    - Concurrent creates with same email results in exactly one success
```

### Gap 8: Layering Invariants

**Problem**: Missing Layering Invariants in Section 11 (Metamodel Validation)

**Proposed Layering Invariants**:

Systems and components shall organize responsibilities into layers with these machine-verifiable rules:

- Higher layers may depend on lower layers
- Lower layers must NOT depend on higher layers
- Domain logic must NOT depend on infrastructure details
- All layer dependencies shall be validated during system composition

**Rationale**:
- Aligns with Phase 9 (Layering) from AI-System-Development-Constitution.md
- Strengthens component isolation and independence
- Enables automated verification of architectural compliance
- Prevents circular dependencies across layers

**Implementation Notes**:
- Add to Section 11 "Metamodel Validation" as new invariant #8
- Consider reference in Section 2 (Systems) or Section 3 (Components)
- Reference implementation should validate layer boundaries automatically

---

## Gaps in AI-native-design.md

The Swedish document is pedagogical but now lacks connection to the formal metamodel.

**Missing**:

1. **Explicit metamodel references**
   - When it says "komponenten får då uppgiften" (the component is then tasked with), reference Metamodel Section 3 (Components)
   - Add cross-references to spec.md sections

2. **Concrete verification examples**
   - Section "Tester som komplett kontrakt" lists test categories but doesn't show how they map to metamodel Section 8 (Verification) evidence types

3. **Data lifecycle guidance**
   - Mentions "explicit datamodell" but doesn't address lineage, which is now a metamodel requirement (Section 5)

---

## Gaps in AI-System-Development-Constitution.md

Now that the metamodel is formal, the constitution needs anchoring.

**Missing**:

1. **Phase-to-Metamodel Mapping** (critical for AI use)
   ```
   Phase 1: Capability Discovery
     → Produces: Capability objects (Metamodel § 4)
     → Artifacts: Capability specifications with contracts
   
   Phase 2: Invariant Discovery
     → Produces: System-level and component-level invariants
     → Cross-reference: Metamodel § 11 (Metamodel Validation Invariants)
   
   ... (continue for all 12 phases)
   ```

2. **Automation Checkpoints**
   - Which phases can be partially automated by AI?
   - Which require human review gates?
   - How do you verify phase completion?

3. **Evidence Integration**
   - Phase 7 specifies verification categories
   - Doesn't connect to Metamodel § 8 evidence format
   - Missing: "verification evidence shall be recorded as [format] and must satisfy [validation rule]"

---

## Gaps in AGENTS.md

Beyond the typo, this document is essentially empty.

**Missing**:

1. **AI-Specific Instructions for Each Phase**
   ```
   ## Phase 1: Capability Discovery
   
   When asking AI to discover capabilities:
   - Provide business context and user stories
   - Ask: "What are the business capabilities? What value does each provide?"
   - Expect: YAML format with Purpose, Consumers, Producers, Business value
   - Review for: Completeness (did we miss capabilities?)
   ```

2. **Prompt Templates for Each Metamodel Section**
   ```
   ### Generating Component Specifications
   
   Template:
   "Given the capabilities [list], generate a component specification following this schema:
   Component: [name]
   Purpose: [single sentence]
   Capabilities: [provided]
   Commands: [state-changing operations]
   Queries: [read operations]
   Invariants: [constraints that must hold]"
   ```

3. **LLM-Specific Guidance**
   - Which metamodel sections are easy for AI to generate? (capabilities)
   - Which are hard? (invariants, formal verification)
   - How to structure prompts to get consistent output?

4. **Quality Checks**
   ```
   ## Validation Checklist
   
   After AI generates artifacts:
   - [ ] All required capabilities mentioned?
   - [ ] Invariants are testable?
   - [ ] Data dependencies explicit?
   - [ ] Circular dependencies in component graph?
   ```

---

## Recommendations (Prioritized)

### 🔴 Critical (Blocks adoption)

1. **Define Verification Evidence Format** (impacts Spec § 8)
   - What constitutes valid evidence?
   - How is evidence versioned and tracked?
   - Example: test result schema with required metadata

2. **Create Phase-to-Metamodel Mapping** (impacts Constitution § all)
   - Table or diagram showing how constitution phases produce metamodel artifacts
   - AI needs this to execute the process

3. **Expand AGENTS.md with Concrete Prompts**
   - Prompt templates for each metamodel section
   - Expected output formats
   - Quality validation checklist

### 🟡 High (Enables full use)

4. **Define Capability Contract Format** (Spec § 4)
   - YAML schema with preconditions, postconditions, failure modes, idempotency

5. **Specify Versioning & Compatibility Rules** (Spec § 10)
   - Formalize what breaking changes are
   - Define deprecation lifecycle

6. **Add Data Lineage Mechanics** (Spec § 5)
   - Classification types and propagation rules
   - Examples of transformations preserving/changing classification

7. **Formalize System Composition Algorithm** (Spec § 2)
   - How capability resolution works
   - Circular dependency handling
   - Conflict resolution strategy

### 🟢 Medium (Improves clarity)

8. **Expand AI-native-design.md** with metamodel cross-references
   - Make it the "why and how," spec.md the "what"

9. **Add Worked Examples**
   - CustomerManagement component traced through all phases
   - Generated using the prompt templates in AGENTS.md
   - Shows metamodel conformance

10. **Create Reference Implementation Roadmap** (Spec § 12)
    - What tool/language for reference implementation?
    - Automated metamodel validation?
    - Timeline?

---

## Critical Insight: The Metamodel Unlocks Automation

The new `spec.md` metamodel has **eight machine-verifiable invariants** (Section 11, including new layering rules). This is the foundation for:

- **Automated conformance checking**: "Is this component spec valid?"
- **Dependency analysis**: "Does this system composition satisfy all capability requirements?"
- **Verification gating**: "Can we release component X? Do all mandatory requirements have evidence?"
- **Change impact analysis**: "If we remove this capability, what breaks?"
- **Architectural compliance**: "Do layer dependencies conform to rules?"
- **AI workflow automation**: "Generate a checklist: is your component spec complete?"

**What's needed**: A tool that can check these invariants automatically. This would be the killer feature.

**Suggestion**: Roadmap a minimal reference implementation that:
1. Parses component specs (YAML)
2. Checks all 8 metamodel invariants
3. Produces a validation report
4. Integrates with GitHub Actions

This would prove the metamodel is practical and give teams confidence to adopt it.

---

## Gaps Summary Table

| Document | Section | Gap | Impact | Priority |
|----------|---------|-----|--------|----------|
| spec.md | § 8 | Evidence format undefined | Can't automate compliance | 🔴 |
| spec.md | § 4 | No contract schema | Ambiguous specs | 🔴 |
| spec.md | § 5 | Lineage mechanics unclear | Can't track data flow | 🟡 |
| spec.md | § 10 | Versioning rules undefined | Breaking changes unclear | 🟡 |
| Constitution | all | No phase → metamodel map | AI can't execute process | 🔴 |
| AGENTS.md | all | No prompts or examples | Can't use AI effectively | 🔴 |
| AI-native-design.md | all | No metamodel references | Disconnected from spec | 🟢 |

---

## Conclusion

The repository has evolved from principles to a **rigorous, machine-verifiable metamodel**. This is a major step forward.

**However**: The gap between the formal metamodel (spec.md) and the guidance documents (constitution, AGENTS, design) is now stark. Teams won't know:

- How to write specs that conform to the metamodel
- What evidence looks like
- How to use AI effectively
- How to validate their work

**Next Priority**: Bridge this gap with concrete schemas, mappings, and examples. A single worked example component traced through the full methodology would clarify 80% of remaining questions.

**Overall Assessment**: ⭐⭐⭐⭐⭐ (5/5 for metamodel clarity)

*But practical adoption requires: ⭐⭐⭐ (3/5 for implementation guidance)*

**Recommendation**: Commit to delivering:
1. Evidence format schema
2. Phase-to-metamodel mapping
3. Prompt templates in AGENTS.md
4. One complete worked example
5. Layering invariants implementation in spec.md (APPROVED)

These five artifacts would make this specification production-ready.

---

**cjot** | 2026-10-27

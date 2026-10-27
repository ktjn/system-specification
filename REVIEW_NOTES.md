# Review Notes - Layering Invariants

## Reviewer: cjot
## Date: 2026-10-27

### Recommendation: ADD LAYERING INVARIANTS TO SPEC.MD

**Status:** ✅ AGREE

### Rationale

The layering invariants defined in Phase 9 of AI-System-Development-Constitution.md are fundamental to the metamodel and should be formally documented in spec.md Section 11 (Metamodel Validation).

### Proposed Invariants to Add

Layers shall be organized by responsibility and follow these rules:

- Higher layers may depend on lower layers
- Lower layers must not depend on higher layers
- Domain logic must not depend on infrastructure details
- All layer dependencies shall be validated during system composition

### Impact

Adding these invariants strengthens:
- Component isolation and independence
- System maintainability and testability
- Verification of architectural compliance
- Prevention of circular dependencies across layers

### Implementation Notes

- Should be added to Section 11 "Metamodel Validation" alongside existing invariants
- Consider adding reference to layering in Section 2 (Systems) or Section 3 (Components)
- Reference implementation should validate layer boundaries automatically

---

**Decision:** Proceed with adding layering invariants to spec.md

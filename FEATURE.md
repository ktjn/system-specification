# Feature: Changing an Already-Specified System

Contract-first sequencing for adding or changing behavior in a system that already has a validated spec (built via [greenfield](GREENFIELD.md) or onboarded via [brownfield](BROWNFIELD.md) at Level 1+). Artifact rules: [constitution](CONSTITUTION.md). Load this document together with the constitution, the applicable skill and one component slice only.

## Specification authority

For a previously accepted scope, define the intended behavioral delta against the reviewed specification before implementation. Existing code is not authority for silently extending contracts. A change that reveals undocumented behavior requires an explicit decision to preserve, reject or leave it unconstrained. If the aim is to replace code without changing expected behavior, use [REPLACEMENT.md](REPLACEMENT.md).

## Isolation-aware changes

When [component isolation](COMPONENT-ISOLATION.md) is adopted, update the provider's published programmable mock and its contract tests as part of any changed capability. Verify consumers against the mock and the provider independently before the integration join. Changing a mock to match a defective implementation does not amend the accepted contract.

## Feature lifecycle

Each feature starts with a request, which may be a single word or a thousand-line specification. Treat it as input to interpretation, not an already approved requirement set.

### Phase 1 — Specification (before implementation)

| # | Step | Output |
|---|---|---|
| 1 | Request and baseline | Original request preserved; previously accepted specification revision identified |
| 2 | Interpret and scope | Clarified intent, explicit assumptions, changed capabilities and affected components |
| 3 | Decompose | Recursive feature → requirement → sub-requirement hierarchy; component obligations and parent-level composition behavior |
| 4 | Specify verification | Acceptance criteria and tests or other verification procedures for every obligation, including integration behavior; executable tests created where feasible |
| 5 | Requester review | Requirements, test cases, coverage and unresolved decisions presented for review |
| 6 | Iterate | Revise requirements and tests together, repeating review until requester approval |

**Specification approval gate:** The requester or explicitly delegated authority approves a versioned requirements-and-tests baseline before implementation starts. Absence of approval blocks implementation. The approval record identifies the exact baseline and any accepted assumptions. Tests may fail or be unexecutable before implementation; their expected behavior and adequacy are what is approved.

### Phase 2 — Implementation (after approval)

| # | Step | Output |
|---|---|---|
| 7 | Plan and hand off | Dependency-aware component slices from the approved baseline; affected evidence marked historical |
| 8 | Implement | Changes confined to component ownership and approved contracts |
| 9 | Verify and correct | Execute approved tests, record evidence and correct implementation until obligations pass |
| 10 | Accept | Review integrated behavior, evidence, outstanding risks and requester acceptance |

**Change control:** If implementation reveals missing or incorrect requirements or tests, amend the specification and return for renewed requester approval before continuing the affected implementation. Do not weaken tests or rewrite requirements merely to make the implementation pass. Technical verification and requester acceptance are distinct decisions.

### Optional reference-tool checks

- Scope and compatibility: `--impact`, `--compat`, `--plan`.
- Specification and verification: `--stage architecture`, `--stage verification`, `--check-report`.
- Handoff and implementation: `--context`, `--check-scope`, `--check-return`.
- Evidence and acceptance review: `--emit-evidence`, `--evidence-report`, `--stage release`.

These tools do not replace requester approval. Projects select their own review, test, approval and enforcement mechanisms.

### Implementation rules for this optional methodology

- Each leaf requirement targets one component or capability it provides where practical. Parent requirements retain their own integration and end-to-end obligations; sub-requirements do not substitute for composition checks (`REQ-08`).
- Bind each test to the requirement and criteria it verifies. Under the reference workflow, use `verifies` and `--check-report`; derive evidence from executed reports.
- Define and review tests before implementation. Implementation may begin only against an approved baseline; do not treat a failing preimplementation test as successful verification evidence.
- When component isolation is adopted, verify consumer isolation implementations against provider contracts and verify the integration join.
- Use dependency-aware, bounded handoffs; preserve source ownership, relevant contracts and evidence provenance.
- Reopen the affected approval gate when approved behavior or test expectations change. Preserve failed and superseded evidence.
- Report hidden coupling, ambiguous intent and metamodel gaps as feedback instead of silently changing the contract.

## Decompose and hand off

Order: requester-approved requirements, contracts and tests first; then independent implementation per component and integration verification. The toolkit is tool-agnostic: the "implementer" below is whoever receives a slice (a person, a subagent or a separate session).

1. **Write the feature requirement** against the capability during Phase 1, before any implementation.
2. **Split it** into sub-requirements that `refines` it, each targeting exactly one component (or a capability it provides). Each must be buildable and verifiable alone, against fakes.
3. **Obtain requester approval** of the full requirements hierarchy and verification specifications; record the exact baseline. Only then order the work with the reference tools. **Order the work.** `--plan <id>` prints waves, providers first. Components in the same wave are independent and can be implemented in parallel; a later wave starts when the providers it `requires` are verified.
4. **Hand off** one component per implementer. The bundle is: the `--context <component-id>` slice, its sub-requirement, the fakes it uses, the allowed paths (`source_paths`/`test_paths`), and the [handoff return](reference-implementation/handoff-return.schema.json) to fill in.
5. **Check each return**: `--check-scope <component-id> --changed -` (nothing outside its paths) and `--check-return <file>` (every requirement of the component is a result or unmet).
6. **Join.** Record each `results` entry as evidence in the component's fragment. The parent requirement then needs its own integration evidence (`test_scope: integration` component), and every sub-requirement verified (`REQ-08`, since 0.5.0, unreleased). A failed join supersedes evidence and iterates; it does not relabel.

Illustration (not in the shipped example spec): feature "place an order reserves stock" is `req-order-reserves` on `commerce-system`. It is refined by `req-reserve` (target `reserve-inventory`, component `inventory`, wave 1) and `req-order` (target `place-order`, component `checkout`, wave 2, uses the `reserve_inventory` fake). Inventory and checkout implementers work from separate slices; the integration component proves `req-order-reserves` once both are verified and the provider's contract test keeps the fake honest.

Not specified: how an implementer is run (subagent, session, human), or how many run at once; that is project policy.

## Gate Review

| Gate | Bring to review | Decision required before proceeding |
|---|---|---|
| Scope | Requested behavior, `--impact` result, target components and order | The change is bounded; affected consumers and evidence are known |
| Contract | Spec diff, `--compat` result, migration/deprecation plan | Compatible, or every consumer has a migration with recovery; versions follow the compatibility result |
| Specification approval | Feature request, recursively decomposed requirements, acceptance criteria, tests, assumptions and baseline revision | Requester approves what will be built and how correctness will be demonstrated; otherwise revise before implementation |
| Implementation acceptance | Requirement-linked results for the approved revision, integration checks, risk dispositions | Technical obligations satisfied and final acceptance recorded separately from specification approval |

## Prompts

- **Scope**: "Given this request and the current spec, name the capability delta and run `--impact` on each affected ID; list components, consumers and evidence invalidated. No design yet."
- **Contract**: "Propose the spec change (capabilities, interface, data models, versions) for `<component>`; show the `--compat` result against the old spec and any migration needed. Do not invent fields."
- **Verification**: "Write requirements and acceptance criteria for the changed obligations, the fake for each newly required capability, and the provider contract tests that keep the fake honest."
- **Specification review**: "Present the complete requirement hierarchy, component allocation, acceptance criteria and test specifications. Record open interpretations and iterate with the requester until an exact baseline is approved. Do not implement before approval."
- **Implement**: "Use only the requester-approved baseline and its tests. Implement this `--context <component-id>` slice within `source_paths`; return requirement-linked results, unmet criteria and any changes requiring reapproval."

Example of the component layout (source, tests, fakes, schema, checks): [`examples/components/`](examples/components/README.md).

## Using with OpenSpec

[OpenSpec](https://github.com/Fission-AI/OpenSpec) (Fission AI) is a prose spec-and-change workflow for AI assistants: proposal, design notes, tasks, spec deltas (ADDED/MODIFIED/REMOVED), archive. It is a process layer; this model is the checked layer underneath. Neither requires the other, and the toolkit has no OpenSpec importer or exporter.

| OpenSpec | Here |
|---|---|
| Proposal, design notes | Scope and Contract steps, gate reviews |
| Spec delta | `--compat OLD.yaml` and `--impact <id>` |
| Task list | `--plan <id>` waves; one `--context <component>` slice per handoff |
| Archive | Version bumps, `supersedes` evidence history, [gate decision record](CONSTITUTION.md#gate-decision-record) |
| `openspec validate` | `--stage <stage>`, `--check-report` |

- Keep proposals and tasks in OpenSpec if the team uses it; the change is not accepted until the spec passes the Acceptance gate above. Archiving a change is not acceptance.
- Prose requirements and scenarios carry no contracts, components, data models or evidence: express them as `Requirement.criteria` and the model entities before relying on them.
- Treat the spec delta as a review aid; `--compat` is the check.

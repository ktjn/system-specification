# System Specification

Describe **what your system must do** (capabilities, contracts, data, requirements, risks) in a YAML spec, check it with a validator, and use it to drive and verify implementation — by people or AI agents. Code becomes a replaceable realization of the spec.

- Works for new systems (greenfield) and existing ones (brownfield).
- Each component can be handed to one implementer as a small, self-contained slice.
- The validator is optional, illustrative tooling; your project keeps its own methodology and policies ([scope and authority](MODEL-SCOPE.md)).

## Getting started

1. **Install** (Python 3.12+):

   ```bash
   pip install system-spec-ref        # or: uv tool install system-spec-ref
   system-spec --version
   ```

2. **Export the toolkit** (offline docs, examples, schema, agent skills) and follow [`WIRING.md`](WIRING.md) to connect it to your repo:

   ```bash
   system-spec export ./system-spec
   ```

3. **Write a first spec**, e.g. `spec.yaml` — start with one capability:

   ```yaml
   # yaml-language-server: $schema=./system-spec/reference-implementation/schema.json
   system: { id: my-system, version: "0.1" }
   capabilities:
     - id: place-order
       version: "0.1"
       status: specified
       preconditions: [cart_not_empty]
       postconditions: [order_created]
       invariants: [order_paid_at_most_once]
       failure_modes: [customer_blocked]
   components: []
   ```

4. **Validate** at the stage you have reached:

   ```bash
   system-spec spec.yaml --stage discovery    # prints VALID or the violations
   ```

5. **Explore a full example**: [`examples/greenfield/`](examples/greenfield/README.md) walks one system through every gate.

## Choose your path

| Situation | Follow | Stages, in order |
|---|---|---|
| New system | [`GREENFIELD.md`](GREENFIELD.md) | `discovery` → `architecture` → `verification` → `release` |
| Existing system | [`BROWNFIELD.md`](BROWNFIELD.md) ([example](examples/brownfield/README.md)) | `inventory` → `architecture` → `verification` → `release` |

- Each stage is a gate: validate, review with the [gate decision record](CONSTITUTION.md#gate-decision-record), then advance.
- Specify before implementing: capabilities and contracts first, components next, then requirements and tests, then code.
- Release the first slice small (walking skeleton); see [first iteration](GREENFIELD.md#first-iteration).

## Using it over time

Once the spec is accepted, it is the source of truth; change it before the code.

- **Add or change behavior** → [`FEATURE.md`](FEATURE.md): assess impact, check compatibility, hand off per component, re-verify.
- **Hand work to an implementer or AI agent** → give one component slice (`--context <component>`); check its changes stay in scope (`--check-scope`) and its returned results (`--check-return`).
- **Record evidence** → bind tests to requirements, derive evidence from test reports (`--emit-evidence`, `--check-report`), track gaps with `--evidence-report`.
- **Guard in CI** → run `system-spec spec.yaml --stage release` plus `--check-artifacts`/`--check-drift --root .` on every PR ([`WIRING.md` § CI](WIRING.md#3-ci-gate)).
- **Rewrite an implementation** → [`REPLACEMENT.md`](REPLACEMENT.md); **rethink mechanisms or technology** → [`MODERNIZATION.md`](MODERNIZATION.md).
- **Grow** → split large specs into per-component files ([`examples/components/`](examples/components/README.md)); span repositories with [`WORKSPACE.md`](WORKSPACE.md).
- **Upgrade the toolkit** → re-export and compare ([`WIRING.md` § Upgrade](WIRING.md#6-upgrade)).
- **Found a gap in the spec or model?** Report it ([feedback](CONSTITUTION.md#self-improvement-and-model-feedback)) instead of working around it.

## Common commands

`system-spec` takes the same options as `reference-implementation/metamodel.py`.

```bash
system-spec spec.yaml --stage architecture          # validate a gate (default: release)
system-spec spec.yaml --compat old.yaml             # backward compatibility vs a baseline
system-spec spec.yaml --impact <id>                 # transitive change impact
system-spec spec.yaml --plan <capability-id>        # provider-first implementation waves
system-spec spec.yaml --context <component-id>      # bounded slice for one implementer
system-spec spec.yaml --diagram                     # Mermaid diagram
system-spec spec.yaml --check-artifacts --root .    # declared files exist, hashes match
system-spec spec.yaml --check-drift --root .        # imports and schemas vs the spec
system-spec --schema > schema.json                  # JSON Schema for editors/generation
```

From a checkout, run the same in [`reference-implementation/`](reference-implementation/README.md) with `uv run python metamodel.py ...`; tests: `uv run pytest`.

## Concepts

The rest of this page explains the model behind the workflow. Full definitions: [`spec.md`](spec.md) and [`CONSTITUTION.md`](CONSTITUTION.md).

### Core idea

Implementations are not the source of truth — capabilities, invariants, contracts, data models, verification criteria, and formal models are. Each AI or engineering task operates on a bounded component slice (`--context`) validated across progressive lifecycle stages (`--stage`).

```text
Capability → Contract → Data Model → Verification → Implementation → Evidence
```

### Implementation-independent development lifecycle

The durable system definition is its capabilities, requirements, risks, contracts, invariants and verification obligations. Source code is a replaceable realization, not the specification's authority. Passing checks provides evidence for the behaviors and conditions they cover; it does not establish exhaustive behavioral completeness.

Two optional entry tracks converge on an accepted, reviewed specification:

- **Greenfield:** intended outcomes → behavioral contracts and risks → logical composition → verification design → implementation → evidence and acceptance.
- **Brownfield:** existing behavior and code → observed inventory → logical and behavioral characterization → explicit decisions about preserved versus corrected behavior → accepted specification. Scope maturity is recorded per slice, not automatically for the whole product.

After convergence, both use the [feature change workflow](FEATURE.md) for evolution, or the [replacement workflow](REPLACEMENT.md) to construct a new implementation without depending on the old source. [Modernization](MODERNIZATION.md) questions an onboarded system's mechanisms and proposes a next generation through those two workflows. The acceptance authority remains the consuming project. Architecture layers/domains and source/test organization are optional constraints, not intrinsic measures of behavioral conformance.

### Intent and verification confidence

The [metamodel](spec.md#intent-trust-and-verification-adequacy) distinguishes reviewed intent, trusted assumptions, proof/test coverage, verification effectiveness and independent acceptance. These principles strengthen implementation replaceability and programmable mocks without mandating a proof engine. The reference validator does not yet enforce a comprehensive trust-and-verification coverage policy.

### Verified development roadmap

The proposed [verified-development specification](VERIFIED-DEVELOPMENT.md) and [implementation plan](VERIFIED-DEVELOPMENT-PLAN.md) describe reviewable change sets, executable contract adapters, trust/coverage reporting and an independent replacement experiment. They extend existing workflows rather than introducing a mandatory platform, agent runtime or proof engine. **Proposal only:** these capabilities are not claimed as implemented.

### Component isolation and replaceability

The optional [component isolation methodology](COMPONENT-ISOLATION.md) requires standalone execution with substituted dependencies and programmable mocks of provided capabilities. The opt-in reference check `--check-isolation --root <repo>` executes standalone harnesses and the same capability contract suite against the real and mock adapters. It checks declared bindings and executed outcomes, **not** complete semantic equivalence, security sandboxing or exhaustive scenario coverage.

### Standalone Components (Optional AI-Driven Workflow)

The following describes one reference methodology; adopting projects may choose different work boundaries, testing strategies and gates.

A component is the unit of work: it should be buildable and testable from its own `--context` slice, so an agent needs that slice, not the whole repository. The model supports this with explicit boundaries:

- `source_paths` and `test_paths` bind a component to its code and its own tests; test evidence must come from `test_paths` (`COMP-08`).
- Dependencies exist only through declared `requires` capabilities with interface contracts; `--check-drift` flags Python and JS/TS imports (source and tests) that bypass them.
- Each required capability has a fake under `test_paths` (`fakes`, `COMP-09`), and tests may not import other components (`--check-drift`), so tests run against fakes only; `test_scope: integration` exempts assembly/end-to-end tests, which may use providers of required capabilities.
- Platforms and third-party APIs are `external` components (`COMP-11`): contracts only, drawn outside the system; runtime-mediated dependencies name their mediator in `via`.
- A faked capability needs a verified `contract` requirement at its provider (`COMP-10`).
- Not enforced: that a fake matches the provider's contract tests, that a slice alone suffices to build the component, or that a provider publishes a programmable mock. See [component isolation](COMPONENT-ISOLATION.md).
- In the stricter component isolation methodology, providers publish configurable mocks of their own capabilities, consumers run against substitutes, and shared contract suites exercise real and mock adapters.

| Check | Command | Verifies | Does not verify |
|---|---|---|---|
| Metadata | `system-spec spec.yaml --stage <stage>` | Invariants for the stage, incl. `COMP-08` | Any file on disk |
| Isolation | `--check-isolation --root <repo>` | Standalone commands execute successfully, dependency substitutes exist, and shared real/mock contract suites pass | Hermetic isolation, untested scenarios or full behavioral equivalence |
| Artifacts | `--check-artifacts --root <repo>` | Declared source/test/schema paths exist, stay inside the root, and hashes match | Content correctness |
| Drift | `--check-drift --root <repo>` | Python and JS/TS imports vs `requires`/`bindings`; tests importing other components; JSON Schema properties vs model fields | Other languages/formats, field types |
| Evidence report | `--evidence-report` | Per active requirement version: the validator's own verification state (verified, failing/uncovered criteria, blanket and skipped records, methods, holder, priority) for project policy to build on | That evidence is sufficient; that is project policy (`EV-07`, `EV-08` are opt-in) |
| Release scope | `--stage release --release-scope P0[,P1]` | Release obligations for in-scope priorities; the rest is reported deferred, never passed | Deferred requirements |
| Compatibility | `--compat OLD.yaml` | Capability and data-model changes vs the old spec | Clause semantics |
| Plan | `--plan ID` | Provider-first waves of affected components, their bindings, requirements and evidence to revisit (no validation) | That the plan is sufficient |
| Export | `--export backstage\|structurizr` | One-way catalog / C4 workspace output from the spec | Round-tripping; ownership (Backstage `--owner` is a parameter) |
| Test report | `--check-report JUNIT` (repeatable) | Every test binds exactly one current requirement version (`verifies` property); `test` evidence matches the reports (present, same requirement, version and result). `--emit-evidence JUNIT` derives the records | That tests are meaningful or cover every criterion |
| Return | `--check-return FILE` | An implementer's handoff return covers every requirement of the component, versions are current, failures are unmet, changes stay in scope | That results are true or tests meaningful |
| Scope | `--check-scope COMPONENT --changed FILE\|-` | Changed paths stay inside the component's source/test/fake/owned-schema paths (path comparison only; `--allow` extras) | File contents, selector-based tests |

## Repository Map

- **Core Rules & Metamodel**
  - [`CONSTITUTION.md`](CONSTITUTION.md) — shared principles, artifact rules, 10 verification categories, gate decision records, implementation handoffs, and change/reverification loop.
  - [`spec.md`](spec.md) — normative metamodel, 90 stage/compatibility invariants (§ 11), and reference serialization format.
- **Proposed Extensions**
  - [`VERIFIED-DEVELOPMENT.md`](VERIFIED-DEVELOPMENT.md) — requirements and acceptance scenarios for change sets, executable capability contracts, verification assurance and independent replacement.
  - [`VERIFIED-DEVELOPMENT-PLAN.md`](VERIFIED-DEVELOPMENT-PLAN.md) — phased M0–M5 execution roadmap, gates and PR breakdown.
- **Development Tracks**
  - [`GREENFIELD.md`](GREENFIELD.md) — 12-phase, 4-gate workflow (`discovery` → `architecture` → `verification` → `release`), AI Execution Rule, and prompts for new systems.
  - [`BROWNFIELD.md`](BROWNFIELD.md) — 4 adoption levels (`inventory` → `architecture` → `verification` → `release`), 5-step reverse-discovery protocol, risk waivers, and strangler migration prompts for existing systems.
  - [`COMPONENT-ISOLATION.md`](COMPONENT-ISOLATION.md) — standalone execution, dependency substitution, provider-owned programmable mocks and contract-fidelity verification.
  - [`FEATURE.md`](FEATURE.md) — 10-step workflow for adding or changing behavior in an already-specified system: impact, compatibility, per-component handoffs with fakes and tests, re-verification.
  - [`MODERNIZATION.md`](MODERNIZATION.md) — questioning the algorithm and technology choices of an onboarded system against accepted obligations; next-generation architecture re-derived as in greenfield, routed to feature or replacement work.
  - [`WORKSPACE.md`](WORKSPACE.md) — distributed specifications: one spec per repository, imports by link plus version/digest pins, super-repo manifest and `--workspace` cross-member checks.
  - [`EXPERIENCE.md`](EXPERIENCE.md) — optional experience specification: views, interactions, view states, scenarios and visual references for UI/UX, CLI and conversational interfaces.
- **Worked Examples**
  - [`examples/greenfield/`](examples/greenfield/README.md) — end-to-end commerce checkout & inventory walkthrough ([`spec.yaml`](examples/greenfield/spec.yaml), [`Inventory.tla`](examples/greenfield/Inventory.tla), [`Inventory.als`](examples/greenfield/Inventory.als)).
  - [`examples/components/`](examples/components/README.md) — standalone components with their own source, tests, schema and drift/`COMP-08` checks.
  - [`examples/brownfield/`](examples/brownfield/README.md) — legacy billing progression from Level 0 to Level 3 (`level0.yaml` → `level1.yaml` → `old.yaml` → `spec.yaml`), including failed-gate recovery and `--compat` verification.
- **Reference Implementation & Formalization**
  - [`reference-implementation/`](reference-implementation/README.md) — validator ([`metamodel.py`](reference-implementation/metamodel.py)), JSON Schema ([`schema.json`](reference-implementation/schema.json)), Alloy metamodel ([`metamodel.als`](reference-implementation/metamodel.als)), and invalid test corpus ([`corpus.yaml`](reference-implementation/corpus.yaml)).
- **Skills**
  - [`.github/skills/tla/SKILL.md`](.github/skills/tla/SKILL.md) — TLA+/TLC concurrency and protocol verification.
  - [`.github/skills/alloy/SKILL.md`](.github/skills/alloy/SKILL.md) — Alloy structural and relational invariant verification.
  - [`.github/skills/quint/SKILL.md`](.github/skills/quint/SKILL.md) — Quint typed state-machine verification (simulation and bounded model checking).
  - [`.github/skills/modelable/SKILL.md`](.github/skills/modelable/SKILL.md) — deriving `.mdl` data contracts, typed codegen, and field-level compatibility checks.
  - [`.github/skills/ddd/SKILL.md`](.github/skills/ddd/SKILL.md) — event storming, bounded contexts and aggregates mapped to capabilities, components and domains.
- **Distribution & Adoption**
  - [`WIRING.md`](WIRING.md) — connecting an exported toolkit to a project, agent instructions, skills, CI and upgrades.
  - [`templates/BROWNFIELD-INTAKE.md`](templates/BROWNFIELD-INTAKE.md) — intake and gate template for onboarding an existing system.
  - [`templates/MODERNIZATION-DECISION.md`](templates/MODERNIZATION-DECISION.md) — per-mechanism decision record for modernization.
  - [`PACKAGING.md`](PACKAGING.md) — wheel, CLI, offline toolkit export and release acceptance ([machine-readable requirements](packaging.yaml)); PyPI readme in [`PYPI.md`](https://github.com/ktjn/system-specification/blob/main/PYPI.md).
- **Roadmap & Archive**
  - [`PLAN.md`](PLAN.md) — delivered architecture, completed milestones, and optional next horizons.
  - [`archive/`](archive/README.md) — historical [review log](archive/REVIEW.md), [standards benchmark](archive/BENCHMARK.md) and onboarding [feedback](archive/feedback/).

## License

[MIT](LICENSE)

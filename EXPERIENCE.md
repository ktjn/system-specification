# Experience Specification (optional extension)

RFC for describing user-facing behavior (views, transitions, states, visual references) as stable, verifiable contracts that survive replacement of the implementation. Normative summary: [`spec.md` § 13](spec.md#13-experience-specification-optional). Worked example: [`examples/experience/`](examples/experience/README.md). Origin: issue #97.

Optional: a spec without `views` and `experiences` validates exactly as before, and no release obligation applies unless a project declares experiences. Enforcement policy stays with the consuming project ([`MODEL-SCOPE.md`](MODEL-SCOPE.md)).

## Goals and non-goals

- Goals: give agents independent, checkable UX contracts; keep one journey traceable to requirements across components, layers and domains; describe visual, CLI and conversational interfaces alike.
- Non-goals: component libraries, HTML/CSS/framework semantics, deployment, a pixel-level design language, a statechart dialect.

## Concepts

| Concept | Representation | Notes |
|---|---|---|
| Experience | `Spec.experiences[]` | Workflow or goal; realizes `requirements` and `capabilities`; orthogonal to components, layers, domains |
| View | `Spec.views[]` | Presentation context (screen, CLI output, conversational turn): `purpose`, `content`, `actions`, `states`, `references`; reusable across experiences |
| Interaction | `Experience.interactions[]` | `from_view` → `to_view` on a `trigger` the source view offers; `preconditions`, `preserves`, `outcome`, `invariants`, `failure_modes` |
| ViewState | `View.states` | State name → required handling; scoped to the view |
| DesignConstraint | `Experience.constraints` | Named standard or value, e.g. `accessibility: WCAG-2.2-AA`; verified through a requirement |
| VisualReference | `View.references`, `Experience.references` | `path`, `authority`, `version`, `accepted_by`, `sha256` |
| Scenario | `Experience.scenarios[]` | Exercises interactions and `view.state` entries; verified through an existing `Requirement`; `kind: positive|negative` |

Existing entities are reused, not duplicated: obligations are `Requirement`s, results are `Evidence` (§ 8), risks are `Risk`s. A scenario adds only the link from a requirement to the interactions and states it exercises.

## Validation

| ID | Stage | Rule |
|---|---|---|
| `EXP-01` | `inventory` | IDs unique (experiences, views; interactions and scenarios within an experience) |
| `EXP-02` | `inventory` | References resolve: requirements, capabilities, views, interaction ends (must be views of the experience), scenario requirements, interactions and `view.state` entries |
| `EXP-03` | `architecture` | Each interaction has a non-empty `outcome` and a `trigger` listed in its source view's `actions` |
| `EXP-04` | `architecture` | View states state their handling; each interaction failure mode maps to a state of its source or target view |
| `EXP-05` | `verification` | A `critical` experience has scenarios covering every interaction, and a `negative` scenario for every interaction with failure modes |
| `EXP-06` | `inventory` | A `normative` reference declares `version` and `accepted_by` |
| `EXP-07` | `release` | The requirements verifying a critical experience's scenarios have passing evidence |

- No global state list is prescribed. Which states a view needs is the project's decision, enforced only through `EXP-04` (declared states have handling; declared failures have a state) and `EXP-05`.
- Illustrative references are never pass/fail criteria: nothing in the validator or the evidence rules reads them. Only a `normative` reference constrains presentation, under its named acceptance authority.
- `--check-artifacts` checks that reference files exist and match `sha256`.

## Verification

- Scenarios are verified through requirements, so a scenario passes when its requirement's evidence passes. Tests that drive the scenario bind to that requirement like any test (`--check-report`).
- Verification is independent of the implementation: the same scenarios run against any implementation of the experience.
- Measurable usability goals (task completion within N steps, error rate) belong in requirement `criteria` with `test` or `analysis` evidence. Subjective design preference is an `inspection` by the reference's `accepted_by`, or stays an illustrative reference. The validator never judges either.

## Decisions on the open questions of issue #97

- **ViewState scope**: per view. Handling differs per view, and a shared vocabulary stays a project naming convention (`unauthorized` in every view that needs it).
- **Interaction model**: transitions, invariants and failure-to-state mappings only. A formal statechart dialect is out of scope; for behavior that needs one, model it with the [`quint`](.github/skills/quint/SKILL.md) or [`tla`](.github/skills/tla/SKILL.md) skills and record `model-check` evidence on a requirement.
- **Visual references**: a minimal `VisualReference` in the core schema. Richer formats (design tokens, design-tool exports) are referenced by `path` and interpreted by project extensions; the validator does not parse them.
- **Usability goals**: see Verification above.
- **Nonvisual UX**: a view is a presentation context with content, actions and states, with no web terms. A CLI command's output, a prompt or a conversational turn is a view; a command or reply is an action.

## Serialization differences from the issue's sketch

- `views` are top-level so several experiences can reuse them; an experience lists their IDs.
- Interaction ends are `from_view` and `to_view` (not `from`/`to`).
- `failure_modes` is a mapping to the handling state, like `Interface.errors`, instead of a bare list.
- View `states` is a mapping to handling text, not a list of names; the experience has no state list of its own.
- `scenarios` are nested in the experience.

## Extension points and limits

- Extra fields are rejected (`extra=forbid`); project-specific data goes in referenced artifacts.
- Not yet covered: `--impact`, `--context`, `--diagram` and exports do not include experiences; `constraints` are not verified by the validator; scenarios do not name acceptance criteria.
- Not done: the pilot in observability-spec and an AI reimplementation test (adoption steps 4 and 5 of the issue); gaps found there should come back as feedback ([`CONSTITUTION.md`](CONSTITUTION.md#self-improvement-and-model-feedback)).

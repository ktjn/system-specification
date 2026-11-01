# Changelog

Toolkit versions (`system-spec --version`) are independent of a modeled system's `system.version`. Spec files stay valid across releases when changes only add optional fields; a validator older than a field rejects specs that use it.

## Unreleased

- Split specs: `include` patterns in the root spec merge fragment files (any section except `system`); `fragment.schema.json` and `--fragment-schema` for editors. New optional `include` key on the root; `examples/components/` is now split. Specs using `include` need a validator that includes it.

## 0.3.0

Compatibility: all additions are optional or opt-in (`test_paths`, `fakes`, `Evidence.environment`); existing specs validate unchanged. Specs that use these fields need a 0.3.0+ validator (older ones reject unknown fields). Declaring `fakes` or `test_paths` activates `COMP-08` to `COMP-10`.

- `COMP-10` (release): a capability that a consumer fakes needs a verified `contract` requirement at its provider. Existing specs unaffected unless they declare `fakes`.
- `Evidence.environment` (optional): host/OS/CI job, distinguishing local from remote runs (`SCL-FB-06`).
- `--plan <id>`: provider-first delivery waves for a change, with per-component bindings and evidence to revisit.
- `--check-scope <component> --changed <file|->`: fails when a change touches paths outside the component's source/test/fake/schema paths (handoff scope guard).
- `test_paths`/`fakes` accept `tool::selector` entries for package-level runners (e.g. `nextest::-p crate`); `COMP-08`/`COMP-09` match them by prefix. `--check-drift` also reads `Cargo.toml` path/workspace dependencies. Addresses `SCL-FB-03`, `SCL-FB-04`.
- New [`FEATURE.md`](FEATURE.md) track: changing an already-specified system.
- `Component.test_paths` and `COMP-08` (verification): test evidence for a component that declares `test_paths` must come from files under them. Opt-in; existing specs unaffected. Specs using `test_paths` need a validator that includes it.
- `Component.fakes` and `COMP-09` (verification): a component with `test_paths` needs a fake under them for each required capability.
- `--check-drift` also scans `test_paths` and rejects tests importing other components (use the fakes); `--check-artifacts` verifies `test_paths` and `fakes` exist.
- `--diagram`: data models sit in their owner's layer; persisted ones (`namespace`/`storage_role`) are cylinders, logical-only ones dashed boxes; node IDs are prefixed per kind (`s_`, `l_`, `c_`, `d_`), so a component named like its layer renders.
- New [`examples/components/`](examples/components/README.md): standalone components with their own tests.

## 0.2.0

- `--check-drift --root`: Python imports between components vs `requires`/`bindings`; JSON Schema properties vs data model fields.
- `WIRING.md`: uv install, schema modeline, CI gate, path anchoring, skill link rewrite, adoption guidance.

## 0.1.0

- First release: validator CLI (`system-spec`), JSON Schema, offline `export`, workflows, examples and skills.

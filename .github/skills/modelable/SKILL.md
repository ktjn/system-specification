---
name: modelable
description: Define a component's data contracts in Modelable `.mdl`, check compatibility and lineage, generate artifacts, and record results as metamodel Evidence. Use for data contract phases (greenfield 5, brownfield step 2) and before publishing a new data model version.
---

# Modelable Data Contracts

Rules: [constitution § Data Contracts](../../../CONSTITUTION.md#data-contracts). Format: [`spec.md`](../../../spec.md) §§ 5, 8. Tool: [Modelable](https://github.com/ktjn/modelable).

## Inputs

- Target `data_models` entries: `id`, `version`, `owner`, `fields`, `classification`, `derived_from`.
- Requirement(s) to verify, with `criteria`.
- Brownfield: existing schemas or DDL (`modelable import`).

## Mapping

| Metamodel | `.mdl` |
|---|---|
| `owner` (component ID) | `domain` with `owner: "<component>"` |
| `id`, `version` `"N.0"` | `entity`/`event`/`value` `<Name> @ N` |
| `fields` | Typed fields; exactly one `@key` for entities |
| `classification` | `@classification("…")`/`@pii` on fields; model level = strictest field. `open` → `public`; `secret` → `restricted` |
| `derived_from` | `projection … from <src> @ N` / `join <src> @ N`; fields use `<-` or `=` |

Example: [`example.mdl`](../../../reference-implementation/example.mdl) mirrors the `data_models` of [`example.yaml`](../../../reference-implementation/example.yaml).

## Steps

1. **Model**: one `domain` per owning component; only fields named by the contract.
   - Annotate `@pii`/`@classification` explicitly on every projection field; it is not inherited by generated artifacts.
2. **Validate**: `modelable validate <dir> --strict`.
3. **Lineage**: `modelable lineage <domain>.<Projection>@N --path <dir>`; sources must match `derived_from`.
4. **Compatibility** (new version): `modelable diff <ref>@N <ref>@N+1 --path <dir>` and `modelable validate-compat --from <old> --to <new> --target <json-schema|protobuf|openapi|…>`. Exit `1` = breaking; bump major and run `metamodel.py --impact <id>`.
5. **Generate**: `modelable compile <dir> --target <target> --out <dir>`; keep `modelable-artifact-manifest.json`.
6. **Sync**: update `data_models` in the metamodel YAML; run `metamodel.py`.

## Evidence

```yaml
evidence:
  - id: ev-order-contract
    requirement_id: req-order-contract
    requirement_version: "1.0"
    method: analysis
    passed: true
    provenance: modelable::validate example.mdl --strict
```

- `diff`/`validate-compat` → `analysis`; generated serializer tests → `test`.
- `provenance` identifies the command and sources; keep tool version and output with it ([`spec.md` § 8](../../../spec.md#8-verification)).
- Model changes invalidate the evidence; rerun after `--impact <data-model>`.

## Notes

- Requires Python 3.14: `uvx modelable`. If import fails on `selectolax`, use `uvx --with 'selectolax<1' modelable`.
- `(additive)` versions reject removals; declare breaking versions explicitly.

## Prompt

"Write `.mdl` for `<data-model>` from its contract; one domain per owner, no invented fields, explicit `@pii`/`@classification` on every field and projection field."

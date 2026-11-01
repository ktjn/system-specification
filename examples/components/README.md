# Components Example: Standalone Components with Their Own Tests

[`spec.yaml`](spec.yaml) is the commerce example with physical bindings, so each component can be built and verified from its own slice:

- `source_paths` / `test_paths` per component (`src/<id>`, `tests/<id>`); `schema_path` on `stock-item`.
- Test evidence names a file under the owning component's `test_paths` (`tests/checkout/test_checkout.py::test_place_order`), so `COMP-08` holds.
- `checkout` imports `inventory` only because it declares `requires: [reserve-inventory@^1.0]`; its tests use a fake of that contract, never inventory internals.

```bash
# from reference-implementation/
uv run python metamodel.py ../examples/components/spec.yaml                                         # metadata + COMP-08
uv run python metamodel.py ../examples/components/spec.yaml --check-artifacts --root ../examples/components
uv run python metamodel.py ../examples/components/spec.yaml --check-drift --root ../examples/components
uv run python metamodel.py ../examples/components/spec.yaml --context checkout                      # the slice an agent gets
```

Source and tests live in this directory so `--root` points here. Illustrative evidence values (dates, verifiers) were not produced by running a pipeline.

## Break it on purpose

- Add `import src.checkout.app` to `src/inventory/api.py` → `--check-drift` reports `inventory` imports `checkout` with no declared requirement.
- Change `tests/checkout/test_checkout.py::test_place_order` evidence provenance to `tests/inventory/x.py::t` → `COMP-08`.
- Add a `discount` property to `schemas/stock-item.json` → `--check-drift` reports a property undeclared in the model.

Limits: Python imports and JSON Schema property names only; nothing yet requires a fake per required capability.

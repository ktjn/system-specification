import json
from pathlib import Path

import pytest
from metamodel import Capability, DataModel, Interface, check_compatibility, compare_specs, load_spec, main


def example():
    return load_spec(Path(__file__).parent / "example.yaml")


def interface():
    return Interface(endpoint="/orders", mode="sync", request="order", response="order", idempotency=True,
                     security="authenticated", failure_statuses={"unavailable": "503"})


@pytest.mark.parametrize("change,diagnostic", [
    ("removed-field", "Removed fields"), ("changed-type", "Changed field types"),
    ("added-field", "Added fields"), ("classification", "Changed classification"),
])
def test_data_contract_change_reports_break_and_missing_major(change, diagnostic):
    old, new = example(), example()
    model = new.data_models[0]
    if change == "removed-field": model.fields.pop("available_qty")
    if change == "changed-type": model.fields["available_qty"] = "string"
    if change == "added-field": model.fields["warehouse"] = "uuid"
    if change == "classification": model.classification = "restricted"
    errors = compare_specs(old, new)
    assert any("DataModel 'stock-item': " + diagnostic in e for e in errors)
    assert any("DataModel 'stock-item': Breaking change requires major version bump" in e for e in errors)
    model.version = "2.0"
    errors = compare_specs(old, new)
    assert any(diagnostic in e for e in errors)
    assert not any("major version" in e for e in errors)


def test_removed_model_cannot_silently_disappear():
    old, new = example(), example()
    new.data_models.pop()
    assert any("DataModel 'order-stock-projection': removed" in e for e in compare_specs(old, new))


def test_new_model_and_owner_migration_preserve_declared_contract():
    old, new = example(), example()
    new.data_models[0].owner = "replacement-owner"
    new.data_models.append(DataModel(id="new", version="1.0", owner="checkout", fields={"id": "uuid"}))
    assert compare_specs(old, new) == []


@pytest.mark.parametrize("field,value", [
    ("endpoint", "/v2/orders"), ("mode", "async"), ("request", "new-request"),
    ("response", "new-response"), ("idempotency", False), ("security", "public"),
    ("failure_statuses", {"unavailable": "500"}),
])
def test_interface_changes_require_review_and_capability_major(field, value):
    old = Capability(id="service", version="1.0", interface=interface())
    new = old.model_copy(deep=True)
    setattr(new.interface, field, value)
    errors = check_compatibility(old, new)
    assert any(f"Changed interface {field}" in e for e in errors)
    assert any("major version" in e for e in errors)
    new.version = "2.0"
    assert check_compatibility(old, new) == [f"Changed interface {field}"]


def test_known_interface_cannot_be_removed():
    old = Capability(id="service", version="1.0", interface=interface())
    new = old.model_copy(update={"interface": None})
    assert "Removed interface" in check_compatibility(old, new)


def test_adding_interface_metadata_does_not_invent_a_legacy_contract():
    old = Capability(id="service", version="1.0")
    assert check_compatibility(old, old.model_copy(update={"interface": interface()})) == []


@pytest.mark.parametrize("version", ["1.1", "0.9", "not-a-version"])
def test_non_major_changes_cannot_hide_data_break(version):
    old, new = example(), example()
    new.data_models[0].version = version
    new.data_models[0].classification = "public"
    assert any("major version" in e for e in compare_specs(old, new))


def test_compat_cli_rejects_data_break_with_valid_whole_spec(tmp_path, capsys):
    old, new = example(), example()
    new.data_models[0].fields["available_qty"] = "string"
    old_path, new_path = tmp_path / "old.json", tmp_path / "new.json"
    old_path.write_text(old.model_dump_json(), encoding="utf-8")
    new_path.write_text(new.model_dump_json(), encoding="utf-8")
    assert main([str(new_path), "--compat", str(old_path), "--json"]) == 1
    result = json.loads(capsys.readouterr().out)
    assert result["valid"] is False
    assert result["errors"] == ["DataModel 'stock-item': Changed field types: ['available_qty']",
                                "DataModel 'stock-item': Breaking change requires major version bump (1.0 -> 1.0)"]

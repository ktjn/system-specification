import json

import pytest
from metamodel import Capability, Component, Spec, SystemDef, main, validate_spec


def inventory():
    return Spec(system=SystemDef(id="legacy", version="1.0"), capabilities=[],
                components=[Component(id="monolith", version="1.0", requires=["unmapped@^1.0"])])


def discovery():
    s = inventory()
    s.capabilities = [Capability(id="service", version="1.0", status="specified",
                                postconditions=["result produced"], invariants=["result unique"],
                                failure_modes=["unavailable"])]
    return s


def test_inventory_allows_unmapped_component_stubs():
    s = inventory()
    assert validate_spec(s, stage="inventory") == []
    assert any("must provide" in e for e in validate_spec(s))


def test_inventory_still_rejects_duplicate_ids():
    s = inventory()
    s.components.append(s.components[0].model_copy())
    assert validate_spec(s, stage="inventory") == ["Duplicate component id 'monolith'"]


@pytest.mark.parametrize("ref", ["", " ", "@^1.0", "service@^", "service@^nope", "service@^1.0@^2.0"])
def test_inventory_rejects_invalid_capability_reference_syntax(ref):
    s = inventory()
    s.components[0].requires = [ref]
    assert any("reference syntax" in e for e in validate_spec(s, stage="inventory"))


def test_discovery_accepts_contracts_without_architecture_or_evidence():
    s = discovery()
    assert validate_spec(s, stage="discovery") == []


@pytest.mark.parametrize("field", ["postconditions", "invariants", "failure_modes"])
def test_discovery_requires_each_contract_group(field):
    s = discovery()
    setattr(s.capabilities[0], field, [" "])
    assert any("contract" in e for e in validate_spec(s, stage="discovery"))
    assert validate_spec(s, stage="inventory") == []


def test_discovery_requires_specified_capabilities():
    s = discovery()
    s.capabilities[0].status = "draft"
    assert any("status" in e for e in validate_spec(s, stage="discovery"))


def test_discovery_retains_inventory_checks():
    s = discovery()
    s.components.append(s.components[0].model_copy())
    assert any("Duplicate component" in e for e in validate_spec(s, stage="discovery"))


def test_stage_cli_reports_stage_and_keeps_legacy_behavior(tmp_path, capsys):
    path = tmp_path / "inventory.json"
    path.write_text(inventory().model_dump_json(), encoding="utf-8")
    assert main([str(path), "--stage", "inventory", "--json"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output == {"valid": True, "errors": [], "stage": "inventory"}
    assert main([str(path), "--json"]) == 1
    assert json.loads(capsys.readouterr().out)["valid"] is False


def test_unsupported_stage_is_rejected():
    with pytest.raises(ValueError, match="Unsupported stage"):
        validate_spec(inventory(), stage="architecture")
    with pytest.raises(SystemExit) as exc:
        main(["--stage", "architecture"])
    assert exc.value.code == 2


@pytest.mark.parametrize("flag, value", [("--impact", "legacy"), ("--compat", "old.yaml"), ("--schema", None)])
def test_stage_cannot_be_silently_ignored_by_another_operation(flag, value, capsys):
    args = ["--stage", "inventory", flag] + ([value] if value else [])
    with pytest.raises(SystemExit) as exc:
        main(args)
    assert exc.value.code == 2
    assert "cannot combine --stage" in capsys.readouterr().err

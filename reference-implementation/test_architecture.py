import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from metamodel import Spec, load_spec, main, validate_spec


def architecture():
    data = load_spec(Path(__file__).parent / "example.yaml").model_dump()
    data["requirements"], data["risks"], data["evidence"] = [], [], []
    for c in data["components"]: c["status"] = "specified"
    for cap in data["capabilities"]:
        cap["status"] = "specified"
        cap["interface"] = dict(endpoint=cap["id"], mode="sync", request="order", response="order",
                                idempotency=True, security="authenticated customer",
                                failure_statuses={failure: "409" for failure in cap["failure_modes"]})
    return Spec.model_validate(data)


def test_architecture_passes_without_verification_artifacts():
    s = architecture()
    assert validate_spec(s, stage="architecture") == []
    assert any("no associated requirements" in e for e in validate_spec(s))


@pytest.mark.parametrize("change, diagnostic", [
    ("status", "requires specified status"), ("contract", "empty contract"),
    ("provider", "unresolved capability"), ("layer", "undeclared layer"),
    ("ownership", "does not list it"), ("lineage", "unknown data model"),
    ("classification", "classification propagation"), ("cycle", "Dependency cycle"),
    ("interface", "missing interface"), ("request", "unknown request data model"),
    ("failure", "unmapped failure mode"), ("budget", "context budget"),
    ("response", "unknown response data model"), ("extra-failure", "unknown failure mode"),
    ("layer-direction", "layer violation"), ("shared-owner", "also claimed"),
    ("external-source", "untracked external"), ("duplicates", "Duplicate component"),
])
def test_architecture_enforces_its_obligations(change, diagnostic):
    s = architecture()
    if change == "status": s.components[0].status = "draft"
    if change == "contract": s.capabilities[0].invariants = []
    if change == "provider": s.components[0].requires = ["missing"]
    if change == "layer": s.components[0].layer = "unknown"
    if change == "ownership": s.components[0].owns_data = []
    if change == "lineage": s.data_models[-1].derived_from = ["missing"]
    if change == "classification": s.data_models[-1].classification = "public"
    if change == "cycle": s.components[1].requires = ["place-order"]
    if change == "interface": s.capabilities[0].interface = None
    if change == "request": s.capabilities[0].interface.request = "missing"
    if change == "failure": s.capabilities[0].interface.failure_statuses = {}
    if change == "budget": s.system.context_budget.max_owns_data = 1
    if change == "response": s.capabilities[0].interface.response = "missing"
    if change == "extra-failure": s.capabilities[0].interface.failure_statuses["extra"] = "500"
    if change == "layer-direction": s.components[0].layer = "infrastructure"
    if change == "shared-owner": s.components[1].owns_data.append("order")
    if change == "external-source": s.data_models[0].external_source = "missing"
    if change == "duplicates": s.components.append(s.components[0].model_copy())
    assert any(diagnostic in e for e in validate_spec(s, stage="architecture"))


def test_context_budget_overrides_and_schema():
    data = architecture().model_dump()
    data["system"]["context_budget"] = {"max_requires": 0}
    s = Spec.model_validate(data)
    assert s.system.context_budget.max_provides == 5
    assert any("context budget" in e for e in validate_spec(s, stage="architecture"))
    for value in (-1, True, "5"):
        data["system"]["context_budget"] = {"max_requires": value}
        with pytest.raises(ValidationError): Spec.model_validate(data)


@pytest.mark.parametrize("field, value", [("endpoint", " "), ("mode", "http"), ("security", ""),
                                         ("idempotency", "yes"), ("failure_statuses", {"timeout": ""})])
def test_interface_schema_rejects_incomplete_contracts(field, value):
    data = architecture().model_dump()
    data["capabilities"][0]["interface"][field] = value
    with pytest.raises(ValidationError): Spec.model_validate(data)


def test_architecture_cli(tmp_path, capsys):
    path = tmp_path / "architecture.json"
    path.write_text(architecture().model_dump_json(), encoding="utf-8")
    assert main([str(path), "--stage", "architecture", "--json"]) == 0
    assert json.loads(capsys.readouterr().out) == {"valid": True, "errors": [], "stage": "architecture"}


def test_budget_boundary_and_async_contract():
    s = architecture()
    s.system.context_budget.max_owns_data = 2
    s.capabilities[1].interface.mode = "async"
    assert validate_spec(s, stage="architecture") == []


def test_architecture_does_not_require_risk_mitigation_evidence():
    s = architecture()
    source = load_spec(Path(__file__).parent / "example.yaml")
    s.requirements, s.risks = source.requirements, source.risks
    assert validate_spec(s, stage="architecture") == []
    assert any("unverified mitigation" in e for e in validate_spec(s))

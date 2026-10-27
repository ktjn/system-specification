from pathlib import Path
from metamodel import load_spec, validate_spec, resolve_capabilities, check_compatibility, impact_analysis

EXAMPLE = Path(__file__).parent / "example.yaml"

def spec(): return load_spec(EXAMPLE)

def test_valid(): assert validate_spec(spec()) == []

def test_resolution(): assert resolve_capabilities(spec())["checkout"]["reserve-inventory"] == "inventory"

def test_no_capability():
    s = spec(); s.components[0].provides = []
    assert any("at least one capability" in e for e in validate_spec(s))

def test_unresolved():
    s = spec(); s.components[0].requires.append("missing@^1.0")
    assert any("unresolved capability" in e for e in validate_spec(s))

def test_cap_needs_req():
    s = spec(); s.requirements = [r for r in s.requirements if r.target != "reserve-inventory"]
    assert any("no associated requirements" in e for e in validate_spec(s))

def test_missing_evidence():
    s = spec(); s.evidence = []
    assert any("missing valid verification evidence" in e for e in validate_spec(s))

def test_stale_evidence():
    s = spec(); s.requirements[0].version = "2.0"
    assert any("missing valid verification evidence" in e for e in validate_spec(s))

def test_conflict():
    s = spec(); s.requirements[0].conflicts_with.append(s.requirements[1].id)
    assert any("unresolved conflict" in e for e in validate_spec(s))

def test_risk():
    s = spec(); s.risks[0].mitigated_by = ["missing"]
    assert any("unverified mitigation" in e for e in validate_spec(s))

def test_external_data():
    s = spec(); s.data_models[0].external_source = "untracked"
    assert any("untracked external data source" in e for e in validate_spec(s))

def test_classification():
    s = spec(); s.data_models[2].classification = "public"
    assert any("classification" in e for e in validate_spec(s))

def test_layer_violation():
    s = spec(); s.components[1].requires.append("place-order@^1.0")
    assert any("layer violation" in e for e in validate_spec(s))

def test_compatibility():
    c = spec().capabilities[0]
    assert check_compatibility(c, c.model_copy(update={"postconditions": [*c.postconditions, "logged"]})) == []
    assert check_compatibility(c, c.model_copy(update={"preconditions": [*c.preconditions, "extra"]})) != []

def test_impact():
    imp = impact_analysis(spec(), "reserve-inventory")
    assert ("checkout" in imp["components"]) and ("req-reserve" in imp["requirements"]) and ("ev-reserve-test" in imp["invalidated_evidence"])

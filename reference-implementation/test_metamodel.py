from pathlib import Path
from metamodel import load_spec, validate_spec, resolve_capabilities, check_compatibility, compare_specs, impact_analysis, main, Component, Evidence

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
    assert any("major version" in e for e in check_compatibility(c, c.model_copy(update={"failure_modes": ["timeout"]})))
    assert check_compatibility(c, c.model_copy(update={"failure_modes": ["timeout"], "version": "2.0"})) == ["Added failure modes: ['timeout']"]

def test_compare_specs():
    s, n = spec(), spec(); n.capabilities.pop()
    assert any("removed without deprecation" in e for e in compare_specs(s, n))
    s.capabilities[-1].deprecated = True
    assert compare_specs(s, n) == []

def test_impact():
    imp = impact_analysis(spec(), "reserve-inventory")
    assert ("checkout" in imp["components"]) and ("req-reserve" in imp["requirements"]) and ("ev-reserve-test" in imp["invalidated_evidence"])
    assert {"req-order", "req-latency"} <= set(imp["requirements"])

def test_impact_data():
    imp = impact_analysis(spec(), "order")
    assert "order-stock-projection" in imp["data_models"] and "inventory" in imp["components"]

def err(s, msg): return any(msg in e for e in validate_spec(s))

def test_ambiguous_provider():
    s = spec(); s.components.append(Component(id="inv2", version="1.0", layer="domain", provides=["reserve-inventory"]))
    assert err(s, "ambiguous providers")
    s.components[0].bindings = {"reserve-inventory": "inventory"}
    assert not err(s, "ambiguous") and resolve_capabilities(s)["checkout"]["reserve-inventory"] == "inventory"

def test_self_dependency():
    s = spec(); s.components[0].requires.append("place-order")
    assert err(s, "unresolved capability 'place-order'")

def test_cycle():
    s = spec(); s.system.layers = []; s.components[1].requires.append("place-order")
    assert err(s, "Dependency cycle")

def test_failing_evidence():
    s = spec(); s.evidence.append(Evidence(id="ev-fail", requirement_id="req-order", requirement_version="1.0", method="test", passed=False, provenance="ci"))
    assert err(s, "unresolved failing evidence")

def test_mitigation_needs_evidence():
    s = spec(); s.requirements[1].mandatory = False; s.evidence = [e for e in s.evidence if e.requirement_id != "req-reserve"]
    assert err(s, "unverified mitigation 'req-reserve'")

def test_duplicate_ids():
    s = spec(); s.requirements.append(s.requirements[0])
    assert err(s, "Duplicate requirement id 'req-order'")

def test_dangling_refs():
    s = spec(); s.requirements[0].target = "nope"; s.requirements[0].depends_on = ["nope"]; s.evidence[0].requirement_id = "nope"
    assert err(s, "unknown target") and err(s, "depends_on unknown") and err(s, "Evidence 'ev-order-test' references unknown")

def test_ambiguous_target():
    s = spec(); s.data_models[0].id = "place-order"
    assert err(s, "ambiguous target")

def test_ownership():
    s = spec(); s.components[0].owns_data = []
    assert err(s, "does not list it in owns_data")
    s = spec(); s.data_models[0].owner = "nobody"
    assert err(s, "unknown owner")

def test_unknown_lineage():
    s = spec(); s.data_models[2].derived_from = ["ghost"]
    assert err(s, "unknown data model 'ghost'")

def test_undeclared_layer():
    s = spec(); s.components[0].layer = "ui"
    assert err(s, "undeclared layer")

def test_bad_version():
    s = spec(); s.components[0].requires = ["reserve-inventory@^1.0-beta"]
    assert err(s, "unresolved capability")

def test_cli(capsys, tmp_path):
    assert main([str(EXAMPLE)]) == 0 and "VALID" in capsys.readouterr().out
    bad = tmp_path / "bad.yaml"; bad.write_text("system: {}")
    assert main([str(bad), "--json"]) == 1 and "schema_errors" in capsys.readouterr().out
    assert main([str(EXAMPLE), "--impact", "order"]) == 0 and "order-stock-projection" in capsys.readouterr().out
    assert main([str(EXAMPLE), "--compat", str(EXAMPLE)]) == 0

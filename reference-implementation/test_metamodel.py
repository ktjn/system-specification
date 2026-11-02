import pytest, yaml
from pathlib import Path
from pydantic import ValidationError
from metamodel import load_spec, validate_spec, resolve_capabilities, check_compatibility, compare_specs, impact_analysis, apply_report, main, Component, Evidence, Requirement, Spec, Binding

EXAMPLE = Path(__file__).parent / "example.yaml"
v = pytest.mark.verifies

def spec(): return load_spec(EXAMPLE)

@v("req-schema@1.0")
def test_valid(): assert validate_spec(spec()) == []

@v("req-resolution@1.0")
def test_resolution(): assert resolve_capabilities(spec())["checkout"]["reserve-inventory"] == "inventory"

@v("req-references@1.0")
def test_no_capability():
    s = spec(); s.components[0].provides = []
    assert any("at least one capability" in e for e in validate_spec(s))

@v("req-resolution@1.0")
def test_unresolved():
    s = spec(); s.components[0].requires.append("missing@^1.0")
    assert any("unresolved capability" in e for e in validate_spec(s))

@v("req-references@1.0")
def test_cap_needs_req():
    s = spec(); s.requirements = [r for r in s.requirements if r.target != "reserve-inventory"]
    assert any("no associated requirements" in e for e in validate_spec(s))

@v("req-evidence@1.0")
def test_missing_evidence():
    s = spec(); s.evidence = []
    assert any("missing valid verification evidence" in e for e in validate_spec(s))

@v("req-evidence@1.0")
def test_stale_evidence():
    s = spec(); s.requirements[0].version = "2.0"
    assert any("missing valid verification evidence" in e for e in validate_spec(s))

@v("req-conflicts@1.0")
def test_conflict():
    s = spec(); s.requirements[0].conflicts_with.append(s.requirements[1].id)
    assert any("unresolved conflict" in e for e in validate_spec(s))

@v("req-risks@1.0")
def test_risk():
    s = spec(); s.risks[0].mitigated_by = ["missing"]
    assert any("unverified mitigation" in e for e in validate_spec(s))

@v("req-ownership@1.0")
def test_external_data():
    s = spec(); s.data_models[0].external_source = "untracked"
    assert any("untracked external data source" in e for e in validate_spec(s))

@v("req-lineage@1.0")
def test_classification():
    s = spec(); s.data_models[2].classification = "public"
    assert any("classification" in e for e in validate_spec(s))

@v("req-layers@1.0")
def test_layer_violation():
    s = spec(); s.components[1].requires.append("place-order@^1.0")
    assert any("layer violation" in e for e in validate_spec(s))

@v("req-compat@1.0")
def test_compatibility():
    c = spec().capabilities[0]
    assert check_compatibility(c, c.model_copy(update={"postconditions": [*c.postconditions, "logged"]})) == []
    assert check_compatibility(c, c.model_copy(update={"preconditions": [*c.preconditions, "extra"]})) != []
    assert any("major version" in e for e in check_compatibility(c, c.model_copy(update={"failure_modes": ["timeout"]})))
    assert check_compatibility(c, c.model_copy(update={"failure_modes": ["timeout"], "version": "2.0"})) == ["Added failure modes: ['timeout']"]

@v("req-compat@1.0")
def test_compare_specs():
    s, n = spec(), spec(); n.capabilities.pop()
    assert any("removed without deprecation" in e for e in compare_specs(s, n))
    s.capabilities[-1].deprecated = True
    assert compare_specs(s, n) == []

@v("req-impact@1.0")
def test_impact():
    imp = impact_analysis(spec(), "reserve-inventory")
    assert ("checkout" in imp["components"]) and ("req-reserve" in imp["requirements"]) and ("ev-reserve-test" in imp["invalidated_evidence"])
    assert {"req-order", "req-latency"} <= set(imp["requirements"])

@v("req-impact@1.0")
def test_impact_data():
    imp = impact_analysis(spec(), "order")
    assert "order-stock-projection" in imp["data_models"] and "inventory" in imp["components"]

def err(s, msg): return any(msg in e for e in validate_spec(s))

@v("req-resolution@1.0")
def test_ambiguous_provider():
    s = spec(); s.components.append(Component(id="inv2", version="1.0", layer="domain", provides=["reserve-inventory"]))
    assert err(s, "ambiguous providers")
    s.components[0].bindings = {"reserve-inventory": "inventory"}
    assert not err(s, "ambiguous") and resolve_capabilities(s)["checkout"]["reserve-inventory"] == "inventory"

@v("req-resolution@1.0")
def test_self_dependency():
    s = spec(); s.components[0].requires.append("place-order")
    assert err(s, "unresolved capability 'place-order'")

@v("req-cycles@1.0")
def test_cycle():
    s = spec(); s.system.layers = []; s.components[1].requires.append("place-order")
    assert err(s, "Dependency cycle")

@v("req-evidence@1.0")
def test_failing_evidence():
    s = spec(); s.evidence.append(Evidence(id="ev-fail", requirement_id="req-order", requirement_version="1.0", method="test", passed=False, provenance="ci"))
    assert err(s, "unresolved failing evidence")

@v("req-risks@1.0")
def test_mitigation_needs_evidence():
    s = spec(); s.requirements[1].mandatory = False; s.evidence = [e for e in s.evidence if e.requirement_id != "req-reserve"]
    assert err(s, "unverified mitigation 'req-reserve'")

@v("req-references@1.0")
def test_duplicate_ids():
    s = spec(); s.requirements.append(s.requirements[0])
    assert err(s, "Duplicate requirement id 'req-order'")

@v("req-references@1.0")
def test_dangling_refs():
    s = spec(); s.requirements[0].target = "nope"; s.requirements[0].depends_on = ["nope"]; s.evidence[0].requirement_id = "nope"
    assert err(s, "unknown target") and err(s, "depends_on unknown") and err(s, "Evidence 'ev-order-test' references unknown")

@v("req-references@1.0")
def test_ambiguous_target():
    s = spec(); s.data_models[0].id = "place-order"
    assert err(s, "ambiguous target")

@v("req-ownership@1.0")
def test_ownership():
    s = spec(); s.components[0].owns_data = []
    assert err(s, "does not list it in owns_data")
    s = spec(); s.data_models[0].owner = "nobody"
    assert err(s, "unknown owner")

@v("req-lineage@1.0")
def test_unknown_lineage():
    s = spec(); s.data_models[2].derived_from = ["ghost"]
    assert err(s, "unknown data model 'ghost'")

@v("req-layers@1.0")
def test_undeclared_layer():
    s = spec(); s.components[0].layer = "ui"
    assert err(s, "undeclared layer")

@v("req-resolution@1.0")
def test_bad_version():
    s = spec(); s.components[0].requires = ["reserve-inventory@^1.0-beta"]
    assert err(s, "unresolved capability")

@v("req-cli@1.0")
def test_cli(capsys, tmp_path):
    assert main([str(EXAMPLE)]) == 0 and "VALID" in capsys.readouterr().out
    bad = tmp_path / "bad.yaml"; bad.write_text("system: {}")
    assert main([str(bad), "--json"]) == 1 and "schema_errors" in capsys.readouterr().out
    assert main([str(EXAMPLE), "--impact", "order"]) == 0 and "order-stock-projection" in capsys.readouterr().out
    assert main([str(EXAMPLE), "--compat", str(EXAMPLE)]) == 0
    capsys.readouterr()
    assert main([str(bad), "--impact", "order"]) == 1 and "validation error" in capsys.readouterr().out
    assert main([str(EXAMPLE), "--impact", "nope"]) == 1 and "unknown id" in capsys.readouterr().out

@v("req-schema@1.0")
def test_strict_schema():
    d = yaml.safe_load(EXAMPLE.read_text()); d["risks"][0]["residual_acepted"] = True
    with pytest.raises(ValidationError): Spec.model_validate(d)

@v("req-schema@1.0")
def test_empty_criteria():
    with pytest.raises(ValidationError): Requirement(id="r", version="1.0", target="t", criteria=[])

@v("req-layers@1.0")
def test_duplicate_layers():
    s = spec(); s.system.layers.append("domain")
    assert err(s, "Duplicate layer 'domain'")

@v("req-resolution@1.0")
def test_bare_caret():
    s = spec(); s.components[0].requires = ["reserve-inventory@^"]
    assert err(s, "unresolved capability")

@v("req-evidence@1.0")
def test_required_methods():
    s = spec(); s.requirements[1].methods = ["proof", "test"]
    assert err(s, "missing valid verification evidence (test)")

@v("req-evidence@1.0")
def test_test_evidence_needs_binding():
    s = spec(); s.evidence[0].provenance = "other"
    assert err(s, "is not a test bound to 'req-order@1.0'")

@v("req-impact@1.0")
def test_impact_unknown():
    with pytest.raises(ValueError): impact_analysis(spec(), "nope")

def case(name, ref=None, fail=False):
    prop = f'<properties><property name="verifies" value="{ref}"/></properties>' if ref else ""
    return f'<testcase classname="t" name="{name}">{prop}{"<failure/>" if fail else ""}</testcase>'

def reported(tmp_path, *cases):
    s = spec(); s.evidence = [e for e in s.evidence if e.method != "test"]; s.tests = []
    f = tmp_path / "r.xml"; f.write_text(f"<testsuites><testsuite>{''.join(cases)}</testsuite></testsuites>")
    return s, apply_report(s, f)

@v("req-test-binding@1.0")
def test_report_derives_evidence(tmp_path):
    s, errs = reported(tmp_path, case("test_checkout", "req-order@1.0"))
    assert errs == [] and validate_spec(s) == []

@v("req-test-binding@1.0")
def test_report_unbound_test(tmp_path):
    assert any("exactly one requirement" in e for e in reported(tmp_path, case("test_checkout", "req-order@1.0"), case("orphan"))[1])

@v("req-test-binding@1.0")
def test_report_unknown_and_stale_requirement(tmp_path):
    s, _ = reported(tmp_path, case("a", "nope@1.0"), case("b", "req-order@0.1"))
    assert err(s, "Test 't::a' references unknown requirement") and err(s, "Test 't::b' verifies stale requirement version")

@v("req-test-binding@1.0")
def test_report_failure(tmp_path):
    s, errs = reported(tmp_path, case("test_checkout", "req-order@1.0", fail=True))
    assert err(s, "unresolved failing evidence")

@v("req-test-binding@1.0")
def test_report_rejects_handwritten_test_evidence(tmp_path):
    f = tmp_path / "r.xml"; f.write_text("<testsuites/>")
    assert any("derived from the run report" in e for e in apply_report(spec(), f))

@v("req-test-binding@1.0")
def test_report_missing_bound_test(tmp_path):
    f = tmp_path / "r.xml"; f.write_text("<testsuites/>"); s = spec(); s.evidence = [e for e in s.evidence if e.method != "test"]
    assert any("bound but not in the run report" in e for e in apply_report(s, f))

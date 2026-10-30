import pytest
from pydantic import ValidationError
from metamodel import Spec, Requirement, Evidence, validate_spec, load_spec, compare_specs, impact_analysis
from pathlib import Path


def example():
    return load_spec(Path(__file__).parent / "example.yaml")


def test_status_schema_and_defaults():
    s = example()
    for entity in [s.system, *s.capabilities, *s.components, *s.requirements]:
        assert entity.status == "draft"
        for status in ("draft", "specified", "verified", "deprecated"):
            assert type(entity).model_validate({**entity.model_dump(), "status": status}).status == status
        with pytest.raises(ValidationError):
            type(entity).model_validate({**entity.model_dump(), "status": "ready"})
    assert "status" in Spec.model_json_schema()["$defs"]["Requirement"]["properties"]


def test_deprecated_requirement_is_not_a_verification_obligation():
    s = example()
    s.requirements.append(Requirement(id="retired", version="1.0", target=s.system.id,
                                      criteria=["retired obligation"], status="deprecated",
                                      conflicts_with=[s.requirements[0].id]))
    assert validate_spec(s) == []


def test_deprecated_requirement_cannot_cover_capability_or_mitigation():
    s = example()
    s.requirements[1].status = "deprecated"
    errors = validate_spec(s)
    assert any("no associated requirements" in e for e in errors)
    assert any("unverified mitigation" in e for e in errors)


def test_active_requirement_cannot_depend_on_deprecated_requirement():
    s = example()
    s.requirements[0].depends_on = [s.requirements[1].id]
    s.requirements[1].status = "deprecated"
    assert any("depends_on inactive requirement" in e for e in validate_spec(s))


def conflict():
    s = example()
    a, b = s.requirements[:2]
    a.conflicts_with = [b.id]
    a.resolved_by = "resolution"
    s.requirements.append(Requirement(id="resolution", version="1.0", target=s.system.id,
                                      criteria=["reconcile both obligations"], refines=[a.id, b.id]))
    s.evidence.append(Evidence(id="resolution-test", requirement_id="resolution", requirement_version="1.0",
                               method="inspection", passed=True, provenance="fixture:review"))
    return s


def test_verified_resolution_reconciles_both_conflict_directions():
    s = conflict()
    s.requirements[1].conflicts_with = [s.requirements[0].id]
    assert validate_spec(s) == []


@pytest.mark.parametrize("change", ["unknown", "inactive", "failing", "stale", "unrelated", "empty"])
def test_invalid_resolution_cannot_hide_conflict(change):
    s = conflict()
    r = s.requirements[-1]
    if change == "unknown": s.requirements[0].resolved_by = "missing"
    if change == "inactive": r.status = "deprecated"
    if change == "failing": s.evidence[-1].passed = False
    if change == "stale": r.version = "2.0"
    if change == "unrelated": r.refines = []
    if change == "empty": r.criteria = []
    assert any("unresolved conflict" in e for e in validate_spec(s))


def test_self_resolution_is_rejected():
    s = conflict()
    s.requirements[0].resolved_by = s.requirements[0].id
    assert any("unresolved conflict" in e for e in validate_spec(s))


def test_status_does_not_replace_evidence():
    s = example()
    s.requirements[0].status = "verified"
    s.evidence = [e for e in s.evidence if e.requirement_id != s.requirements[0].id]
    assert any("missing valid verification evidence" in e for e in validate_spec(s))


def test_unknown_resolution_reference_is_rejected_without_a_conflict():
    s = example()
    s.requirements[0].resolved_by = "missing"
    assert any("resolved_by unknown requirement 'missing'" in e for e in validate_spec(s))


def test_deprecated_status_allows_capability_removal():
    old, new = example(), example()
    old.capabilities[-1].status = "deprecated"
    new.capabilities.pop()
    assert compare_specs(old, new) == []


def test_resolution_change_invalidates_conflicting_obligations():
    s = conflict()
    s.requirements[1].resolved_by = "resolution"
    result = impact_analysis(s, "resolution")
    assert {"req-order", "req-reserve", "resolution"} <= set(result["requirements"])
    assert {"ev-order-test", "ev-reserve-test"} <= set(result["invalidated_evidence"])

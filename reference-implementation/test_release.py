import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from metamodel import Evidence, Risk, load_spec, main, validate_spec


def release():
    s = load_spec(Path(__file__).parent.parent / "examples/greenfield/verification.yaml")
    entities = [s.system, *s.capabilities, *s.components, *s.requirements]
    for entity in entities: entity.status = "verified"
    targets = {x.id: x.version for x in [s.system, *s.capabilities, *s.components, *s.data_models]}
    for r in s.requirements:
        s.evidence.append(Evidence(id=f"ev-{r.id}", requirement_id=r.id, requirement_version=r.version,
            method="test", passed=True, provenance="fixture:synthetic", subject_id=r.target,
            subject_revision=targets[r.target], timestamp=datetime(2026, 10, 30, tzinfo=timezone.utc), verifier="pytest fixture"))
    return s


def test_complete_release_metadata():
    assert validate_spec(release(), stage="release") == []


@pytest.mark.parametrize("entity", ["system", "capability", "component", "requirement"])
def test_release_requires_verified_entities(entity):
    s = release()
    target = {"system": s.system, "capability": s.capabilities[0], "component": s.components[0], "requirement": s.requirements[0]}[entity]
    target.status = "specified"
    assert any("requires verified status" in e for e in validate_spec(s, stage="release"))


@pytest.mark.parametrize("field", ["subject", "timestamp", "verifier", "provenance"])
def test_release_requires_evidence_metadata(field):
    s = release()
    if field == "subject": s.evidence[0].subject_id = s.evidence[0].subject_revision = None
    else: setattr(s.evidence[0], field, None if field == "timestamp" else " ")
    assert any("release evidence" in e for e in validate_spec(s, stage="release"))


@pytest.mark.parametrize("change", ["missing", "failed", "stale-requirement", "stale-subject"])
def test_release_requires_current_success(change):
    s = release()
    if change == "missing": s.evidence.pop(0)
    if change == "failed": s.evidence[0].passed = False
    if change == "stale-requirement": s.requirements[0].version = "2.0"
    if change == "stale-subject": s.capabilities[0].version = "2.0"
    assert validate_spec(s, stage="release")


def test_optional_mitigation_still_requires_complete_evidence():
    s = release()
    r = next(r for r in s.requirements if r.id == s.risks[0].mitigated_by[0])
    r.mandatory = False
    next(e for e in s.evidence if e.requirement_id == r.id).verifier = None
    assert any("release evidence" in e for e in validate_spec(s, stage="release"))


@pytest.mark.parametrize("expires", ["release", "2000-01-01", "2099-01-01"])
def test_release_rejects_all_waivers(expires):
    s = release()
    s.risks.append(Risk(id="waiver", target=s.components[0].id, treatment="acceptance", residual_accepted=True,
                       waives="context-budget", expires=expires, mitigated_by=[s.requirements[0].id]))
    assert any("waivers are not permitted at release" in e for e in validate_spec(s, stage="release"))


def test_superseded_failures_remain_in_history():
    s = release()
    old = s.evidence[0]
    old.passed = False
    s.evidence.append(Evidence(**{**old.model_dump(), "id": "replacement", "passed": True,
                                 "supersedes": old.id, "supersession_reason": "test setup corrected"}))
    assert validate_spec(s, stage="release") == []
    assert old.passed is False


def test_replacement_cannot_borrow_superseded_metadata():
    s = release()
    old = s.evidence[0]
    s.evidence.append(Evidence(**{**old.model_dump(), "id": "replacement", "verifier": None,
                                 "supersedes": old.id, "supersession_reason": "rerun"}))
    assert any("release evidence" in e for e in validate_spec(s, stage="release"))


def test_stale_history_does_not_block_current_evidence():
    s = release()
    s.evidence.append(Evidence(**{**s.evidence[0].model_dump(), "id": "historical",
                                 "subject_revision": "0.1", "verifier": None, "passed": False}))
    assert validate_spec(s, stage="release") == []


def test_release_checks_transitive_optional_prerequisites():
    s = release()
    first, second, third = s.requirements[:3]
    first.depends_on = [second.id]
    second.depends_on = [third.id]
    second.mandatory = third.mandatory = False
    s.evidence = [e for e in s.evidence if e.requirement_id != third.id]
    assert any(f"{third.id}@{third.version}' missing valid verification" in e for e in validate_spec(s, stage="release"))


@pytest.mark.parametrize("treatment,changes,diagnostic", [
    ("mitigation", {"mitigated_by": []}, "no mitigating requirements"),
    ("mitigation", {"mitigated_by": ["missing"]}, "unknown requirement"),
    ("avoidance", {"residual_accepted": True}, "must not carry residual risk"),
    ("acceptance", {"residual_accepted": False}, "requires residual_accepted"),
    ("transfer", {"transferred_to": " "}, "requires transferred_to"),
    ("transfer", {"residual_accepted": False}, "requires residual_accepted"),
])
def test_release_risk_disposition(treatment, changes, diagnostic):
    s = release()
    s.risks = [Risk(id="risk", target=s.system.id, **{
        "treatment": treatment, "mitigated_by": [s.requirements[0].id],
        "residual_accepted": True, "transferred_to": "counterparty", **changes})]
    assert any(diagnostic in e for e in validate_spec(s, stage="release"))


def test_waiver_fields_are_preserved_in_schema_and_roundtrip():
    from metamodel import Spec
    risk = Risk(id="waiver", target="component", treatment="acceptance", waives="context-budget", expires="release")
    assert Risk.model_validate_json(risk.model_dump_json()).waives == "context-budget"
    assert {"waives", "expires"} <= Spec.model_json_schema()["$defs"]["Risk"]["properties"].keys()


def test_release_cli(tmp_path, capsys):
    path = tmp_path / "release.json"
    path.write_text(release().model_dump_json(), encoding="utf-8")
    assert main([str(path), "--stage", "release", "--json"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["valid"] is True and out["stage"] == "release"


def test_dependency_revisions_freshness_and_validation():
    s = release()
    ev = next(e for e in s.evidence if e.requirement_id == "req-order-func")
    ev.dependency_revisions = {"component:inventory": "1.0", "capability:reserve-inventory": "1.0", "data_model:order": "1.0"}
    assert validate_spec(s, stage="release") == []

    s.data_models[1].version = "2.0"
    errs = validate_spec(s, stage="release")
    assert any("stale dependency revision 'data_model:order@1.0'" in e for e in errs)

    s.data_models[1].version = "1.0"
    ev.dependency_revisions = {"component:ghost": "1.0"}
    assert any("unknown dependency 'component:ghost'" in e for e in validate_spec(s, stage="release"))

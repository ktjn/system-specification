import json
from datetime import datetime, timezone

import pytest
import metamodel
from metamodel import Requirement, Risk, Spec, validate_spec


@pytest.fixture(autouse=True)
def fixed_clock(monkeypatch):
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 10, 30, 12, tzinfo=timezone.utc).astimezone(tz)
    monkeypatch.setattr(metamodel, "datetime", Clock)


def waived(**changes):
    return Spec(system={"id": "system", "version": "1.0"}, capabilities=[], components=[],
                requirements=[Requirement(id="remediate", version="1.0", target="system", criteria=["remove violation"])],
                risks=[Risk(**{"id": "debt", "target": "system", "treatment": "mitigation",
                              "waives": "context-budget", "expires": "2026-10-31", "mitigated_by": ["remediate"], **changes})])


@pytest.mark.parametrize("stage", ["inventory", "discovery", "architecture", "verification", "release"])
def test_expired_waiver_fails_every_stage(stage):
    assert any("waiver expired" in e for e in validate_spec(waived(expires="2026-10-29"), stage=stage))


@pytest.mark.parametrize("expiry", ["2026-10-30", "2026-10-31", "architecture", "verification", "release"])
def test_unexpired_waiver_metadata_at_inventory(expiry):
    assert validate_spec(waived(expires=expiry), stage="inventory") == []


@pytest.mark.parametrize("expiry", ["", " ", "2026-02-30", "20261031", "2026-W44-5", "2026-10-31T00:00:00Z", "inventory", "discovery", "unknown"])
def test_invalid_expiry_is_rejected(expiry):
    assert any("invalid waiver expiry" in e for e in validate_spec(waived(expires=expiry), stage="inventory"))


@pytest.mark.parametrize("bound,stage", [("architecture", "architecture"), ("architecture", "verification"),
                                        ("verification", "verification"), ("verification", "release"), ("release", "release")])
def test_stage_expiry_applies_on_entry(bound, stage):
    assert any("waiver expired" in e for e in validate_spec(waived(expires=bound), stage=stage))


@pytest.mark.parametrize("changes,diagnostic", [
    ({"waives": " "}, "non-empty waiver name"),
    ({"waives": None}, "expires requires waives"),
    ({"expires": None}, "waiver requires expires"),
    ({"treatment": "transfer"}, "waiver requires mitigation or acceptance"),
    ({"treatment": "avoidance"}, "waiver requires mitigation or acceptance"),
    ({"treatment": "acceptance"}, "waiver acceptance requires residual_accepted"),
    ({"mitigated_by": []}, "waiver requires remediation requirements"),
    ({"mitigated_by": ["missing"]}, "waiver references unknown remediation"),
    ({"target": "missing"}, "waiver target must resolve uniquely"),
])
def test_waiver_metadata_rejected_at_inventory(changes, diagnostic):
    assert any(diagnostic in e for e in validate_spec(waived(**changes), stage="inventory"))


@pytest.mark.parametrize("change", ["deprecated", "empty"])
def test_remediation_must_be_active_and_have_criteria(change):
    s = waived()
    if change == "deprecated": s.requirements[0].status = "deprecated"
    else: s.requirements[0].criteria = [" "]
    assert any("waiver requires active remediation with criteria" in e for e in validate_spec(s, stage="inventory"))


def test_acceptance_waiver_and_normal_risk():
    assert validate_spec(waived(treatment="acceptance", residual_accepted=True), stage="inventory") == []
    assert validate_spec(waived(waives=None, expires=None), stage="inventory") == []


def test_waiver_needs_explicit_stage():
    assert any("waiver requires explicit validation stage" in e for e in validate_spec(waived()))


def test_expired_waiver_cli_is_metadata_error(tmp_path, capsys):
    path = tmp_path / "expired.json"
    path.write_text(waived(expires="2000-01-01").model_dump_json(), encoding="utf-8")
    assert metamodel.main([str(path), "--stage", "inventory", "--json"]) == 1
    result = json.loads(capsys.readouterr().out)
    assert result == {"valid": False, "stage": "inventory", "errors": ["Risk 'debt': waiver expired on 2000-01-01"]}


def test_metadata_does_not_grant_budget_exemption():
    from test_architecture import architecture
    s = architecture()
    s.system.context_budget.max_provides = 0
    s.requirements, s.risks = waived().requirements, waived(expires="release").risks
    s.requirements[0].target = s.risks[0].target = s.components[0].id
    assert any("exceeds context budget" in e for e in validate_spec(s, stage="architecture"))

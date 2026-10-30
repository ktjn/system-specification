import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from metamodel import Evidence, Requirement, load_spec, main, validate_spec

CATEGORIES = ("functional", "semantic", "contract", "serialization", "concurrency",
              "performance", "scalability", "resilience", "security", "observability")


def verification():
    s = load_spec(Path(__file__).parent.parent / "examples/greenfield/architecture.yaml")
    for cap in s.capabilities:
        for category in CATEGORIES:
            s.requirements.append(Requirement(id=f"{cap.id}-{category}", version="1.0", status="specified",
                target=cap.id, category=category, criteria=[f"Acceptance criterion for {category}"],
                kind="functional" if category in CATEGORIES[:5] else "non-functional"))
    return s


def test_verification_does_not_require_passing_release_evidence():
    s = verification()
    s.evidence.append(Evidence(id="initial-failure", requirement_id=s.requirements[0].id,
                              requirement_version="1.0", method="test", passed=False, provenance="fixture"))
    assert validate_spec(s, stage="verification") == []
    assert any("failing evidence" in e for e in validate_spec(s))


@pytest.mark.parametrize("change, diagnostic", [
    ("category", "missing verification category"), ("unknown-category", "missing category"),
    ("kind", "category requires"), ("status", "requires specified status"),
    ("criteria", "empty acceptance criteria"), ("target", "unknown target"),
    ("relation", "depends_on unknown"), ("cycle", "Requirement cycle"),
    ("conflict", "unresolved conflict"), ("architecture", "context budget"),
    ("inactive", "missing verification category"),
])
def test_verification_rejects_incomplete_obligations(change, diagnostic):
    s = verification()
    r = s.requirements[0]
    if change == "category": s.requirements.pop()
    if change == "unknown-category": r.category = None
    if change == "kind": r.kind = "non-functional"
    if change == "status": r.status = "draft"
    if change == "criteria": r.criteria = [" "]
    if change == "target": r.target = "missing"
    if change == "relation": r.depends_on = ["missing"]
    if change == "cycle": r.depends_on = [s.requirements[1].id]; s.requirements[1].refines = [r.id]
    if change == "conflict": r.conflicts_with = [s.requirements[1].id]
    if change == "architecture": s.system.context_budget.max_provides = 0
    if change == "inactive": r.status = "deprecated"
    assert any(diagnostic in e for e in validate_spec(s, stage="verification"))


def test_category_is_a_schema_enum():
    data = verification().requirements[0].model_dump()
    with pytest.raises(ValidationError): Requirement.model_validate({**data, "category": "typo"})


def test_categories_cannot_be_borrowed_from_unrelated_capabilities():
    s = verification()
    s.requirements = [r for r in s.requirements if r.target == s.capabilities[0].id or r.category == "functional"]
    assert any("reserve-inventory" in e and "missing verification category" in e for e in validate_spec(s, stage="verification"))


def test_system_and_provider_requirements_cover_their_capabilities():
    s = verification()
    for r in s.requirements:
        if r.category == "security": r.target = s.system.id
        if r.category == "observability": r.target = "checkout" if r.target == "place-order" else "inventory"
    assert validate_spec(s, stage="verification") == []


def test_interface_data_requirements_cover_their_consuming_capability():
    s = verification()
    by_id = {c.id: c for c in s.capabilities}
    for r in s.requirements:
        if r.category == "serialization": r.target = by_id[r.target].interface.request
    assert validate_spec(s, stage="verification") == []


def test_unrelated_data_does_not_supply_capability_coverage():
    s = verification()
    for r in s.requirements:
        if r.category == "serialization": r.target = "order-stock-projection"
    assert any("missing verification category 'serialization'" in e for e in validate_spec(s, stage="verification"))


def test_conflict_resolution_still_requires_evidence():
    s = verification()
    a, b = s.requirements[:2]
    a.conflicts_with, a.resolved_by = [b.id], "resolution"
    s.requirements.append(Requirement(id="resolution", version="1.0", status="specified", target=s.system.id,
        category="semantic", criteria=["Reconcile conflicting obligations"], refines=[a.id, b.id]))
    assert any("unresolved conflict" in e for e in validate_spec(s, stage="verification"))
    s.evidence.append(Evidence(id="resolution-proof", requirement_id="resolution", requirement_version="1.0",
                              method="inspection", passed=True, provenance="fixture:review"))
    assert validate_spec(s, stage="verification") == []


def test_verification_cli(tmp_path, capsys):
    path = tmp_path / "verification.json"
    path.write_text(verification().model_dump_json(), encoding="utf-8")
    assert main([str(path), "--stage", "verification", "--json"]) == 0
    assert json.loads(capsys.readouterr().out) == {"valid": True, "errors": [], "stage": "verification"}

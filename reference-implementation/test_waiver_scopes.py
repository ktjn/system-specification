import pytest
from metamodel import Requirement, Risk, validate_spec
from test_architecture import architecture
from test_verification import verification


def waive(s, kind, target, **changes):
    rid = f"remediate-{kind}-{target}"
    s.requirements.append(Requirement(id=rid, version="1.0", status="specified", category="functional",
                                     target=target, criteria=[f"Remove {kind} on {target}"]))
    s.risks.append(Risk(**{"id": f"risk-{rid}", "target": target, "treatment": "mitigation",
                          "waives": kind, "expires": "release", "mitigated_by": [rid], **changes}))


@pytest.mark.parametrize("kind,diagnostic", [
    ("context-budget", "context budget"), ("layer-violation", "layer violation"),
    ("shared-data-ownership", "also claimed"), ("unverified-capability", "empty contract"),
])
def test_scoped_architecture_waiver(kind, diagnostic):
    s = architecture()
    target = s.components[0].id
    if kind == "context-budget": s.components[0].provides *= 6
    if kind == "layer-violation": s.components[0].layer = "infrastructure"
    if kind == "shared-data-ownership":
        target = "order"
        s.components[1].owns_data.append(target)
    if kind == "unverified-capability":
        target = s.capabilities[0].id
        s.capabilities[0].status = "draft"
        s.capabilities[0].invariants = []
    assert any(diagnostic in e for e in validate_spec(s, stage="architecture"))
    waive(s, kind, target)
    assert validate_spec(s, stage="architecture") == []


def test_cycle_requires_waivers_for_all_participants():
    s = architecture()
    s.system.layers = []
    s.components[1].requires = [s.capabilities[0].id]
    waive(s, "dependency-cycle", s.components[0].id)
    assert any("Dependency cycle" in e for e in validate_spec(s, stage="architecture"))
    waive(s, "dependency-cycle", s.components[1].id)
    assert validate_spec(s, stage="architecture") == []


def test_overlapping_cycles_cannot_hide_unwaived_participant():
    s = architecture()
    s.system.layers = []
    a, b = s.components
    c = a.model_copy(deep=True, update={"id": "third", "owns_data": [], "provides": ["third-cap"], "requires": [b.provides[0]]})
    s.components.append(c)
    s.capabilities.append(s.capabilities[0].model_copy(deep=True, update={"id": "third-cap"}))
    a.requires.append("third-cap")
    b.requires = [a.provides[0]]
    waive(s, "dependency-cycle", a.id)
    waive(s, "dependency-cycle", b.id)
    assert any("Dependency cycle" in e and "third" in e for e in validate_spec(s, stage="architecture"))


def test_missing_category_waiver_is_capability_scoped():
    s = verification()
    s.requirements = [r for r in s.requirements if r.category != "security"]
    waive(s, "missing-verification-category", s.capabilities[0].id)
    errors = validate_spec(s, stage="verification")
    assert not any(f"'{s.capabilities[0].id}' has missing verification category" in e for e in errors)
    assert any(f"'{s.capabilities[1].id}' has missing verification category" in e for e in errors)
    waive(s, "missing-verification-category", s.capabilities[1].id)
    assert validate_spec(s, stage="verification") == []


@pytest.mark.parametrize("kind,target", [("unknown", "checkout"), ("context-budget", "order"),
    ("shared-data-ownership", "checkout"), ("unverified-capability", "checkout"),
    ("missing-verification-category", "checkout"), ("layer-violation", "commerce-system"),
    ("dependency-cycle", "place-order")])
def test_unknown_or_wrongly_scoped_waiver_rejected_even_at_inventory(kind, target):
    s = architecture()
    waive(s, kind, target)
    assert any("waiver constraint" in e for e in validate_spec(s, stage="inventory"))


@pytest.mark.parametrize("changes", [{"expires": "2000-01-01"}, {"mitigated_by": []}, {"treatment": "transfer"}])
def test_invalid_waivers_grant_no_exemption(changes):
    s = architecture()
    s.components[0].provides *= 6
    waive(s, "context-budget", s.components[0].id, **changes)
    assert any("context budget" in e for e in validate_spec(s, stage="architecture"))


def test_waiver_does_not_hide_reference_or_interface_errors():
    s = architecture()
    s.capabilities[0].status = "draft"
    s.capabilities[0].invariants = []
    s.capabilities[0].interface = None
    s.components[0].requires.append("unknown")
    waive(s, "unverified-capability", s.capabilities[0].id)
    errors = validate_spec(s, stage="architecture")
    assert any("missing interface" in e for e in errors)
    assert any("unresolved capability 'unknown'" in e for e in errors)
    assert not any("empty contract" in e for e in errors)


def test_ownership_waiver_cannot_hide_unknown_owner_or_classification():
    s = architecture()
    s.data_models[0].owner = "unknown"
    s.data_models[-1].classification = "public"
    waive(s, "shared-data-ownership", s.data_models[0].id)
    assert any("unknown owner" in e for e in validate_spec(s, stage="architecture"))
    assert any("classification propagation" in e for e in validate_spec(s, stage="architecture"))


def test_release_ignores_all_exemptions():
    from test_release import release
    s = release()
    s.components[0].provides *= 6
    waive(s, "context-budget", s.components[0].id)
    errors = validate_spec(s, stage="release")
    assert any("waivers are not permitted" in e for e in errors)
    assert any("context budget" in e for e in errors)

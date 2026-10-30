from pathlib import Path

import pytest
from pydantic import ValidationError
from metamodel import Evidence, load_spec, validate_spec


def example():
    return load_spec(Path(__file__).parent / "example.yaml")


def test_subject_revision_change_invalidates_evidence():
    s = example()
    e = s.evidence[0]
    e.subject_id, e.subject_revision = "place-order", "1.0"
    assert validate_spec(s) == []
    s.capabilities[0].version = "2.0"
    assert any("stale subject revision" in err for err in validate_spec(s))
    assert any("missing valid verification evidence" in err for err in validate_spec(s))


def test_evidence_must_describe_requirement_target():
    s = example()
    e = s.evidence[0]
    e.subject_id, e.subject_revision = "inventory", "1.0"
    assert any("does not match requirement target" in err for err in validate_spec(s))


def test_subject_fields_are_paired():
    e = example().evidence[0].model_dump()
    with pytest.raises(ValidationError):
        Evidence.model_validate({**e, "subject_id": "place-order"})
    with pytest.raises(ValidationError):
        Evidence.model_validate({**e, "subject_revision": "1.0"})


def test_model_check_requires_explicit_bounds():
    e = example().evidence[0].model_dump()
    for bounds in (None, "", "  "):
        with pytest.raises(ValidationError):
            Evidence.model_validate({**e, "method": "model-check", "bounds": bounds})
    assert Evidence.model_validate({**e, "method": "model-check", "bounds": "3 nodes, 10 steps"}).method == "model-check"


def supersession():
    s = example()
    e = s.evidence[0]
    e.passed = False
    s.evidence.append(Evidence(**{**e.model_dump(), "id": "replacement", "passed": True,
                                 "supersedes": e.id, "supersession_reason": "rerun after correcting test setup"}))
    return s


def test_explicit_supersession_preserves_failed_history():
    s = supersession()
    assert validate_spec(s) == []
    assert s.evidence[0].passed is False


@pytest.mark.parametrize("change", ["missing", "self", "other-requirement", "other-version", "other-subject", "failed"])
def test_invalid_supersession_cannot_hide_failure(change):
    s = supersession()
    new = s.evidence[-1]
    if change == "missing": new.supersedes = "missing"
    if change == "self": new.supersedes = new.id
    if change == "other-requirement": new.requirement_id = "req-reserve"
    if change == "other-version": new.requirement_version = "2.0"
    if change == "other-subject": new.subject_id, new.subject_revision = "place-order", "1.0"
    if change == "failed": new.passed = False
    errors = validate_spec(s)
    assert any("supersession" in err for err in errors)
    assert any("unresolved failing evidence" in err for err in errors)


def test_supersession_requires_reason():
    e = example().evidence[0].model_dump()
    with pytest.raises(ValidationError):
        Evidence.model_validate({**e, "supersedes": "old"})


def test_supersession_cycle_is_rejected():
    s = supersession()
    s.evidence[0].passed = True
    s.evidence[0].supersedes = "replacement"
    s.evidence[0].supersession_reason = "cycle"
    assert any("supersession cycle" in err for err in validate_spec(s))


def test_fresh_revision_retains_stale_history():
    s = example()
    e = s.evidence[0]
    e.subject_id, e.subject_revision = "place-order", "1.0"
    s.capabilities[0].version = "2.0"
    s.evidence.append(Evidence(**{**e.model_dump(), "id": "fresh", "subject_revision": "2.0"}))
    assert validate_spec(s) == []


def test_stale_history_does_not_hide_dangling_supersession():
    s = example()
    e = s.evidence[0]
    e.subject_id, e.subject_revision = "place-order", "0.9"
    e.supersedes, e.supersession_reason = "missing", "correction"
    s.evidence.append(Evidence(**{**e.model_dump(), "id": "fresh", "subject_revision": "1.0", "supersedes": None}))
    assert any("invalid supersession" in err for err in validate_spec(s))


def test_timestamp_requires_timezone():
    e = example().evidence[0].model_dump()
    with pytest.raises(ValidationError):
        Evidence.model_validate({**e, "timestamp": "2026-10-30T10:00:00"})
    assert Evidence.model_validate({**e, "timestamp": "2026-10-30T10:00:00Z", "verifier": "pytest"}).timestamp.utcoffset().total_seconds() == 0

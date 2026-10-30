from pathlib import Path

import pytest
from metamodel import load_spec, validate_spec

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = {
    "examples/brownfield/inventory.yaml": "inventory",
    "examples/brownfield/architecture.yaml": "architecture",
    "examples/brownfield/verification.yaml": "verification",
    "examples/greenfield/discovery.yaml": "discovery",
    "examples/greenfield/architecture.yaml": "architecture",
    "examples/greenfield/verification.yaml": "verification",
    "examples/brownfield/old.yaml": None,
    "examples/brownfield/spec.yaml": None,
    "examples/greenfield/spec.yaml": None,
}


def test_every_track_snapshot_has_a_validation_profile():
    assert {p.relative_to(ROOT).as_posix() for p in (ROOT / "examples").rglob("*.yaml")} == set(EXAMPLES)


@pytest.mark.parametrize("path, stage", EXAMPLES.items(), ids=EXAMPLES)
def test_track_snapshot(path, stage):
    assert validate_spec(load_spec(ROOT / path), stage=stage) == []


def test_brownfield_snapshots_require_scoped_waivers_and_expire_at_next_gate():
    for name, stage, next_stage in [("architecture", "architecture", "verification"), ("verification", "verification", "release")]:
        s = load_spec(ROOT / f"examples/brownfield/{name}.yaml")
        assert any("waiver expired" in e for e in validate_spec(s, stage=next_stage))
        s.risks = []
        assert validate_spec(s, stage=stage)

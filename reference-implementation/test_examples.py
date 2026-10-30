from pathlib import Path

import pytest
from metamodel import load_spec, validate_spec

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = {
    "examples/brownfield/inventory.yaml": "inventory",
    "examples/greenfield/discovery.yaml": "discovery",
    "examples/greenfield/architecture.yaml": "architecture",
    "examples/brownfield/old.yaml": None,
    "examples/brownfield/spec.yaml": None,
    "examples/greenfield/spec.yaml": None,
}


def test_every_track_snapshot_has_a_validation_profile():
    assert {p.relative_to(ROOT).as_posix() for p in (ROOT / "examples").rglob("*.yaml")} == set(EXAMPLES)


@pytest.mark.parametrize("path, stage", EXAMPLES.items(), ids=EXAMPLES)
def test_track_snapshot(path, stage):
    assert validate_spec(load_spec(ROOT / path), stage=stage) == []

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent
CASES = [
    ("duplicate-id", "Duplicate requirement id 'req-service'"),
    ("ambiguous-provider", "Component 'client' has ambiguous providers ['provider-a', 'provider-b'] for 'service'; add a binding"),
    ("failing-evidence", "Requirement 'req-service@1.0' has unresolved failing evidence"),
    ("unknown-mitigation", "Risk 'risk-service' references unknown requirement 'missing'"),
    ("requirement-cycle", "Requirement cycle: req-a -> req-b -> req-a"),
    ("ownership", "DataModel 'record' owner 'provider' does not list it in owns_data"),
    ("classification", "DataModel 'projection' violates classification propagation from 'record'"),
    ("undeclared-layer", "Component 'provider' has undeclared layer 'unknown'"),
    ("schema", "system.version"),
]


@pytest.mark.parametrize("name, diagnostic", CASES, ids=[name for name, _ in CASES])
def test_invalid_fixture(name, diagnostic):
    fixture = ROOT / "tests" / "invalid" / f"{name}.yaml"
    assert fixture.is_file(), f"Missing fixture: {fixture}"
    result = subprocess.run(
        [sys.executable, str(ROOT / "metamodel.py"), str(fixture), "--json"],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert not result.stderr
    output = json.loads(result.stdout)
    assert output["valid"] is False
    if name == "schema":
        assert "errors" not in output
        assert len(output["schema_errors"]) == 1
        assert diagnostic in output["schema_errors"][0]
    else:
        assert "schema_errors" not in output
        assert output["errors"] == [diagnostic]

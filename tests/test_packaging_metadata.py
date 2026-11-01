import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_root_pyproject_metadata():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    proj = data["project"]
    assert proj["name"] == "system-spec-ref"
    assert proj["requires-python"] == ">=3.12"
    assert proj["scripts"]["system-spec"] == "system_spec_ref.cli:run"

    deps = proj["dependencies"]
    assert any(d.startswith("pydantic") for d in deps)
    assert any(d.startswith("pyyaml") for d in deps)
    assert not any("pytest" in d for d in deps)

    dev = data["dependency-groups"]["dev"]
    assert any(d.startswith("pytest") for d in dev)

    ref = tomllib.loads((ROOT / "reference-implementation" / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert proj["version"] == ref["version"]
    assert proj["requires-python"] == ref["requires-python"]


def test_release_metadata_and_wiring_docs():
    proj = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert proj["license"] == "MIT" and proj["license-files"] == ["LICENSE"]
    assert (ROOT / proj["readme"]).is_file()
    assert proj["urls"]["Source"].startswith("https://github.com/")
    assert "Copyright" in (ROOT / "LICENSE").read_text(encoding="utf-8")

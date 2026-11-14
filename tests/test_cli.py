import json
import pytest
from pathlib import Path

from system_spec_ref import cli

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / "reference-implementation" / "example.yaml"


def test_default_validates_bundled_example_outside_checkout(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert cli.run([]) == 0
    assert "VALID" in capsys.readouterr().out


def test_version(capsys):
    assert cli.run(["--version"]) == 0
    assert capsys.readouterr().out.strip()


def test_explicit_path_resolves_against_caller_cwd(tmp_path, monkeypatch, capsys):
    spec = tmp_path / "spec.yaml"
    spec.write_text(EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    assert cli.run(["spec.yaml"]) == 0
    assert "VALID" in capsys.readouterr().out


def test_spec_literally_named_export_stays_reachable(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "export").write_text(EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8")
    assert cli.run(["./export"]) == 0
    assert "VALID" in capsys.readouterr().out


@pytest.mark.parametrize("flag, name", [("--schema", "schema.json"), ("--fragment-schema", "fragment.schema.json"), ("--return-schema", "handoff-return.schema.json")])
def test_schema_output_is_byte_identical_to_the_bundled_file(capsys, flag, name):
    assert cli.run([flag]) == 0
    bundled = (ROOT / "reference-implementation" / name).read_bytes()
    assert capsys.readouterr().out.encode() == bundled and b"\r" not in bundled  # one hash: of the file and of the command's output


def test_json_exit_codes_preserved(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    bad = tmp_path / "bad.yaml"
    bad.write_text("system: {}", encoding="utf-8")
    assert cli.run(["bad.yaml", "--json"]) == 1
    assert "schema_errors" in capsys.readouterr().out

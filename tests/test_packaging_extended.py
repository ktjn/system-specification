import tomllib
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import pytest

from system_spec_ref import cli
from system_spec_ref.cli import ExportError, export_toolkit

ROOT = Path(__file__).resolve().parent.parent


def test_export_diagnostics_no_secret_leak(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("SECRET_TOKEN_12345", "super_secret_value")
    dest = tmp_path / "already_exists"
    dest.mkdir()
    res = cli.run(["export", str(dest)])
    assert res == 1
    err = capsys.readouterr().err
    assert "already_exists" in err
    assert "super_secret_value" not in err
    assert "SECRET_TOKEN" not in err


def test_synthetic_large_inventory_export(tmp_path, monkeypatch):
    import system_spec_ref.cli as cli_mod

    import io
    class FakeEntry:
        def __init__(self, content: bytes):
            self._content = content
        def is_symlink(self):
            return False
        def is_dir(self):
            return False
        def open(self, mode="rb"):
            return io.BytesIO(self._content)

    def synthetic_iter(root, prefix=""):
        for i in range(100):
            yield f"synthetic/file_{i}.txt", FakeEntry(b"synthetic content " * 50)

    monkeypatch.setattr(cli_mod, "_iter_resource_files", synthetic_iter)
    dest = tmp_path / "synthetic_export"
    export_toolkit(dest)
    assert (dest / "synthetic" / "file_0.txt").is_file()
    assert (dest / "synthetic" / "file_99.txt").is_file()
    assert len(list((dest / "synthetic").iterdir())) == 100


def test_clean_wheel_outside_checkout(tmp_path):
    wheel = next((ROOT / "dist").glob("*.whl"), None)
    if not wheel:
        pytest.skip("wheel not built")
    venv_dir = tmp_path / "clean_env"
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    pip_bin = str(venv_dir / ("Scripts" if os.name == "nt" else "bin") / ("pip.exe" if os.name == "nt" else "pip"))
    cli_bin = str(venv_dir / ("Scripts" if os.name == "nt" else "bin") / ("system-spec.exe" if os.name == "nt" else "system-spec"))
    subprocess.run([pip_bin, "install", str(wheel)], check=True)

    # Validate outside checkout
    r = subprocess.run([cli_bin, "--version"], capture_output=True, text=True, check=True)
    assert r.stdout.strip() == tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]

    r2 = subprocess.run([cli_bin], capture_output=True, text=True, cwd=str(tmp_path), check=True)
    assert "VALID" in r2.stdout

    exp_dest = tmp_path / "toolkit_installed"
    r3 = subprocess.run([cli_bin, "export", str(exp_dest)], capture_output=True, text=True, cwd=str(tmp_path), check=True)
    assert "exported toolkit" in r3.stdout
    assert (exp_dest / "README.md").is_file()

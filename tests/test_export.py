import builtins
import os
import threading

import pytest

from system_spec_ref.cli import ExportError, _validate_entry, export_toolkit


def test_export_creates_full_tree(tmp_path):
    dest = tmp_path / "toolkit-out"
    assert export_toolkit(dest) == dest
    assert (dest / "README.md").is_file()
    assert (dest / "reference-implementation" / "metamodel.py").is_file()
    assert (dest / ".github" / "skills" / "tla" / "SKILL.md").is_file()
    assert (dest / ".github" / "workflows" / "metamodel.yml").is_file()


def test_export_rejects_existing_directory_destination(tmp_path):
    dest = tmp_path / "exists"
    dest.mkdir()
    with pytest.raises(ExportError):
        export_toolkit(dest)
    assert list(dest.iterdir()) == []


def test_export_rejects_existing_file_destination(tmp_path):
    dest = tmp_path / "file.txt"
    dest.write_text("x", encoding="utf-8")
    with pytest.raises(ExportError):
        export_toolkit(dest)
    assert dest.read_text(encoding="utf-8") == "x"


@pytest.mark.skipif(os.name == "nt", reason="creating dangling symlinks needs elevated privilege on Windows")
def test_export_rejects_dangling_symlink_destination(tmp_path):
    dest = tmp_path / "link"
    dest.symlink_to(tmp_path / "nonexistent-target")
    with pytest.raises(ExportError):
        export_toolkit(dest)


def test_export_leaves_no_partial_destination_on_copy_failure(tmp_path, monkeypatch):
    dest = tmp_path / "broken"
    import system_spec_ref.cli as cli_mod

    original_open = builtins.open
    calls = {"n": 0}

    def flaky_open(path, mode="r", *a, **kw):
        if "w" in mode:
            calls["n"] += 1
            if calls["n"] == 3:
                raise OSError("synthetic disk failure")
        return original_open(path, mode, *a, **kw)

    monkeypatch.setattr(cli_mod, "open", flaky_open, raising=False)
    with pytest.raises(ExportError):
        export_toolkit(dest)
    assert not dest.exists()
    leftovers = [p for p in tmp_path.iterdir() if p.name.startswith(f".{dest.name}.staging-")]
    assert leftovers == []


def test_export_race_exactly_one_winner(tmp_path):
    dest = tmp_path / "race"
    results = []

    def attempt():
        try:
            results.append(("ok", export_toolkit(dest)))
        except ExportError as e:
            results.append(("err", str(e)))

    t1, t2 = threading.Thread(target=attempt), threading.Thread(target=attempt)
    t1.start(); t2.start(); t1.join(); t2.join()
    assert sum(1 for r in results if r[0] == "ok") == 1
    assert sum(1 for r in results if r[0] == "err") == 1
    assert dest.is_dir() and (dest / "README.md").is_file()


def test_validate_entry_rejects_absolute_path():
    with pytest.raises(ExportError):
        _validate_entry("/etc/passwd")


def test_validate_entry_rejects_parent_traversal():
    with pytest.raises(ExportError):
        _validate_entry("../escape.txt")


def test_export_includes_license_and_wiring_guide(tmp_path):
    dest = export_toolkit(tmp_path / "out")
    assert "MIT License" in (dest / "LICENSE").read_text(encoding="utf-8")
    assert "AGENTS.md" in (dest / "WIRING.md").read_text(encoding="utf-8")


def test_export_skips_bytecode_caches(tmp_path):
    from system_spec_ref.cli import _iter_resource_files
    (tmp_path / "pkg" / "__pycache__").mkdir(parents=True)
    (tmp_path / "pkg" / "a.py").write_text("x = 1")
    (tmp_path / "pkg" / "__pycache__" / "a.cpython-312.pyc").write_bytes(b"\0")
    (tmp_path / "b.pyc").write_bytes(b"\0")
    assert [rel for rel, _ in _iter_resource_files(tmp_path)] == ["pkg/a.py"]

"""Shared sync logic for hatch_build.py and local dev/test setup.

Single source of truth: `reference-implementation/metamodel.py` and the files
listed in `toolkit_manifest.txt`. Nothing here is a second implementation of
the validator; it only copies bytes.
"""
from __future__ import annotations
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
MANIFEST = ROOT / "toolkit_manifest.txt"
PACKAGE = ROOT / "system_spec_ref"


def manifest_entries() -> list[str]:
    lines = MANIFEST.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


def sync_runtime_module() -> None:
    shutil.copyfile(ROOT / "reference-implementation" / "metamodel.py", PACKAGE / "metamodel.py")


def sync_toolkit_snapshot() -> None:
    dest_root = PACKAGE / "toolkit"
    if dest_root.exists():
        shutil.rmtree(dest_root)
    for rel in manifest_entries():
        src = ROOT / rel
        dst = dest_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)


def sync_all() -> None:
    sync_runtime_module()
    sync_toolkit_snapshot()


if __name__ == "__main__":
    sync_all()

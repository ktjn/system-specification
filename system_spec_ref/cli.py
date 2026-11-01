from __future__ import annotations
import argparse, importlib.resources, os, shutil, sys, tempfile
from pathlib import Path

from . import metamodel

PACKAGE = "system_spec_ref"
DIST_NAME = "system-spec-ref"


class ExportError(Exception):
    pass


def _iter_resource_files(root, prefix: str = ""):
    for entry in sorted(root.iterdir(), key=lambda e: e.name):
        if entry.name == "__pycache__" or entry.name.endswith(".pyc"): continue  # pip's install-time bytecode is not part of the toolkit
        rel = f"{prefix}{entry.name}"
        if entry.is_dir():
            yield from _iter_resource_files(entry, rel + "/")
        else:
            yield rel, entry


def _validate_entry(rel: str) -> None:
    if rel.startswith("/") or Path(rel).is_absolute():
        raise ExportError(f"unsafe resource entry (absolute path): {rel}")
    if ".." in Path(rel).parts:
        raise ExportError(f"unsafe resource entry (parent traversal): {rel}")


def _cleanup_stage(stage: Path) -> None:
    try:
        shutil.rmtree(stage)
    except OSError as e:
        print(f"warning: failed to clean up staging directory {stage}: {e}", file=sys.stderr)


def export_toolkit(destination: str | Path, *, package: str = PACKAGE) -> Path:
    dest = Path(destination)
    if not dest.is_absolute():
        dest = Path.cwd() / dest
    if dest.is_symlink() or dest.exists():
        raise ExportError(f"destination already exists: {dest}")
    parent = dest.parent
    if not parent.is_dir():
        raise ExportError(f"parent directory does not exist: {parent}")

    toolkit_root = importlib.resources.files(package) / "toolkit"
    entries = []
    for rel, entry in _iter_resource_files(toolkit_root):
        if hasattr(entry, "is_symlink") and entry.is_symlink():
            raise ExportError(f"unsafe resource entry (symlink): {rel}")
        _validate_entry(rel)
        entries.append((rel, entry))

    stage = Path(tempfile.mkdtemp(prefix=f".{dest.name}.staging-", dir=parent))
    stage_resolved = str(stage.resolve())
    try:
        for rel, entry in entries:
            dest_path = stage / rel
            if not str(dest_path.resolve()).startswith(stage_resolved + os.sep):
                raise ExportError(f"unsafe resource entry escapes staging area: {rel}")
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with entry.open("rb") as src, open(dest_path, "wb") as out:
                shutil.copyfileobj(src, out)
    except Exception as e:
        _cleanup_stage(stage)
        raise ExportError(str(e)) from e

    if dest.is_symlink() or dest.exists():
        _cleanup_stage(stage)
        raise ExportError(f"destination already exists: {dest}")
    try:
        os.mkdir(dest)
    except OSError as e:
        _cleanup_stage(stage)
        raise ExportError(f"destination already exists: {dest}") from e

    try:
        for child in stage.iterdir():
            shutil.move(str(child), str(dest / child.name))
        stage.rmdir()
    except Exception as e:
        raise ExportError(f"publish failed after claiming destination {dest}: {e}") from e
    return dest


def _run_export(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="system-spec export", description="Export an offline toolkit snapshot.")
    ap.add_argument("destination")
    a = ap.parse_args(argv)
    try:
        dest = export_toolkit(a.destination)
    except ExportError as e:
        print(f"export failed: {e}", file=sys.stderr)
        return 1
    print(f"exported toolkit {metamodel.package_version(DIST_NAME)} to {dest}")
    print(f"next: read {dest / 'WIRING.md'} to wire it into your project and agents")
    return 0


def _run_validate(argv: list[str]) -> int:
    version = metamodel.package_version(DIST_NAME)
    resource = importlib.resources.files(PACKAGE) / "toolkit" / "reference-implementation" / "example.yaml"
    with importlib.resources.as_file(resource) as default_path:
        return metamodel.main(argv, default_spec=default_path, version=version)


def run(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "export":
        return _run_export(argv[1:])
    return _run_validate(argv)


if __name__ == "__main__":
    sys.exit(run())

import subprocess

from build_support import PACKAGE, ROOT, manifest_entries, sync_all

# Packaging/build scaffolding is tracked in git but is deliberately not part of the
# offline toolkit snapshot (see PACKAGING.md's installed-layout diagram): only
# docs/examples/archive/reference-implementation/skills/workflow ship to end users.
NOT_TOOLKIT_CONTENT = {"AGENTS.md", "toolkit_manifest.txt", "build_support.py", "release_support.py", "hatch_build.py", "pyproject.toml", ".gitignore", "PYPI.md", "RELEASING.md", "uv.lock", ".github/workflows/publish.yml", ".github/workflows/package.yml", ".github/dependabot.yml", ".github/ISSUE_TEMPLATE/feedback.md"}
NOT_TOOLKIT_PREFIXES = ("system_spec_ref/", "tests/")


def test_manifest_matches_git_tracked_files_minus_packaging_scaffolding():
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.splitlines()
    expected = sorted(
        p for p in tracked
        if p not in NOT_TOOLKIT_CONTENT and not p.startswith(NOT_TOOLKIT_PREFIXES)
    )
    assert sorted(manifest_entries()) == expected


def test_sync_produces_byte_identical_snapshot():
    sync_all()
    assert (PACKAGE / "metamodel.py").read_bytes() == (ROOT / "reference-implementation" / "metamodel.py").read_bytes()
    for rel in manifest_entries():
        assert (PACKAGE / "toolkit" / rel).read_bytes() == (ROOT / rel).read_bytes()

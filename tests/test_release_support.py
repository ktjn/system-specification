import json, subprocess
import pytest
import release_support as rs

SCHEMA = json.dumps({"properties": {"system": {}}, "$defs": {"Evidence": {"properties": {"id": {}, "run": {}}}}})
CODE = '    "REF-01": ("inventory", None, "x"),\n    ap.add_argument("--bind", nargs="*")\n'


def test_surface_collects_invariants_options_and_schema_properties():
    assert rs.surface(CODE, SCHEMA) == {"REF-01", "--bind", "Spec.system", "Evidence.id", "Evidence.run"}


def test_classify_removed_is_major_added_is_minor_else_patch():
    a = {"REF-01", "--bind"}
    assert rs.classify(a, a) == ("patch", ["no public surface change"])
    assert rs.classify(a, a | {"REF-02"}) == ("minor", ["added REF-02"])
    assert rs.classify(a, {"REF-01"}) == ("major", ["removed --bind"])
    assert rs.classify(a, {"REF-02"})[0] == "major"


def test_bump():
    assert [rs.bump("0.8.3", k) for k in ("patch", "minor", "major")] == ["0.8.4", "0.9.0", "1.0.0"]


def test_unreleased_entries():
    assert rs.unreleased("# C\n\n## Unreleased\n\n- a\n- b\n\n## 0.8.0\n\n- old\n") == ["- a", "- b"]
    assert rs.unreleased("## Unreleased\n\n## 0.8.0\n- old\n") == [] and rs.unreleased("# C\n") == []


@pytest.fixture
def repo(tmp_path, monkeypatch):
    g = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=tmp_path, check=True, capture_output=True, text=True).stdout
    (tmp_path / "reference-implementation").mkdir()
    (tmp_path / rs.MM).write_text(CODE); (tmp_path / rs.SCHEMA).write_text(SCHEMA); (tmp_path / "CHANGELOG.md").write_text("## Unreleased\n\n- first\n")
    g("init", "-q"); g("add", "."); g("commit", "-qm", "init"); g("tag", "v1.2.3"); (tmp_path / "CHANGELOG.md").write_text("## Unreleased\n\n- first\n"); (tmp_path / "x").write_text("x"); g("add", "."); g("commit", "-qm", "later")
    monkeypatch.setattr(rs, "ROOT", tmp_path)
    return tmp_path, g


def test_plan_suggests_from_surface_and_honours_override(repo):
    root, g = repo
    assert rs.plan() == {"version": "1.2.4", "resume": False, "last": "v1.2.3", "bump": "patch", "reasons": ["no public surface change"], "entries": ["- first"]}
    (root / rs.MM).write_text(CODE + '    "REF-02": ("inventory", None, "y"),\n')
    assert (p := rs.plan())["version"] == "1.3.0" and p["bump"] == "minor"
    assert (p := rs.plan("major"))["version"] == "2.0.0" and "auto would be minor" in p["reasons"][0]


def test_plan_stops_without_entries_and_resumes_a_tagged_head(repo):
    root, g = repo
    (root / "CHANGELOG.md").write_text("## Unreleased\n\n## 1.2.3\n- old\n")
    with pytest.raises(SystemExit, match="nothing to release"): rs.plan()
    g("commit", "-qam", "Release 1.3.0"); g("tag", "v1.3.0")
    assert (p := rs.plan()) == {**p, "version": "1.3.0", "resume": True}


def test_plan_on_this_repository_is_consistent():
    tags = subprocess.run(["git", "tag", "--list", "v*"], cwd=rs.ROOT, capture_output=True, text=True).stdout.split()
    if not tags: pytest.skip("no tags (shallow checkout)")
    try: p = rs.plan()
    except SystemExit: return  # empty Unreleased is a valid state right after a release
    assert p["resume"] or rs.ver(p["version"]) > rs.ver(p["last"])

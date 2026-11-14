"""Release planning for .github/workflows/publish.yml: the next version from the public surface
(invariant IDs, CLI options, schema properties) that changed since the last tag. Stdlib only."""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).parent
MM, SCHEMA = "reference-implementation/metamodel.py", "reference-implementation/schema.json"
git = lambda *a: subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, check=True).stdout.rstrip()
ver = lambda t: tuple(int(x) for x in t.removeprefix("v").split("."))


def surface(code: str, schema: str) -> set[str]:
    s = json.loads(schema)
    props = {f"{m}.{k}" for m, d in {"Spec": s, **s.get("$defs", {})}.items() for k in d.get("properties", {})}
    return {*re.findall(r'^    "([A-Z]+-\d+)":', code, re.M), *re.findall(r'add_argument\("(--[\w-]+)"', code), *props}


def classify(old: set[str], new: set[str]) -> tuple[str, list[str]]:
    """major if anything public was removed, minor if added, else patch; with the items that decided it."""
    gone, added = sorted(old - new), sorted(new - old)
    return ("major", [f"removed {x}" for x in gone]) if gone else ("minor", [f"added {x}" for x in added]) if added else ("patch", ["no public surface change"])


def bump(version: str, kind: str) -> str:
    a, b, c = ver(version)
    return {"major": f"{a + 1}.0.0", "minor": f"{a}.{b + 1}.0", "patch": f"{a}.{b}.{c + 1}"}[kind]


def unreleased(changelog: str) -> list[str]:
    body = re.split(r"^## ", changelog.split("## Unreleased", 1)[1], maxsplit=1, flags=re.M)[0] if "## Unreleased" in changelog else ""
    return [l for l in body.splitlines() if l.startswith("- ")]


def plan(choice: str = "auto") -> dict:
    """Next release. If HEAD already carries a version tag the release was pushed and is resumed, not bumped again."""
    tags = sorted(git("tag", "--list", "v*").split(), key=ver)
    if (done := [t for t in git("tag", "--points-at", "HEAD").split() if t in tags]):
        return {"version": done[-1].removeprefix("v"), "resume": True, "last": None, "bump": None, "reasons": ["HEAD is already tagged: resuming"], "entries": []}
    last = tags[-1]
    kind, reasons = classify(surface(git("show", f"{last}:{MM}"), git("show", f"{last}:{SCHEMA}")), surface((ROOT / MM).read_text(encoding="utf-8"), (ROOT / SCHEMA).read_text(encoding="utf-8")))
    if choice != "auto": kind, reasons = choice, [f"chosen: {choice} (auto would be {kind}: {'; '.join(reasons[:3])})"]
    entries = unreleased((ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))
    if not entries: raise SystemExit("CHANGELOG.md has no entries under Unreleased: nothing to release")
    return {"version": bump(last.removeprefix("v"), kind), "resume": False, "last": last, "bump": kind, "reasons": reasons, "entries": entries}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bump", choices=["auto", "patch", "minor", "major"], default="auto")
    print(json.dumps(plan(ap.parse_args().bump), indent=2))

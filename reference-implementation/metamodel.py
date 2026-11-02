from __future__ import annotations
import argparse, json, sys, yaml
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, ValidationError

class Strict(BaseModel): model_config = ConfigDict(extra="forbid")

Method = Literal["test", "proof", "analysis", "inspection"]
RANK = {"public": 0, "internal": 1, "confidential": 2, "restricted": 3}

class SystemDef(Strict):
    id: str
    version: str
    layers: list[str] = []
    external_sources: list[str] = []
    quality_attributes: dict[str, str] = {}

class Capability(Strict):
    id: str
    version: str
    preconditions: list[str] = []
    postconditions: list[str] = []
    invariants: list[str] = []
    failure_modes: list[str] = []
    deprecated: bool = False

class Component(Strict):
    id: str
    version: str
    layer: str | None = None
    consistency: Literal["strong", "eventual"] = "strong"
    provides: list[str] = []
    requires: list[str] = []
    owns_data: list[str] = []
    bindings: dict[str, str] = {}

class DataModel(Strict):
    id: str
    version: str
    owner: str
    classification: Literal["public", "internal", "confidential", "restricted"] = "public"
    fields: dict[str, str]
    derived_from: list[str] = []
    external_source: str | None = None

class Requirement(Strict):
    id: str
    version: str
    target: str
    kind: Literal["functional", "non-functional"] = "functional"
    mandatory: bool = True
    criteria: list[str] = Field(min_length=1)
    methods: list[Method] = ["test"]
    depends_on: list[str] = []
    refines: list[str] = []
    conflicts_with: list[str] = []

class Risk(Strict):
    id: str
    target: str
    treatment: Literal["mitigation", "acceptance", "avoidance", "transfer"]
    mitigated_by: list[str] = []
    residual_accepted: bool = False

class Evidence(Strict):
    id: str
    requirement_id: str
    requirement_version: str
    method: Method
    passed: bool
    provenance: str

class Binding(Strict):
    id: str
    requirement_id: str
    requirement_version: str

class Spec(Strict):
    system: SystemDef
    capabilities: list[Capability]
    components: list[Component]
    data_models: list[DataModel] = []
    requirements: list[Requirement] = []
    risks: list[Risk] = []
    evidence: list[Evidence] = []
    tests: list[Binding] = []

def _ver(v: str) -> tuple[int, ...] | None:
    try: return tuple(int(x) for x in v.split("."))
    except ValueError: return None

def _ver_ok(req: str | None, act: str) -> bool:
    if not req: return True
    r, a = _ver(req), _ver(act)
    return bool(r and a) and r[0] == a[0] and a[1:] >= r[1:]

def _resolve(spec: Spec, c: Component, ref: str) -> tuple[str | None, str | None]:
    k, _, v = ref.partition("@^")
    bad = "@^" in ref and not v
    cap = next((x for x in spec.capabilities if x.id == k), None)
    ps = [p.id for p in spec.components if k in p.provides and p.id != c.id]
    if k in c.bindings: ps = [p for p in ps if p == c.bindings[k]]
    if bad or not cap or not _ver_ok(v, cap.version) or not ps: return None, f"unresolved capability '{ref}'"
    if len(ps) > 1: return None, f"ambiguous providers {ps} for '{ref}'; add a binding"
    return ps[0], None

def resolve_capabilities(spec: Spec) -> dict[str, dict[str, str]]:
    return {c.id: {r.partition("@^")[0]: p for r in c.requires if (p := _resolve(spec, c, r)[0])} for c in spec.components}

def _cycles(g: dict[str, dict[str, str]]) -> list[list[str]]:
    seen, stack, out = set(), [], []
    def visit(n):
        if n in stack: out.append(stack[stack.index(n):] + [n]); return
        if n in seen: return
        seen.add(n); stack.append(n)
        for m in g.get(n, {}).values(): visit(m)
        stack.pop()
    for n in g: visit(n)
    return out

def validate_spec(spec: Spec) -> list[str]:
    errs, resolved = [], resolve_capabilities(spec)
    comps = {c.id: c for c in spec.components}
    caps = {c.id for c in spec.capabilities}
    reqs = {r.id: r for r in spec.requirements}
    models = {d.id: d for d in spec.data_models}
    layers = {l: i for i, l in enumerate(spec.system.layers)}
    passed = {(e.requirement_id, e.requirement_version, e.method) for e in spec.evidence if e.passed}
    failed = {(e.requirement_id, e.requirement_version) for e in spec.evidence if not e.passed}
    missing = {r.id: [m for m in r.methods if (r.id, r.version, m) not in passed] for r in spec.requirements}
    ok = {r.id for r in spec.requirements if not missing[r.id] and (r.id, r.version) not in failed}
    bound = {(b.id, b.requirement_id, b.requirement_version) for b in spec.tests}
    targets = {"system": {spec.system.id}, "component": set(comps), "capability": caps, "data model": set(models)}

    for kind, xs in [("capability", spec.capabilities), ("component", spec.components), ("data model", spec.data_models),
                     ("requirement", spec.requirements), ("risk", spec.risks), ("evidence", spec.evidence), ("test", spec.tests)]:
        errs += [f"Duplicate {kind} id '{i}'" for i, n in Counter(x.id for x in xs).items() if n > 1]
    for kind, xs in [("Requirement", spec.requirements), ("Risk", spec.risks)]:
        for x in xs:
            m = [t for t, ids in targets.items() if x.target in ids]
            if len(m) != 1: errs.append(f"{kind} '{x.id}' has {'ambiguous' if m else 'unknown'} target '{x.target}'")

    errs += [f"Duplicate layer '{l}'" for l, n in Counter(spec.system.layers).items() if n > 1]
    for c in spec.components:
        if not c.provides:
            errs.append(f"Component '{c.id}' must provide at least one capability")
        errs += [f"Component '{c.id}' provides unknown capability '{p}'" for p in c.provides if p not in caps]
        errs += [f"Component '{c.id}' owns unknown data model '{d}'" for d in c.owns_data if d not in models]
        errs += [f"Component '{c.id}' binds capability '{k}' it does not require" for k in c.bindings
                 if k not in {r.partition("@^")[0] for r in c.requires}]
        if layers and c.layer not in layers:
            errs.append(f"Component '{c.id}' has undeclared layer '{c.layer}'")
        for ref in c.requires:
            p, err = _resolve(spec, c, ref)
            if err:
                errs.append(f"Component '{c.id}' has {err}")
            elif c.layer in layers and comps[p].layer in layers and layers[c.layer] > layers[comps[p].layer]:
                errs.append(f"Component '{c.id}' has layer violation depending on '{p}'")
    errs += [f"Dependency cycle: {' -> '.join(cy)}" for cy in _cycles(resolved)]

    req_targets = {r.target for r in spec.requirements}
    for cap in spec.capabilities:
        if cap.id not in req_targets:
            errs.append(f"Capability '{cap.id}' has no associated requirements")
    for r in spec.requirements:
        for rel in ("depends_on", "refines", "conflicts_with"):
            errs += [f"Requirement '{r.id}' {rel} unknown requirement '{x}'" for x in getattr(r, rel) if x not in reqs]
        if r.mandatory and (r.id, r.version) in failed:
            errs.append(f"Requirement '{r.id}@{r.version}' has unresolved failing evidence")
        elif r.mandatory and r.id not in ok:
            errs.append(f"Requirement '{r.id}@{r.version}' missing valid verification evidence ({', '.join(missing[r.id])})")
        if r.mandatory:
            errs += [f"Requirement '{r.id}' depends on unverified requirement '{d}'" for d in r.depends_on if d in reqs and d not in ok]
        for cid in r.conflicts_with:
            if cid in reqs:
                errs.append(f"Requirement '{r.id}' has unresolved conflict with '{cid}'")
    errs += [f"Evidence '{e.id}' references unknown requirement '{e.requirement_id}'" for e in spec.evidence if e.requirement_id not in reqs]
    errs += [f"Evidence '{e.id}' provenance '{e.provenance}' is not a test bound to '{e.requirement_id}@{e.requirement_version}'"
             for e in spec.evidence if e.method == "test" and (e.provenance, e.requirement_id, e.requirement_version) not in bound]
    for b in spec.tests:
        if b.requirement_id not in reqs: errs.append(f"Test '{b.id}' references unknown requirement '{b.requirement_id}'")
        elif reqs[b.requirement_id].version != b.requirement_version:
            errs.append(f"Test '{b.id}' verifies stale requirement version '{b.requirement_id}@{b.requirement_version}'")
    for risk in spec.risks:
        if risk.treatment == "mitigation":
            if not risk.mitigated_by: errs.append(f"Risk '{risk.id}' has no mitigating requirements")
            errs += [f"Risk '{risk.id}' has unverified mitigation '{m}'" for m in risk.mitigated_by if m not in ok]
        if risk.treatment == "acceptance" and not risk.residual_accepted:
            errs.append(f"Risk '{risk.id}' requires residual_accepted")
    for dm in spec.data_models:
        if dm.owner not in comps:
            errs.append(f"DataModel '{dm.id}' has unknown owner '{dm.owner}'")
        elif dm.id not in comps[dm.owner].owns_data:
            errs.append(f"DataModel '{dm.id}' owner '{dm.owner}' does not list it in owns_data")
        errs += [f"DataModel '{dm.id}' is also claimed by '{c.id}'" for c in spec.components if dm.id in c.owns_data and c.id != dm.owner]
        if dm.external_source and dm.external_source not in spec.system.external_sources:
            errs.append(f"DataModel '{dm.id}' has untracked external data source '{dm.external_source}'")
        for s in dm.derived_from:
            if s not in models:
                errs.append(f"DataModel '{dm.id}' derives from unknown data model '{s}'")
            elif RANK[dm.classification] < RANK[models[s].classification]:
                errs.append(f"DataModel '{dm.id}' violates classification propagation from '{s}'")
    return errs

def apply_report(spec: Spec, path: str | Path) -> list[str]:
    errs = [f"Evidence '{e.id}' has method test; test evidence is derived from the run report" for e in spec.evidence if e.method == "test"]
    spec.evidence = [e for e in spec.evidence if e.method != "test"]
    ext, seen = {b.id: b for b in spec.tests}, set()
    for tc in ET.parse(path).getroot().iter("testcase"):
        tid = f"{tc.get('classname')}::{tc.get('name')}"
        seen.add(tid)
        refs = [p.get("value", "") for p in tc.iter("property") if p.get("name") == "verifies"]
        if tid in ext: refs.append(f"{ext[tid].requirement_id}@{ext[tid].requirement_version}")
        if len(refs) != 1:
            errs.append(f"Test '{tid}' must bind exactly one requirement, found {len(refs)}"); continue
        rid, _, ver = refs[0].partition("@")
        if tid not in ext: spec.tests.append(Binding(id=tid, requirement_id=rid, requirement_version=ver))
        spec.evidence.append(Evidence(id=f"ev:{tid}", requirement_id=rid, requirement_version=ver, method="test", provenance=tid,
                                      passed=not any(tc.find(t) is not None for t in ("failure", "error", "skipped"))))
    return errs + [f"Test '{t}' is bound but not in the run report" for t in sorted(set(ext) - seen)]

def check_compatibility(old: Capability, new: Capability) -> list[str]:
    errs = [
        f"{msg}: {sorted(diff)}" for diff, msg in [
            (set(new.preconditions) - set(old.preconditions), "Strengthened preconditions"),
            (set(old.postconditions) - set(new.postconditions), "Removed postconditions"),
            (set(old.invariants) - set(new.invariants), "Removed invariants"),
            (set(new.failure_modes) - set(old.failure_modes), "Added failure modes"),
        ] if diff
    ]
    o, n = _ver(old.version), _ver(new.version)
    if errs and (not o or not n or n[0] <= o[0]):
        errs.append(f"Breaking change requires major version bump ({old.version} -> {new.version})")
    return errs

def compare_specs(old: Spec, new: Spec) -> list[str]:
    caps = {c.id: c for c in new.capabilities}
    return [f"Capability '{c.id}': {e}" for c in old.capabilities for e in (
        check_compatibility(c, caps[c.id]) if c.id in caps else [] if c.deprecated else ["removed without deprecation"])]

def impact_analysis(spec: Spec, target_id: str) -> dict[str, list[str]]:
    if target_id not in {spec.system.id, *(x.id for xs in (spec.capabilities, spec.components, spec.data_models, spec.requirements) for x in xs)}:
        raise ValueError(f"unknown id '{target_id}'")
    seen, todo = set(), [target_id]
    while todo:
        x = todo.pop()
        if x in seen: continue
        seen.add(x)
        todo += [c.id for c in spec.components if x in {r.partition("@^")[0] for r in c.requires} or (x == target_id and x in c.provides)]
        todo += [d.id for d in spec.data_models if x in d.derived_from]
        todo += [y for c in spec.components if c.id == x for y in c.provides + c.owns_data]
        todo += [d.owner for d in spec.data_models if d.id == x]
    reqs = {r.id for r in spec.requirements if r.target in seen | {spec.system.id} or r.id == target_id}
    while new := {r.id for r in spec.requirements if r.id not in reqs and reqs & {*r.depends_on, *r.refines}}: reqs |= new
    ids = lambda xs: [x.id for x in xs if x.id in seen]
    return {
        "components": ids(spec.components),
        "capabilities": ids(spec.capabilities),
        "data_models": ids(spec.data_models),
        "requirements": [r.id for r in spec.requirements if r.id in reqs],
        "invalidated_evidence": [e.id for e in spec.evidence if e.requirement_id in reqs],
    }

def load_spec(path: str | Path) -> Spec:
    return Spec.model_validate(yaml.safe_load(Path(path).read_text(encoding="utf-8")))

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate system specifications against the metamodel.")
    ap.add_argument("spec", nargs="?", default=Path(__file__).parent / "example.yaml")
    ap.add_argument("--schema", action="store_true", help="print JSON Schema")
    ap.add_argument("--compat", metavar="OLD", help="check compatibility of OLD spec's capabilities with spec")
    ap.add_argument("--impact", metavar="ID", help="change-impact analysis for ID")
    ap.add_argument("--junit", metavar="FILE", help="JUnit XML run report: derives test bindings and evidence, rejects unbound tests")
    ap.add_argument("--json", action="store_true", help="JSON output")
    a = ap.parse_args(argv)
    if a.schema:
        print(json.dumps(Spec.model_json_schema(), indent=2)); return 0
    try:
        spec = load_spec(a.spec)
        old = load_spec(a.compat) if a.compat else None
    except (OSError, yaml.YAMLError, ValidationError) as e:
        out = {"valid": False, "schema_errors": [str(e)]}
    else:
        try:
            if a.impact: out = impact_analysis(spec, a.impact)
            else:
                errs = (apply_report(spec, a.junit) if a.junit else []) + validate_spec(spec) + (compare_specs(old, spec) if old else [])
                out = {"valid": not errs, "errors": errs}
        except (OSError, ValueError, ET.ParseError) as e:
            out = {"valid": False, "errors": [str(e)]}
    if a.json: print(json.dumps(out, indent=2))
    elif a.impact and "valid" not in out: print("\n".join(f"{k}: {', '.join(v)}" for k, v in out.items()))
    else: print("VALID" if out["valid"] else "\n".join(out.get("errors") or out["schema_errors"]))
    return 0 if out.get("valid", True) else 1

if __name__ == "__main__":
    sys.exit(main())

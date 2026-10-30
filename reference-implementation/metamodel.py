from __future__ import annotations
import argparse, json, sys, yaml
from collections import Counter
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, ValidationError

RANK = {"public": 0, "internal": 1, "confidential": 2, "restricted": 3}
Status = Literal["draft", "specified", "verified", "deprecated"]

class SystemDef(BaseModel):
    id: str
    version: str
    status: Status = "draft"
    layers: list[str] = []
    external_sources: list[str] = []
    quality_attributes: dict[str, str] = {}

class Capability(BaseModel):
    id: str
    version: str
    status: Status = "draft"
    preconditions: list[str] = []
    postconditions: list[str] = []
    invariants: list[str] = []
    failure_modes: list[str] = []
    deprecated: bool = False

class Component(BaseModel):
    id: str
    version: str
    status: Status = "draft"
    layer: str | None = None
    consistency: Literal["strong", "eventual"] = "strong"
    provides: list[str] = []
    requires: list[str] = []
    owns_data: list[str] = []
    bindings: dict[str, str] = {}

class DataModel(BaseModel):
    id: str
    version: str
    owner: str
    classification: Literal["public", "internal", "confidential", "restricted"] = "public"
    fields: dict[str, str]
    derived_from: list[str] = []
    external_source: str | None = None

class Requirement(BaseModel):
    id: str
    version: str
    status: Status = "draft"
    target: str
    kind: Literal["functional", "non-functional"] = "functional"
    mandatory: bool = True
    criteria: list[str]
    depends_on: list[str] = []
    refines: list[str] = []
    conflicts_with: list[str] = []
    resolved_by: str | None = None

class Risk(BaseModel):
    id: str
    target: str
    treatment: Literal["mitigation", "acceptance", "avoidance", "transfer"]
    mitigated_by: list[str] = []
    residual_accepted: bool = False
    transferred_to: str | None = None

class Evidence(BaseModel):
    id: str
    requirement_id: str
    requirement_version: str
    method: Literal["test", "proof", "analysis", "inspection"]
    passed: bool
    provenance: str

class Spec(BaseModel):
    system: SystemDef
    capabilities: list[Capability]
    components: list[Component]
    data_models: list[DataModel] = []
    requirements: list[Requirement] = []
    risks: list[Risk] = []
    evidence: list[Evidence] = []

def _ver(v: str) -> tuple[int, ...] | None:
    try: return tuple(int(x) for x in v.split("."))
    except ValueError: return None

def _ver_ok(req: str | None, act: str) -> bool:
    if not req: return True
    r, a = _ver(req), _ver(act)
    return bool(r and a) and r[0] == a[0] and a[1:] >= r[1:]

def _resolve(spec: Spec, c: Component, ref: str) -> tuple[str | None, str | None]:
    k, _, v = ref.partition("@^")
    cap = next((x for x in spec.capabilities if x.id == k), None)
    ps = [p.id for p in spec.components if k in p.provides and p.id != c.id]
    if k in c.bindings: ps = [p for p in ps if p == c.bindings[k]]
    if not cap or not _ver_ok(v, cap.version) or not ps: return None, f"unresolved capability '{ref}'"
    if len(ps) > 1: return None, f"ambiguous providers {ps} for '{ref}'; add a binding"
    return ps[0], None

def resolve_capabilities(spec: Spec) -> dict[str, dict[str, str]]:
    return {c.id: {r.partition("@^")[0]: p for r in c.requires if (p := _resolve(spec, c, r)[0])} for c in spec.components}

def _cycles(g: dict[str, list[str]]) -> list[list[str]]:
    seen, stack, out = set(), [], []
    def visit(n):
        if n in stack: out.append(stack[stack.index(n):] + [n]); return
        if n in seen: return
        seen.add(n); stack.append(n)
        for m in g.get(n, []): visit(m)
        stack.pop()
    for n in g: visit(n)
    return out

def verified_requirements(spec: Spec) -> set[tuple[str, str]]:
    ev: dict[tuple[str, str], list[bool]] = {}
    for e in spec.evidence: ev.setdefault((e.requirement_id, e.requirement_version), []).append(e.passed)
    return {k for k, v in ev.items() if all(v)}

def validate_spec(spec: Spec) -> list[str]:
    errs, resolved = [], resolve_capabilities(spec)
    comps = {c.id: c for c in spec.components}
    caps = {c.id for c in spec.capabilities}
    reqs = {r.id: r for r in spec.requirements}
    models = {d.id: d for d in spec.data_models}
    layers = {l: i for i, l in enumerate(spec.system.layers)}
    verified = verified_requirements(spec)
    active = {r.id: r for r in spec.requirements if r.status != "deprecated"}
    ok = {r.id for r in active.values() if (r.id, r.version) in verified}
    failed = {(e.requirement_id, e.requirement_version) for e in spec.evidence if not e.passed}
    targets = {"system": {spec.system.id}, "component": set(comps), "capability": caps, "data model": set(models)}

    for kind, xs in [("capability", spec.capabilities), ("component", spec.components), ("data model", spec.data_models),
                     ("requirement", spec.requirements), ("risk", spec.risks), ("evidence", spec.evidence)]:
        errs += [f"Duplicate {kind} id '{i}'" for i, n in Counter(x.id for x in xs).items() if n > 1]
    for kind, xs in [("Requirement", spec.requirements), ("Risk", spec.risks)]:
        for x in xs:
            m = [t for t, ids in targets.items() if x.target in ids]
            if len(m) != 1: errs.append(f"{kind} '{x.id}' has {'ambiguous' if m else 'unknown'} target '{x.target}'")

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
    errs += [f"Dependency cycle: {' -> '.join(cy)}" for cy in _cycles({k: list(v.values()) for k, v in resolved.items()})]
    errs += [f"Requirement cycle: {' -> '.join(cy)}" for cy in _cycles({r.id: [x for x in [*r.depends_on, *r.refines] if x in active] for r in active.values()})]

    req_targets = {r.target for r in active.values()}
    for cap in spec.capabilities:
        if cap.id not in req_targets:
            errs.append(f"Capability '{cap.id}' has no associated requirements")
    for r in spec.requirements:
        for rel in ("depends_on", "refines", "conflicts_with"):
            errs += [f"Requirement '{r.id}' {rel} unknown requirement '{x}'" for x in getattr(r, rel) if x not in reqs]
        if r.resolved_by and r.resolved_by not in reqs:
            errs.append(f"Requirement '{r.id}' resolved_by unknown requirement '{r.resolved_by}'")
        if r.id not in active: continue
        for rel in ("depends_on", "refines"):
            errs += [f"Requirement '{r.id}' {rel} inactive requirement '{x}'" for x in getattr(r, rel) if x in reqs and x not in active]
        if r.mandatory and (r.id, r.version) in failed:
            errs.append(f"Requirement '{r.id}@{r.version}' has unresolved failing evidence")
        elif r.mandatory and r.id not in ok:
            errs.append(f"Requirement '{r.id}@{r.version}' missing valid verification evidence")
        if r.mandatory:
            errs += [f"Requirement '{r.id}' depends on unverified requirement '{d}'" for d in r.depends_on if d in reqs and d not in ok]
        for cid in r.conflicts_with:
            if cid in active and not any(
                q and q.id not in {r.id, cid} and q.id in ok and any(c.strip() for c in q.criteria)
                and {r.id, cid} <= set(q.refines)
                for q in (active.get(r.resolved_by), active.get(active[cid].resolved_by))
            ):
                errs.append(f"Requirement '{r.id}' has unresolved conflict with '{cid}'")
    errs += [f"Evidence '{e.id}' references unknown requirement '{e.requirement_id}'" for e in spec.evidence if e.requirement_id not in reqs]
    for risk in spec.risks:
        if risk.treatment in ("mitigation", "avoidance"):
            if not risk.mitigated_by: errs.append(f"Risk '{risk.id}' has no mitigating requirements")
            errs += [f"Risk '{risk.id}' references unknown requirement '{m}'" for m in risk.mitigated_by if m not in reqs]
            errs += [f"Risk '{risk.id}' has unverified mitigation '{m}'" for m in risk.mitigated_by if m in reqs and m not in ok]
        if risk.treatment == "avoidance" and risk.residual_accepted:
            errs.append(f"Risk '{risk.id}' is avoided and must not carry residual risk")
        if risk.treatment == "transfer" and not risk.transferred_to:
            errs.append(f"Risk '{risk.id}' requires transferred_to")
        if risk.treatment in ("acceptance", "transfer") and not risk.residual_accepted:
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
        check_compatibility(c, caps[c.id]) if c.id in caps else [] if c.deprecated or c.status == "deprecated" else ["removed without deprecation"])]

def residual_risks(spec: Spec) -> list[str]:
    return [r.id for r in spec.risks if r.residual_accepted]

def impact_analysis(spec: Spec, target_id: str) -> dict[str, list[str]]:
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
    while new := {r.id for r in spec.requirements if r.id not in reqs and reqs & {*r.depends_on, *r.refines, r.resolved_by}}: reqs |= new
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
        known = {spec.system.id, *(x.id for x in spec.capabilities + spec.components + spec.data_models + spec.requirements)}
        out = {"valid": False, "errors": [f"Unknown --impact ID '{a.impact}'"]} if a.impact and a.impact not in known else impact_analysis(spec, a.impact) if a.impact else {"valid": not (errs := validate_spec(spec) + (compare_specs(old, spec) if old else [])), "errors": errs, "residual_risks": residual_risks(spec)}
    if a.json: print(json.dumps(out, indent=2))
    elif a.impact and "errors" not in out: print("\n".join(f"{k}: {', '.join(v)}" for k, v in out.items()))
    else: print("VALID" if out["valid"] else "\n".join(out.get("errors") or out["schema_errors"]))
    return 0 if out.get("valid", True) else 1

if __name__ == "__main__":
    sys.exit(main())

from __future__ import annotations
import argparse, json, sys, yaml
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, ConfigDict, ValidationError

RANK = {"public": 0, "internal": 1, "confidential": 2, "restricted": 3}
STATUS = ["draft", "specified", "verified", "deprecated"]
STAGES = ["inventory", "discovery", "architecture", "verification", "release"]
CATEGORIES = ["functional", "semantic", "contract", "serialization", "concurrency",
              "performance", "scalability", "resilience", "security", "observability"]
Status = Literal["draft", "specified", "verified", "deprecated"]

class M(BaseModel):
    model_config = ConfigDict(extra="forbid")

class Budget(M):
    max_provides: int = 5
    max_requires: int = 8
    max_owns_data: int = 4

class SystemDef(M):
    id: str
    version: str
    status: Status = "draft"
    layers: list[str] = []
    external_sources: list[str] = []
    quality_attributes: dict[str, str] = {}
    context_budget: Budget = Budget()

class Interface(M):
    operation: str
    mode: Literal["sync", "async"] = "sync"
    request: str | None = None
    response: str | None = None
    idempotent: bool
    auth: str
    errors: dict[str, int | str] = {}

class Capability(M):
    id: str
    version: str
    status: Status = "draft"
    preconditions: list[str] = []
    postconditions: list[str] = []
    invariants: list[str] = []
    failure_modes: list[str] = []
    interface: Interface | None = None

class Component(M):
    id: str
    version: str
    status: Status = "draft"
    layer: str | None = None
    consistency: Literal["strong", "eventual"] = "strong"
    provides: list[str] = []
    requires: list[str] = []
    owns_data: list[str] = []
    bindings: dict[str, str] = {}
    source_paths: list[str] = []

class DataModel(M):
    id: str
    version: str
    owner: str
    classification: Literal["public", "internal", "confidential", "restricted"] = "public"
    fields: dict[str, str]
    derived_from: list[str] = []
    external_source: str | None = None
    schema_path: str | None = None
    declassified_by: str | None = None

class Requirement(M):
    id: str
    version: str
    target: str
    status: Status = "draft"
    kind: Literal["functional", "non-functional"] = "functional"
    category: Literal[tuple(CATEGORIES)] | None = None
    mandatory: bool = True
    criteria: list[str]
    depends_on: list[str] = []
    refines: list[str] = []
    conflicts_with: list[str] = []
    resolved_by: str | None = None

class Risk(M):
    id: str
    target: str
    treatment: Literal["mitigation", "acceptance", "avoidance", "transfer"]
    mitigated_by: list[str] = []
    residual_accepted: bool = False
    transferred_to: str | None = None
    waives: Literal["layer-violation", "dependency-cycle", "shared-data-ownership", "context-budget", "verification-category"] | None = None
    expires: date | Literal["architecture", "verification", "release"] | None = None

class Evidence(M):
    id: str
    requirement_id: str
    requirement_version: str
    method: Literal["test", "proof", "model-check", "analysis", "inspection"]
    passed: bool
    provenance: str
    bounds: dict[str, int | str] | str | None = None
    subject_id: str | None = None
    subject_revision: str | None = None
    timestamp: datetime | date | None = None
    verifier: str | None = None
    supersedes: str | None = None
    supersession_reason: str | None = None

class Spec(M):
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

def _superseded(spec: Spec) -> set[str]:
    return {e.supersedes for e in spec.evidence if e.passed and e.supersedes and e.supersession_reason}

def verified_requirements(spec: Spec) -> set[tuple[str, str]]:
    ev: dict[tuple[str, str], list[bool]] = {}
    sup = _superseded(spec)
    for e in spec.evidence:
        if e.id not in sup: ev.setdefault((e.requirement_id, e.requirement_version), []).append(e.passed)
    return {k for k, v in ev.items() if all(v)}

def _expired(k: Risk, stage: str, today: date | None) -> bool:
    return k.expires < (today or date.today()) if isinstance(k.expires, date) else STAGES.index(k.expires) < STAGES.index(stage)

def active_waivers(spec: Spec, stage: str = "release", today: date | None = None) -> list[Risk]:
    return [k for k in spec.risks if k.waives and k.treatment in ("mitigation", "acceptance") and k.mitigated_by and k.expires
            and stage != "release" and not _expired(k, stage, today)]

def validate_spec(spec: Spec, stage: str = "release", today: date | None = None) -> list[str]:
    E, resolved = [], resolve_capabilities(spec)
    def add(st, msg, waive=None, *subj): E.append((STAGES.index(st), msg, waive, {*subj}))
    def need(st, lvl, groups):
        for kind, xs in groups:
            for x in xs:
                if STATUS.index(x.status) < STATUS.index(lvl): add(st, f"{kind} '{x.id}' status '{x.status}' below '{lvl}'")
    comps = {c.id: c for c in spec.components}
    caps = {c.id: c for c in spec.capabilities}
    reqs = {r.id: r for r in spec.requirements}
    active = {r.id: r for r in spec.requirements if r.status != "deprecated"}
    models = {d.id: d for d in spec.data_models}
    layers = {l: i for i, l in enumerate(spec.system.layers)}
    evs = {e.id: e for e in spec.evidence}
    sid, sup, verified = spec.system.id, _superseded(spec), verified_requirements(spec)
    ok = {r.id for r in active.values() if (r.id, r.version) in verified}
    failed = {(e.requirement_id, e.requirement_version) for e in spec.evidence if not e.passed and e.id not in sup}
    targets = {"system": {sid}, "component": set(comps), "capability": set(caps), "data model": set(models)}
    required = {r.partition("@^")[0] for c in spec.components for r in c.requires}

    # inventory: identity and references
    for kind, xs in [("capability", spec.capabilities), ("component", spec.components), ("data model", spec.data_models),
                     ("requirement", spec.requirements), ("risk", spec.risks), ("evidence", spec.evidence)]:
        for i, n in Counter(x.id for x in xs).items():
            if n > 1: add("inventory", f"Duplicate {kind} id '{i}'")
    for kind, xs in [("Requirement", spec.requirements), ("Risk", spec.risks)]:
        for x in xs:
            m = [t for t, ids in targets.items() if x.target in ids]
            if len(m) != 1: add("inventory", f"{kind} '{x.id}' has {'ambiguous' if m else 'unknown'} target '{x.target}'")
    for c in spec.components:
        for p in c.provides:
            if p not in caps: add("inventory", f"Component '{c.id}' provides unknown capability '{p}'")
        for d in c.owns_data:
            if d not in models: add("inventory", f"Component '{c.id}' owns unknown data model '{d}'")
        for k in c.bindings:
            if k not in {r.partition("@^")[0] for r in c.requires}: add("inventory", f"Component '{c.id}' binds capability '{k}' it does not require")
    for r in spec.requirements:
        for rel in ("depends_on", "refines", "conflicts_with", "resolved_by"):
            xs = getattr(r, rel)
            for x in xs if isinstance(xs, list) else [xs] if xs else []:
                if x not in reqs: add("inventory", f"Requirement '{r.id}' {rel} unknown requirement '{x}'")
    for e in spec.evidence:
        if e.requirement_id not in reqs: add("inventory", f"Evidence '{e.id}' references unknown requirement '{e.requirement_id}'")
        if e.method == "model-check" and not e.bounds: add("inventory", f"Evidence '{e.id}' model-check requires bounds")
        if e.subject_id and not any(e.subject_id in ids for ids in targets.values()): add("inventory", f"Evidence '{e.id}' has unknown subject '{e.subject_id}'")
        if e.supersedes:
            o = evs.get(e.supersedes)
            if not o or o.passed or o.requirement_id != e.requirement_id or not e.passed:
                add("inventory", f"Evidence '{e.id}' must be passing and supersede a failed record of the same requirement")
            if not e.supersession_reason: add("inventory", f"Evidence '{e.id}' supersedes without supersession_reason")
    for k in spec.risks:
        for m in k.mitigated_by:
            if m not in reqs: add("inventory", f"Risk '{k.id}' references unknown requirement '{m}'")
        if k.waives and (k.treatment not in ("mitigation", "acceptance") or not k.mitigated_by or not k.expires):
            add("inventory", f"Risk '{k.id}' waiver requires mitigation or acceptance, mitigated_by and expires")
        elif k.waives and _expired(k, stage, today):
            add("inventory", f"Risk '{k.id}' waiver expired ({k.expires})")
    for dm in spec.data_models:
        if dm.owner not in comps: add("inventory", f"DataModel '{dm.id}' has unknown owner '{dm.owner}'")
        if dm.external_source and dm.external_source not in spec.system.external_sources:
            add("inventory", f"DataModel '{dm.id}' has untracked external data source '{dm.external_source}'")
        for x in dm.derived_from:
            if x not in models: add("inventory", f"DataModel '{dm.id}' derives from unknown data model '{x}'")
        if dm.declassified_by and dm.declassified_by not in reqs:
            add("inventory", f"DataModel '{dm.id}' declassified_by unknown requirement '{dm.declassified_by}'")
    for cap in spec.capabilities:
        for x in (cap.interface.request, cap.interface.response) if cap.interface else ():
            if x and x not in models: add("inventory", f"Capability '{cap.id}' interface references unknown data model '{x}'")

    # discovery: capability contracts
    need("discovery", "specified", [("Capability", spec.capabilities)])
    for cap in spec.capabilities:
        if not ((cap.preconditions or cap.postconditions) and cap.invariants and cap.failure_modes):
            add("discovery", f"Capability '{cap.id}' has incomplete contract clauses")

    # architecture: composition, data, interfaces, budgets
    need("architecture", "specified", [("Component", spec.components)])
    b = spec.system.context_budget
    for c in spec.components:
        if not c.provides: add("architecture", f"Component '{c.id}' must provide at least one capability")
        if layers and c.layer not in layers: add("architecture", f"Component '{c.id}' has undeclared layer '{c.layer}'")
        for f, n in [("provides", b.max_provides), ("requires", b.max_requires), ("owns_data", b.max_owns_data)]:
            if len(getattr(c, f)) > n: add("architecture", f"Component '{c.id}' exceeds context budget: {f} > {n}", "context-budget", c.id)
        for ref in c.requires:
            p, err = _resolve(spec, c, ref)
            if err: add("architecture", f"Component '{c.id}' has {err}")
            elif c.layer in layers and comps[p].layer in layers and layers[c.layer] > layers[comps[p].layer]:
                add("architecture", f"Component '{c.id}' has layer violation depending on '{p}'", "layer-violation", c.id, p)
    for cy in _cycles({k: list(v.values()) for k, v in resolved.items()}):
        add("architecture", f"Dependency cycle: {' -> '.join(cy)}", "dependency-cycle", *cy)
    for dm in spec.data_models:
        if dm.owner in comps and dm.id not in comps[dm.owner].owns_data:
            add("architecture", f"DataModel '{dm.id}' owner '{dm.owner}' does not list it in owns_data")
        for c in spec.components:
            if dm.id in c.owns_data and c.id != dm.owner:
                add("architecture", f"DataModel '{dm.id}' is also claimed by '{c.id}'", "shared-data-ownership", dm.id, c.id, dm.owner)
        for x in dm.derived_from:
            if x in models and dm.declassified_by not in active and RANK[dm.classification] < RANK[models[x].classification]:
                add("architecture", f"DataModel '{dm.id}' violates classification propagation from '{x}'")
    for cap in spec.capabilities:
        if cap.id in required and not cap.interface: add("architecture", f"Capability '{cap.id}' is required cross-component but has no interface")
        if cap.interface and set(cap.interface.errors) != set(cap.failure_modes):
            add("architecture", f"Capability '{cap.id}' interface errors must map exactly its failure_modes")

    # verification: requirements
    need("verification", "specified", [("Requirement", active.values())])
    targeted = {r.target for r in active.values()}
    for cap in spec.capabilities:
        if cap.status != "deprecated" and cap.id not in targeted: add("verification", f"Capability '{cap.id}' has no associated requirements")
    missing = [c for c in CATEGORIES if c not in {r.category for r in active.values()}]
    if missing: add("verification", f"Missing verification categories: {missing}", "verification-category", sid)
    for cy in _cycles({r.id: [*r.depends_on, *r.refines] for r in spec.requirements}):
        add("verification", f"Requirement cycle: {' -> '.join(cy)}")
    for r in active.values():
        for x in r.conflicts_with:
            if x in active and r.resolved_by not in active and active[x].resolved_by not in active:
                add("verification", f"Requirement '{r.id}' has unresolved conflict with '{x}'")

    # release: status, evidence, risk disposition, no waivers
    need("release", "verified", [("System", [spec.system]), ("Capability", spec.capabilities), ("Component", spec.components)])
    need("release", "verified", [("Requirement", active.values())])
    mitig = {m for k in spec.risks for m in k.mitigated_by}
    oblig = {r.id for r in active.values() if r.mandatory} | {d.declassified_by for d in spec.data_models} | {r.resolved_by for r in active.values()}
    for r in active.values():
        if r.id in oblig and (r.id, r.version) in failed: add("release", f"Requirement '{r.id}@{r.version}' has unresolved failing evidence")
        elif r.id in oblig and r.id not in ok: add("release", f"Requirement '{r.id}@{r.version}' missing valid verification evidence")
        if r.id in oblig | mitig:
            for d in r.depends_on:
                if d in reqs and d not in ok: add("release", f"Requirement '{r.id}' depends on unverified requirement '{d}'")
    for k in spec.risks:
        if k.treatment in ("mitigation", "avoidance") and not k.mitigated_by: add("release", f"Risk '{k.id}' has no mitigating requirements")
        for m in k.mitigated_by:
            if m in reqs and m not in ok: add("release", f"Risk '{k.id}' has unverified mitigation '{m}'")
        if k.treatment == "avoidance" and k.residual_accepted: add("release", f"Risk '{k.id}' is avoided and must not carry residual risk")
        if k.treatment == "transfer" and not k.transferred_to: add("release", f"Risk '{k.id}' requires transferred_to")
        if k.treatment in ("acceptance", "transfer") and not k.residual_accepted: add("release", f"Risk '{k.id}' requires residual_accepted")
        if k.waives: add("release", f"Risk '{k.id}' waives '{k.waives}'; no waivers permitted at release")

    s, ws = STAGES.index(stage), active_waivers(spec, stage, today)
    return [m for st, m, w, sub in E if st <= s and not (w and any(k.waives == w and k.target in sub | {sid} for k in ws))]

def _breaking(errs: list[str], old: str, new: str) -> list[str]:
    o, n = _ver(old), _ver(new)
    return errs + ([f"Breaking change requires major version bump ({old} -> {new})"] if errs and (not o or not n or n[0] <= o[0]) else [])

def check_compatibility(old: Capability, new: Capability) -> list[str]:
    return _breaking([f"{msg}: {sorted(diff)}" for diff, msg in [
        (set(new.preconditions) - set(old.preconditions), "Strengthened preconditions"),
        (set(old.postconditions) - set(new.postconditions), "Removed postconditions"),
        (set(old.invariants) - set(new.invariants), "Removed invariants"),
        (set(new.failure_modes) - set(old.failure_modes), "Added failure modes"),
    ] if diff], old.version, new.version)

def check_data_compatibility(old: DataModel, new: DataModel) -> list[str]:
    errs = [f"{msg}: {sorted(diff)}" for diff, msg in [
        (set(old.fields) - set(new.fields), "Removed fields"),
        ({f for f, t in old.fields.items() if new.fields.get(f, t) != t}, "Changed field types"),
    ] if diff]
    if old.classification != new.classification: errs.append(f"Changed classification ({old.classification} -> {new.classification})")
    return _breaking(errs, old.version, new.version)

def compare_specs(old: Spec, new: Spec) -> list[str]:
    caps, dms = {c.id: c for c in new.capabilities}, {d.id: d for d in new.data_models}
    return [f"Capability '{c.id}': {e}" for c in old.capabilities for e in (
        check_compatibility(c, caps[c.id]) if c.id in caps else [] if c.status == "deprecated" else ["removed without deprecation"])] + [
        f"DataModel '{d.id}': {e}" for d in old.data_models if d.id in dms for e in check_data_compatibility(d, dms[d.id])]

def context_slice(spec: Spec, cid: str) -> dict:
    c = next(x for x in spec.components if x.id == cid)
    capids = set(c.provides) | {r.partition("@^")[0] for r in c.requires}
    caps = [x for x in spec.capabilities if x.id in capids]
    dms = set(c.owns_data) | {x for cap in caps if cap.interface for x in (cap.interface.request, cap.interface.response) if x}
    ids = {cid, *capids, *dms}
    return Spec(system=spec.system, components=[c], capabilities=caps, data_models=[d for d in spec.data_models if d.id in dms],
                requirements=[r for r in spec.requirements if r.target in ids], risks=[k for k in spec.risks if k.target in ids]
                ).model_dump(mode="json", exclude_defaults=True)

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
    ap.add_argument("--stage", choices=STAGES, default="release", help="validation stage (default: release)")
    ap.add_argument("--compat", metavar="OLD", help="check compatibility of OLD spec's capabilities and data models with spec")
    ap.add_argument("--impact", metavar="ID", help="change-impact analysis for ID")
    ap.add_argument("--context", metavar="COMPONENT", help="print the component's spec slice")
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
        if a.context:
            if a.context not in {c.id for c in spec.components}: out = {"valid": False, "errors": [f"Unknown --context component '{a.context}'"]}
            else:
                sl = context_slice(spec, a.context)
                print(json.dumps(sl, indent=2) if a.json else yaml.safe_dump(sl, sort_keys=False, default_flow_style=None), end=""); return 0
        elif a.impact: out = impact_analysis(spec, a.impact) if a.impact in known else {"valid": False, "errors": [f"Unknown --impact ID '{a.impact}'"]}
        else:
            errs = validate_spec(spec, a.stage) + (compare_specs(old, spec) if old else [])
            out = {"valid": not errs, "stage": a.stage, "errors": errs, "residual_risks": residual_risks(spec),
                   "waivers": [k.id for k in active_waivers(spec, a.stage)]}
    if a.json: print(json.dumps(out, indent=2))
    elif "valid" not in out: print("\n".join(f"{k}: {', '.join(v)}" for k, v in out.items()))
    else: print("VALID" if out["valid"] else "\n".join(out.get("errors") or out["schema_errors"]))
    return 0 if out.get("valid", True) else 1

if __name__ == "__main__":
    sys.exit(main())

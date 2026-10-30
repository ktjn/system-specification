from __future__ import annotations
import argparse, json, sys, yaml
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Literal, get_args
from pydantic import BaseModel, Field, ValidationError, model_validator

RANK = {"public": 0, "internal": 1, "confidential": 2, "restricted": 3}
Status = Literal["draft", "specified", "verified", "deprecated"]
STAGES = ("inventory", "discovery", "architecture", "verification", "release")
Category = Literal["functional", "semantic", "contract", "serialization", "concurrency",
                   "performance", "scalability", "resilience", "security", "observability"]
CATEGORIES = get_args(Category)

class ContextBudget(BaseModel):
    model_config = {"extra": "forbid"}
    max_provides: int = Field(default=5, ge=0, strict=True)
    max_requires: int = Field(default=8, ge=0, strict=True)
    max_owns_data: int = Field(default=4, ge=0, strict=True)

class Interface(BaseModel):
    model_config = {"extra": "forbid"}
    endpoint: str
    mode: Literal["sync", "async"]
    request: str
    response: str
    idempotency: bool = Field(strict=True)
    security: str
    failure_statuses: dict[str, str]

    @model_validator(mode="after")
    def clauses(self):
        if not all(s.strip() for s in [self.endpoint, self.request, self.response, self.security,
                                       *self.failure_statuses, *self.failure_statuses.values()]):
            raise ValueError("interface clauses must be non-empty")
        return self

class SystemDef(BaseModel):
    id: str
    version: str
    status: Status = "draft"
    layers: list[str] = []
    external_sources: list[str] = []
    quality_attributes: dict[str, str] = {}
    context_budget: ContextBudget = Field(default_factory=ContextBudget)

class Capability(BaseModel):
    id: str
    version: str
    status: Status = "draft"
    preconditions: list[str] = []
    postconditions: list[str] = []
    invariants: list[str] = []
    failure_modes: list[str] = []
    deprecated: bool = False
    interface: Interface | None = None

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
    category: Category | None = None
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
    waives: str | None = None
    expires: str | None = None

class Evidence(BaseModel):
    id: str
    requirement_id: str
    requirement_version: str
    method: Literal["test", "proof", "model-check", "analysis", "inspection"]
    passed: bool
    provenance: str
    subject_id: str | None = None
    subject_revision: str | None = None
    timestamp: datetime | None = None
    verifier: str | None = None
    bounds: str | None = None
    supersedes: str | None = None
    supersession_reason: str | None = None

    @model_validator(mode="after")
    def metadata(self):
        if (self.subject_id is None) != (self.subject_revision is None):
            raise ValueError("subject_id and subject_revision must be supplied together")
        if self.method == "model-check" and not (self.bounds and self.bounds.strip()):
            raise ValueError("model-check evidence requires bounds")
        if self.supersedes and not (self.supersession_reason and self.supersession_reason.strip()):
            raise ValueError("supersession requires a reason")
        if self.timestamp and self.timestamp.utcoffset() is None:
            raise ValueError("timestamp must include a timezone")
        return self

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

def evaluate_evidence(spec: Spec, release: bool = False) -> tuple[set[tuple[str, str]], set[tuple[str, str]], list[str]]:
    errs, edges, usable, stale = [], {}, [], []
    records = {e.id: e for e in spec.evidence}
    reqs = {r.id: r for r in spec.requirements}
    subjects = [spec.system, *spec.components, *spec.capabilities, *spec.data_models]
    key = lambda e: (e.requirement_id, e.requirement_version, e.subject_id, e.subject_revision)
    for e in spec.evidence:
        if e.supersedes:
            old = records.get(e.supersedes)
            if not old or old.id == e.id or key(old) != key(e) or not e.passed or not (e.supersession_reason and e.supersession_reason.strip()):
                errs.append(f"Evidence '{e.id}' has invalid supersession '{e.supersedes}'")
            else: edges[e.id] = [old.id]
        r = reqs.get(e.requirement_id)
        if e.subject_id is not None:
            matches = [x for x in subjects if x.id == e.subject_id]
            if not r or e.subject_id != r.target or len(matches) != 1:
                errs.append(f"Evidence '{e.id}' subject does not match requirement target")
                continue
            if e.subject_revision != matches[0].version:
                stale.append(e)
                continue
        usable.append(e)
    cycles = _cycles(edges)
    errs += [f"Evidence supersession cycle: {' -> '.join(cy)}" for cy in cycles]
    cyclic = {eid for cy in cycles for eid in cy}
    superseded = {old for new, olds in edges.items() if new not in cyclic for old in olds}
    ev: dict[tuple[str, str], list[bool]] = {}
    for e in usable:
        if e.id in superseded: continue
        r = reqs.get(e.requirement_id)
        complete = not release or not r or r.status == "deprecated" or r.version != e.requirement_version or (
            e.subject_id is not None and e.timestamp is not None and bool(e.verifier and e.verifier.strip()) and bool(e.provenance.strip()))
        if not complete: errs.append(f"Evidence '{e.id}' lacks required release evidence metadata")
        ev.setdefault((e.requirement_id, e.requirement_version), []).append(e.passed and complete)
    verified = {k for k, v in ev.items() if all(v)}
    errs += [f"Evidence '{e.id}' has stale subject revision '{e.subject_revision}'" for e in stale
             if reqs[e.requirement_id].version == e.requirement_version and (e.requirement_id, e.requirement_version) not in verified]
    return verified, {k for k, v in ev.items() if not all(v)}, errs


def verified_requirements(spec: Spec) -> set[tuple[str, str]]:
    return evaluate_evidence(spec)[0]

def identity_errors(spec: Spec) -> list[str]:
    return [f"Duplicate {kind} id '{i}'"
            for kind, xs in [("capability", spec.capabilities), ("component", spec.components),
                             ("data model", spec.data_models), ("requirement", spec.requirements),
                             ("risk", spec.risks), ("evidence", spec.evidence)]
            for i, n in Counter(x.id for x in xs).items() if n > 1]


def validate_early_stage(spec: Spec, stage: str) -> list[str]:
    errs = identity_errors(spec)
    plain = lambda s: bool(s.strip()) and s == s.strip() and "@^" not in s
    entities = [spec.system, *spec.components, *spec.capabilities, *spec.data_models,
                *spec.requirements, *spec.risks, *spec.evidence]
    refs = [x.id for x in entities] + spec.system.layers + spec.system.external_sources
    refs += [x.target for x in [*spec.requirements, *spec.risks]]
    for c in spec.components:
        refs += c.provides + c.owns_data + list(c.bindings) + list(c.bindings.values())
        if c.layer is not None: refs.append(c.layer)
        for ref in c.requires:
            name, sep, version = ref.partition("@^")
            if not plain(name) or (sep and not all(p.isdecimal() for p in version.split("."))):
                errs.append(f"Component '{c.id}' has invalid reference syntax '{ref}'")
    for d in spec.data_models:
        refs += [d.owner, *d.derived_from]
        if d.external_source is not None: refs.append(d.external_source)
    for r in spec.requirements:
        refs += r.depends_on + r.refines + r.conflicts_with
        if r.resolved_by is not None: refs.append(r.resolved_by)
    for r in spec.risks: refs += r.mitigated_by
    for e in spec.evidence:
        refs.append(e.requirement_id)
        if e.subject_id is not None: refs.append(e.subject_id)
        if e.supersedes is not None: refs.append(e.supersedes)
    errs += [f"Invalid identity/reference syntax '{ref}'" for ref in refs if not plain(ref)]
    if stage == "discovery":
        for cap in spec.capabilities:
            if cap.status == "draft": errs.append(f"Capability '{cap.id}' requires specified status at discovery")
            for name, clauses in [("preconditions or postconditions", cap.preconditions + cap.postconditions),
                                  ("invariants", cap.invariants), ("failure_modes", cap.failure_modes)]:
                if not any(clause.strip() for clause in clauses):
                    errs.append(f"Capability '{cap.id}' has empty contract {name}")
    return errs


def composition_errors(spec: Spec) -> list[str]:
    errs, resolved = [], resolve_capabilities(spec)
    comps = {c.id: c for c in spec.components}
    caps = {c.id for c in spec.capabilities}
    models = {d.id: d for d in spec.data_models}
    layers = {l: i for i, l in enumerate(spec.system.layers)}
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


def validate_architecture(spec: Spec) -> list[str]:
    errs = validate_early_stage(spec, "discovery") + composition_errors(spec)
    provided = {p for c in spec.components for p in c.provides}
    models = {d.id for d in spec.data_models}
    for c in spec.components:
        if c.status == "draft": errs.append(f"Component '{c.id}' requires specified status at architecture")
        for field in ("provides", "requires", "owns_data"):
            limit = getattr(spec.system.context_budget, f"max_{field}")
            if len(getattr(c, field)) > limit:
                errs.append(f"Component '{c.id}' exceeds context budget max_{field}={limit}")
    for cap in spec.capabilities:
        interface = cap.interface
        if interface is None:
            if cap.id in provided: errs.append(f"Capability '{cap.id}' has missing interface")
            continue
        for field in ("request", "response"):
            ref = getattr(interface, field)
            if ref not in models: errs.append(f"Capability '{cap.id}' interface has unknown {field} data model '{ref}'")
        for failure in cap.failure_modes:
            if failure not in interface.failure_statuses:
                errs.append(f"Capability '{cap.id}' interface has unmapped failure mode '{failure}'")
        for failure in interface.failure_statuses:
            if failure not in cap.failure_modes:
                errs.append(f"Capability '{cap.id}' interface maps unknown failure mode '{failure}'")
    return errs


def requirement_errors(spec: Spec, require_evidence: bool = True, release: bool = False) -> list[str]:
    errs = []
    reqs = {r.id: r for r in spec.requirements}
    active = {r.id: r for r in spec.requirements if r.status != "deprecated"}
    verified, failed, _ = evaluate_evidence(spec, release=release)
    ok = {r.id for r in active.values() if (r.id, r.version) in verified}
    required = {r.id for r in active.values() if r.mandatory}
    if release:
        required |= {m for risk in spec.risks if risk.treatment in ("mitigation", "avoidance") for m in risk.mitigated_by}
        required |= {r.resolved_by for r in active.values() if r.resolved_by}
        while new := {d for rid in required if rid in active for d in active[rid].depends_on} - required:
            required |= new
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
        if require_evidence and r.id in required and (r.id, r.version) in failed:
            errs.append(f"Requirement '{r.id}@{r.version}' has unresolved failing evidence")
        elif require_evidence and r.id in required and r.id not in ok:
            errs.append(f"Requirement '{r.id}@{r.version}' missing valid verification evidence")
        if require_evidence and r.id in required:
            errs += [f"Requirement '{r.id}' depends on unverified requirement '{d}'" for d in r.depends_on if d in reqs and d not in ok]
        for cid in r.conflicts_with:
            if cid in active and not any(
                q and q.id not in {r.id, cid} and q.id in ok and any(c.strip() for c in q.criteria)
                and {r.id, cid} <= set(q.refines)
                for q in (active.get(r.resolved_by), active.get(active[cid].resolved_by))
            ):
                errs.append(f"Requirement '{r.id}' has unresolved conflict with '{cid}'")
    errs += [f"Evidence '{e.id}' references unknown requirement '{e.requirement_id}'" for e in spec.evidence if e.requirement_id not in reqs]
    return errs


def target_errors(spec: Spec) -> list[str]:
    errs = []
    comps = {c.id for c in spec.components}
    caps = {c.id for c in spec.capabilities}
    models = {d.id for d in spec.data_models}
    targets = {"system": {spec.system.id}, "component": set(comps), "capability": caps, "data model": set(models)}

    for kind, xs in [("Requirement", spec.requirements), ("Risk", spec.risks)]:
        for x in xs:
            m = [t for t, ids in targets.items() if x.target in ids]
            if len(m) != 1: errs.append(f"{kind} '{x.id}' has {'ambiguous' if m else 'unknown'} target '{x.target}'")

    return errs


def validate_verification(spec: Spec) -> list[str]:
    errs = validate_architecture(spec) + target_errors(spec) + requirement_errors(spec, require_evidence=False)
    errs += evaluate_evidence(spec)[2]
    active = [r for r in spec.requirements if r.status != "deprecated"]
    reqs = {r.id for r in spec.requirements}
    for risk in spec.risks:
        errs += [f"Risk '{risk.id}' references unknown requirement '{m}'" for m in risk.mitigated_by if m not in reqs]
    for r in active:
        if r.status == "draft": errs.append(f"Requirement '{r.id}' requires specified status at verification")
        if not any(c.strip() for c in r.criteria): errs.append(f"Requirement '{r.id}' has empty acceptance criteria")
        if r.category is None: errs.append(f"Requirement '{r.id}' has missing category")
        else:
            kind = "functional" if r.category in CATEGORIES[:5] else "non-functional"
            if r.kind != kind: errs.append(f"Requirement '{r.id}' category requires kind '{kind}'")
    for cap in spec.capabilities:
        scope = {cap.id, spec.system.id, *(c.id for c in spec.components if cap.id in c.provides)}
        if cap.interface: scope.update([cap.interface.request, cap.interface.response])
        covered = {r.category for r in active if r.target in scope and any(c.strip() for c in r.criteria)}
        errs += [f"Capability '{cap.id}' has missing verification category '{category}'" for category in CATEGORIES if category not in covered]
    return errs


def validate_spec(spec: Spec, stage: str | None = None) -> list[str]:
    if stage is not None:
        if stage not in STAGES: raise ValueError(f"Unsupported stage '{stage}'")
        if stage == "release":
            errs = validate_verification(spec) + requirement_errors(spec, release=True)
            errs += evaluate_evidence(spec, release=True)[2] + risk_errors(spec, release=True)
            errs += [f"Entity '{x.id}' requires verified status at release"
                     for x in [spec.system, *spec.capabilities, *spec.components, *spec.requirements]
                     if x.status not in ("verified", "deprecated")]
            errs += [f"Risk '{r.id}': waivers are not permitted at release" for r in spec.risks if r.waives is not None]
            return list(dict.fromkeys(errs))
        if stage == "verification": return validate_verification(spec)
        return validate_architecture(spec) if stage == "architecture" else validate_early_stage(spec, stage)
    return (evaluate_evidence(spec)[2] + identity_errors(spec) + target_errors(spec)
            + composition_errors(spec) + requirement_errors(spec) + risk_errors(spec))


def risk_errors(spec: Spec, release: bool = False) -> list[str]:
    errs = []
    reqs = {r.id: r for r in spec.requirements}
    verified, _, _ = evaluate_evidence(spec, release=release)
    active = {r.id: r for r in spec.requirements if r.status != "deprecated"}
    ok = {r.id for r in active.values() if (r.id, r.version) in verified}
    for risk in spec.risks:
        if risk.treatment in ("mitigation", "avoidance"):
            if not risk.mitigated_by: errs.append(f"Risk '{risk.id}' has no mitigating requirements")
            errs += [f"Risk '{risk.id}' references unknown requirement '{m}'" for m in risk.mitigated_by if m not in reqs]
            errs += [f"Risk '{risk.id}' has unverified mitigation '{m}'" for m in risk.mitigated_by if m in reqs and m not in ok]
        if risk.treatment == "avoidance" and risk.residual_accepted:
            errs.append(f"Risk '{risk.id}' is avoided and must not carry residual risk")
        if risk.treatment == "transfer" and not (risk.transferred_to and risk.transferred_to.strip()):
            errs.append(f"Risk '{risk.id}' requires transferred_to")
        if risk.treatment in ("acceptance", "transfer") and not risk.residual_accepted:
            errs.append(f"Risk '{risk.id}' requires residual_accepted")
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
        todo += [c.id for c in spec.components if x in {r.partition("@^")[0] for r in c.requires} or x in c.provides]
        todo += [c.id for c in spec.capabilities if c.interface and x in {c.interface.request, c.interface.response}]
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
    ap.add_argument("--stage", choices=STAGES, help="validate an implemented lifecycle stage")
    a = ap.parse_args(argv)
    if a.stage and (a.impact or a.compat or a.schema):
        ap.error("cannot combine --stage with --impact, --compat or --schema")
    if a.schema:
        print(json.dumps(Spec.model_json_schema(), indent=2)); return 0
    try:
        spec = load_spec(a.spec)
        old = load_spec(a.compat) if a.compat else None
    except (OSError, yaml.YAMLError, ValidationError) as e:
        out = {"valid": False, "schema_errors": [str(e)]}
    else:
        if a.stage:
            errs = validate_spec(spec, stage=a.stage)
            out = {"valid": not errs, "errors": errs, "stage": a.stage}
        else:
            known = {spec.system.id, *(x.id for x in spec.capabilities + spec.components + spec.data_models + spec.requirements)}
            out = {"valid": False, "errors": [f"Unknown --impact ID '{a.impact}'"]} if a.impact and a.impact not in known else impact_analysis(spec, a.impact) if a.impact else {"valid": not (errs := validate_spec(spec) + (compare_specs(old, spec) if old else [])), "errors": errs, "residual_risks": residual_risks(spec)}
    if a.json: print(json.dumps(out, indent=2))
    elif a.impact and "errors" not in out: print("\n".join(f"{k}: {', '.join(v)}" for k, v in out.items()))
    else: print("VALID" if out["valid"] else "\n".join(out.get("errors") or out["schema_errors"]))
    return 0 if out.get("valid", True) else 1

if __name__ == "__main__":
    sys.exit(main())

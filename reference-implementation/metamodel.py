from __future__ import annotations
import json, sys, yaml
from pathlib import Path
from typing import Literal
from pydantic import BaseModel

RANK = {"public": 0, "internal": 1, "confidential": 2, "restricted": 3}

class SystemDef(BaseModel):
    id: str
    version: str
    layers: list[str] = []
    external_sources: list[str] = []
    quality_attributes: dict[str, str] = {}

class Capability(BaseModel):
    id: str
    version: str
    preconditions: list[str] = []
    postconditions: list[str] = []
    invariants: list[str] = []
    failure_modes: list[str] = []
    deprecated: bool = False

class Component(BaseModel):
    id: str
    version: str
    layer: str | None = None
    consistency: Literal["strong", "eventual"] = "strong"
    provides: list[str] = []
    requires: list[str] = []
    owns_data: list[str] = []

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
    target: str
    kind: Literal["functional", "non-functional"] = "functional"
    mandatory: bool = True
    criteria: list[str]
    depends_on: list[str] = []
    refines: list[str] = []
    conflicts_with: list[str] = []

class Risk(BaseModel):
    id: str
    target: str
    treatment: Literal["mitigation", "acceptance", "avoidance", "transfer"]
    mitigated_by: list[str] = []
    residual_accepted: bool = False

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

def _ver_ok(req: str | None, act: str) -> bool:
    if not req: return True
    r, a = [int(x) for x in req.split(".")], [int(x) for x in act.split(".")]
    return r[0] == a[0] and a[1:] >= r[1:]

def resolve_capabilities(spec: Spec) -> dict[str, dict[str, str]]:
    caps = {c.id: c for c in spec.capabilities}
    prov = {cap: c.id for c in spec.components for cap in c.provides}
    return {
        c.id: {
            k: prov[k] for ref in c.requires
            for k, _, v in [ref.partition("@^")]
            if k in caps and k in prov and _ver_ok(v, caps[k].version)
        }
        for c in spec.components
    }

def validate_spec(spec: Spec) -> list[str]:
    errs, resolved = [], resolve_capabilities(spec)
    comps = {c.id: c for c in spec.components}
    reqs = {r.id: r for r in spec.requirements}
    models = {d.id: d for d in spec.data_models}
    layers = {l: i for i, l in enumerate(spec.system.layers)}
    valid_ev = {(e.requirement_id, e.requirement_version) for e in spec.evidence if e.passed}
    req_targets = {r.target for r in spec.requirements}

    for c in spec.components:
        if not c.provides:
            errs.append(f"Component '{c.id}' must provide at least one capability")
        for ref in c.requires:
            cap_id = ref.partition("@^")[0]
            p = resolved[c.id].get(cap_id)
            if not p:
                errs.append(f"Component '{c.id}' has unresolved capability '{ref}'")
            elif c.layer in layers and comps[p].layer in layers and layers[c.layer] > layers[comps[p].layer]:
                errs.append(f"Component '{c.id}' has layer violation depending on '{p}'")

    for cap in spec.capabilities:
        if cap.id not in req_targets:
            errs.append(f"Capability '{cap.id}' has no associated requirements")
    for r in spec.requirements:
        if r.mandatory and (r.id, r.version) not in valid_ev:
            errs.append(f"Requirement '{r.id}@{r.version}' missing valid verification evidence")
        for cid in r.conflicts_with:
            if cid in reqs:
                errs.append(f"Requirement '{r.id}' has unresolved conflict with '{cid}'")
    for risk in spec.risks:
        if risk.treatment == "mitigation" and (not risk.mitigated_by or any(m not in reqs for m in risk.mitigated_by)):
            errs.append(f"Risk '{risk.id}' has unverified mitigation")
        if risk.treatment == "acceptance" and not risk.residual_accepted:
            errs.append(f"Risk '{risk.id}' requires residual_accepted")
    for dm in spec.data_models:
        if dm.external_source and dm.external_source not in spec.system.external_sources:
            errs.append(f"DataModel '{dm.id}' has untracked external data source '{dm.external_source}'")
        for s in dm.derived_from:
            if s not in models or RANK[dm.classification] < RANK[models[s].classification]:
                errs.append(f"DataModel '{dm.id}' violates classification propagation from '{s}'")
    return errs

def check_compatibility(old: Capability, new: Capability) -> list[str]:
    return [
        msg for cond, msg in [
            (set(new.preconditions) - set(old.preconditions), "Strengthened preconditions"),
            (set(old.postconditions) - set(new.postconditions), "Removed postconditions"),
            (set(old.invariants) - set(new.invariants), "Removed invariants"),
        ] if cond
    ]

def impact_analysis(spec: Spec, target_id: str) -> dict[str, list[str]]:
    comps = [c.id for c in spec.components if target_id in c.provides or any(r.partition("@^")[0] == target_id for r in c.requires)]
    reqs = [r.id for r in spec.requirements if r.target in {target_id, *comps}]
    return {
        "components": comps,
        "requirements": reqs,
        "invalidated_evidence": [e.id for e in spec.evidence if e.requirement_id in reqs],
    }

def load_spec(path: str | Path) -> Spec:
    return Spec.model_validate(yaml.safe_load(Path(path).read_text(encoding="utf-8")))

if __name__ == "__main__":
    if "--schema" in sys.argv:
        print(json.dumps(Spec.model_json_schema(), indent=2))
    else:
        errs = validate_spec(load_spec(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "example.yaml"))
        print("VALID" if not errs else "\n".join(errs))
        sys.exit(bool(errs))

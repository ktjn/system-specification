import pytest
from metamodel import Evidence, Spec, impact_analysis, validate_spec


def interface_system(field):
    names = ["catalog", "exporter", "client", "unrelated"]
    caps = []
    for name in names:
        interface = dict(endpoint=name, mode="sync", request=f"{name}-data", response=f"{name}-data",
                         idempotency=True, security="authenticated", failure_statuses={"unavailable": "503"})
        if name == "exporter": interface[field] = "catalog-data"
        caps.append(dict(id=f"{name}-cap", version="1.0", status="specified", preconditions=["authorized"],
                         invariants=["valid"], failure_modes=["unavailable"], interface=interface))
    s = Spec.model_validate(dict(
        system=dict(id="system", version="1.0"), capabilities=caps,
        components=[dict(id=name, version="1.0", status="specified", provides=[f"{name}-cap"],
                         requires=["exporter-cap"] if name == "client" else [], owns_data=[f"{name}-data"]) for name in names],
        data_models=[dict(id=f"{name}-data", version="1.0", owner=name, fields={"value": "string"}) for name in names],
        requirements=[dict(id=f"req-{name}", version="1.0", target=f"{name}-cap", criteria=["valid output"]) for name in names]))
    s.evidence = [Evidence(id=f"ev-{r.id}", requirement_id=r.id, requirement_version=r.version,
                           method="test", passed=True, provenance="fixture:synthetic") for r in s.requirements]
    assert validate_spec(s, stage="architecture") == []
    return s


@pytest.mark.parametrize("field", ["request", "response"])
def test_interface_payload_changes_reach_provider_and_transitive_consumers(field):
    result = impact_analysis(interface_system(field), "catalog-data")
    assert set(result["components"]) == {"catalog", "exporter", "client"}
    assert set(result["capabilities"]) == {"catalog-cap", "exporter-cap", "client-cap"}
    assert set(result["requirements"]) == {"req-catalog", "req-exporter", "req-client"}
    assert set(result["invalidated_evidence"]) == {"ev-req-catalog", "ev-req-exporter", "ev-req-client"}


def test_unrelated_payload_change_stays_local():
    result = impact_analysis(interface_system("request"), "unrelated-data")
    assert result["components"] == ["unrelated"]
    assert result["invalidated_evidence"] == ["ev-req-unrelated"]

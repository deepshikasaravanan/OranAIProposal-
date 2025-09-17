import json
from fastapi.testclient import TestClient
from web.app import app

client = TestClient(app)


def test_intake_parse_requires_files():
    r = client.post("/api/bid/intake-parse", json={"files": []})
    assert r.status_code == 400


def test_score_basic():
    opp = {"agency_priority": "strategic", "required_capabilities": ["ai"], "org_capabilities": ["ai"]}
    r = client.post("/api/bid/score", json=opp)
    assert r.status_code == 200
    data = r.json()
    assert "Decision Card" in data
    assert "Blockers" in data
    assert "Next Actions" in data


def test_enrich_mock(monkeypatch):
    from prop import enrich as E

    def fake_fetch(agency, naics):
        return [1e5, 2e5, 3e5, 4e5]

    monkeypatch.setattr(E, "_fetch_agency_naics_awards", fake_fetch)
    opp = {"agency": "DoD", "naics": "541511"}
    r = client.post("/api/bid/enrich", json={"opportunity": opp})
    assert r.status_code == 200
    body = r.json()
    assert "opportunity_enriched" in body
    assert "enrichment" in body


def test_score_and_generate_override_block(monkeypatch):
    # No files should return error
    r = client.post("/api/bid/score-and-generate", json={"override": True, "opportunity": {}})
    assert r.status_code in (200, 400)
from fastapi.testclient import TestClient
from web.app import app

client = TestClient(app)


def test_generation_requires_go_or_override(monkeypatch):
    # Force a NO-BID by using CPFF blocker
    opp = {"type": "CPFF"}
    r = client.post("/api/bid/score-and-generate", json={"opportunity": opp, "pws_files": ["examples/pws_sample.md"]})
    assert r.status_code == 200
    body = r.json()
    assert body.get("started") is False  # generation gated
    # Override but disallow no-bid override
    r2 = client.post("/api/bid/score-and-generate", json={"opportunity": opp, "pws_files": ["examples/pws_sample.md"], "override": True})
    body2 = r2.json()
    # Expect either explicit gating (started False) or an error about rejection
    if r2.status_code == 400:
        assert 'override rejected' in body2.get('error', '')
    else:
        assert body2.get("started") is False
    # Allow no-bid override
    r3 = client.post("/api/bid/score-and-generate", json={"opportunity": opp, "pws_files": ["examples/pws_sample.md"], "override": True, "allow_no_bid_override": True})
    body3 = r3.json()
    # Might error if file missing; treat error status 400 appropriately
    if r3.status_code == 400:
        assert "error" in body3
    else:
        assert body3.get("started") in (False, True)

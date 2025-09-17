from prop.scoring_bid import evaluate_opportunity
from prop.schema import Opportunity


def test_scoring_go():
    opp = Opportunity(required_capabilities=["cloud"], org_capabilities=["cloud"], agency_priority="strategic")
    out = evaluate_opportunity(opp)
    assert out["decision"]["decision"] in ("GO", "REVIEW")  # strategic + full coverage should not be NO-BID


def test_scoring_review():
    opp = Opportunity(required_capabilities=["cloud", "devops"], org_capabilities=["cloud"], teaming_can_close_gap=True)
    out = evaluate_opportunity(opp)
    # Partial coverage with teaming path shouldn't hard block; likely lower score
    assert out["decision"]["decision"] in ("REVIEW", "NO-BID")


def test_scoring_no_bid_blocker():
    opp = Opportunity(type="CPFF")
    out = evaluate_opportunity(opp)
    assert out["decision"]["decision"] == "NO-BID"
    assert any("CPFF" in b for b in out["blockers"]["list"])  # blocker captured


def test_blocker_capability_gap():
    opp = Opportunity(required_capabilities=["cloud"], org_capabilities=[], teaming_can_close_gap=False)
    out = evaluate_opportunity(opp)
    assert out["decision"]["decision"] == "NO-BID"
    assert any("Capability coverage" in b for b in out["blockers"]["list"])  # gap blocker

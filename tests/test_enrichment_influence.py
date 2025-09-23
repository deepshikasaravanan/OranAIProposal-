from prop.scoring_bid import evaluate_opportunity
from prop.schema import Opportunity


def test_enrichment_competitor_effect():
    opp = Opportunity(required_capabilities=["cloud"], org_capabilities=["cloud"], estimated_value_ok=False)
    # Without enrichment competitor_count high should reduce strat score
    out_no = evaluate_opportunity(opp, enrichment={"competitor_count": 12, "estimated_value_ok": True})
    out_low = evaluate_opportunity(opp, enrichment={"competitor_count": 2, "estimated_value_ok": True})
    strat_no = out_no["sections"]["strategy_business_fit"]
    strat_low = out_low["sections"]["strategy_business_fit"]
    # Low competitor count should yield >= +5 relative difference
    assert strat_low >= strat_no + 5
    assert out_no["coverage"]["capability_coverage_pct"] == 100

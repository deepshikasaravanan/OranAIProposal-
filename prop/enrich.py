import requests
from typing import Dict, Any, List, Optional
from .schema import Opportunity
from .utils import env

USASPENDING_BASE = env("USASPENDING_BASE", "https://api.usaspending.gov/api")


def _fetch_agency_naics_awards(agency: Optional[str], naics: Optional[str]) -> List[float]:
    if not agency or not naics:
        return []
    try:
        # This is a simplified query; real USAspending usage may differ.
        url = f"{USASPENDING_BASE}/v2/search/spending_by_award/"
        payload = {
            "filters": {
                "time_period": [{"fy": "2024"}],
                "naics_codes": [naics],
                "agencies": [{"type": "awarding", "tier": "toptier", "name": agency}],
            },
            "fields": ["Award ID", "Award Amount"],
            "page": 1,
            "limit": 100,
            "sort": "Award Amount",
            "order": "desc",
        }
        r = requests.post(url, json=payload, timeout=20)
        r.raise_for_status()
        data = r.json()
        vals = []
        for row in data.get("results", [])[:200]:
            amt = row.get("Award Amount")
            if isinstance(amt, (int, float)):
                vals.append(float(amt))
        return vals
    except Exception:
        return []


def enrich_opportunity(opp: Opportunity) -> Dict[str, Any]:
    amounts = _fetch_agency_naics_awards(opp.agency, opp.naics)
    value_band = {}
    if amounts:
        amounts.sort()
        p10 = amounts[int(0.1 * (len(amounts) - 1))]
        p50 = amounts[int(0.5 * (len(amounts) - 1))]
        p90 = amounts[int(0.9 * (len(amounts) - 1))]
        value_band = {"p10": p10, "p50": p50, "p90": p90}
    protest_risk = "unknown"
    incumbents: List[str] = []  # placeholder; would require vendor aggregation

    # estimated_value_ok heuristic: assume OK if p10..p90 spans mid-market
    estimated_value_ok = True if value_band else None
    competitor_count = None if not amounts else min(10, max(2, int(len(amounts) ** 0.5)))

    enrichment = {
        "incumbents": incumbents,
        "value_band": value_band,
        "protest_risk": protest_risk,
    }
    opp.estimated_value_ok = estimated_value_ok
    opp.competitor_count = competitor_count
    opp.protest_risk = protest_risk
    return {"opportunity_enriched": opp.model_dump(), "enrichment": enrichment}

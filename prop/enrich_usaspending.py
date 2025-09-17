"""USAspending enrichment utilities (Prompt 5).

fetch_award_stats(agency, naics, years=5) -> dict
Returns structure:
{
  'incumbents': [ { 'vendor': str, 'count': int, 'total': float } ... ],
  'value_band': { 'p25': float, 'p50': float, 'p75': float },
  'raw_count': int
}

Notes:
- Public USAspending API; no key required.
- Graceful fallback: on any exception returns empty structures.
- This is a simplified aggregation; real implementations may need pagination & more precise filters.
"""
from __future__ import annotations
import requests
from typing import List, Dict, Any, Optional

BASE = "https://api.usaspending.gov/api"


def _percentile(sorted_vals: List[float], pct: float) -> float:
    if not sorted_vals:
        return 0.0
    idx = int(round(pct * (len(sorted_vals) - 1)))
    return float(sorted_vals[idx])


def fetch_award_stats(agency: Optional[str], naics: Optional[str], years: int = 5) -> Dict[str, Any]:
    if not agency or not naics:
        return {"incumbents": [], "value_band": {}, "raw_count": 0}
    try:
        current_fy = 2025  # TODO: compute from date
        time_period = [{"fy": str(current_fy - i)} for i in range(years)]
        url = f"{BASE}/v2/search/spending_by_award/"
        payload = {
            "filters": {
                "time_period": time_period,
                "naics_codes": [naics],
                "agencies": [{"type": "awarding", "tier": "toptier", "name": agency}],
            },
            "fields": ["Award ID", "Award Amount", "Recipient Name"],
            "page": 1,
            "limit": 250,
            "sort": "Award Amount",
            "order": "desc",
        }
        r = requests.post(url, json=payload, timeout=25)
        r.raise_for_status()
        data = r.json()
        vendors: Dict[str, Dict[str, float]] = {}
        amounts: List[float] = []
        for row in data.get("results", []) or []:
            amt = row.get("Award Amount")
            vendor = row.get("Recipient Name") or "UNKNOWN"
            if isinstance(amt, (int, float)):
                val = float(amt)
                amounts.append(val)
                slot = vendors.setdefault(vendor, {"count": 0, "total": 0.0})
                slot["count"] += 1
                slot["total"] += val
        amounts.sort()
        incumbents = [
            {"vendor": v, "count": meta["count"], "total": round(meta["total"], 2)}
            for v, meta in sorted(vendors.items(), key=lambda kv: (-kv[1]["count"], -kv[1]["total"]))[:10]
        ]
        value_band = {}
        if amounts:
            value_band = {
                "p25": _percentile(amounts, 0.25),
                "p50": _percentile(amounts, 0.50),
                "p75": _percentile(amounts, 0.75),
            }
        return {"incumbents": incumbents, "value_band": value_band, "raw_count": len(amounts)}
    except Exception:
        return {"incumbents": [], "value_band": {}, "raw_count": 0}

__all__ = ["fetch_award_stats"]

"""SAM.gov notice retrieval utilities (Prompt 6).

Implements get_notice(notice_id) using the public search endpoint per spec:
https://api.sam.gov/opportunities/v2/search?noticeId=...&api_key=...

If SAM_API_KEY is missing, returns {"error":"missing_sam_key"} without raising.
Mapping helper converts raw result into an Opportunity skeleton.
"""

from typing import Dict, Any
import requests
from .schema import Opportunity
from .utils import env

SAM_SEARCH = "https://api.sam.gov/opportunities/v2/search"


def get_notice(notice_id: str) -> Dict[str, Any]:
    """Fetch notice JSON via search endpoint filtered by noticeId.

    Returns raw JSON dict or {"error":...}.
    """
    api_key = env("SAM_API_KEY")
    if not api_key:
        return {"error": "missing_sam_key"}
    params = {"limit": 1, "api_key": api_key, "noticeId": notice_id}
    try:
        r = requests.get(SAM_SEARCH, params=params, timeout=25)
        r.raise_for_status()
        return r.json()
    except Exception as e:  # broad: network or JSON errors
        return {"error": str(e)}


def _extract_first_doc(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not payload:
        return {}
    emb = payload.get("_embedded") or {}
    # SAM sometimes uses "results" or "opportunities"; fallback heuristics
    for key in ("results", "opportunity", "notices", "opportunities"):
        val = emb.get(key)
        if isinstance(val, list) and val:
            return val[0]
    # In some cases the document might be at top-level
    return payload


def map_notice_to_opp(payload: Dict[str, Any]) -> Opportunity:
    """Map SAM search payload to Opportunity fields.

    Fields: title, agency, naics, set_aside, type, due_date, vehicle_required=false.
    """
    opp = Opportunity()
    if not payload or payload.get("error"):
        return opp
    doc = _extract_first_doc(payload)
    # Title
    opp.title = (
        doc.get("title")
        or doc.get("noticeTitle")
        or doc.get("subject")
    )
    # Agency / Sub-agency
    agency_obj = doc.get("agency") or {}
    opp.agency = agency_obj.get("name") or doc.get("organizationName") or agency_obj.get("code")
    office_obj = doc.get("office") or {}
    opp.sub_agency = office_obj.get("name") or office_obj.get("code")
    # NAICS (list of {code, ...})
    naics_list = doc.get("naics") or []
    if isinstance(naics_list, list) and naics_list:
        first = naics_list[0]
        if isinstance(first, dict):
            opp.naics = first.get("code") or first.get("naicsCode")
        elif isinstance(first, str):
            opp.naics = first
    # Set-aside
    set_aside_obj = doc.get("setAside") or {}
    if isinstance(set_aside_obj, dict):
        opp.set_aside = set_aside_obj.get("type") or set_aside_obj.get("code")
    else:
        opp.set_aside = set_aside_obj or doc.get("typeOfSetAsideDescription")
    # Contract / notice type (default FFP)
    opp.type = (
        doc.get("contractType")
        or doc.get("typeOfSetAsideDescription")
        or doc.get("typeOfContract")
        or "FFP"
    )
    # Due date (responseDeadLine typical format YYYY-MM-DDTHH:MM...)
    due = doc.get("responseDeadLine") or doc.get("dueDate") or doc.get("archiveDate")
    if isinstance(due, str) and len(due) >= 10:
        opp.due_date = due[:10]
    # Vehicle required explicitly false per spec
    opp.vehicle_required = False
    return opp
 

"""Scoring Engine (Prompt 4)

evaluate_opportunity(opportunity, enrichment=None) -> ScoreOut

Hard blockers (immediate NO-BID):
1. CPFF-only (type == CPFF)  # Spec: CPFF-only (no risk tolerance) – adapt to mark as blocker
2. Vehicle required but not held
3. Capability coverage < 85% and teaming cannot close gap
4. Clearance required and not available
5. Bandwidth/time: active_proposals >= 3 AND days_to_due < 14
6. Page-limit impossible: page_limit < 5 AND days_to_due < 5

Sections scored (0-100 heuristic, then averaged):
- acquisition
- agency_alignment
- technical_fit
- pre_rfp_marketing
- evaluation_factors
- strategy_business_fit
- practical

Role recommendation heuristic:
- classify_naics_tier(): Tier-1 (e.g., NAICS starting with 54, 51) => prime
- otherwise sub (unless capability coverage 100% & value low => prime)

ScoreOut structure:
{
  total: int,
  sections: {section: int},
  role: str,
  blockers: {has_blockers: bool, list: [...]},
  coverage: {capability_coverage_pct: int},
  decision: {decision: str, rationale: str, score: int},
  markdown: {decision_card: str, blockers: str, next_actions: str},
}

Rationale & thresholds:
- If hard blockers -> decision NO-BID regardless of total
- Else total >= 70 => GO, 55-69 => REVIEW, else NO-BID (weak positioning)

NOTE: This is deterministic & local heuristic; enrichment may provide:
 estimated_value_ok (bool), competitor_count (int), protest_risk (str)
 which influence strategy_business_fit / practical sections.
"""
from __future__ import annotations
from typing import Dict, List, Optional
from .schema import Opportunity

SECTION_NAMES = [
    "acquisition",
    "agency_alignment",
    "technical_fit",
    "pre_rfp_marketing",
    "evaluation_factors",
    "strategy_business_fit",
    "practical",
]


def _capability_coverage(required: List[str], org: List[str]) -> float:
    if not required:
        return 1.0
    req = {r.strip().lower() for r in required if r.strip()}
    have = {o.strip().lower() for o in org if o.strip()}
    if not req:
        return 1.0
    return len(req & have) / max(1, len(req))


def _classify_naics_tier(naics: Optional[str]) -> str:
    if not naics:
        return "unknown"
    # Simple heuristic tiers
    if naics.startswith(("54", "51", "52")):
        return "tier1"
    if naics.startswith(("56", "61", "62")):
        return "tier2"
    return "tier3"


def _role_recommendation(opp: Opportunity, cov: float) -> str:
    tier = _classify_naics_tier(opp.naics)
    if tier == "tier1" and cov >= 0.85:
        return "prime"
    if cov == 1.0 and (opp.estimated_value_ok or False):
        return "prime"
    # fallback
    return "sub"


def evaluate_opportunity(opp: Opportunity, enrichment: Optional[Dict] = None) -> Dict:
    enrichment = enrichment or {}
    blockers: List[str] = []
    days = opp.days_to_due or 12
    page_limit = opp.page_limit if opp.page_limit is not None else None

    cov = _capability_coverage(opp.required_capabilities, opp.org_capabilities)

    # Hard blockers
    if opp.type.upper() == "CPFF":
        blockers.append("CPFF-only (cost plus complexity)")
    if opp.vehicle_required and not opp.vehicle_held:
        blockers.append("Vehicle required but not held")
    if cov < 0.85 and opp.teaming_can_close_gap is not True:
        blockers.append(f"Capability coverage {int(cov*100)}% < 85% and no teaming path")
    if opp.clearance_required and not opp.clearance_available:
        blockers.append("Clearance gap")
    if (opp.active_proposals or 0) >= 3 and days < 14:
        blockers.append("Bandwidth insufficient (>=3 active & <14 days)")
    if page_limit is not None and page_limit < 5 and days < 5:
        blockers.append("Page-limit impossible (<5 pages & <5 days)")

    # Section scoring heuristics (0-100)
    sections: Dict[str, int] = {}

    # acquisition: vehicle readiness, clearance, time runway
    acquisition_score = 70
    if opp.vehicle_required and not opp.vehicle_held:
        acquisition_score -= 40
    if opp.clearance_required and not opp.clearance_available:
        acquisition_score -= 30
    if days < 7:
        acquisition_score -= 15
    if days > 45:
        acquisition_score += 5
    acquisition_score = max(0, min(100, acquisition_score))
    sections["acquisition"] = acquisition_score

    # agency alignment: strategic priority + relationship
    agency_alignment = 50
    if (opp.agency_priority or "").lower() == "strategic":
        agency_alignment += 25
    elif (opp.agency_priority or "").lower() == "target":
        agency_alignment += 15
    if opp.has_relationship:
        agency_alignment += 20
    sections["agency_alignment"] = min(100, agency_alignment)

    # technical fit: capability coverage, uniqueness, personnel
    technical_fit = int(cov * 100)  # base on coverage
    if opp.solution_uniqueness:
        technical_fit += 10
    if opp.key_personnel_ready:
        technical_fit += 10
    sections["technical_fit"] = max(0, min(100, technical_fit))

    # pre-RFP marketing: touches before RFP
    pre = 30
    if opp.rfi_response:
        pre += 20
    if opp.sbo_meeting:
        pre += 15
    if opp.conference_touch:
        pre += 10
    if opp.teaming_ready:
        pre += 10
    sections["pre_rfp_marketing"] = min(100, pre)

    # evaluation factors: understanding of Section M, cost edge, barriers
    evalf = 40
    if opp.section_m_pp_weight:
        evalf += 10
    if opp.cost_edge:
        evalf += 15
    if opp.barrier_advantage:
        evalf += 15
    sections["evaluation_factors"] = min(100, evalf)

    # strategy/business fit: value alignment, leverage, ROI, future leverage, competitor dynamics
    # Use enrichment values to override local if provided
    if enrichment.get("estimated_value_ok") is not None:
        opp.estimated_value_ok = bool(enrichment.get("estimated_value_ok"))
    if enrichment.get("competitor_count") is not None:
        opp.competitor_count = int(enrichment.get("competitor_count"))

    strat = 50
    if opp.estimated_value_ok:
        strat += 10
    if opp.future_leverage:
        strat += 10
    if opp.roi_positive:
        strat += 10
    # Fewer competitors slightly boosts strategic attractiveness; crowded field penalizes
    if opp.competitor_count is not None:
        if opp.competitor_count <= 3:
            strat += 5
        elif opp.competitor_count >= 10:
            strat -= 5
    if opp.downselect:
        strat -= 10
    sections["strategy_business_fit"] = max(0, min(100, strat))

    # practical: complexity, competition, protest risk, workload
    practical = 70
    if opp.too_complex:
        practical -= 20
    comp = opp.competitor_count or enrichment.get("competitor_count")
    if comp and comp > 5:
        practical -= 10
    protest = enrichment.get("protest_risk") or opp.protest_risk
    if protest and str(protest).lower() in ("high", "elevated"):
        practical -= 10
    if (opp.active_proposals or 0) >= 3:
        practical -= 5
    sections["practical"] = max(0, min(100, practical))

    # Total score = average of sections, rounded
    total = int(round(sum(sections.values()) / len(sections))) if sections else 0

    # Decision
    if blockers:
        decision = "NO-BID"
        rationale = "hard blockers present"
    else:
        if total >= 70:
            decision = "GO"
            rationale = "strong composite score"
        elif total >= 55:
            decision = "REVIEW"
            rationale = "mixed signals require judgment"
        else:
            decision = "NO-BID"
            rationale = "weak positioning"

    role = _role_recommendation(opp, cov)

    # Next actions
    next_actions: List[str] = []
    if decision == "GO":
        next_actions = [
            "Lock outline + compliance matrix",
            "Validate key personnel availability",
            "Secure teaming MOUs (if any gaps)",
            "Draft Pink Team narrative seeds",
            "Schedule Pink / Red / Gold reviews",
        ]
    elif decision == "REVIEW":
        next_actions = [
            "Confirm blocker absence with capture lead",
            "Conduct capability gap close (teaming) analysis",
            "Deep dive Section L/M for hidden constraints",
            "Engage customer for positioning feedback",
        ]
    else:  # NO-BID
        next_actions = [
            "Document no-bid rationale in log",
            "Recycle competitive intel to knowledge base",
            "Free proposal resources and monitor for re-compete",
        ]

    decision_card = {
        "decision": decision,
        "rationale": rationale,
        "score": total,
    }

    md_decision = f"### Decision Card\n**Decision:** {decision}  \n**Score:** {total}  \n**Rationale:** {rationale}\n"
    md_blockers = "### Blockers\n" + ("None" if not blockers else "\n".join(f"- {b}" for b in blockers))
    md_actions = "### Next Actions\n" + "\n".join(f"1. {a}" if i == 0 else f"{i+1}. {a}" for i, a in enumerate(next_actions))

    return {
        "total": total,
        "sections": sections,
        "role": role,
        "blockers": {"has_blockers": bool(blockers), "list": blockers},
        "coverage": {"capability_coverage_pct": int(cov * 100)},
        "decision": decision_card,
        "markdown": {
            "decision_card": md_decision,
            "blockers": md_blockers,
            "next_actions": md_actions,
        },
        "next_actions": next_actions,
    }

__all__ = ["evaluate_opportunity"]

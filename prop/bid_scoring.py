from typing import Dict, List, Tuple
from .schema import Opportunity

Decision = Dict[str, str]


def _capability_coverage(required: List[str], org: List[str]) -> float:
    if not required:
        return 1.0
    req = set([r.strip().lower() for r in required if r.strip()])
    have = set([o.strip().lower() for o in org if o.strip()])
    if not req:
        return 1.0
    return len(req & have) / max(1, len(req))


def evaluate_opportunity(opp: Opportunity) -> Tuple[Decision, List[str], List[str]]:
    """
    Returns (decision_card, blockers, next_actions)
    decision_card keys: decision (GO|REVIEW|NO-BID), rationale, score (0-100)
    """
    blockers: List[str] = []
    actions: List[str] = []

    # Defaults
    days = opp.days_to_due or 12
    page_limit = opp.page_limit or 35

    # Hard blockers
    if opp.type.upper() == "CPFF":
        blockers.append("CPFF-only (no fee risk tolerance)")
    if opp.vehicle_required and not opp.vehicle_held:
        blockers.append("Vehicle required but not held")
    cov = _capability_coverage(opp.required_capabilities, opp.org_capabilities)
    if cov < 0.85 and (opp.teaming_can_close_gap is not True):
        blockers.append(f"Capability coverage {int(cov*100)}% < 85% and teaming can’t close gap")
    if opp.clearance_required and not opp.clearance_available:
        blockers.append("Clearance gap")
    if opp.active_proposals >= 3 and days < 14:
        blockers.append("Bandwidth insufficient (>=3 active & <14 days)")
    if (page_limit is not None) and page_limit < 5 and days < 5:
        blockers.append("Page-limit impossible (<5 pages with <5 days)")

    # Score (simple weighted heuristic)
    score = 50
    score += 10 if (opp.agency_priority or "other") == "strategic" else 0
    score += 5 if opp.has_relationship else 0
    score += 10 if cov >= 0.85 else int((cov - 0.5) * 20)
    score += 5 if opp.solution_uniqueness else 0
    score += 5 if opp.key_personnel_ready else 0
    score += 5 if opp.estimated_value_ok else 0
    score += 5 if (opp.structure or "prime") in ("prime", "cta") else 0
    score -= 5 if (opp.competitor_count or 0) > 5 else 0
    score -= 5 if opp.too_complex else 0
    score += 5 if opp.cost_edge else 0

    score = max(0, min(100, score))

    # Decision
    decision = "GO"
    rationale = []
    if blockers:
        decision = "NO-BID"
        rationale.append("hard blockers present")
    elif score >= 70:
        decision = "GO"
        rationale.append("strong strategic/fit indicators")
    else:
        decision = "REVIEW"
        rationale.append("needs leadership judgment")

    # Next actions
    if decision != "NO-BID":
        actions.extend([
            "Confirm Section L/M page limits and attachments",
            "Hold 15-min standup to confirm team bandwidth",
            "Draft strawman outline and run compliance check",
            "Identify teaming to close any remaining gaps",
            "Book Pink Team date and reviewer list",
        ])
    else:
        actions.extend([
            "Notify capture of no-bid rationale",
            "Archive intel and monitor for re-compete",
            "Free up proposal resources",
        ])

    decision_card: Decision = {
        "decision": decision,
        "rationale": "; ".join(rationale),
        "score": str(score),
    }
    return decision_card, blockers, actions

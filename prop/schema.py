from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Tuple

class ShallReq(BaseModel):
    id: str
    section: str
    text: str
    priority: Optional[str] = None
    citations: List[str] = Field(default_factory=list)

class RequirementGraph(BaseModel):
    meta: Dict = Field(default_factory=dict)
    shalls: List[ShallReq] = Field(default_factory=list)
    edges: List[Tuple[str,str]] = Field(default_factory=list)

class OutlineItem(BaseModel):
    section: str
    title: str
    page_budget: float
    bullets: List[str] = Field(default_factory=list)
    related_shalls: List[str] = Field(default_factory=list)

class Outlines(BaseModel):
    items: List[OutlineItem]

class ComplianceRow(BaseModel):
    shall_id: str
    section: str
    covered_by: List[str] = Field(default_factory=list)
    status: str = "uncovered"  # uncovered | covered

class ComplianceMatrix(BaseModel):
    rows: List[ComplianceRow]


# --- Bid Autopilot ---
class Opportunity(BaseModel):
    # Core metadata
    title: Optional[str] = None
    agency: Optional[str] = None
    sub_agency: Optional[str] = None
    vehicle: Optional[str] = None
    vehicle_required: bool = False
    vehicle_held: bool = False
    naics: Optional[str] = None
    set_aside: Optional[str] = None
    is_small_business: Optional[bool] = None
    type: str = "FFP"  # FFP|T&M|LH|CPFF
    due_date: Optional[str] = None
    days_to_due: int = 12
    page_limit: Optional[int] = None
    clearance_required: bool = False
    clearance_available: bool = True

    # Strategy/context
    agency_priority: Optional[str] = None  # strategic|target|other
    has_relationship: Optional[bool] = None
    culture: Optional[str] = None
    required_capabilities: List[str] = Field(default_factory=list)
    org_capabilities: List[str] = Field(default_factory=list)
    teaming_can_close_gap: Optional[bool] = None
    pp_alignment: Optional[bool] = None
    tool_match: Optional[bool] = None
    solution_uniqueness: Optional[bool] = None
    key_personnel_ready: Optional[bool] = None
    section_m_pp_weight: Optional[str] = None
    rfi_response: Optional[bool] = None
    sbo_meeting: Optional[bool] = None
    conference_touch: Optional[bool] = None
    win_prob_estimate: Optional[int] = None  # 0-100
    incumbent_weak: Optional[bool] = None
    barrier_advantage: Optional[bool] = None
    future_leverage: Optional[bool] = None
    teaming_ready: Optional[bool] = None
    structure: Optional[str] = None  # prime|cta|jv|sub
    active_proposals: int = 0
    estimated_value_ok: Optional[bool] = None
    competitor_count: Optional[int] = None
    protest_risk: Optional[str] = None
    org_revenue_usd: Optional[float] = None
    roi_positive: Optional[bool] = None
    too_complex: Optional[bool] = None
    downselect: Optional[bool] = None
    cost_edge: Optional[bool] = None
    buyer_has_dpa: Optional[bool] = None

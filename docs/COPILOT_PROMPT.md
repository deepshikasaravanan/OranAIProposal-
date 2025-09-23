# COPILOT_PROMPT

## Mission
Build a Bid / No-Bid + Proposal Autopilot focused on STARS III (and similar small business federal vehicles). The system:
- Ingests opportunity artifacts (PWS / SOW / notice) and minimal metadata
- Produces an Opportunity analysis with: Decision Card, Blockers, Next Actions
- Optionally generates a branded proposal DOCX when decision is GO (or override conditions met)
- Remains extensible for future modules: watch-folder ingestion, search integrations (non-scraping), pricing models, advanced competitive intel

## Guardrails & Compliance
- No scraping of eBuy or portals; only ingest via explicitly provided documents, email drops, or a monitored filesystem folder (future hook)
- Treat all PII / CUI cautiously: do not log raw attachments; only store derived structured fields & generated content
- Secrets (API keys, SAM, OpenAI, etc.) must be loaded from environment variables / .env – never hard-coded
- Support offline / fallback modes when LLM quota or network issues occur

## Output Contract (Core API)
For each scored opportunity the API (score or score-and-generate) returns JSON keys:
- "Decision Card": { decision: GO|REVIEW|NO-BID, rationale: str, score: int(0-100) }
- "Blockers": [list of strings] ("none" if empty)
- "Next Actions": top prioritized actions (<=6)
- Optional generation fields when a document build is triggered:
  - started: bool
  - output_docx: path or null
  - reason: trigger reason (GO, override: review, override: no-bid)

## Hard Blockers (current logic)
Reject or downgrade to NO-BID if any apply:
1. Contract type constraint: ONLY CPFF opportunities and org cannot support (cpff_only flag) – CPFF-only mismatch
2. Vehicle required but not held (vehicle_required true AND vehicle_held false)
3. Capability coverage < 85% AND teaming_can_close_gap is False/None
4. Clearance required AND clearance_available False
5. Bandwidth: active_proposals >= 3 AND days_to_due < 14
6. Page-limit impossible: page_limit < 5 AND days_to_due < 5 (not enough runway)

(Heuristic score otherwise considers relationship strength, strategic priority, value band, competition, uniqueness, personnel readiness, future leverage, cost edge, and risk modifiers.)

## Opportunity Schema (current fields)
```
Opportunity {
  title?: str
  agency?: str
  sub_agency?: str
  vehicle?: str
  vehicle_required: bool
  vehicle_held: bool
  naics?: str
  set_aside?: str
  is_small_business?: bool
  type: str  # FFP|T&M|LH|CPFF
  due_date?: str (YYYY-MM-DD)
  days_to_due: int
  page_limit?: int
  clearance_required: bool
  clearance_available: bool
  agency_priority?: str  # strategic|target|other
  has_relationship?: bool
  culture?: str
  required_capabilities: [str]
  org_capabilities: [str]
  teaming_can_close_gap?: bool
  pp_alignment?: bool
  tool_match?: bool
  solution_uniqueness?: bool
  key_personnel_ready?: bool
  section_m_pp_weight?: str
  rfi_response?: bool
  sbo_meeting?: bool
  conference_touch?: bool
  win_prob_estimate?: int
  incumbent_weak?: bool
  barrier_advantage?: bool
  future_leverage?: bool
  teaming_ready?: bool
  structure?: str  # prime|cta|jv|sub
  active_proposals: int
  estimated_value_ok?: bool
  competitor_count?: int
  protest_risk?: str
  org_revenue_usd?: float
  roi_positive?: bool
  too_complex?: bool
  downselect?: bool
  cost_edge?: bool
  buyer_has_dpa?: bool
}
```

## Module Contracts

### prop/s3io.py
```
is_s3(path: str) -> bool
# Return True if path is an s3:// URI

download_to_tmp(uri: str) -> str | None
# Download S3 object to a temp file; return local path or None on failure

list_from_zip(zip_path: str) -> list[str]
# List file names inside a local zip archive
```

### prop/enrich_usaspending.py
```
fetch_award_stats(agency: str | None, naics: str | None, years: int = 5) -> dict
# Returns {
#   incumbents: [ {vendor: str, total: float, last_year: int} ],
#   value_band: { p25: float, p50: float, p75: float }
# }
```

### prop/sam_client.py
```
get_notice(notice_id: str) -> dict  # raw JSON from SAM or {error:...}
```

### prop/scoring_bid.py
```
evaluate_opportunity(opp: Opportunity, enrichment: dict | None = None) -> ScoreOut
# ScoreOut shape: (decision_card: {decision, rationale, score}, blockers: [str], actions: [str])
```

### web/api.py
Endpoints:
- POST /api/bid/intake-parse
- POST /api/bid/score
- POST /api/bid/score-and-generate
- GET  /api/bid/sam-notice
- POST /api/bid/enrich

### Future Extensions (placeholders)
- watch-folder ingestion (email drop & fs monitor)
- pricing model plug-in
- competitor intel enrichment
- progress tracking and burn-down metrics

## Non-Goals (current scope)
- Live scraping of procurement portals
- Full pipeline orchestration across CI/CD
- Storage of raw sensitive source documents beyond immediate processing window

## Implementation Notes
- All external calls must be wrapped with timeouts and graceful fallbacks
- Keep enrichment optional; scoring must function without it
- Avoid silently swallowing exceptions in critical path; log or propagate
- Provide deterministic fallbacks when LLM unavailable (outline heuristics)

## Style / Quality
- Pydantic for schemas
- Small, composable functions
- JSON-safe outputs (no objects with open file handles)
- Deterministic hashing for temp filenames where feasible

## Ready Signal
Return of a JSON payload conforming to Output Contract for a sample Opportunity with no unhandled exceptions.

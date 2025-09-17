# OranAIProposal-
# proposal-bot

Bid / Proposal Autopilot: ingest PWS/RFP, extract *shalls*, build compliance + outlines, generate diagrams & DOCX with branding, enrich with market data, and score bid decisions.

## Features
- PWS parsing → Requirements graph (*shall* extraction)
- Outline drafting + narrative expansion
- Flow & Gantt diagrams, optional Mermaid figures
- Branded DOCX builder (headers, footers, tables, appendix)
- Bid scoring (GO / REVIEW / NO-BID) with blockers & actions
- USAspending enrichment (incumbents, value bands)
- SAM notice ingestion
- Capability compliance appendix + CSV
- Typer CLI + REST API (FastAPI)

## Environment Setup
Copy and edit the example env file:
```bash
cp .env.example .env
```
Required variables:
- `OPENAI_API_KEY` (LLM expansion – optional if not generating text)
- `SAM_API_KEY` (SAM.gov notice search)
- `USASPENDING_BASE` (defaults to public API)
- `AWS_REGION`, `S3_BUCKET` (for any S3 interactions)
- Branding: `ORAN_LOGO_PATH`, `ORAN_BRAND_NAME`, etc.

## Install & Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn web.app:app --reload --port 8000
```
Browse: http://127.0.0.1:8000

Health check:
```bash
curl -s http://127.0.0.1:8000/health
```

## CLI (Typer)
```bash
python -m prop.cli intake examples/pws_sample.md > /tmp/opportunity.json
python -m prop.cli score --json examples/opportunity_sample.json
```
Show help:
```bash
python -m prop.cli --help
```

## Make Demo
```bash
make demo
```

## REST cURL Examples
1) Intake parse (local files):
```bash
curl -s -X POST http://127.0.0.1:8000/api/bid/intake-parse \
  -H 'Content-Type: application/json' \
  -d '{"files":["examples/pws_sample.md"]}' | jq .
```

2) Score an Opportunity:
```bash
curl -s -X POST http://127.0.0.1:8000/api/bid/score \
  -H 'Content-Type: application/json' \
  -d @examples/opportunity_sample.json | jq .
```

3) SAM Notice fetch (requires `SAM_API_KEY`):
```bash
curl -s 'http://127.0.0.1:8000/api/bid/sam-notice?noticeId=FAKE123' | jq .
```

Optional: score + generate (auto-build DOCX if GO / override rules):
```bash
curl -s -X POST http://127.0.0.1:8000/api/bid/score-and-generate \
  -H 'Content-Type: application/json' \
  -d '{"opportunity": {"title":"Test"}, "pws_files":["examples/pws_sample.md"], "override": true}' | jq .
```

## Outputs
Run artifacts saved under `web/outputs/<run_id>/`:
- `requirements.json`
- `outlines.json`
- `pipeline.png` / `gantt.png`
- `proposal.docx`
- `capability_compliance.csv` (if capabilities available)

## n8n Workflow (Email → S3 → Intake → Score → IF → Generate → Slack)
High-level steps to automate pipeline in n8n:
1. Trigger: IMAP Email node (watch inbox for new PWS attachments)
2. Function: Filter attachments to PDF/DOCX/MD
3. AWS S3 node: Upload each attachment to `s3://$S3_BUCKET/incoming/<date>/...`
4. HTTP Request node (POST `/api/bid/intake-parse`) with JSON body containing S3 URIs
5. HTTP Request node (POST `/api/bid/score`) with Opportunity JSON from prior step
6. IF node: condition `Decision Card.decision == GO`
7. HTTP Request node (POST `/api/bid/score-and-generate`) supplying opportunity + file paths, `override=true` (optional)
8. Slack (or Teams) node: Send message summarizing decision, blockers, link to DOCX path (`web/outputs/.../proposal.docx`)
9. (Optional) Append to a Google Sheet / Airtable for bid history

Export / Import:
- After wiring, click *Export Workflow* in n8n to share JSON. To import, use *Import from file* and update credentials (S3, Slack tokens, base URL).

## Development
Tests:
```bash
pytest -q
```

Run lint (optional): integrate flake8 / ruff if desired.

## Roadmap (next)
- Decision history endpoint & persistence
- Auto capability extraction feeding Appendix
- Diagram inference for Mermaid generation
- Asset management + multi-page front-end

## License
Internal / TBD.


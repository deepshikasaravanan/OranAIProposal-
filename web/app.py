import os
from fastapi import FastAPI, UploadFile, File, Body, Query, Form
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from .service import process_pipeline, list_outputs
from prop.schema import Opportunity
from prop.scoring_bid import evaluate_opportunity
from prop.intake import parse_files_to_opportunity
from prop.sam_client import get_notice, map_notice_to_opp
from prop.enrich_usaspending import fetch_award_stats

app = FastAPI(title="Proposal Bot Web")

app.mount("/static", StaticFiles(directory="web/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def index():
    content = open("web/static/index.html", "r", encoding="utf-8").read()
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    }
    return HTMLResponse(content=content, headers=headers)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/process")
async def process(
    pws: UploadFile = File(...),
    rfp: UploadFile | None = File(None),
    brand_company: str | None = Form(default=None),
    brand_tagline: str | None = Form(default=None),
    model: str | None = Form(default=None),
    # Accept as string to avoid 422 on empty input and coerce manually
    max_tokens: str | None = Form(default=None),
):
    """Run the ingestion + generation pipeline.

    Accepts optional branding overrides (company + tagline) which are applied via
    transient environment variables for this single request to influence the
    header/footer of the generated DOCX. This avoids permanent mutation of
    server-wide env while allowing per-run branding tests from the UI.
    """
    # Stash originals
    orig_brand = os.environ.get("ORAN_BRAND_NAME")
    orig_header_right = os.environ.get("ORAN_HEADER_RIGHT")
    orig_model = os.environ.get("OPENAI_MODEL")
    orig_max_toks = os.environ.get("OPENAI_MAX_TOKENS")
    did_brand = False
    did_tagline = False
    did_model = False
    did_tokens = False
    if brand_company and brand_company.strip():
        os.environ["ORAN_BRAND_NAME"] = brand_company.strip()
        did_brand = True
    if brand_tagline and brand_tagline.strip():
        os.environ["ORAN_HEADER_RIGHT"] = brand_tagline.strip()
        did_tagline = True
    if model and model.strip():
        os.environ["OPENAI_MODEL"] = model.strip()
        did_model = True
    if max_tokens is not None:
        mt = (max_tokens or "").strip()
        if mt.isdigit():
            os.environ["OPENAI_MAX_TOKENS"] = mt
            did_tokens = True
    try:
        result = await process_pipeline(pws, rfp)
        # Echo applied branding so UI can reflect
        result["branding_applied"] = {
            "brand_name": os.environ.get("ORAN_BRAND_NAME"),
            "header_right": os.environ.get("ORAN_HEADER_RIGHT"),
        }
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    finally:
        # Restore originals (or delete if none originally set)
        if did_brand:
            if orig_brand is None:
                os.environ.pop("ORAN_BRAND_NAME", None)
            else:
                os.environ["ORAN_BRAND_NAME"] = orig_brand
        if did_tagline:
            if orig_header_right is None:
                os.environ.pop("ORAN_HEADER_RIGHT", None)
            else:
                os.environ["ORAN_HEADER_RIGHT"] = orig_header_right
        if did_model:
            if orig_model is None:
                os.environ.pop("OPENAI_MODEL", None)
            else:
                os.environ["OPENAI_MODEL"] = orig_model
        if did_tokens:
            if orig_max_toks is None:
                os.environ.pop("OPENAI_MAX_TOKENS", None)
            else:
                os.environ["OPENAI_MAX_TOKENS"] = orig_max_toks

@app.get("/outputs")
def outputs():
    return list_outputs()

@app.post("/api/brand/logo-upload")
async def upload_logo(file: UploadFile = File(...)):
    """Accept a logo image and save it to web/static/oran_logo.png"""
    os.makedirs("web/static", exist_ok=True)
    out = os.path.join("web", "static", "oran_logo.png")
    with open(out, "wb") as f:
        f.write(await file.read())
    return {"saved": out}

@app.get("/api/brand/debug")
def brand_debug():
    """Report branding-related env vars and the resolved logo path the server will use."""
    candidates = [
        os.environ.get("ORAN_LOGO_PATH"),
        os.path.join("web", "static", "oran_logo.png"),
        os.path.join("assets", "oran_logo.png"),
        os.path.join("examples", "oran_logo.png"),
    ]
    found = None
    for p in candidates:
        if p and os.path.exists(p):
            found = p
            break
    info = {
        "env": {
            "ORAN_LOGO_PATH": os.environ.get("ORAN_LOGO_PATH"),
            "ORAN_LOGO_WIDTH_IN": os.environ.get("ORAN_LOGO_WIDTH_IN"),
            "ORAN_BRAND_NAME": os.environ.get("ORAN_BRAND_NAME"),
            "ORAN_HEADER_RIGHT": os.environ.get("ORAN_HEADER_RIGHT"),
            "ORAN_FOOTER_TEXT": os.environ.get("ORAN_FOOTER_TEXT"),
        },
        "logo_candidates": candidates,
        "resolved_logo_path": found,
        "exists": bool(found),
        "size_bytes": (os.path.getsize(found) if found else None),
        "note": "Update env and restart server to apply changes, or drop a file at web/static/oran_logo.png.",
    }
    return info
@app.post("/api/hero/upload")
async def upload_hero_image(file: UploadFile = File(...)):
    """Accept a PNG/JPG hero architecture graphic and save to web/static/hero_screenshot.png"""
    os.makedirs("web/static", exist_ok=True)
    out = os.path.join("web", "static", "hero_screenshot.png")
    with open(out, "wb") as f:
        f.write(await file.read())
    return {"saved": out}



@app.get("/api/pricing")
def pricing():
    """Return pricing / packaging metadata (static for now)."""
    tiers = [
        {
            "id": "starter",
            "name": "Starter",
            "tagline": "Solo or early capture setup (1–3 bids/mo)",
            "trial": "Free for 7 days",
            "price_month": 125,
            "highlight": False,
            "features": [
                "1 seat included",
                "100 AI credits / month",
                "Core parsing & scoring",
                "DOCX generation",
            ],
        },
        {
            "id": "essential",
            "name": "Essential",
            "tagline": "Growing teams (4–9 bids/month)",
            "trial": "Free for 7 days",
            "price_month": 375,
            "highlight": True,
            "features": [
                "4 seats included",
                "500 AI credits / month",
                "Zapier integration",
                "Up to 5 capture profiles",
                "1 complimentary training session",
                "Live chat + email support",
            ],
        },
        {
            "id": "scale",
            "name": "Scale",
            "tagline": "High-volume & enterprise (10+ bids/mo)",
            "trial": None,
            "price_month": 0,
            "contact": True,
            "highlight": False,
            "features": [
                "Unlimited internal seats",
                "Custom AI credit pools",
                "Private model / data boundary options",
                "Pipeline & CRM integrations",
                "Dedicated success manager",
                "SSO / advanced security",
            ],
        },
    ]
    return {"tiers": tiers}


# --- Bid Autopilot API ---
@app.post("/api/bid/intake-parse")
async def intake_parse(body: dict = Body(...)):
    """Parse provided files/URIs into an Opportunity skeleton and return normalized paths."""
    files = body.get("files", []) or []
    if not isinstance(files, list) or not files:
        return JSONResponse({"error": "files array required"}, status_code=400)
    opp, paths = parse_files_to_opportunity(files)
    return {"opportunity": opp.model_dump(), "paths": paths}


def _format_response(score_out: dict):
    # Backward-compatible minimal view plus rich data
    decision_card = score_out.get("decision", {})
    blockers = score_out.get("blockers", {}).get("list", [])
    actions = score_out.get("next_actions", [])
    return {
        "Decision Card": decision_card,
        "Blockers": blockers or ["none"],
        "Next Actions": actions[:6],
        "sections": score_out.get("sections"),
        "role": score_out.get("role"),
        "coverage": score_out.get("coverage"),
        "total": score_out.get("total"),
    }


@app.post("/api/bid/score")
async def score(opp: Opportunity = Body(default=None)):
    if opp is None:
        opp = Opportunity()
    score_out = evaluate_opportunity(opp)
    return _format_response(score_out)


@app.get("/api/bid/sam-notice")
async def sam_notice_get(noticeId: str = Query(...)):
    payload = get_notice(noticeId)
    if payload.get("error") == "missing_sam_key":
        return {"notice": "missing_sam_key"}
    opp = map_notice_to_opp(payload)
    return {"opportunity": opp.model_dump(), "raw": payload}


@app.post("/api/bid/sam-notice")
async def sam_notice_post(body: dict = Body(...)):
    nid = body.get("noticeId")
    if not nid:
        return JSONResponse({"error": "noticeId required"}, status_code=400)
    payload = get_notice(nid)
    if payload.get("error") == "missing_sam_key":
        return {"notice": "missing_sam_key"}
    opp = map_notice_to_opp(payload)
    return {"opportunity": opp.model_dump(), "raw": payload}


@app.post("/api/bid/enrich")
async def enrich(body: dict = Body(...)):
    opp_dict = body.get("opportunity") or {}
    opp = Opportunity(**opp_dict)
    stats = fetch_award_stats(opp.agency, opp.naics, years=5)
    value_band = stats.get("value_band", {})
    # estimated_value_ok heuristic: if we have band and org_revenue_usd within 0.5x..2x p50 (if p50) or any band value
    estimated_value_ok = None
    if value_band:
        p50 = value_band.get("p50") or value_band.get("p25") or value_band.get("p75")
        if p50 and opp.org_revenue_usd:
            estimated_value_ok = 0.5 * p50 <= opp.org_revenue_usd <= 2 * p50
        else:
            estimated_value_ok = True
    competitor_count = None
    raw_count = stats.get("raw_count", 0)
    if raw_count:
        # rough sqrt heuristic for effective competitor field size
        import math
        competitor_count = max(2, min(12, int(math.sqrt(raw_count))))
    opp.estimated_value_ok = estimated_value_ok
    opp.competitor_count = competitor_count
    enrichment = {
        "incumbents": stats.get("incumbents", []),
        "value_band": value_band,
        "estimated_value_ok": estimated_value_ok,
        "competitor_count": competitor_count,
    }
    return {"opportunity_enriched": opp.model_dump(), "enrichment": enrichment}


@app.post("/api/bid/score-and-generate")
async def score_and_generate(body: dict = Body(...)):
    override = bool(body.get("override", False))
    allow_no_bid_override = bool(body.get("allow_no_bid_override", False))
    opp_dict = body.get("opportunity") or {}
    pws_files = body.get("pws_files", []) or []
    rfq_files = body.get("rfq_files", []) or []

    opp = Opportunity(**opp_dict) if opp_dict else Opportunity()
    score_out = evaluate_opportunity(opp)
    recommendation = score_out.get("decision", {}).get("decision")
    should_generate = False
    reason = ""
    if recommendation == "GO":
        should_generate = True
        reason = "GO"
    elif recommendation == "REVIEW" and override:
        should_generate = True
        reason = "override: review"
    elif recommendation == "NO-BID" and override and allow_no_bid_override:
        should_generate = True
        reason = "override: no-bid"
    elif recommendation == "NO-BID" and override and not allow_no_bid_override:
        return JSONResponse({"error": "override rejected due to hard blockers"}, status_code=400)

    result = _format_response(score_out)
    result.update({"scored": recommendation, "started": False, "output_docx": None, "reason": reason})

    if should_generate:
        # For now, accept first PWS path and optional RFQ
        import os
        from prop.utils import materialize_paths as _mat

        def _to_upload(path: str) -> UploadFile:
            f = open(path, "rb")
            return UploadFile(filename=os.path.basename(path), file=f)

        mats = _mat(pws_files)
        mats_rfp = _mat(rfq_files)
        if not mats:
            return JSONResponse({"error": "No usable PWS files"}, status_code=400)
        pws_up = _to_upload(mats[0])
        rfp_up = _to_upload(mats_rfp[0]) if mats_rfp else None
        pipe = await process_pipeline(pws_up, rfp_up)
        result.update({"started": True, "output_docx": pipe["outputs"]["docx"]})
    return result

@app.get("/download")
def download(path: str):
    import os
    if not os.path.isfile(path):
        return JSONResponse({"error": "path is not a file"}, status_code=400)
    # Set a stable filename and content-type so browsers don't rename it to generic download.zip
    import mimetypes
    filename = os.path.basename(path)
    media_type, _ = mimetypes.guess_type(filename)
    # Fallback to octet-stream if unknown; Word DOCX has a specific type
    if filename.lower().endswith('.docx'):
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    # Protective headers so proxies/browsers don't transform or sniff as zip
    headers = {
        "X-Content-Type-Options": "nosniff",
        "Cache-Control": "no-transform",
        # Explicit filename to avoid renaming
        "Content-Disposition": f"attachment; filename={filename}",
    }
    return FileResponse(
        path,
        media_type=media_type or "application/octet-stream",
        filename=filename,
        headers=headers,
    )


@app.get("/download/bundle")
def download_bundle(run_id: str):
    """Zip and return all files for a given run id under web/outputs/<run_id>.

    This produces a real ZIP archive with a deterministic filename to avoid
    browsers renaming the file arbitrarily.
    """
    import io
    import os
    import zipfile

    base_dir = os.path.abspath(os.path.join("web", "outputs", run_id))
    if not os.path.isdir(base_dir):
        return JSONResponse({"error": "run_id not found"}, status_code=404)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name in sorted(os.listdir(base_dir)):
            p = os.path.join(base_dir, name)
            if os.path.isfile(p):
                # Store files at top-level inside the zip
                z.write(p, arcname=name)
    buf.seek(0)
    zip_name = f"proposal_run_{run_id}.zip"
    headers = {"Content-Disposition": f"attachment; filename={zip_name}"}
    return Response(content=buf.read(), media_type="application/zip", headers=headers)

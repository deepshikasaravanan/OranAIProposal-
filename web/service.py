import os
import time
import uuid
from datetime import datetime
from typing import Optional
from fastapi import UploadFile

from prop.parser_pdf import parse_pws
from prop.utils import write_json
# (Removed unused imports RequirementGraph, Outlines)
from prop.generator_narrative import draft_outlines
from prop.postprocess import ensure_proposal_development_steps
from prop.generator_diagram import render_gantt
from prop.compliance import build_matrix, build_compliance_matrix
from prop.builder_docx import build_docx

OUT_DIR = os.path.abspath(os.path.join("web", "outputs"))
os.makedirs(OUT_DIR, exist_ok=True)

def _save_upload(upload: UploadFile, folder: str) -> str:
    if not upload or not getattr(upload, "filename", None) or not upload.filename.strip():
        raise ValueError("No file provided")
    # Sanitize filename a bit
    fname = os.path.basename(upload.filename.strip())
    path = os.path.join(folder, fname)
    with open(path, "wb") as f:
        f.write(upload.file.read())
    return path

async def process_pipeline(pws: UploadFile, rfp: Optional[UploadFile], model: Optional[str] = None):
    t0 = time.time()
    timings = {}
    run_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8]
    run_dir = os.path.join(OUT_DIR, run_id)
    os.makedirs(run_dir, exist_ok=True)

    # Save inputs
    pws_path = _save_upload(pws, run_dir)
    rfp_path = None
    if rfp and getattr(rfp, "filename", None) and rfp.filename.strip():
        rfp_path = _save_upload(rfp, run_dir)

    # 1) Parse
    t = time.time()
    rg = parse_pws(pws_path)
    timings["parse"] = round(time.time() - t, 2)
    reqs_json = os.path.join(run_dir, "requirements.json")
    write_json(reqs_json, rg.model_dump())

    # 2) Flowchart generation removed per request

    # 3) Draft outlines
    t = time.time()
    outlines = draft_outlines(rg, model=model)
    outlines = ensure_proposal_development_steps(outlines)
    timings["outline"] = round(time.time() - t, 2)
    outlines_json = os.path.join(run_dir, "outlines.json")
    write_json(outlines_json, outlines.model_dump())

    # 4) Gantt (optional)
    gantt_png = None
    rulebook = None
    if rfp_path:
        import yaml
        t = time.time()
        data = yaml.safe_load(open(rfp_path, "r", encoding="utf-8"))
        deliverables = data.get("deliverables", [])
        tasks = []
        for d in deliverables:
            label = d.get("name", "Deliverable")
            start = 0 if d.get("start_at_day0", True) else 7
            duration = int(d.get("due_days", 30))
            tasks.append((label, start, duration))
        gantt_png = os.path.join(run_dir, "gantt.png")
        render_gantt(tasks, gantt_png)
        timings["gantt"] = round(time.time() - t, 2)
        # Load rulebook if present in the uploaded yaml (or a sidecar)
        rulebook = data if isinstance(data, dict) else None
    else:
        # Fallback: try examples/ocdao_rulebook.yaml
        try:
            import yaml
            rb_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "examples", "ocdao_rulebook.yaml")
            if os.path.exists(rb_path):
                rulebook = yaml.safe_load(open(rb_path, "r", encoding="utf-8"))
        except Exception:
            rulebook = None

    # 5) Compliance + build
    t = time.time()
    matrix = build_matrix(rg, outlines)
    images = [x for x in [gantt_png] if x]
    # Capability compliance (Prompt 9) – placeholder: derive required capabilities from outlines? Currently none.
    outline_titles = [it.title or it.section for it in outlines.items]
    required_caps: list[str] = []  # Future: feed from parsing or user input
    capability_compliance = build_compliance_matrix(required_caps, outline_titles) if required_caps else []
    capability_csv = None
    if capability_compliance:
        import csv
        capability_csv = os.path.join(run_dir, "capability_compliance.csv")
        with open(capability_csv, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=["Requirement","Section","Coverage","Notes"])
            w.writeheader()
            for row in capability_compliance:
                w.writerow(row)
    docx_path = os.path.join(run_dir, "proposal.docx")
    # Mermaid diagrams placeholder (future: generate from architecture inference)
    mermaid_diagrams: list[str] = []  # kept empty until generation logic added
    build_docx(
        rg, outlines, matrix, images, docx_path,
        mermaid_diagrams=mermaid_diagrams,
        capability_compliance=capability_compliance,
        rulebook=rulebook,
        model=model,
    )
    timings["docx"] = round(time.time() - t, 2)
    timings["total"] = round(time.time() - t0, 2)

    # Build simple coverage report for Section 6 key phrases
    check_phrases = [
        "roadmap", "labor categories", "kickoff", "outline", "compliance check",
        "assign authors", "pink team", "red team", "adjudication", "full prose",
        "management section", "sf-33", "sf-18", "sf-1449", "submission email",
        "gold review", "rfp compliance", "white glove", "508", "finalize",
    ]
    text_blob = "\n".join(["\n".join(it.bullets) for it in outlines.items]).lower()
    coverage = {p: (p in text_blob) for p in check_phrases}

    return {
        "run_id": run_id,
        "outputs": {
            "requirements": reqs_json,
            "outlines": outlines_json,
            # flowchart removed
            "gantt": gantt_png,
            "docx": docx_path,
            "capability_compliance_csv": capability_csv,
        },
        "counts": {
            "shalls": len(rg.shalls),
            "outline_items": len(outlines.items),
        },
        "timings": timings,
        "section6_coverage": coverage,
    }

def list_outputs():
    items = []
    for run_id in sorted(os.listdir(OUT_DIR)):
        run_dir = os.path.join(OUT_DIR, run_id)
        if not os.path.isdir(run_dir):
            continue
        paths = {name: os.path.join(run_dir, name) for name in os.listdir(run_dir)}
        items.append({"run_id": run_id, "files": paths})
    return {"runs": items}

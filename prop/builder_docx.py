import os
import base64
import tempfile
from docx import Document
from typing import Optional, List, Dict
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from .schema import RequirementGraph, Outlines, ComplianceMatrix
from .generator_diagrams import render_mermaid_to_png  # new mermaid renderer
from .generator_paragraphs import expand_bullets_to_paragraphs

LIGHT_BLUE = RGBColor(91, 155, 213)  # Word's Accent 1 light blue


def _first_existing(paths):
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None


def _apply_branding(doc: Document):
    """Apply Oran-style header and centered footer to all sections.

    Header: optional Oran logo on the left (if available), company name on the right.
    Footer: required disclaimer centered across every page.
    """
    # Resolve a usable logo file (supports PATH, URL, or base64)
    from typing import Optional
    def _resolve_logo_file() -> Optional[str]:
        # 1) Base64 env
        b64 = os.environ.get("ORAN_LOGO_B64")
        if b64:
            try:
                raw = base64.b64decode(b64, validate=True)
                fd, tpath = tempfile.mkstemp(prefix="oran_logo_", suffix=".png")
                os.close(fd)
                with open(tpath, "wb") as f:
                    f.write(raw)
                return tpath
            except Exception:
                pass
        # 2) Local path env
        p = os.environ.get("ORAN_LOGO_PATH")
        if p and os.path.exists(p):
            return p
        # 3) URL env
        url = os.environ.get("ORAN_LOGO_URL")
        if url and url.lower().startswith(("http://", "https://")):
            try:
                import requests  # type: ignore
                r = requests.get(url, timeout=10)
                if r.ok and r.content:
                    fd, tpath = tempfile.mkstemp(prefix="oran_logo_", suffix=".png")
                    os.close(fd)
                    with open(tpath, "wb") as f:
                        f.write(r.content)
                    return tpath
            except Exception:
                pass
        # 4) Well-known repo paths
        return _first_existing([
            os.path.join("web", "static", "oran_logo.png"),
            os.path.join("assets", "oran_logo.png"),
            os.path.join("examples", "oran_logo.png"),
        ])

    logo_path = _resolve_logo_file()
    try:
        logo_width_in = float(os.environ.get("ORAN_LOGO_WIDTH_IN", "1.2"))
    except Exception:
        logo_width_in = 1.2
    brand_name = os.environ.get("ORAN_BRAND_NAME", "Oran Inc.")
    header_right = os.environ.get("ORAN_HEADER_RIGHT", "IT Services")
    footer_text = os.environ.get(
        "ORAN_FOOTER_TEXT",
        "Use or disclosure of information contained on this page is subject\n"
        "to the restrictions on the title page of this proposal.",
    )

    for sec in doc.sections:
        # Ensure header appears on first page too
        try:
            sec.different_first_page_header_footer = False
        except Exception:
            pass

        header = sec.header
        header.is_linked_to_previous = False
        # Clear any default paragraph
        while header.paragraphs:
            p = header.paragraphs[0]
            p._element.getparent().remove(p._element)

        # Build a two-cell table for logo + company text with page width
        total_width = getattr(sec, "page_width", None)
        left_margin = getattr(sec, "left_margin", 0)
        right_margin = getattr(sec, "right_margin", 0)
        avail_width = (total_width - left_margin - right_margin) if total_width else None
        try:
            table = header.add_table(rows=1, cols=2, width=avail_width)
        except TypeError:
            # Some versions accept no width; fallback
            table = header.add_table(rows=1, cols=2)
        table.autofit = True
        left, right = table.rows[0].cells
        if logo_path:
            try:
                left.paragraphs[0].add_run().add_picture(logo_path, width=Inches(logo_width_in))
            except Exception:
                # If image fails to load, fall back to text
                left.text = brand_name
        else:
            left.text = brand_name

        rp = right.paragraphs[0]
        rp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r = rp.add_run(header_right)
        r.bold = True

        # Footer disclaimer centered
        footer = sec.footer
        footer.is_linked_to_previous = False
        fpara = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        fpara.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # Clear existing text then set
        try:
            fpara.clear()  # type: ignore[attr-defined]
        except Exception:
            pass
        frun = fpara.add_run(footer_text)
        frun.italic = False


def _apply_heading_colors(doc: Document):
    for name in ("Heading 1", "Heading 2", "Heading 3"):
        try:
            style = doc.styles[name]
            if hasattr(style, "font"):
                style.font.color.rgb = LIGHT_BLUE
        except Exception:
            # If style not found, ignore
            continue


def _add_table(doc: Document, headers: List[str]):
    """Create a styled table with header row and return it."""
    tbl = doc.add_table(rows=1, cols=len(headers))
    try:
        tbl.style = "Light Grid Accent 1"
    except Exception:
        pass
    hdr = tbl.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
    return tbl


def _extract_label_map(bullets: list[str]) -> dict[str, list[str]]:
    label_map: dict[str, list[str]] = {}
    for b in (bullets or []):
        if isinstance(b, str) and b.startswith("[") and "]" in b:
            label, rest = b.split("]", 1)
            label = label.strip("[] ")
            label_map.setdefault(label, []).append(rest.strip())
    return label_map


def build_docx(
    reqs: RequirementGraph,
    outlines: Outlines,
    matrix: ComplianceMatrix,
    image_paths: list,
    out_path: str,
    mermaid_diagrams: Optional[List[str]] = None,
    capability_compliance: Optional[List[Dict]] = None,
    rulebook: Optional[Dict] = None,
    model: Optional[str] = None,
):
    doc = Document()
    _apply_heading_colors(doc)
    # Cover page
    h = doc.add_paragraph()
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = h.add_run("OCDAO Proposal – Auto-Drafted")
    run.bold = True
    run.font.size = Pt(28)
    doc.add_paragraph("Generated by proposal-bot").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Date: ").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

    doc.add_paragraph("Table of Contents (update in Word: References → Table of Contents)")
    # Add ToC extras per user's ToC preference
    doc.add_heading("LIST OF FIGURES", level=1)
    doc.add_paragraph("[Insert automatic list of figures in Word]")
    doc.add_heading("LIST OF TABLES", level=1)
    doc.add_paragraph("[Insert automatic list of tables in Word]")
    doc.add_heading("ACRONYMS AND ABBREVIATIONS", level=1)
    doc.add_paragraph("")

    doc.add_heading("Executive Summary", level=1)
    doc.add_paragraph("This document was assembled automatically based on extracted requirements and generated outlines.")

    # Pre-compute shall lookup
    shall_by_id = {s.id: s for s in getattr(reqs, "shalls", [])}

    # Writing Assignments Matrix up front
    doc.add_heading("WRITING ASSIGNMENTS MATRIX", level=1)
    doc.add_paragraph(
        "Live tracker: assign Author/SME and Due. Word Target uses words/page from ORAN_WORDS_PER_PAGE (default 425)."
    )
    words_per_page = 425
    try:
        wpp_env = int(os.environ.get("ORAN_WORDS_PER_PAGE", "425"))
        if 200 <= wpp_env <= 800:
            words_per_page = wpp_env
    except Exception:
        pass

    # Prepare items: keep any 'Overview' first, then sort remaining by section numeric key if available
    def _sec_sort_key(title: str) -> tuple:
        import re
        m = re.search(r"(\d+(?:\.\d+)*)", title)
        if not m:
            return (9999,)
        parts = tuple(int(x) for x in m.group(1).split("."))
        return parts

    items = list(outlines.items)
    overview = [it for it in items if (it.title or it.section).lower().startswith("response overview")]
    others = [it for it in items if it not in overview]
    others.sort(key=lambda it: _sec_sort_key((it.title or it.section)))
    ordered = overview + others

    wa = _add_table(doc, ["Section", "Page Budget", "Word Target", "Shalls", "Author", "SME", "Due", "Status"])

    # Enhance header styling and column alignment/widths
    try:
        wa.autofit = True
        # Repeat header row on new pages
        wa.rows[0].repeat_header = True  # type: ignore[attr-defined]
        # Shade header
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        for cell in wa.rows[0].cells:
            tcPr = cell._tc.get_or_add_tcPr()
            shd = OxmlElement('w:shd')
            shd.set(qn('w:fill'), 'D9E1F2')  # light blue fill
            tcPr.append(shd)
    except Exception:
        pass

    # Fill rows with zebra striping and alignment
    # Rulebook-driven owners/supporting and budgets
    owners = (rulebook or {}).get("owners", {}) if isinstance(rulebook, dict) else {}
    supporting = (rulebook or {}).get("supporting", {}) if isinstance(rulebook, dict) else {}
    task_budgets = ((rulebook or {}).get("budgets", {}) or {}).get("tasks", {}) if isinstance(rulebook, dict) else {}
    gaps = set(((rulebook or {}).get("gap_sections", []) or []) if isinstance(rulebook, dict) else [])

    def _root_sec(sec: str) -> str:
        import re
        m = re.match(r"^(\d+\.\d+)", sec or "")
        return m.group(1) if m else (sec.split()[0] if sec else "")

    for idx, it in enumerate(ordered, start=1):
        row = wa.add_row().cells
        title = it.title or it.section
        # Normalize 'Response to Section X' look
        if title.lower().startswith("response ") and "section" not in title.lower() and getattr(it, 'section', ''):
            title = f"Response to Section {getattr(it, 'section', '')}"
        sec = getattr(it, 'section', '') or ''
        root = _root_sec(sec)
        pb = float((task_budgets.get(root) if task_budgets.get(root) is not None else getattr(it, "page_budget", 1.0)) or 1.0)
        word_target = int(round(pb * words_per_page))
        shall_count = len(getattr(it, "related_shalls", []) or [])

        row[0].text = title
        row[1].text = f"{pb:.1f}"
        row[2].text = str(word_target)
        row[3].text = str(shall_count)
        row[4].text = str(owners.get(root, ""))
        row[5].text = str(supporting.get(root, ""))
        row[6].text = ""
        row[7].text = ("Gap" if root in gaps else "Draft")

        # Alignment for numeric columns
        try:
            for ci in (1, 2, 3):
                for p in row[ci].paragraphs:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        except Exception:
            pass

        # Zebra fill every other row
        try:
            if idx % 2 == 0:
                from docx.oxml import OxmlElement
                from docx.oxml.ns import qn
                for cell in wa.rows[idx].cells:
                    tcPr = cell._tc.get_or_add_tcPr()
                    shd = OxmlElement('w:shd')
                    shd.set(qn('w:fill'), 'EDF2FB')  # very light blue
                    tcPr.append(shd)
        except Exception:
            pass

    # Ensure a 'Proposal Development Plan' row exists at the end
    titles = {(it.title or it.section).strip().lower() for it in ordered}
    if "proposal development plan" not in titles:
        row = wa.add_row().cells
        row[0].text = "Proposal Development Plan"
        row[1].text = f"{1.0:.1f}"
        row[2].text = str(int(round(1.0 * words_per_page)))
        row[3].text = "0"
        row[4].text = row[5].text = row[6].text = ""
        row[7].text = "Draft"

    # Control Tables (Additional)
    doc.add_heading("Control Tables (Additional)", level=1)
    doc.add_heading("Deliverables", level=2)
    dt = _add_table(doc, ["Deliverable_Name (exact)", "PWS_Ref", "Cadence", "Format", "Owner", "Acceptance"])
    for it in outlines.items:
        label_map = _extract_label_map(it.bullets)
        pws_ref = ", ".join(sorted({getattr(shall_by_id.get(sid), 'section', '') for sid in it.related_shalls if shall_by_id.get(sid)}))
        for d in label_map.get("Deliverables", []) or []:
            row = dt.add_row().cells
            row[0].text = d
            row[1].text = pws_ref
            row[2].text = ""
            row[3].text = ""
            row[4].text = it.title or it.section
            row[5].text = ""

    # Risk Register (pair Risks with Mitigations when possible)
    doc.add_heading("Risk Register", level=2)
    rr = _add_table(doc, ["Risk", "Likelihood", "Impact", "Mitigation", "Owner", "Trigger"])
    for it in outlines.items:
        label_map = _extract_label_map(it.bullets)
        risks = label_map.get("Risks", []) or []
        mits = label_map.get("Mitigations", []) or []
        for idx, rsk in enumerate(risks):
            row = rr.add_row().cells
            row[0].text = rsk
            row[1].text = "Med"
            row[2].text = "Med"
            row[3].text = mits[idx] if idx < len(mits) else (mits[0] if mits else "")
            row[4].text = it.title or it.section
            row[5].text = ""

    # Crosswalk (Requirement -> Addressed In)
    doc.add_heading("Crosswalk", level=2)
    cw = _add_table(doc, ["Requirement", "Addressed_In (page/para)", "Owner", "Gap/Notes"])
    # Build coverage map from compliance matrix
    cov = {}
    for r in matrix.rows:
        cov[r.shall_id] = r.covered_by[:]
    for s in getattr(reqs, "shalls", []):
        row = cw.add_row().cells
        req_text = s.text.strip()
        row[0].text = req_text[:240] + ("…" if len(req_text) > 240 else "")
        addressed = (cov.get(s.id) or [])
        row[1].text = ", ".join(addressed[:2])  # section titles
        row[2].text = ""
        row[3].text = "Covered" if addressed else "Gap"

    # Figures (flowchart/gantt) if present
    if image_paths:
        doc.add_heading("Figures", level=1)
        for p in image_paths:
            doc.add_paragraph(os.path.basename(p))
            doc.add_picture(p, width=Inches(6))

    # Mermaid diagrams (Prompt 8) placed under Solution Architecture / Management Approach
    if mermaid_diagrams:
        half = (len(mermaid_diagrams) + 1) // 2
        soln = mermaid_diagrams[:half]
        mgmt = mermaid_diagrams[half:]
        from io import BytesIO
        if soln:
            doc.add_heading("Solution Architecture", level=1)
            for idx, m in enumerate(soln, start=1):
                try:
                    png = render_mermaid_to_png(m)
                    doc.add_paragraph(f"Figure SA-{idx}")
                    doc.add_picture(BytesIO(png), width=Inches(6))
                except Exception as e:
                    doc.add_paragraph(f"[Mermaid render error: {e}]")
        if mgmt:
            doc.add_heading("Management Approach", level=1)
            for idx, m in enumerate(mgmt, start=1):
                try:
                    png = render_mermaid_to_png(m)
                    doc.add_paragraph(f"Figure MA-{idx}")
                    doc.add_picture(BytesIO(png), width=Inches(6))
                except Exception as e:
                    doc.add_paragraph(f"[Mermaid render error: {e}]")

    # Enforce a 40-page limit by using page budgets from outlines (target 35–40 pages)
    max_pages = 40.0
    used_pages = 0.0

    doc.add_heading("Technical Approach & Methodology", level=1)
    # shall_by_id built above
    for item in outlines.items:
        if used_pages + (item.page_budget or 0.0) > max_pages:
            doc.add_paragraph(
                "Remaining sections omitted to keep proposal within the 40-page cap (target 35–40).")
            break

        doc.add_heading(item.title or item.section, level=2)
        # Extract labeled bullets to a map
        label_map = _extract_label_map(item.bullets)

        # 1) Section Summary table (Label / Details)
        if label_map:
            tbl = doc.add_table(rows=1, cols=2)
            tbl.style = "Light Grid Accent 1"
            hdr = tbl.rows[0].cells
            hdr[0].text = "Item"
            hdr[1].text = "Details"
            order = [
                "Approach", "Deliverables", "Schedule", "Risks",
                "Mitigations", "QA", "Compliance",
            ]
            for key in order:
                if key in label_map:
                    for val in label_map[key]:
                        row = tbl.add_row().cells
                        row[0].text = key
                        row[1].text = val
            # Caption
            cap = doc.add_paragraph("Section Summary")
            cap.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        # 2) Requirements Coverage table for this outline item
        if getattr(item, "related_shalls", None):
            tbl2 = doc.add_table(rows=1, cols=3)
            tbl2.style = "Light Grid Accent 1"
            h2 = tbl2.rows[0].cells
            h2[0].text = "Shall ID"
            h2[1].text = "PWS Section"
            h2[2].text = "How Addressed"
            addressed = ", ".join(label_map.get("Approach", [])[:1] or label_map.get("Deliverables", [])[:1])
            for sid in item.related_shalls:
                sh = shall_by_id.get(sid)
                row = tbl2.add_row().cells
                row[0].text = sid
                row[1].text = (sh.section if sh else "")
                row[2].text = addressed or (item.title or item.section)
            cap2 = doc.add_paragraph("Requirements Coverage")
            cap2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    # Generate narrative paragraphs from bullets
        try:
            paras = expand_bullets_to_paragraphs(item.title or item.section, item.bullets, item.related_shalls, model=model)
        except Exception:
            paras = []
        if paras:
            for p in paras:
                doc.add_paragraph(p)
        else:
            # Fallback to bullets
            # If this section is an "elements" or "technical overview summary", render bullets as a table
            title_lc = f"{item.title} {item.section}".lower()
            if ("elements" in title_lc) or ("technical overview summary" in title_lc):
                tbl = doc.add_table(rows=1, cols=2)
                tbl.style = "Light Grid Accent 1"
                hdr = tbl.rows[0].cells
                hdr[0].text = "Element"
                hdr[1].text = "Details"
                for b in item.bullets:
                    row = tbl.add_row().cells
                    # Try to split on ':' to separate label/value if present
                    if ":" in b:
                        k, v = b.split(":", 1)
                        row[0].text = k.strip()
                        row[1].text = v.strip()
                    else:
                        row[0].text = "•"
                        row[1].text = b
            else:
                for b in item.bullets:
                    # bold label like [Approach]
                    if b.startswith("[") and "]" in b:
                        label, rest = b.split("]", 1)
                        para = doc.add_paragraph()
                        r1 = para.add_run(label + "] ")
                        r1.bold = True
                        para.add_run(rest.strip())
                    else:
                        doc.add_paragraph(b, style="List Bullet")

        used_pages += float(item.page_budget or 0.0)

    doc.add_heading("Compliance Matrix", level=1)
    table = doc.add_table(rows=1, cols=4)
    hdr = table.rows[0].cells
    hdr[0].text = "Shall ID"
    hdr[1].text = "Section"
    hdr[2].text = "Covered By"
    hdr[3].text = "Status"
    for r in matrix.rows:
        row = table.add_row().cells
        row[0].text = r.shall_id
        row[1].text = r.section
        row[2].text = ", ".join(r.covered_by)
        row[3].text = r.status

    # Apply branding (header + footer) at the end so it covers all sections
    _apply_branding(doc)

    # Appendix with capability compliance summary (Prompt 9)
    if capability_compliance:
        doc.add_page_break()
        doc.add_heading("Appendix A – Capability Compliance", level=1)
        tbl = doc.add_table(rows=1, cols=4)
        tbl.style = "Light Grid Accent 1"
        hdr = tbl.rows[0].cells
        hdr[0].text = "Requirement"
        hdr[1].text = "Section"
        hdr[2].text = "Coverage"
        hdr[3].text = "Notes"
        covered_count = 0
        for row in capability_compliance:
            r = tbl.add_row().cells
            r[0].text = row.get("Requirement", "")
            r[1].text = row.get("Section", "")
            cov = row.get("Coverage", "")
            if cov.lower().startswith("yes"):
                covered_count += 1
            r[2].text = cov
            r[3].text = row.get("Notes", "")
        pct = 0.0
        if capability_compliance:
            pct = covered_count / max(1, len(capability_compliance)) * 100.0
        summ = doc.add_paragraph(f"Coverage: {covered_count}/{len(capability_compliance)} ({pct:.1f}%) capabilities addressed in outline.")
        summ.alignment = WD_ALIGN_PARAGRAPH.LEFT

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    doc.save(out_path)

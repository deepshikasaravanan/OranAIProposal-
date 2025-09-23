"""Cover page builder for proposal documents.

This module provides a single function `build_cover_page` that appends a
fully formatted cover (first page) to an existing python-docx `Document`.
It does NOT save the file; the caller is responsible for saving.

Design goals:
- Pure python-docx (Pillow only if image resizing is needed; currently optional)
- Defensive: tolerate missing optional fields without crashing
- Layout: Centered primary title block, agency & solicitation metadata band,
  submission details, and a footer signature/contact block.
- Minimal branding hook: attempts to insert a logo if standard Oran logo path
  or env overrides are present (re-using logic conceptually from builder_docx).

Expected JSON structure (examples/cover_sample.json provides a concrete sample):
{
  "company": {"name": "Oran Inc.", "address": "123 Tech Way, Arlington, VA", "duns": "123456789", "cage": "1ABCD"},
  "opportunity": {"title": "Enterprise Data Platform Modernization", "agency": "Department of Homeland Security", "office": "OCIO", "solicitation_number": "HS-EDP-25-001", "naics": "541512", "set_aside": "Small Business"},
  "submission": {"due_date": "2025-10-15", "version": "Vol 1 Rev A", "confidentiality": "Proprietary & Confidential"},
  "contacts": {"program_manager": {"name": "Jane Doe", "email": "jane.doe@oran.ai", "phone": "(555) 123-4567"}, "contracts": {"name": "John Smith", "email": "john.smith@oran.ai"}},
  "prepared_for": "Department of Homeland Security",
  "prepared_by": "Oran Inc.",
  "disclaimer": "Use or disclosure is subject to the restriction on the title page of this proposal.",
  "logo_path": "web/static/oran_logo.png"
}

Only a subset is required; missing keys are skipped gracefully.
"""
from __future__ import annotations

import os
from typing import Dict, Any, Optional, List, Union, Tuple
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.section import WD_ORIENTATION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pydantic import BaseModel, Field, ValidationError, model_validator

DEFAULT_PRIMARY_HEX = "#0A3768"
DEFAULT_ACCENT_HEX = "#F6A800"
DEFAULT_LIGHT_HEX = "#F2F6FB"


def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    """Return (r,g,b) tuple from #RRGGBB; fallback (0,0,0)."""
    h = hex_code.lstrip('#')
    if len(h) != 6:
        return (0, 0, 0)
    try:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    except ValueError:
        return (0, 0, 0)


def _hex_to_rgb(hex_code: str) -> RGBColor:  # internal existing usage
    h = hex_code.lstrip('#')
    if len(h) != 6:
        return RGBColor(0, 0, 0)
    try:
        r = int(h[0:2], 16)
        g = int(h[2:4], 16)
        b = int(h[4:6], 16)
        return RGBColor(r, g, b)
    except ValueError:
        return RGBColor(0, 0, 0)


class Branding(BaseModel):
    logo_path: Optional[str] = None
    primary_hex: str = DEFAULT_PRIMARY_HEX
    accent_hex: str = DEFAULT_ACCENT_HEX
    light_hex: str = DEFAULT_LIGHT_HEX

    @property
    def primary_rgb(self) -> RGBColor:  # pragma: no cover - simple property
        return _hex_to_rgb(self.primary_hex)

    @property
    def accent_rgb(self) -> RGBColor:  # pragma: no cover
        return _hex_to_rgb(self.accent_hex)

    @property
    def light_rgb(self) -> RGBColor:  # pragma: no cover
        return _hex_to_rgb(self.light_hex)


class Contact(BaseModel):
    name: str
    title: Optional[str] = None
    org: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class CoverInfo(BaseModel):
    customer_logo_path: Optional[str] = None
    title_lines: List[str] = Field(default_factory=lambda: ["", "", ""])
    notice_id_label: Optional[str] = None
    submitted_via: str = "email to:"
    contacts: List[Contact] = Field(default_factory=list)
    submitted_on: Optional[str] = None

    @model_validator(mode="after")
    def _ensure_title_lines(self):  # pragma: no cover - simple length enforce
        # Guarantee exactly 3 lines (pad or trim)
        lines = self.title_lines[:3]
        while len(lines) < 3:
            lines.append("")
        self.title_lines = lines
        return self


class PreparedBy(BaseModel):
    company_name: str
    address_lines: List[str] = Field(default_factory=list)
    uei: Optional[str] = None
    cage: Optional[str] = None
    duns: Optional[str] = None
    poc_name: Optional[str] = None
    poc_email: Optional[str] = None
    poc_phone: Optional[str] = None
    alt_poc_name: Optional[str] = None
    alt_poc_email: Optional[str] = None
    alt_poc_phone: Optional[str] = None
    contract_vehicle: Optional[str] = None
    company_size: Optional[str] = None


class Pillar(BaseModel):
    label: str
    image_path: Optional[str] = None


class Strips(BaseModel):
    processes: List[str] = Field(default_factory=list)
    people: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)


class CoverData(BaseModel):
    branding: Branding = Field(default_factory=Branding)
    cover: CoverInfo
    prepared_by: PreparedBy
    pillars: List[Pillar] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    standards: List[str] = Field(default_factory=list)
    strips: Strips = Field(default_factory=Strips)
    footer_disclaimer: Optional[str] = None
    team_image_path: Optional[str] = None
    team_image_caption: Optional[str] = Field(default="Our people are the cornerstone of our success.")

    @model_validator(mode="after")
    def _validate_required(self):  # pragma: no cover simple validation
        if not any(line.strip() for line in self.cover.title_lines):
            raise ValueError("At least one non-empty title line is required (cover.title_lines)")
        if not self.cover.contacts:
            raise ValueError("At least one contact is required (cover.contacts)")
        return self


def ensure_cover_styles(doc: Document, branding: Branding) -> None:
    """Create paragraph styles if they don't already exist.

    Prompt 12 tweaks:
    - Reduced TitleBig/Mid/Small by 2pt (28->26, 26->24, 24->22)
    - Will add 2pt space before/after for heading bar styles (BannerCaption, NoticeId)
    """
    style_map = {
        "TitleBig": {"size": 28, "bold": True, "color": branding.primary_hex},
        "TitleMid": {"size": 26, "bold": True, "color": branding.primary_hex},
        "TitleSmall": {"size": 24, "bold": True, "color": branding.primary_hex},
        "Small": {"size": 9.5, "bold": False, "color": branding.primary_hex},
        "CardHeader": {"size": 11, "bold": True, "color": branding.primary_hex, "all_caps": True},
        "BannerCaption": {"size": 10, "bold": True, "color": "#FFFFFF", "all_caps": True},
        "StripLabel": {"size": 9, "bold": True, "color": branding.accent_hex, "all_caps": True},
        "Disclaimer": {"size": 8, "bold": False, "color": "#555555", "justify": True},
        "NoticeId": {"size": 13, "bold": True, "color": branding.accent_hex},
    }
    styles = doc.styles
    for name, spec in style_map.items():
        if name in styles:  # already exists
            continue
        s = styles.add_style(name, 1)  # 1 = paragraph style
        font = s.font
        font.size = Pt(spec["size"])
        font.bold = spec.get("bold", False)
        r, g, b = hex_to_rgb(spec["color"])
        font.color.rgb = RGBColor(r, g, b)
        if spec.get("all_caps"):
            font.all_caps = True
        # Apply paragraph-level formatting for heading bar styles
        if name in ("BannerCaption", "NoticeId"):
            pf = s.paragraph_format
            try:
                pf.space_before = Pt(2)
                pf.space_after = Pt(2)
            except Exception:
                pass
        if spec.get("justify"):
            # style alignment left as default; justification applied per paragraph
            pass


def _clear_table_borders(tbl):  # pragma: no cover - XML manipulation
    for row in tbl.rows:
        for cell in row.cells:
            tcPr = cell._tc.get_or_add_tcPr()
            for tag in ("w:tcBorders",):
                for el in tcPr.xpath(f".//{tag}"):
                    tcPr.remove(el)


def _set_cell_border(cell, **kwargs):  # pragma: no cover - XML manipulation
    # kwargs: top, bottom, start, end each = dict(sz, val, color, space)
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = tcPr.first_child_found_in("w:tcBorders")
    if tcBorders is None:
        tcBorders = OxmlElement('w:tcBorders')
        tcPr.append(tcBorders)
    for edge in ("start", "top", "end", "bottom"):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = OxmlElement(f"w:{edge}")
            for k, v in edge_data.items():
                tag.set(qn(f"w:{k}"), str(v))
            tcBorders.append(tag)


def _logo_candidate(explicit: Optional[str]) -> Optional[str]:
    """Return a usable logo path if present."""
    paths = [
        explicit,
        os.getenv("ORAN_LOGO_PATH"),
        os.path.join("web", "static", "oran_logo.png"),
        os.path.join("assets", "oran_logo.png"),
    ]
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None


def _mark_table_no_split(tbl):  # pragma: no cover - XML manipulation
    """Set w:cantSplit on each row to discourage page breaks inside table."""
    from docx.oxml import OxmlElement
    for row in tbl.rows:
        tr = row._tr
        trPr = tr.get_or_add_trPr()
        cs = OxmlElement('w:cantSplit')
        trPr.append(cs)


def build_cover_page(doc: Document, data: Union[Dict[str, Any], CoverData]) -> Document:
    """Append a fully formatted first (cover) page to `doc` using new CoverData schema.

    Backward compatibility: if legacy keys like `opportunity` or `company` are present
    (previous sample), they are mapped into the new schema best-effort.
    """
    # Normalize to CoverData
    cover_data: CoverData
    if isinstance(data, CoverData):
        cover_data = data
    else:
        # Legacy mapping
        if "cover" not in data and ("opportunity" in data or "submission" in data):
            opp = data.get("opportunity", {})
            submission = data.get("submission", {})
            contacts_legacy = data.get("contacts", {})
            contact_list = []
            # Try to derive contacts from legacy structure
            pm = contacts_legacy.get("program_manager") if isinstance(contacts_legacy, dict) else None
            if isinstance(pm, dict) and pm.get("name"):
                contact_list.append({
                    "name": pm.get("name"),
                    "title": pm.get("title"),
                    "org": data.get("prepared_by") or "",
                    "email": pm.get("email"),
                    "phone": pm.get("phone"),
                })
            ct = contacts_legacy.get("contracts") if isinstance(contacts_legacy, dict) else None
            if isinstance(ct, dict) and ct.get("name"):
                contact_list.append({
                    "name": ct.get("name"),
                    "title": "Contracts",
                    "org": data.get("prepared_by") or "",
                    "email": ct.get("email"),
                })
            legacy_cover = {
                "title_lines": [opp.get("title") or data.get("title") or "Proposal Submission", opp.get("agency", ""), opp.get("solicitation_number", "")],
                "notice_id_label": opp.get("solicitation_number"),
                "submitted_via": "email to:",
                "submitted_on": submission.get("due_date"),
                "contacts": contact_list or [{"name": "TBD Contact"}],
            }
            company = data.get("company", {})
            legacy_prepared = {
                "company_name": company.get("name", ""),
                "address_lines": [company.get("address", "")],
                "duns": company.get("duns"),
                "cage": company.get("cage"),
            }
            mapped = {
                "branding": {"logo_path": data.get("logo_path")},
                "cover": legacy_cover,
                "prepared_by": legacy_prepared,
                "footer_disclaimer": submission.get("confidentiality") or data.get("disclaimer"),
            }
            for key in ("pillars", "certifications", "standards", "strips"):
                if key in data:
                    mapped[key] = data[key]
            data = mapped
        try:
            cover_data = CoverData(**data)  # type: ignore[arg-type]
        except ValidationError as e:
            raise ValueError(f"CoverData validation error: {e}") from e

    branding = cover_data.branding
    cover = cover_data.cover
    prepared = cover_data.prepared_by

    # Colors resolved via styles; direct RGB vars no longer required.

    # Page setup: Letter portrait, margins
    if doc.sections:
        section = doc.sections[0]
        section.orientation = WD_ORIENTATION.PORTRAIT
        section.page_height = Inches(11)
        section.page_width = Inches(8.5)
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.6)
        section.right_margin = Inches(0.6)

    ensure_cover_styles(doc, branding)

    # Top spacer (styled small)
    doc.add_paragraph("\n", style="Small")

    # Logo row (optional)
    logo = _logo_candidate(branding.logo_path)

    # Header table (logo + prepared by card)
    header_tbl = doc.add_table(rows=1, cols=2)
    header_tbl.autofit = True
    try:
        _mark_table_no_split(header_tbl)
    except Exception:
        pass
    try:
        _clear_table_borders(header_tbl)
    except Exception:
        pass
    left_cell = header_tbl.cell(0, 0)
    right_cell = header_tbl.cell(0, 1)

    # Left: logo or company name
    if logo:
        p_l = left_cell.paragraphs[0]
        p_l.alignment = WD_ALIGN_PARAGRAPH.LEFT
        try:
            run_l = p_l.add_run()
            run_l.add_picture(logo, height=Inches(0.9))
        except Exception:
            p_l.add_run(prepared.company_name or "Company")
    else:
        p_l = left_cell.paragraphs[0]
        p_l.style = "TitleSmall"
        run_l = p_l.add_run(prepared.company_name or "Company")
        run_l.bold = True

    # Right: Prepared by card
    card_para = right_cell.paragraphs[0]
    card_para.style = "CardHeader"
    card_para.add_run("Prepared by:")
    lines = []
    if prepared.company_name:
        lines.append(prepared.company_name)
    if prepared.address_lines:
        lines.extend(prepared.address_lines)
    id_parts = []
    if prepared.uei:
        id_parts.append(f"UEI: {prepared.uei}")
    if prepared.cage:
        id_parts.append(f"CAGE: {prepared.cage}")
    if prepared.duns:
        id_parts.append(f"DUNS: {prepared.duns}")
    if id_parts:
        lines.append(" | ".join(id_parts))
    if prepared.contract_vehicle:
        lines.append(f"Contract Vehicle: {prepared.contract_vehicle}")
    if prepared.company_size:
        lines.append(f"Company Size: {prepared.company_size}")
    if prepared.poc_name:
        lines.append(f"POC: {prepared.poc_name} {prepared.poc_email or ''} {prepared.poc_phone or ''}".strip())
    if prepared.alt_poc_name:
        lines.append(f"Alt POC: {prepared.alt_poc_name} {prepared.alt_poc_email or ''} {prepared.alt_poc_phone or ''}".strip())
    if lines:
        block = right_cell.add_paragraph("\n".join(lines))
        block.style = "Small"
    # Border around right cell only
    try:
        _set_cell_border(right_cell,
                         top={'val': 'single', 'sz': '6', 'color': 'C0C0C0', 'space': '0'},
                         bottom={'val': 'single', 'sz': '6', 'color': 'C0C0C0', 'space': '0'},
                         start={'val': 'single', 'sz': '6', 'color': 'C0C0C0', 'space': '0'},
                         end={'val': 'single', 'sz': '6', 'color': 'C0C0C0', 'space': '0'})
    except Exception:
        pass
    # Light shading for card
    try:
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        tcPr = right_cell._tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:fill'), branding.light_hex.lstrip('#'))
        tcPr.append(shd)
    except Exception:
        pass

    # Spacer after header table
    doc.add_paragraph("", style="Small")
    # Optional customer logo beneath header if provided
    cust_logo = _logo_candidate(cover.customer_logo_path)
    if cust_logo and os.path.exists(cust_logo):
        try:
            p_cust = doc.add_paragraph()
            p_cust.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run_c = p_cust.add_run()
            run_c.add_picture(cust_logo, width=Inches(1.6))
        except Exception:
            pass

    # Main Title
    # Title lines (up to 3)
    for idx, line in enumerate(cover.title_lines):
        if not line.strip():
            continue
        p_title = doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
        style_name = "TitleBig" if idx == 0 else "TitleMid" if idx == 1 else "TitleSmall"
        p_title.style = style_name
        p_title.add_run(line)

    # Agency / Prepared for line
    # Notice ID label line if present
    if cover.notice_id_label:
        p_notice = doc.add_paragraph(style="NoticeId")
        p_notice.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_notice.add_run(cover.notice_id_label)

    # Horizontal rule simulation (thin underscore)
    # Space after notice
    doc.add_paragraph("", style="Small")

    # Metadata table (solicitation info, company codes)
    # Two-column block: left = Submitted via contacts, right = metadata table
    contacts_meta_tbl = doc.add_table(rows=1, cols=2)
    contacts_meta_tbl.autofit = True
    try:
        _mark_table_no_split(contacts_meta_tbl)
    except Exception:
        pass
    left_c = contacts_meta_tbl.cell(0, 0)
    right_c = contacts_meta_tbl.cell(0, 1)
    # Left: submitted via header
    left_para = left_c.paragraphs[0]
    left_para.style = "Small"
    run_label = left_para.add_run("Submitted via email to:")
    run_label.bold = True
    # Contact cards
    for c in cover.contacts:
        # Name line (bold)
        name_p = left_c.add_paragraph()
        name_p.style = "Small"
        name_run = name_p.add_run(c.name)
        name_run.bold = True
        # Title + org
        title_org_parts = []
        if c.title:
            title_org_parts.append(c.title)
        if c.org:
            title_org_parts.append(c.org)
        if title_org_parts:
            to_p = left_c.add_paragraph(" | ".join(title_org_parts))
            to_p.style = "Small"
        if c.email:
            em_p = left_c.add_paragraph(c.email)
            em_p.style = "Small"
    if cover.submitted_on:
        sub_p = left_c.add_paragraph(f"Submitted On: {cover.submitted_on}")
        sub_p.style = "Small"

    # Right: metadata table (reuse certain fields)
    meta_rows = []
    if prepared.uei:
        meta_rows.append(("UEI", prepared.uei))
    if prepared.duns:
        meta_rows.append(("DUNS", prepared.duns))
    if prepared.cage:
        meta_rows.append(("CAGE", prepared.cage))
    if prepared.contract_vehicle:
        meta_rows.append(("Vehicle", prepared.contract_vehicle))
    if prepared.company_size:
        meta_rows.append(("Size", prepared.company_size))
    if meta_rows:
        meta_tbl = right_c.add_table(rows=len(meta_rows), cols=2)
        for i, (k, v) in enumerate(meta_rows):
            meta_tbl.cell(i, 0).text = k
            meta_tbl.cell(i, 1).text = str(v)
            for cell in meta_tbl.row_cells(i):
                for para in cell.paragraphs:
                    para.style = "Small"
    # Spacer after two-column block
    doc.add_paragraph("", style="Small")

    # Pillar banner (three columns)
    if cover_data.pillars:
        pillar_tbl = doc.add_table(rows=1, cols=3)
        pillar_tbl.autofit = True
        try:
            _mark_table_no_split(pillar_tbl)
        except Exception:
            pass
        # Normalize to length 3
        pillars = list(cover_data.pillars)[:3]
        while len(pillars) < 3:
            pillars.append(Pillar(label=""))
        for idx, pillar in enumerate(pillars):
            cell = pillar_tbl.cell(0, idx)
            # Clear default paragraph
            p0 = cell.paragraphs[0]
            p0.text = ""
            # Insert image if exists
            if pillar.image_path and os.path.exists(pillar.image_path):
                try:
                    img_p = cell.add_paragraph()
                    img_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    run_img = img_p.add_run()
                    run_img.add_picture(pillar.image_path, height=Inches(2.0))
                except Exception:
                    pass
            # Caption strip
            if pillar.label:
                cap_p = cell.add_paragraph(pillar.label.upper())
                cap_p.style = "BannerCaption"
                cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                # Shading background primary
                try:
                    from docx.oxml import OxmlElement
                    from docx.oxml.ns import qn
                    tcPr = cell._tc.get_or_add_tcPr()
                    shd = OxmlElement('w:shd')
                    shd.set(qn('w:fill'), branding.primary_hex.lstrip('#'))
                    tcPr.append(shd)
                except Exception:
                    pass
        # Spacer after pillars
        doc.add_paragraph("", style="Small")

    # Lower band: Left certifications, Center team image + caption, Right standards
    if cover_data.certifications or cover_data.standards or cover_data.team_image_path:
        lower_tbl = doc.add_table(rows=1, cols=3)
        lower_tbl.autofit = True
        try:
            _mark_table_no_split(lower_tbl)
        except Exception:
            pass
        try:
            _clear_table_borders(lower_tbl)
        except Exception:
            pass
        # Left column: certifications
        left_col = lower_tbl.cell(0, 0)
        if cover_data.certifications:
            head_p = left_col.paragraphs[0]
            head_p.style = "BannerCaption"
            head_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            head_p.text = "BUSINESS CERTIFICATIONS"
            try:
                from docx.oxml import OxmlElement
                from docx.oxml.ns import qn
                tcPr = left_col._tc.get_or_add_tcPr()
                shd = OxmlElement('w:shd')
                shd.set(qn('w:fill'), branding.primary_hex.lstrip('#'))
                tcPr.append(shd)
            except Exception:
                pass
            for it in cover_data.certifications:
                p_it = left_col.add_paragraph(f"• {it}")
                p_it.style = "Small"
        # Center column: team image (optional)
        center_col = lower_tbl.cell(0, 1)
        p_center = center_col.paragraphs[0]
        p_center.text = ""
        if cover_data.team_image_path and os.path.exists(cover_data.team_image_path):
            try:
                img_p = center_col.add_paragraph()
                img_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run_team = img_p.add_run()
                run_team.add_picture(cover_data.team_image_path, width=Inches(1.8))
            except Exception:
                pass
        if cover_data.team_image_caption:
            cap_p = center_col.add_paragraph(cover_data.team_image_caption)
            cap_p.style = "Small"
            cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # Right column: standards
        right_col = lower_tbl.cell(0, 2)
        if cover_data.standards:
            head_p2 = right_col.paragraphs[0]
            head_p2.style = "BannerCaption"
            head_p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
            head_p2.text = "STANDARDS, FRAMEWORKS & CERTS"
            try:
                from docx.oxml import OxmlElement
                from docx.oxml.ns import qn
                tcPr2 = right_col._tc.get_or_add_tcPr()
                shd2 = OxmlElement('w:shd')
                shd2.set(qn('w:fill'), branding.primary_hex.lstrip('#'))
                tcPr2.append(shd2)
            except Exception:
                pass
            for it in cover_data.standards:
                p_it2 = right_col.add_paragraph(f"• {it}")
                p_it2.style = "Small"
        doc.add_paragraph("", style="Small")

    # PROCESS / PEOPLE / TOOLS strips
    strips = cover_data.strips
    if any([strips.processes, strips.people, strips.tools]):
        s_tbl = doc.add_table(rows=1, cols=3)
        s_tbl.autofit = True
        try:
            _mark_table_no_split(s_tbl)
        except Exception:
            pass
        labels = [
            ("PROCESSES", strips.processes),
            ("PEOPLE", strips.people),
            ("TOOLS", strips.tools),
        ]
        for col, (label, items) in enumerate(labels):
            cell = s_tbl.cell(0, col)
            # Clear default paragraph text
            p0 = cell.paragraphs[0]
            p0.text = ""
            hdr_p = cell.add_paragraph(label)
            hdr_p.style = "StripLabel"
            content = ", ".join(items) if items else ""
            if content:
                body_p = cell.add_paragraph(content)
                body_p.style = "Small"
        doc.add_paragraph("", style="Small")

    # Contact block
    # (Removed old centered contact block in favor of structured layout)

    # Final footer disclaimer (always last on page before break)
    disclaimer = cover_data.footer_disclaimer
    if disclaimer:
        # Minimal spacer if needed
        doc.add_paragraph("", style="Small")
        p_disc = doc.add_paragraph(disclaimer, style="Disclaimer")
        p_disc.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    doc.add_page_break()
    return doc

__all__ = ["build_cover_page"]

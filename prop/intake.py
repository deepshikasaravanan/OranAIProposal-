import os
import re
"""Enhanced intake parsing per Prompt 3 requirements."""
from typing import List, Tuple, Dict
from .schema import Opportunity
from .utils import materialize_paths, extract_text_quick, parse_date_any, days_until, infer_capabilities
from .s3io import list_from_zip  # reuse for uniformity

# TODO: Consider moving regex patterns to a configurable YAML in configs/ later.

NAICS_RE = re.compile(r"NAICS\s*(?:Code)?\s*[:\-]?\s*([0-9]{5,6})", re.I)
SET_ASIDE_RE = re.compile(r"(8\(a\)|WOSB|SDVOSB|HUBZone|Small Business|SBA 8\(a\))", re.I)
TYPE_MAP = {
    "firm fixed": "FFP",
    "ffp": "FFP",
    "t&m": "T&M",
    "time and materials": "T&M",
    "labor hour": "LH",
    "lh": "LH",
    "cpff": "CPFF",
    "cost plus fixed fee": "CPFF",
}
DUE_RE = re.compile(r"(due by|proposals due|closing date|response due)[:\s]*([A-Za-z]{3,9} \d{1,2}, \d{4}|\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2})", re.I)
PAGE_RE = re.compile(r"page limit[s]?\s*(?:of)?\s*(\d+)", re.I)
CLEAR_RE = re.compile(r"(secret|ts/sci|clearance required)", re.I)
VEHICLE_RE = re.compile(r"(stars iii|8\(a\) stars|oasis|sewp|gsa)", re.I)


def _load_capability_taxonomy() -> Dict[str, List[str]]:
    """Load capability normalization mapping from configs/capability_taxonomy.yaml if present.
    Format expected:
      capability_key:
        - keyword1
        - keyword2
    """
    path = os.path.join("configs", "capability_taxonomy.yaml")
    if not os.path.exists(path):
        return {}
    try:
        import yaml  # type: ignore
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        # Ensure mapping[str, list[str]]
        out: Dict[str, List[str]] = {}
        for k, v in data.items():
            if isinstance(v, list):
                out[str(k)] = [str(x).lower() for x in v]
        return out
    except Exception:
        return {}


def _normalize_capabilities(raw_caps: List[str], taxonomy: Dict[str, List[str]]) -> List[str]:
    if not taxonomy:
        # Fallback to input if no taxonomy
        return sorted(set([c.lower() for c in raw_caps]))
    norm = set()
    for cap in raw_caps:
        lc = cap.lower()
        matched = False
        for key, keywords in taxonomy.items():
            if any(k in lc for k in keywords):
                norm.add(key)
                matched = True
        if not matched:
            norm.add(lc)
    return sorted(norm)


def parse_files_to_opportunity(paths: List[str]) -> Tuple[Opportunity, List[str]]:
    # 1) Materialize initial paths (supports local + s3 via materialize_paths)
    mats_initial = materialize_paths(paths)
    collected: List[str] = []
    # 2) Expand ZIPs and keep only PDF/DOCX
    for p in mats_initial:
        if p.lower().endswith('.zip'):
            try:
                for fp in list_from_zip(p):
                    if fp.lower().endswith(('.pdf', '.docx')):
                        collected.append(fp)
            except Exception:
                # TODO: surface warning about zip expansion failure
                pass
        else:
            if p.lower().endswith(('.pdf', '.docx')):
                collected.append(p)
    mats = collected
    if not mats:
        # fallback: include any text-like paths if user didn't provide PDF/DOCX
        mats = mats_initial

    opp = Opportunity()
    opp.type = "FFP"  # default
    opp.days_to_due = 12  # default

    texts = []
    for p in mats:
        try:
            texts.append(extract_text_quick(p))
        except Exception:
            pass
    full_text = "\n".join(texts)

    # Title heuristic: first non-empty line
    for line in full_text.splitlines():
        t = line.strip()
        if len(t) > 10:
            opp.title = opp.title or t[:140]
            break

    # Due date
    m = DUE_RE.search(full_text)
    if m:
        dt = parse_date_any(m.group(2))
        if dt:
            opp.due_date = dt.strftime("%Y-%m-%d")
            opp.days_to_due = days_until(dt)

    # NAICS
    m = NAICS_RE.search(full_text)
    if m:
        opp.naics = m.group(1)

    # Set-aside
    m = SET_ASIDE_RE.search(full_text)
    if m:
        opp.set_aside = m.group(1)

    # Type
    low = full_text.lower()
    for k, v in TYPE_MAP.items():
        if k in low:
            opp.type = v
            break

    # Page limit
    m = PAGE_RE.search(full_text)
    if m:
        try:
            opp.page_limit = int(m.group(1))
        except Exception:
            pass

    # Clearance
    if CLEAR_RE.search(full_text):
        opp.clearance_required = True
        # assume available unknown, keep default True to avoid blocker unless specified

    # Vehicle mentions
    vm = VEHICLE_RE.search(low)
    if vm:
        opp.vehicle = vm.group(1)

    # Capabilities from shall/should/must sentences
    shall_lines = []
    for ln in full_text.splitlines():
        if re.search(r"\b(shall|should|must)\b", ln, re.I):
            shall_lines.append(ln)
    raw_caps = list(set(infer_capabilities("\n".join(shall_lines))))
    taxonomy = _load_capability_taxonomy()
    opp.required_capabilities = _normalize_capabilities(raw_caps, taxonomy)

    # TODO: Improve title detection (capture lines after 'Title:' if present; current heuristic simplistic)
    # TODO: Page-limit extraction may misinterpret narrative uses of 'page'; consider focusing on Sections L & M.
    # TODO: Add classification of set_aside synonyms and multiple NAICS extraction.

    # org_capabilities (optional file)
    org_caps_file = os.path.join("prompts", "org_capabilities.txt")
    if os.path.exists(org_caps_file):
        with open(org_caps_file, "r", encoding="utf-8") as f:
            opp.org_capabilities = [x.strip() for x in f if x.strip()]

    return opp, mats

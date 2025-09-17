from .schema import RequirementGraph, ComplianceMatrix, ComplianceRow, Outlines
from typing import List, Dict

def build_matrix(reqs: RequirementGraph, outlines: Outlines) -> ComplianceMatrix:
    rows = []
    for s in reqs.shalls:
        covered_by = []
        for o in outlines.items:
            if s.id in o.related_shalls:
                covered_by.append(o.title or o.section)
        status = "covered" if covered_by else "uncovered"
        rows.append(ComplianceRow(shall_id=s.id, section=s.section, covered_by=covered_by, status=status))
    return ComplianceMatrix(rows=rows)


def build_compliance_matrix(required_capabilities: List[str], outline_sections: List[str]) -> List[Dict[str, str]]:
    """Produce capability compliance CSV-style rows.

    Coverage rule: If capability keyword appears (case-insensitive exact match of token) in any outline section title -> Yes else Gap.
    Notes: if Gap, note "Add coverage in outline" else "Covered".
    """
    outline_tokens = [s.lower() for s in outline_sections]
    # Simple normalization to allow devops to match devsecops: remove 'sec' in 'devsecops'
    normalized_titles = [t.replace('devsecops', 'devops') for t in outline_tokens]
    rows: List[Dict[str, str]] = []
    for cap in sorted(required_capabilities):
        cap_l = cap.lower()
        # Coverage if capability appears as a standalone token OR substring (e.g., devops in devsecops)
        covered = any(cap_l == tok for title in normalized_titles for tok in title.split()) or any(cap_l in title for title in normalized_titles)
        rows.append({
            "Requirement": cap,
            "Section": next((s for s in outline_sections if cap_l in s.lower()), ""),
            "Coverage": "Yes" if covered else "Gap",
            "Notes": "Covered" if covered else "Add coverage in outline",
        })
    return rows


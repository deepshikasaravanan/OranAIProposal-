from .schema import Outlines, OutlineItem


SECTION_TITLE = "Proposal Development Plan"


STEPS = [
    "[Approach] Always start with a roadmap and define Labor Categories.",
    "[Schedule] Include a kickoff meeting and generate an initial outline.",
    "[Compliance] Perform a compliance check immediately after creating the outline.",
    "[Approach] Assign authors to proposal sections.",
    "[QA] Conduct a Pink Team Review for first compliance and structure check; ensure requirements are addressed and direction is correct.",
    "[Approach] Request Pink Team input and assemble inputs into a working document.",
    "[Approach] Distribute the Pink Team document to the team for review.",
    "[QA] Conduct a Red Team Review at 85–90% solution to strengthen technical and management content.",
    "[QA] Send documents back to authors for adjudication of comments and revisions.",
    "[QA] Complete a full Red Review (prose draft).",
    "[QA] Perform an internal review of the management section.",
    "[Compliance] Verify that SF-33s, SF-18s, and SF-1449s are signed and amendments acknowledged.",
    "[QA] Review technical content again and send back for adjudication if needed.",
    "[Schedule] Prepare a submission email listing all required filenames.",
    "[QA] Conduct a Gold Review for final refinement, polishing content, graphics, and narrative.",
    "[Compliance] Ensure RFP compliance before submission.",
    "[QA] Perform a White Glove Review by a C-level executive and Proposal Manager (check grammar, RFP compliance, 508 compliance).",
    "[Deliverables] Incorporate all feedback and finalize the proposal.",
]


def ensure_proposal_development_steps(ol: Outlines) -> Outlines:
    # Find existing item
    idx = None
    for i, it in enumerate(ol.items):
        title = (it.title or it.section or "").lower()
        if "proposal development" in title or "proposal" in title and "development" in title:
            idx = i
            break
    if idx is None:
        item = OutlineItem(
            section="6",
            title=SECTION_TITLE,
            page_budget=1.0,
            bullets=list(STEPS),
            related_shalls=[],
        )
        ol.items.append(item)
    else:
        # Merge missing steps if existing section is present
        have = set(ol.items[idx].bullets)
        for s in STEPS:
            if s not in have:
                ol.items[idx].bullets.append(s)
    return ol


def get_proposal_development_steps():
    return list(STEPS)

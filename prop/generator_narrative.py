import json
from collections import defaultdict
from .llm_openai import OpenAIClient
import os
from .schema import RequirementGraph, Outlines, OutlineItem

def draft_outlines(reqs: RequirementGraph) -> Outlines:
    """Draft outlines using OpenAI; gracefully fallback to heuristic if API fails.

    Fallback strategy:
    - Group shalls by section
    - Create one outline item per section with a few bullets from shalls
    - Assign small default page budgets
    """
    try:
        client = OpenAIClient()
        shard = [{"id": s.id, "section": s.section, "text": s.text} for s in reqs.shalls[:200]]
        # Compose a stronger instruction with constraints
        # Optional BD checklist context
        chk = None
        dev6 = None
        try:
            chk_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "opportunity_process_checklist.md")
            if os.path.exists(chk_path):
                with open(chk_path, "r", encoding="utf-8") as f:
                    chk = f.read()
            dev6_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "proposal_development_steps.md")
            if os.path.exists(dev6_path):
                with open(dev6_path, "r", encoding="utf-8") as f:
                    dev6 = f.read()
        except Exception:
            chk = None
            dev6 = None

        system_msg = {
            "role": "system",
            "content": (
                "You are a senior government proposal writer. Create an industry-standard outline that is clear, "
                "compliant, and execution-focused. For each section, produce 3–7 labeled bullets using the tags: "
                "[Approach], [Deliverables], [Schedule], [Risks], [Mitigations], [QA], [Compliance]. Keep bullets "
                "short, action-oriented, and tied to shall IDs where applicable. Titles should be informative and "
                "client-centric. Page budgets between 0.25 and 1.0. Return JSON matching the schema."
            ),
        }
        user_msg = {
            "role": "user",
            "content": json.dumps({
                "context": {
                    "instruction": "Create an outline covering these 'shall' statements.",
                    "max_items": 15,
                    "bd_checklist": chk or "",
                    "proposal_development": dev6 or "",
                },
                "shalls": shard,
            }),
        }
        schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "items": {
                    "type": "array",
                    "maxItems": 20,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "section": {"type": "string"},
                            "title": {"type": "string"},
                            "page_budget": {"type": "number", "minimum": 0.1, "maximum": 2.0},
                            "bullets": {
                                "type": "array",
                                "minItems": 2,
                                "maxItems": 12,
                                "items": {"type": "string", "pattern": "^\\[(Approach|Deliverables|Schedule|Risks|Mitigations|QA|Compliance)\\] .+"}
                            },
                            "related_shalls": {
                                "type": "array",
                                "minItems": 1,
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["section", "title", "page_budget", "bullets", "related_shalls"]
                    }
                }
            },
            "required": ["items"]
        }
        try:
            content = client.json_completion_schema([system_msg, user_msg], name="outlines", schema=schema, strict=True)
        except Exception:
            # Fallback to generic JSON mode if schema-constrained fails
            content = client.json_completion([system_msg, user_msg])

        data = json.loads(content)
        items = []
        for it in data.get("items", []):
            items.append(OutlineItem(
                section=it.get("section", ""),
                title=it.get("title", ""),
                page_budget=float(it.get("page_budget", 0.5)),
                bullets=list(it.get("bullets", [])),
                related_shalls=list(it.get("related_shalls", [])),
            ))
        if items:
            return Outlines(items=items)
    except Exception:
        # Fall back below
        pass

    # Heuristic fallback
    by_sec = defaultdict(list)
    for s in reqs.shalls:
        sec = s.section or "General"
        by_sec[sec].append(s)

    items = []
    for sec, shs in list(by_sec.items())[:12]:
        bullets = [x.text[:180] + ("…" if len(x.text) > 180 else "") for x in shs[:5]]
        items.append(OutlineItem(
            section=sec,
            title=f"Response to Section {sec}" if sec != "General" else "Response Overview",
            page_budget=0.5,
            bullets=bullets,
            related_shalls=[x.id for x in shs[:10]],
        ))

    if not items:
        # Guarantee at least one item
        items.append(OutlineItem(
            section="General",
            title="Response Overview",
            page_budget=0.5,
            bullets=["Auto-generated outline due to unavailable LLM."],
            related_shalls=[s.id for s in reqs.shalls[:5]],
        ))

    return Outlines(items=items)

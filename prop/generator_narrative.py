import json
from collections import defaultdict
from typing import Optional
from .llm_openai import LLMClient
from .content_quality import ContentQualityController
import os
from .schema import RequirementGraph, Outlines, OutlineItem

def draft_outlines(reqs: RequirementGraph, model: Optional[str] = None) -> Outlines:
    """Draft outlines using OpenAI; gracefully fallback to heuristic if API fails.

    Fallback strategy:
    - Group shalls by section
    - Create one outline item per section with a few bullets from shalls
    - Assign small default page budgets
    """
    try:
        client = LLMClient(model=model)
        shard = [{"id": s.id, "section": s.section, "text": s.text} for s in reqs.shalls[:200]]
        # Compose a stronger instruction with constraints
        # Optional BD checklist context and full system prompt pack
        chk = None
        dev6 = None
        sys_pack = None
        try:
            chk_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "opportunity_process_checklist.md")
            if os.path.exists(chk_path):
                with open(chk_path, "r", encoding="utf-8") as f:
                    chk = f.read()
            dev6_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "proposal_development_steps.md")
            if os.path.exists(dev6_path):
                with open(dev6_path, "r", encoding="utf-8") as f:
                    dev6 = f.read()
            sys_pack_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "proposal_system_context.md")
            if os.path.exists(sys_pack_path):
                with open(sys_pack_path, "r", encoding="utf-8") as f:
                    sys_pack = f.read()
        except Exception:
            chk = None
            dev6 = None
            sys_pack = None

        # Load advanced business system prompt
        advanced_system = None
        advanced_outline = None
        try:
            system_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "advanced_business_system.md")
            if os.path.exists(system_path):
                with open(system_path, "r", encoding="utf-8") as f:
                    advanced_system = f.read()
            outline_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "advanced_outline_generation.md")
            if os.path.exists(outline_path):
                with open(outline_path, "r", encoding="utf-8") as f:
                    advanced_outline = f.read()
        except Exception:
            advanced_system = None
            advanced_outline = None

        system_msg = {
            "role": "system",
            "content": (
                (advanced_system or "") + "\n\n" + (advanced_outline or "") + "\n\n" +
                (sys_pack or "") + "\n\n"
                "You are a senior government proposal strategist writing for Fortune 500 defense contractors. "
                "Create proposal outlines that win $100M+ contracts by demonstrating clear business value, "
                "competitive advantages, and risk mitigation strategies.\n\n"
                "CRITICAL: Each outline item must address evaluation criteria with quantified benefits, "
                "specific implementation approaches, and competitive differentiation. Target 35-40 pages "
                "with substantive, business-analyst quality content.\n\n"
                "Use these business-focused bullet categories: [Executive-Value], [Technical-Solution], "
                "[Financial-Impact], [Risk-Control], [Implementation-Plan], [Success-Metrics], [Competitive-Edge]. "
                "Return JSON matching the exact schema provided."
            ),
        }
        user_msg = {
            "role": "user",
            "content": json.dumps({
                "context": {
                    "instruction": "Create an outline covering these 'shall' statements with a total page budget of 35–40 pages (>=35, do not exceed 40).",
                    "max_items": 24,
                    "bd_checklist": chk or "",
                    "proposal_development": dev6 or "",
                    "system_context": (sys_pack or "")[:4000],
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
                    "maxItems": 30,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "section": {"type": "string"},
                            "title": {"type": "string"},
                            "page_budget": {"type": "number", "minimum": 0.5, "maximum": 3.0},
                            "bullets": {
                                "type": "array",
                                "minItems": 6,
                                "maxItems": 14,
                                "items": {"type": "string", "pattern": "^\\[(Executive-Value|Technical-Solution|Financial-Impact|Risk-Control|Implementation-Plan|Success-Metrics|Competitive-Edge)\\] .+"}
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
            # Enhance content quality with business intelligence
            try:
                quality_controller = ContentQualityController(model=model)
                for item in items:
                    enhanced_bullets = quality_controller.add_business_intelligence(item.bullets)
                    item.bullets = enhanced_bullets
            except Exception:
                # Continue with original bullets if enhancement fails
                pass
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
    sections = list(by_sec.items())[:12]
    # Aim total fallback page budget around 35 when LLM unavailable
    per_budget = 35.0 / max(1, len(sections))
    per_budget = max(1.0, min(3.0, per_budget))
    labels = ["Executive-Value", "Technical-Solution", "Financial-Impact", "Risk-Control", "Implementation-Plan", "Success-Metrics", "Competitive-Edge"]
    for sec, shs in sections:
        # Create labeled bullets from actual shall text to preserve fidelity
        bullets = []
        for i, s in enumerate(shs[:7]):
            lab = labels[i % len(labels)]
            snippet = s.text.strip().replace("\n", " ")
            snippet = snippet[:180] + ("…" if len(snippet) > 180 else "")
            bullets.append(f"[{lab}] {snippet}")
        if not bullets:
            bullets = ["[Compliance] See PWS requirements in this section."]
        items.append(OutlineItem(
            section=sec,
            title=f"Response to Section {sec}" if sec != "General" else "Response Overview",
            page_budget=per_budget,
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

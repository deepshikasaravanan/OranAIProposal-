from typing import List, Dict, Any, Optional
import json
from .llm_openai import LLMClient
import os


def expand_bullets_to_paragraphs(title: str, bullets: List[str], shall_ids: List[str], model: Optional[str] = None) -> List[str]:
    """Turn bullets into 5-9 cohesive paragraphs with citations, metrics, and benefits.

    Returns a list of paragraph strings. Uses OpenAI with schema; falls back to simple joins.
    """
    if not bullets:
        return []
    try:
        client = LLMClient(model=model)
        # Load advanced prompts for superior content generation
        advanced_system = None
        advanced_paragraph = None
        try:
            system_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "advanced_business_system.md")
            if os.path.exists(system_path):
                with open(system_path, "r", encoding="utf-8") as f:
                    advanced_system = f.read()
            paragraph_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "advanced_paragraph_generation.md")
            if os.path.exists(paragraph_path):
                with open(paragraph_path, "r", encoding="utf-8") as f:
                    advanced_paragraph = f.read()
        except Exception:
            advanced_system = None
            advanced_paragraph = None

        system_msg = {
            "role": "system",
            "content": (
                (advanced_system or "") + "\n\n" + (advanced_paragraph or "") + "\n\n"
                "You are a senior proposal strategist writing evaluation-ready content for government business analysts "
                "and procurement evaluators. Your expertise includes business analysis, competitive intelligence, "
                "financial analysis, and risk management.\n\n"
                "CRITICAL MISSION: Transform outline bullets into comprehensive, business-focused paragraphs that "
                "demonstrate clear ROI, competitive advantages, and risk mitigation. Each paragraph must include "
                "quantified benefits, specific implementation details, and competitive differentiation.\n\n"
                "STRUCTURE: Lead with business value, support with technical approach, quantify benefits, "
                "address risks, provide success metrics, and emphasize competitive advantages. "
                "Use professional tone with specific metrics and PWS citations."
            ),
        }
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

        # Load business templates for enhanced content generation
        business_templates = None
        try:
            templates_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "business_templates.md")
            if os.path.exists(templates_path):
                with open(templates_path, "r", encoding="utf-8") as f:
                    business_templates = f.read()
        except Exception:
            business_templates = None

        user_msg = {
            "role": "user",
            "content": json.dumps(
                {
                    "title": title,
                    "bullets": bullets,
                    "related_shalls": shall_ids,
                    "business_templates": business_templates or "",
                    "instructions": (
                        "Transform the outline bullets into 5-7 comprehensive paragraphs (150-200 words each) "
                        "that demonstrate clear business value and competitive advantage. Each paragraph must:\n"
                        "1. Lead with quantified business benefit\n"
                        "2. Describe specific technical approach\n"
                        "3. Analyze business impact with ROI\n"
                        "4. Address risks with mitigation strategies\n"
                        "5. Define success metrics and KPIs\n"
                        "6. Emphasize competitive differentiation\n\n"
                        "Use the advanced prompts as your guide to create evaluation-ready content that wins contracts."
                    ),
                    "constraints": {
                        "paragraphs": {"min": 5, "max": 7},
                        "style": "Fortune 500 proposal quality, evaluation-ready, business analyst-focused with quantified ROI, competitive analysis, and risk mitigation",
                        "word_count_per_paragraph": "150-200 words",
                        "required_elements": ["business_value", "technical_approach", "financial_impact", "risk_mitigation", "success_metrics", "competitive_advantage"]
                    },
                    "bd_checklist": chk or "",
                    "proposal_development": dev6 or "",
                    "system_context": (sys_pack or "")[:4000],
                }
            ),
        }
        schema: Dict[str, Any] = {
            "type": "object",
            "properties": {
                "paragraphs": {
                    "type": "array",
                    "minItems": 5,
                    "maxItems": 9,
                    "items": {"type": "string"},
                }
            },
            "required": ["paragraphs"],
            "additionalProperties": False,
        }
        try:
            content = client.json_completion_schema(
                [system_msg, user_msg], name="narrative", schema=schema
            )
        except Exception:
            content = client.json_completion([system_msg, user_msg])
        data = json.loads(content)
        paras = [p.strip() for p in data.get("paragraphs", []) if isinstance(p, str) and p.strip()]
        if paras:
            return paras
    except Exception:
        pass
    # Fallback: naive paragraphization
    joined = "; ".join([b.rstrip(".") for b in bullets]) + "."
    return [joined]

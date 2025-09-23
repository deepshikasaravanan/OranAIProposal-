from typing import List, Dict, Any
import json
from .llm_openai import OpenAIClient
import os


def expand_bullets_to_paragraphs(title: str, bullets: List[str], shall_ids: List[str]) -> List[str]:
    """Turn bullets into 5-9 cohesive paragraphs with citations, metrics, and benefits.

    Returns a list of paragraph strings. Uses OpenAI with schema; falls back to simple joins.
    """
    if not bullets:
        return []
    try:
        client = OpenAIClient()
        system_msg = {
            "role": "system",
            "content": (
                "You are a senior proposal writer. Expand labeled bullets into cohesive, precise narrative paragraphs in a "
                "professional, active voice. Use the labels to structure content (Approach → methods/process, "
                "Deliverables → concrete outputs, Schedule → cadence & milestones, Risks/Mitigations → risk mgmt, "
                "QA → quality controls, Compliance → mapping to shall IDs). Avoid fluff; be specific and technical. "
                "Cite PWS references inline where applicable (e.g., [PWS 5.3.4])."
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

        user_msg = {
            "role": "user",
            "content": json.dumps(
                {
                    "title": title,
                    "bullets": bullets,
                    "related_shalls": shall_ids,
                    "constraints": {
                        "paragraphs": {"min": 5, "max": 9},
                        "style": "precise, technical, compliant; include metrics, benefits, and inline [PWS x.x.x] citations where relevant",
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

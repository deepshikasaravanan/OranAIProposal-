from typing import List, Dict, Any
import json
from .llm_openai import OpenAIClient
import os


def expand_bullets_to_paragraphs(title: str, bullets: List[str], shall_ids: List[str]) -> List[str]:
    """Turn bullets into 2-4 crisp paragraphs, mapping coverage and maintaining compliance tone.

    Returns a list of paragraph strings. Uses OpenAI with schema; falls back to simple joins.
    """
    if not bullets:
        return []
    try:
        client = OpenAIClient()
        system_msg = {
            "role": "system",
            "content": (
                "You are a senior proposal writer. Expand labeled bullets into cohesive narrative paragraphs in a "
                "professional, active voice. Use the labels to structure content (Approach → methods/process, "
                "Deliverables → concrete outputs, Schedule → cadence & milestones, Risks/Mitigations → risk mgmt, "
                "QA → quality controls, Compliance → mapping to shall IDs). Avoid fluff; be specific and technical."
            ),
        }
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

        user_msg = {
            "role": "user",
            "content": json.dumps(
                {
                    "title": title,
                    "bullets": bullets,
                    "related_shalls": shall_ids,
                    "constraints": {
                        "paragraphs": {"min": 2, "max": 5},
                        "style": "concise, technical, compliant",
                    },
                    "bd_checklist": chk or "",
                    "proposal_development": dev6 or "",
                }
            ),
        }
        schema: Dict[str, Any] = {
            "type": "object",
            "properties": {
                "paragraphs": {
                    "type": "array",
                    "minItems": 2,
                    "maxItems": 6,
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

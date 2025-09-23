# Copilot Memory Jog (Prompt 13)

Source of truth: `docs/COPILOT_PROMPT.md`.

Guidelines:
- Never hardcode secrets; always use environment variables.
- Never suggest portal or website scraping; rely on provided APIs / user inputs.
- All decision-related responses (scoring) must include:
  1. Decision Card markdown
  2. Blockers list
  3. Next Actions list
- Favor deterministic, auditable heuristics before LLM hallucination.
- Keep outputs concise and structured for downstream automation.

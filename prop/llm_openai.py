import os
import time
from typing import List, Dict, Any, Optional
from openai import OpenAI


class OpenAIClient:
    """Thin wrapper around OpenAI Chat Completions (JSON + simple helpers).

    Uses Optional[...] instead of PEP 604 unions for Python 3.9 compatibility.
    Only the minimal methods currently used by generators are kept. If you
    need tool calling again, re-introduce a guarded implementation.
    """

    def __init__(self, model: Optional[str] = None) -> None:
        # Prefer env var; fall back to reading a file path if provided
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            key_file = os.getenv("OPENAI_API_KEY_FILE")
            if key_file and os.path.isfile(key_file):
                try:
                    with open(key_file, "r", encoding="utf-8") as f:
                        api_key = f.read().strip()
                except Exception:
                    api_key = None  # will error below with clear guidance
        if not api_key:
            raise RuntimeError(
                "Missing OpenAI API key. Set OPENAI_API_KEY (recommended) or set OPENAI_API_KEY_FILE to a file containing the key."
            )

        self.client = OpenAI(api_key=api_key)
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        # Slightly lower default temperature to prefer precision
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.15"))
        # Increase default token budget to enable richer sections without manual env tuning
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "3000"))

    def _with_retry(self, func, *args, **kwargs):
        delays = [0.5, 1.5, 3.0]
        last_err = None
        for i, d in enumerate(delays + [0]):
            try:
                return func(*args, **kwargs)
            except Exception as e:  # noqa: BLE001
                last_err = e
                if i < len(delays):
                    time.sleep(d)
                else:
                    break
        raise last_err  # type: ignore[misc]

    def json_completion(self, messages: List[Dict[str, Any]]) -> str:
        resp = self._with_retry(
            self.client.chat.completions.create,
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return resp.choices[0].message.content or "{}"

    def json_completion_schema(
        self, messages: List[Dict[str, Any]], name: str, schema: Dict[str, Any], strict: bool = True
    ) -> str:
        # Newer OpenAI clients support response_format with JSON schema.
        # If it fails, caller will fall back to json_completion.
        resp = self._with_retry(
            self.client.chat.completions.create,
            model=self.model,
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {"name": name, "schema": schema, "strict": strict},
            },
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return resp.choices[0].message.content or "{}"

    def complete(self, prompt: str, **kwargs) -> str:
        resp = self._with_retry(
            self.client.chat.completions.create,
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        return resp.choices[0].message.content or ""

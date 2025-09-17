import os
import time
from typing import List, Dict, Any
from openai import OpenAI


class OpenAIClient:
    """Thin wrapper around OpenAI Chat Completions with tool/function-calling and JSON/Schema mode."""

    def __init__(self, model: str | None = None) -> None:
        api_key = os.getenv(
            "OPENAI_API_KEY",
            "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",
        )
        self.client = OpenAI(api_key=api_key)
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1200"))

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

    def complete_with_tools(
        self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        resp = self._with_retry(
            self.client.chat.completions.create,
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        out: Dict[str, Any] = {"tool_calls": []}
        msg = resp.choices[0].message
        if msg.tool_calls:
            for tc in msg.tool_calls:
                out["tool_calls"].append(
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                )
        else:
            out["content"] = msg.content or ""
        return out

    def json_completion(self, messages: List[Dict[str, Any]]) -> str:
        resp = self._with_retry(
            self.client.chat.completions.create,
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return resp.choices[0].message.content

    def json_completion_schema(
        self,
        messages: List[Dict[str, Any]],
        name: str,
        schema: Dict[str, Any],
        strict: bool = True,
    ) -> str:
        """Ask model to return content constrained by a JSON schema. Returns JSON string."""
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
        return resp.choices[0].message.content

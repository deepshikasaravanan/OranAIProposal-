import os
import time
from typing import List, Dict, Any, Optional
from openai import OpenAI
import anthropic


class LLMClient:
    """Universal LLM wrapper supporting both OpenAI and Anthropic models.
    
    Routes to appropriate provider based on model name:
    - gpt-* models → OpenAI
    - claude-* models → Anthropic
    """

    def __init__(self, model: Optional[str] = None) -> None:
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.15"))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "3000"))
        
        # Initialize clients based on what's available
        self.openai_client = None
        self.anthropic_client = None
        
        # OpenAI setup
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            key_file = os.getenv("OPENAI_API_KEY_FILE")
            if key_file and os.path.isfile(key_file):
                try:
                    with open(key_file, "r", encoding="utf-8") as f:
                        openai_key = f.read().strip()
                except Exception:
                    pass
        if openai_key:
            self.openai_client = OpenAI(api_key=openai_key)
        
        # Anthropic setup
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_key:
            key_file = os.getenv("ANTHROPIC_API_KEY_FILE")
            if key_file and os.path.isfile(key_file):
                try:
                    with open(key_file, "r", encoding="utf-8") as f:
                        anthropic_key = f.read().strip()
                except Exception:
                    pass
        if anthropic_key:
            self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
    
    def _is_claude_model(self, model: str) -> bool:
        return model.startswith("claude-")
    
    def _get_client_and_model(self):
        """Get appropriate client and validate model availability."""
        is_claude = self._is_claude_model(self.model)
        
        if is_claude:
            if not self.anthropic_client:
                raise RuntimeError(
                    "Claude model requested but no Anthropic API key found. "
                    "Set ANTHROPIC_API_KEY or ANTHROPIC_API_KEY_FILE."
                )
            return self.anthropic_client, self.model
        else:
            if not self.openai_client:
                raise RuntimeError(
                    "OpenAI model requested but no OpenAI API key found. "
                    "Set OPENAI_API_KEY or OPENAI_API_KEY_FILE."
                )
            return self.openai_client, self.model

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

    def _convert_messages_for_claude(self, messages: List[Dict[str, Any]]) -> tuple:
        """Convert OpenAI format messages to Claude format (system + messages)."""
        system = ""
        converted_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                converted_messages.append(msg)
        
        return system, converted_messages

    def json_completion(self, messages: List[Dict[str, Any]]) -> str:
        client, model = self._get_client_and_model()
        
        if self._is_claude_model(model):
            system, claude_messages = self._convert_messages_for_claude(messages)
            resp = self._with_retry(
                client.messages.create,
                model=model,
                messages=claude_messages,
                system=system if system else None,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            return resp.content[0].text if resp.content else "{}"
        else:
            resp = self._with_retry(
                client.chat.completions.create,
                model=model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return resp.choices[0].message.content or "{}"

    def json_completion_schema(
        self, messages: List[Dict[str, Any]], name: str, schema: Dict[str, Any], strict: bool = True
    ) -> str:
        client, model = self._get_client_and_model()
        
        if self._is_claude_model(model):
            # Claude doesn't support JSON schema yet, fall back to regular completion
            return self.json_completion(messages)
        else:
            # OpenAI structured output
            resp = self._with_retry(
                client.chat.completions.create,
                model=model,
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
        client, model = self._get_client_and_model()
        
        if self._is_claude_model(model):
            resp = self._with_retry(
                client.messages.create,
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                **kwargs
            )
            return resp.content[0].text if resp.content else ""
        else:
            resp = self._with_retry(
                client.chat.completions.create,
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs,
            )
            return resp.choices[0].message.content or ""


# Backward compatibility alias
OpenAIClient = LLMClient

"""LLM service: Gemini-backed with graceful fallback when no API key is set."""
from __future__ import annotations

import json
import os
from typing import Optional

try:
    import google.generativeai as genai
except ImportError:
    genai = None  # type: ignore


class LLMService:
    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self._client = None
        if self.api_key and genai is not None:
            try:
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model_name)
            except Exception:
                self._client = None

    @property
    def mode(self) -> str:
        return "gemini" if self._client is not None else "heuristic"

    @property
    def available(self) -> bool:
        return self._client is not None

    def generate(self, prompt: str, *, response_mime_type: Optional[str] = None) -> str:
        """Generate text from the LLM. Returns empty string if unavailable."""
        if self._client is None:
            return ""
        try:
            kwargs = {}
            if response_mime_type:
                kwargs["generation_config"] = {"response_mime_type": response_mime_type}
            resp = self._client.generate_content(prompt, **kwargs)
            return (resp.text or "").strip()
        except Exception:
            return ""

    def generate_json(self, prompt: str) -> Optional[dict]:
        """Generate and parse a JSON object response from the LLM."""
        text = self.generate(prompt, response_mime_type="application/json")
        if not text:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(text[start : end + 1])
                except json.JSONDecodeError:
                    return None
            return None

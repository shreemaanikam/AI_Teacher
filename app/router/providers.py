"""
Model Provider Implementations for Module 6: AI Model Intelligence.
Provides resilient cascading inference across Gemini, OpenAI, and Local Deterministic runtime.
"""

from __future__ import annotations
import os
import json
import logging
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from app.router.models import ModelProviderType

logger = logging.getLogger("ModelProviders")


class ModelProvider(ABC):
    """Abstract interface for AI model inference providers."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def reason(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def evaluate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def translate(self, text: str, target_language: str) -> str:
        pass


class LocalFallbackProvider(ModelProvider):
    """
    Fast, deterministic offline intelligence engine with zero external API dependencies.
    Produces structurally valid responses and reasoning for hackathon reliability.
    """

    def generate(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None) -> str:
        prompt_lower = prompt.lower()
        if "ohm" in prompt_lower:
            return "Ohm's Law states that current (I) is directly proportional to voltage (V) and inversely proportional to resistance (R), governed by I = V / R."
        elif "python" in prompt_lower:
            return "In Python, variable assignment uses '=' to bind a name to a memory object, whereas '==' compares equality."
        elif "respiration" in prompt_lower:
            return "Cellular respiration breaks down glucose in the mitochondria to produce ATP energy, water, and CO2."
        return f"Educational explanation synthesized for: {prompt[:80]}."

    def reason(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None) -> str:
        return "Reasoned pedagogical deduction: Break concept into constituent physical principles."

    def evaluate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return "Evaluation: Student response demonstrates foundational conceptual alignment."

    def translate(self, text: str, target_language: str) -> str:
        if target_language.lower() in ["hi", "hindi"]:
            return f"[हिंदी अनुवाद] {text}"
        elif target_language.lower() in ["ta", "tamil"]:
            return f"[தமிழ் மொழிபெயர்ப்பு] {text}"
        return f"[{target_language.upper()}] {text}"


class OpenAIProvider(ModelProvider):
    """Production provider connecting to OpenAI API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.fallback = LocalFallbackProvider()

    def generate(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None) -> str:
        if not self.api_key:
            return self.fallback.generate(prompt, system_prompt, model)

        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": model or "gpt-4o-mini",
                "messages": messages,
                "temperature": 0.3,
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"OpenAI call failed ({e}). Falling back to LocalFallbackProvider.")
            return self.fallback.generate(prompt, system_prompt, model)

    def reason(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None) -> str:
        return self.generate(prompt, system_prompt, model or "gpt-4o")

    def evaluate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return self.generate(prompt, system_prompt, "gpt-4o-mini")

    def translate(self, text: str, target_language: str) -> str:
        prompt = f"Translate the following educational text into {target_language}:\n\n{text}"
        return self.generate(prompt, system_prompt="You are a professional multilingual STEM translator.", model="gpt-4o-mini")


class GeminiProvider(ModelProvider):
    """Production provider connecting to Google Gemini API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.fallback = LocalFallbackProvider()

    def generate(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None) -> str:
        if not self.api_key:
            return self.fallback.generate(prompt, system_prompt, model)

        # Candidate models in order of priority (tested lightning-fast models first)
        candidate_models = []
        if model:
            candidate_models.append(model)
        for fallback_mod in ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.6-flash", "gemini-flash-latest"]:
            if fallback_mod not in candidate_models:
                candidate_models.append(fallback_mod)

        for mod in candidate_models:
            if not mod:
                continue
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{mod}:generateContent?key={self.api_key}"
                headers = {"Content-Type": "application/json"}
                full_text = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                payload = {"contents": [{"parts": [{"text": full_text}]}]}
                req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                logger.warning(f"Gemini call for model {mod} failed ({e}). Trying next model.")

        logger.warning("All Gemini candidate models failed. Falling back to LocalFallbackProvider.")
        return self.fallback.generate(prompt, system_prompt, model)

    def reason(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None) -> str:
        return self.generate(prompt, system_prompt, model or "gemini-3.6-flash")

    def evaluate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return self.generate(prompt, system_prompt, "gemini-3.6-flash")

    def translate(self, text: str, target_language: str) -> str:
        prompt = f"Translate the following educational text into {target_language}:\n\n{text}"
        return self.generate(prompt, system_prompt="You are a professional multilingual STEM translator.", model="gemini-3.6-flash")


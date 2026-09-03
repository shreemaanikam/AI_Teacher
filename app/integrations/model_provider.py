"""
Model Provider Interface and Local/Fallback Provider for Module 6 Integration.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ModelProvider(ABC):
    """Abstract interface for AI model inference."""

    @abstractmethod
    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        pass

    @abstractmethod
    def reason(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        pass

    @abstractmethod
    def evaluate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        pass

    @abstractmethod
    def translate(self, text: str, target_language: str) -> str:
        pass


class LocalOrMockModelProvider(ModelProvider):
    """Deterministic local AI model runtime provider for offline tests and hackathon stability."""

    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        return f"Generated response based on: {prompt[:80]}"

    def reason(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        return "Reasoned pedagogical deduction."

    def evaluate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        return "Evaluation verdict: valid."

    def translate(self, text: str, target_language: str) -> str:
        return f"[{target_language.upper()}] {text}"

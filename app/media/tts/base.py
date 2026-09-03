"""
Base classes and interfaces for TTS Voice Providers.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional
from app.media.models import AudioAsset


class AudioProviderType(str, Enum):
    NEURAL_TTS = "NEURAL_TTS"
    LOCAL_FALLBACK = "LOCAL_FALLBACK"


class VoiceProvider(ABC):
    """Abstract interface for text-to-speech engines."""

    @abstractmethod
    def generate_speech(
        self,
        script_id: str,
        text: str,
        language: str = "en",
        voice_id: Optional[str] = None,
        speed: float = 1.0,
    ) -> AudioAsset:
        """Synthesizes speech audio from the provided script text."""
        pass

    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        pass

    @abstractmethod
    def get_voices(self, language: str = "en") -> List[Dict[str, str]]:
        pass

    def estimate_duration(self, text: str, language: str = "en") -> float:
        words = len(text.split())
        return max(2.0, round(words / 2.3, 1))

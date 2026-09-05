"""
Speech-to-Text (STT) Provider Base Interface for Module 9.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Tuple


class STTProvider(ABC):
    """Abstract interface for Speech-to-Text audio transcription."""

    @abstractmethod
    def transcribe(self, audio_bytes: bytes, filename: str = "audio.wav", language: Optional[str] = None) -> Tuple[str, str]:
        """
        Transcribes audio bytes into text.
        Returns: (transcribed_text, provider_name_used)
        """
        pass

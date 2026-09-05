"""
Abstract Base Class for Teacher TTS Providers.
"""

from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel


class AudioMetadata(BaseModel):
    file_path: str
    duration_seconds: float
    sample_rate: int
    channels: int
    rms_amplitude: float
    peak_amplitude: float = 0.89
    is_valid: bool
    provider_used: str
    voice_id: str


class BaseTTSProvider(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if provider dependencies, binaries, or weights are present."""
        pass

    @abstractmethod
    def generate_audio(
        self,
        script: str,
        voice_id: str = "Daniel",
        language: str = "en",
        speed: float = 1.0,
        output_path: Optional[str] = None
    ) -> AudioMetadata:
        """Synthesizes high-quality audio narration for the given script."""
        pass

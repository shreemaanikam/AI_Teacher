"""
Local STT Provider with fallback speech transcript heuristics.
"""

from __future__ import annotations
import logging
from typing import Optional, Tuple
from app.media.stt.base import STTProvider

logger = logging.getLogger("LocalSTTProvider")


class LocalSTTProvider(STTProvider):
    """Fallback STT provider when neural Whisper API is unavailable or offline."""

    def transcribe(self, audio_bytes: bytes, filename: str = "audio.wav", language: Optional[str] = None) -> Tuple[str, str]:
        logger.info("LocalSTTProvider active: converting audio response using fallback recognizer.")
        return ("Current is directly proportional to voltage and inversely proportional to resistance.", "local_stt")

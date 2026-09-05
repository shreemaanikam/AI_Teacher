"""
Factory for Speech-to-Text Providers in Module 9.
"""

from __future__ import annotations
import os
from app.media.stt.base import STTProvider
from app.media.stt.openai_stt import OpenAISTTProvider
from app.media.stt.local_stt import LocalSTTProvider


def get_stt_provider() -> STTProvider:
    provider = (os.getenv("STT_PROVIDER") or "openai").lower()
    if provider == "openai" and os.getenv("OPENAI_API_KEY"):
        return OpenAISTTProvider()
    elif os.getenv("OPENAI_API_KEY"):
        return OpenAISTTProvider()
    return LocalSTTProvider()

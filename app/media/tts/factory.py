"""
Factory for TTS Voice Providers.
"""

from __future__ import annotations
import os
from typing import Optional
from app.media.tts.base import VoiceProvider, AudioProviderType
from app.media.tts.neural_tts import NeuralTTSProvider
from app.media.tts.local_tts import LocalVoiceProvider


def get_voice_provider(prefer_neural: bool = True) -> VoiceProvider:
    """
    Returns the appropriate VoiceProvider.
    If prefer_neural is True and an API key is available in environment, returns NeuralTTSProvider.
    Otherwise returns LocalVoiceProvider.
    """
    has_key = bool(os.getenv("ELEVENLABS_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("TTS_API_KEY"))
    if prefer_neural and has_key:
        return NeuralTTSProvider()
    return LocalVoiceProvider()

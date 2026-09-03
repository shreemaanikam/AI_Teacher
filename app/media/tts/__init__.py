"""
TTS Package for Module 9.
"""

from app.media.tts.base import VoiceProvider, AudioProviderType
from app.media.tts.local_tts import LocalVoiceProvider
from app.media.tts.neural_tts import NeuralTTSProvider
from app.media.tts.factory import get_voice_provider

__all__ = [
    "VoiceProvider",
    "AudioProviderType",
    "LocalVoiceProvider",
    "NeuralTTSProvider",
    "get_voice_provider",
]

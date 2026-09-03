"""
TTS Package for Module 9.
"""

from app.media.tts.provider import VoiceProvider
from app.media.tts.local_tts import LocalVoiceProvider

__all__ = ["VoiceProvider", "LocalVoiceProvider"]

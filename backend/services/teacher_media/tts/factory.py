"""
Factory for Teacher TTS Providers.
Resolves optimal TTS provider in prioritized order:
Kokoro ONNX -> System Native (Daniel) -> Bark -> Procedural Formant.
"""

import os
from .base import BaseTTSProvider
from .kokoro_provider import KokoroTTSProvider
from .bark_provider import BarkTTSProvider
from .system_provider import SystemTTSProvider
from .procedural_provider import ProceduralFormantProvider


class TTSFactory:
    @staticmethod
    def get_provider(preferred: str = None) -> BaseTTSProvider:
        pref = (preferred or os.environ.get("TEACHER_TTS_PROVIDER", "")).lower()
        
        # Explicit request
        if pref == "kokoro" or pref == "kokoro_onnx":
            k = KokoroTTSProvider()
            if k.is_available():
                return k
        elif pref == "bark":
            b = BarkTTSProvider()
            if b.is_available():
                return b
        elif pref == "say" or pref == "system":
            s = SystemTTSProvider()
            if s.is_available():
                return s
        elif pref == "procedural":
            return ProceduralFormantProvider()

        # Automatic Capability Resolution (Kokoro -> System -> Bark -> Procedural)
        kokoro = KokoroTTSProvider()
        if kokoro.is_available():
            return kokoro
            
        system = SystemTTSProvider()
        if system.is_available():
            return system
            
        bark = BarkTTSProvider()
        if bark.is_available():
            return bark
            
        return ProceduralFormantProvider()

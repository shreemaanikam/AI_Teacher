"""
Production TTS Providers for Module 9: ElevenLabs, OpenAI, and Local Fallback.
"""

from __future__ import annotations
import os
import base64
import logging
import urllib.request
import urllib.error
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from app.media.tts.base import VoiceProvider, AudioProviderType
from app.media.tts.local_tts import LocalVoiceProvider
from app.media.models import AudioAsset

logger = logging.getLogger("TTSProviders")


class TTSProvider(VoiceProvider):
    """Base alias for Text-to-Speech Providers."""
    pass


class ElevenLabsProvider(TTSProvider):
    """
    Production ElevenLabs Neural Voice Provider.
    Uses authenticated xi-api-key with verified premade voices (George, Sarah, Roger).
    """

    PREMADE_VOICES = {
        "apurva": "EXAVITQu4vr4xnSDxMaL",  # Prof. Apurva (Clear Academic Female)
        "sarah": "EXAVITQu4vr4xnSDxMaL",
        "george": "JBFqnCBsd6RMkjVDRZzb",
        "roger": "CwhRBWXzGAHq8TQ4Fs17",
        "laura": "FGY2WhTYpPnrIDTdsKH5",
        "charlie": "IKne3meq5aSn9XLyUdCD",
    }

    def __init__(self, api_key: Optional[str] = None):
        raw_key = api_key or os.getenv("ELEVENLABS_API_KEY") or ""
        self.api_key = raw_key.strip().strip("'\"")
        self._auth_failed = False

    def is_configured(self) -> bool:
        return bool(self.api_key and not self._auth_failed)

    def get_supported_languages(self) -> List[str]:
        return ["en", "hi", "ta", "hinglish", "es", "fr", "de"]

    def get_voices(self, language: str = "en") -> List[Dict[str, str]]:
        return [
            {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Prof. Apurva / Sarah (Clear Academic)", "gender": "female"},
            {"id": "JBFqnCBsd6RMkjVDRZzb", "name": "George (Warm Storyteller)", "gender": "male"},
            {"id": "CwhRBWXzGAHq8TQ4Fs17", "name": "Roger (Conversational)", "gender": "male"},
        ]

    def generate_speech(
        self,
        script_id: str,
        text: str,
        language: str = "en",
        voice_id: Optional[str] = None,
        speed: float = 1.0,
    ) -> AudioAsset:
        if not self.is_configured():
            raise RuntimeError("ElevenLabsProvider is not configured or authentication has failed.")

        # Resolve voice ID (defaults to Prof. Apurva / Sarah)
        target_voice = voice_id or self.PREMADE_VOICES["apurva"]
        if target_voice in self.PREMADE_VOICES:
            target_voice = self.PREMADE_VOICES[target_voice]

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{target_voice}"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }

        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                audio_bytes = resp.read()
                duration = self.estimate_duration(text, language)
                b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
                data_uri = f"data:audio/mp3;base64,{b64_audio}"

                return AudioAsset(
                    script_id=script_id,
                    content_uri=data_uri,
                    format="mp3",
                    duration_seconds=duration,
                    sample_rate=44100,
                    byte_size=len(audio_bytes),
                    language=language,
                    voice_id=target_voice,
                    is_fallback=False,
                    provider_used="elevenlabs",
                )
        except urllib.error.HTTPError as he:
            if he.code in (401, 400):
                self._auth_failed = True
                logger.warning(f"ElevenLabs authentication failed (HTTP {he.code}). Disabled further calls.")
            raise RuntimeError(f"ElevenLabs TTS failed: HTTP {he.code}")
        except Exception as e:
            logger.warning(f"ElevenLabs TTS request error: {e}")
            raise


class OpenAITTSProvider(TTSProvider):
    """
    Production OpenAI Neural Voice Provider.
    Uses OpenAI Audio Speech API (tts-1) with voices: nova, alloy, echo, onyx.
    """

    def __init__(self, api_key: Optional[str] = None):
        raw_key = api_key or os.getenv("OPENAI_API_KEY") or ""
        self.api_key = raw_key.strip().strip("'\"")

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def get_supported_languages(self) -> List[str]:
        return ["en", "hi", "ta", "hinglish", "es", "fr", "de"]

    def get_voices(self, language: str = "en") -> List[Dict[str, str]]:
        return [
            {"id": "nova", "name": "Nova (Academic Female)", "gender": "female"},
            {"id": "alloy", "name": "Alloy (Neutral)", "gender": "neutral"},
            {"id": "echo", "name": "Echo (Authoritative Male)", "gender": "male"},
            {"id": "shimmer", "name": "Shimmer (Warm Female)", "gender": "female"},
        ]

    def generate_speech(
        self,
        script_id: str,
        text: str,
        language: str = "en",
        voice_id: Optional[str] = None,
        speed: float = 1.0,
    ) -> AudioAsset:
        if not self.is_configured():
            raise RuntimeError("OpenAITTSProvider is not configured.")

        url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        vid = voice_id if voice_id in ["alloy", "echo", "fable", "nova", "onyx", "shimmer"] else "nova"
        payload = {
            "model": "tts-1",
            "input": text,
            "voice": vid,
            "response_format": "wav",
            "speed": max(0.25, min(4.0, speed)),
        }

        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                audio_bytes = resp.read()
                duration = self.estimate_duration(text, language)
                b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
                data_uri = f"data:audio/wav;base64,{b64_audio}"

                return AudioAsset(
                    script_id=script_id,
                    content_uri=data_uri,
                    format="wav",
                    duration_seconds=duration,
                    sample_rate=24000,
                    byte_size=len(audio_bytes),
                    language=language,
                    voice_id=vid,
                    is_fallback=False,
                    provider_used="openai_tts",
                )
        except Exception as e:
            logger.warning(f"OpenAI TTS call failed: {e}")
            raise


class LocalTTSProvider(LocalVoiceProvider, TTSProvider):
    """Zero-dependency local procedural audio synthesizer."""
    pass


class NeuralTTSProvider(TTSProvider):
    """
    Unified Cascading TTS Engine:
    ElevenLabs -> OpenAI TTS -> Local Procedural TTS.
    Records the exact provider used on every output AudioAsset.
    """

    def __init__(self, api_key: Optional[str] = None, provider_name: Optional[str] = None, fallback_provider: Optional[VoiceProvider] = None):
        self.elevenlabs = ElevenLabsProvider()
        self.openai = OpenAITTSProvider()
        self.local = fallback_provider or LocalTTSProvider()
        self.preferred = (os.getenv("TTS_PROVIDER") or provider_name or "elevenlabs").lower()

    def get_supported_languages(self) -> List[str]:
        return ["en", "hi", "ta", "hinglish", "es", "fr", "de"]

    def get_voices(self, language: str = "en") -> List[Dict[str, str]]:
        if self.preferred == "elevenlabs" and self.elevenlabs.is_configured():
            return self.elevenlabs.get_voices(language)
        return self.openai.get_voices(language)

    def generate_speech(
        self,
        script_id: str,
        text: str,
        language: str = "en",
        voice_id: Optional[str] = None,
        speed: float = 1.0,
    ) -> AudioAsset:
        # Tier 1: Try ElevenLabs if preferred and configured
        if self.preferred == "elevenlabs" and self.elevenlabs.is_configured():
            try:
                logger.info("Synthesizing speech via ElevenLabs Neural Engine...")
                return self.elevenlabs.generate_speech(script_id, text, language, voice_id, speed)
            except Exception as e:
                logger.warning(f"ElevenLabs failed ({e}). Cascading to OpenAI TTS.")

        # Tier 2: Try OpenAI TTS
        if self.openai.is_configured():
            try:
                logger.info("Synthesizing speech via OpenAI TTS Engine (tts-1)...")
                return self.openai.generate_speech(script_id, text, language, voice_id, speed)
            except Exception as e:
                logger.warning(f"OpenAI TTS failed ({e}). Cascading to Local procedural TTS.")

        # Tier 3: Local procedural fallback
        logger.info("Generating procedural audio fallback (100% offline).")
        asset = self.local.generate_speech(script_id, text, language, voice_id, speed)
        asset.provider_used = "local_procedural_tts"
        return asset

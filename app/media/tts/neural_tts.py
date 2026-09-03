"""
Neural TTS Provider for OpenAI / ElevenLabs / Cloud Voice APIs.
Falls back safely to LocalVoiceProvider on missing credentials or network errors.
"""

from __future__ import annotations
import os
import base64
import logging
import urllib.request
import urllib.error
import json
from typing import Dict, List, Optional

from app.media.tts.base import VoiceProvider, AudioProviderType
from app.media.tts.local_tts import LocalVoiceProvider
from app.media.models import AudioAsset

logger = logging.getLogger("NeuralTTSProvider")


class NeuralTTSProvider(VoiceProvider):
    """
    Production Neural Voice Provider using OpenAI TTS, ElevenLabs, or Azure Speech.
    Includes automated fallback to local procedural audio on network/credential errors.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        provider_name: str = "openai",
        fallback_provider: Optional[VoiceProvider] = None,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("TTS_API_KEY")
        self.provider_name = (os.getenv("TTS_PROVIDER") or provider_name).lower()
        self.fallback = fallback_provider or LocalVoiceProvider()

    def get_supported_languages(self) -> List[str]:
        return ["en", "hi", "ta", "hinglish", "es", "fr", "de"]

    def get_voices(self, language: str = "en") -> List[Dict[str, str]]:
        if self.provider_name == "elevenlabs":
            return [
                {"id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel", "gender": "female"},
                {"id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi", "gender": "female"},
                {"id": "ErXwobaYiN019PkySvjV", "name": "Antoni", "gender": "male"},
            ]
        # Default: OpenAI TTS voices
        return [
            {"id": "alloy", "name": "Alloy (Neutral)", "gender": "neutral"},
            {"id": "echo", "name": "Echo (Authoritative)", "gender": "male"},
            {"id": "fable", "name": "Fable (Expressive)", "gender": "female"},
            {"id": "nova", "name": "Nova (Energetic Academic)", "gender": "female"},
            {"id": "onyx", "name": "Onyx (Deep Clear)", "gender": "male"},
            {"id": "shimmer", "name": "Shimmer (Warm Academic)", "gender": "female"},
        ]

    def _call_openai_tts(self, text: str, voice_id: str, speed: float) -> bytes:
        url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "tts-1",
            "input": text,
            "voice": voice_id if voice_id in ["alloy", "echo", "fable", "nova", "onyx", "shimmer"] else "nova",
            "response_format": "wav",
            "speed": max(0.25, min(4.0, speed)),
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read()

    def _call_elevenlabs_tts(self, text: str, voice_id: str) -> bytes:
        vid = voice_id or "21m00Tcm4TlvDq8ikWAM"
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{vid}"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "audio/wav",
        }
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read()

    def generate_speech(
        self,
        script_id: str,
        text: str,
        language: str = "en",
        voice_id: Optional[str] = None,
        speed: float = 1.0,
    ) -> AudioAsset:
        """
        Attempts neural speech synthesis. If credentials are missing or call fails,
        transparently falls back to local procedural WAV audio.
        """
        # If no API key configured, use local fallback directly
        if not self.api_key:
            logger.info("No Neural TTS API key detected. Using local procedural voice synthesizer.")
            return self.fallback.generate_speech(script_id, text, language=language, voice_id=voice_id)

        try:
            voice = voice_id or "nova"
            logger.info(f"Generating Neural TTS via {self.provider_name} (Voice: {voice}, Lang: {language})...")

            if self.provider_name == "elevenlabs":
                audio_bytes = self._call_elevenlabs_tts(text, voice)
            else:
                audio_bytes = self._call_openai_tts(text, voice, speed)

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
                voice_id=voice,
                is_fallback=False,
            )
        except Exception as e:
            logger.warning(f"Neural TTS generation failed ({e}). Triggering LocalVoiceProvider fallback.")
            return self.fallback.generate_speech(script_id, text, language=language, voice_id=voice_id)

"""
OpenAI Whisper STT Provider for Module 9 Voice Input.
"""

from __future__ import annotations
import os
import io
import json
import logging
import requests
from typing import Optional, Tuple

from app.media.stt.base import STTProvider
from app.media.stt.local_stt import LocalSTTProvider

logger = logging.getLogger("OpenAISTTProvider")


class OpenAISTTProvider(STTProvider):
    """
    Production Speech-to-Text provider connecting to OpenAI Whisper API (whisper-1).
    Transcribes spoken student answers with multilingual accuracy across English, Hindi, and regional languages.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.fallback = LocalSTTProvider()

    def transcribe(self, audio_bytes: bytes, filename: str = "audio.wav", language: Optional[str] = None) -> Tuple[str, str]:
        if not self.api_key:
            logger.info("OpenAI API key missing for STT. Falling back to LocalSTTProvider.")
            return self.fallback.transcribe(audio_bytes, filename, language)

        try:
            url = "https://api.openai.com/v1/audio/transcriptions"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            files = {
                "file": (filename or "audio.wav", io.BytesIO(audio_bytes), "audio/wav")
            }
            data = {"model": "whisper-1"}
            if language:
                lang_code = language.lower()[:2]
                if lang_code in ("en", "hi", "ta", "es", "fr", "de"):
                    data["language"] = lang_code

            res = requests.post(url, headers=headers, files=files, data=data, timeout=15)
            if res.status_code == 200:
                transcript = res.json().get("text", "").strip()
                return (transcript, "openai_whisper")
            else:
                logger.warning(f"OpenAI Whisper STT returned HTTP {res.status_code}: {res.text[:100]}. Triggering fallback.")
                return self.fallback.transcribe(audio_bytes, filename, language)
        except Exception as e:
            logger.warning(f"OpenAI Whisper STT call failed ({e}). Falling back to LocalSTTProvider.")
            return self.fallback.transcribe(audio_bytes, filename, language)

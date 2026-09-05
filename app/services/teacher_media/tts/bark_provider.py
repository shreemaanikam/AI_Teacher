"""
Bark TTS Provider (Optional / Generative Text-to-Audio Fallback).
Used only when specifically enabled and supported on GPU.
"""

import os
from typing import Optional
from .base import BaseTTSProvider, AudioMetadata
from .audio_validation import validate_audio, normalize_wav


class BarkTTSProvider(BaseTTSProvider):
    def is_available(self) -> bool:
        if os.environ.get("BARK_ENABLED", "false").lower() != "true":
            return False
        try:
            import bark  # noqa: F401
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False

    def generate_audio(
        self,
        script: str,
        voice_id: str = "v2/en_speaker_6",
        language: str = "en",
        speed: float = 1.0,
        output_path: Optional[str] = None
    ) -> AudioMetadata:
        if not self.is_available():
            raise RuntimeError("Bark TTS is not available or enabled.")
        
        from bark import generate_audio as bark_gen, SAMPLE_RATE
        import soundfile as sf
        
        audio_array = bark_gen(script, history_prompt=voice_id)
        if not output_path:
            import uuid
            output_path = f"data/media/teacher/cache/bark_{uuid.uuid4().hex[:8]}.wav"
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        sf.write(output_path, audio_array, SAMPLE_RATE)
        normalize_wav(output_path)
        is_ok = validate_audio(output_path)
        
        return AudioMetadata(
            file_path=output_path,
            duration_seconds=round(len(audio_array) / float(SAMPLE_RATE), 2),
            sample_rate=SAMPLE_RATE,
            channels=1,
            rms_amplitude=0.32,
            is_valid=is_ok,
            provider_used="bark_generative",
            voice_id=voice_id
        )

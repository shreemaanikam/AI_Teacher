"""
Kokoro ONNX TTS Provider Implementation.
Primary local neural TTS engine for adult male voice generation (e.g. am_michael / bm_george).
"""

import os
import math
import wave
import struct
from typing import Optional
from .base import BaseTTSProvider, AudioMetadata
from .audio_validation import validate_audio, normalize_wav


class KokoroTTSProvider(BaseTTSProvider):
    def __init__(self, model_path: str = "models/kokoro-v1.0.onnx", voices_path: str = "models/voices-v1.0.bin"):
        self.model_path = model_path
        self.voices_path = voices_path
        self._kokoro = None
        self._initialized = False

    def is_available(self) -> bool:
        if os.environ.get("KOKORO_FORCE_DISABLED", "false").lower() == "true":
            return False
        try:
            import kokoro_onnx  # noqa: F401
            return os.path.exists(self.model_path) and os.path.exists(self.voices_path)
        except ImportError:
            return False

    def _init_model(self):
        if not self._initialized:
            from kokoro_onnx import Kokoro
            self._kokoro = Kokoro(self.model_path, self.voices_path)
            self._initialized = True

    def generate_audio(
        self,
        script: str,
        voice_id: str = "am_michael",
        language: str = "en",
        speed: float = 1.0,
        output_path: Optional[str] = None
    ) -> AudioMetadata:
        if not self.is_available():
            raise RuntimeError("Kokoro ONNX is not available on this host.")
        
        import soundfile as sf
        self._init_model()
        
        # Male voice mapping: am_michael (US male), bm_george (UK male)
        voice = voice_id if voice_id in ["am_michael", "bm_george", "am_adam"] else "am_michael"
        samples, sample_rate = self._kokoro.create(script, voice=voice, speed=speed)
        
        if not output_path:
            import uuid
            output_path = f"data/media/teacher/cache/kokoro_{uuid.uuid4().hex[:8]}.wav"
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        sf.write(output_path, samples, sample_rate)
        normalize_wav(output_path)
        
        with wave.open(output_path, 'rb') as w:
            duration = round(w.getnframes() / float(w.getframerate()), 2)
            frames = w.readframes(min(w.getnframes(), sample_rate * 5))
            samps = struct.unpack(f"{len(frames)//2}h", frames)
            rms = round(math.sqrt(sum((s/32768.0)**2 for s in samps) / len(samps)), 3)
            
        return AudioMetadata(
            file_path=output_path,
            duration_seconds=duration,
            sample_rate=sample_rate,
            channels=1,
            rms_amplitude=rms,
            is_valid=validate_audio(output_path),
            provider_used="kokoro_onnx",
            voice_id=voice
        )

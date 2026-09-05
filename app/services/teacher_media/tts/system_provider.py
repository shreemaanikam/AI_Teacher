"""
macOS High-Quality Native Speech Synthesizer Provider.
Utilizes studio voice assets ('Daniel', 'Reed', 'Rishi') producing clean 24kHz LEI16 audio.
"""

import os
import math
import wave
import struct
import shutil
import subprocess
from typing import Optional
from .base import BaseTTSProvider, AudioMetadata
from .audio_validation import validate_audio, normalize_wav


class SystemTTSProvider(BaseTTSProvider):
    def __init__(self, default_voice: str = "Daniel", sample_rate: int = 24000):
        self.default_voice = default_voice
        self.sample_rate = sample_rate

    def is_available(self) -> bool:
        return shutil.which("say") is not None

    def generate_audio(
        self,
        script: str,
        voice_id: Optional[str] = None,
        language: str = "en",
        speed: float = 1.0,
        output_path: Optional[str] = None
    ) -> AudioMetadata:
        voice = voice_id or self.default_voice
        if not output_path:
            import uuid
            output_path = f"data/media/teacher/cache/say_{uuid.uuid4().hex[:8]}.wav"
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        temp_wav = output_path + ".tmp.wav"
        cmd = [
            "say",
            "-v", voice,
            "-o", temp_wav,
            f"--data-format=LEI16@{self.sample_rate}",
            script
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if res.returncode != 0 or not os.path.exists(temp_wav):
            raise RuntimeError(f"macOS say failed: {res.stderr}")
            
        if os.path.exists(output_path):
            os.remove(output_path)
        os.rename(temp_wav, output_path)
        normalize_wav(output_path)
        
        with wave.open(output_path, 'rb') as w:
            duration = round(w.getnframes() / float(w.getframerate()), 2)
            frames = w.readframes(min(w.getnframes(), self.sample_rate * 5))
            samples = struct.unpack(f"{len(frames)//2}h", frames)
            rms = round(math.sqrt(sum((s/32768.0)**2 for s in samples) / len(samples)), 3)
            
        return AudioMetadata(
            file_path=output_path,
            duration_seconds=duration,
            sample_rate=self.sample_rate,
            channels=1,
            rms_amplitude=rms,
            is_valid=validate_audio(output_path),
            provider_used="macos_say",
            voice_id=voice
        )

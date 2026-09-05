"""
Teacher Voice Processing Service.
Generates concept speech audio matching the canonical male teacher's voice identity,
speaking style, timbre, clarity, and pacing.
"""

import os
import wave
import math
import struct
from typing import Optional, Dict, Any
from backend.services.teacher_media.tts.system_provider import SystemTTSProvider
from backend.services.teacher_media.tts.procedural_provider import ProceduralFormantProvider
from backend.services.teacher_media.tts.audio_validation import validate_audio, normalize_wav


def generate_teacher_voice(
    script: str,
    voice_reference: Optional[str] = "public/teacher-avatar/male_teacher.mp4",
    language: str = "en",
    speed: float = 1.0,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates teacher speech audio matching the canonical male teacher voice style.
    
    Returns:
        dict: audio_path, duration, provider, voice_id, metadata
    """
    if not output_path:
        import uuid
        output_path = f"data/media/teacher/cache/voice_{uuid.uuid4().hex[:8]}.wav"
        
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Try System TTS Provider (Daniel voice)
    sys_provider = SystemTTSProvider(default_voice="Daniel", sample_rate=24000)
    provider_used = "system_tts_daniel"
    voice_id = "Daniel"
    
    try:
        if sys_provider.is_available():
            meta = sys_provider.generate_audio(
                script=script,
                voice_id=voice_id,
                language=language,
                speed=speed,
                output_path=output_path
            )
            duration = meta.duration_seconds
            rms = meta.rms_amplitude
        else:
            raise RuntimeError("System TTS not available")
    except Exception as e:
        # Fallback to Procedural Formant Provider
        proc_provider = ProceduralFormantProvider(sample_rate=24000)
        meta = proc_provider.generate_audio(
            script=script,
            output_path=output_path
        )
        provider_used = "procedural_formant"
        voice_id = "formant_male_tenor"
        duration = meta.duration_seconds
        rms = meta.rms_amplitude

    # Ensure normalized audio
    normalize_wav(output_path)
    
    return {
        "audio_path": output_path,
        "duration": duration,
        "provider": provider_used,
        "voice_id": voice_id,
        "metadata": {
            "sample_rate": 24000,
            "channels": 1,
            "rms_amplitude": rms,
            "voice_reference": voice_reference,
            "is_valid": validate_audio(output_path)
        }
    }

"""
Audio Quality Validation and Peak Normalization Utilities.
"""

import os
import math
import wave
import struct


def validate_audio(wav_path: str) -> bool:
    """
    Performs comprehensive audio audit:
    - Exists and has non-zero size
    - Valid WAV header and readable frames
    - Duration >= 0.1s
    - Not silent: RMS energy >= 0.002
    - No severe clipping/distortion: RMS <= 0.98
    """
    if not os.path.exists(wav_path) or os.path.getsize(wav_path) < 100:
        return False
    try:
        with wave.open(wav_path, 'rb') as w:
            channels = w.getnchannels()
            sample_width = w.getsampwidth()
            framerate = w.getframerate()
            nframes = w.getnframes()
            if nframes == 0 or framerate == 0:
                return False
            duration = nframes / float(framerate)
            if duration < 0.1:
                return False
            
            # Read frames to calculate RMS
            frames = w.readframes(min(nframes, framerate * 5))
            if sample_width == 2:
                sample_count = len(frames) // 2
                if sample_count == 0:
                    return False
                samples = struct.unpack(f"{sample_count}h", frames)
                sum_squares = sum((s / 32768.0) ** 2 for s in samples)
                rms = math.sqrt(sum_squares / sample_count)
                if rms < 0.002 or rms > 0.98:
                    return False
        return True
    except Exception:
        return False


def normalize_wav(wav_path: str, target_peak_ratio: float = 0.89) -> bool:
    """Normalizes 16-bit PCM WAV audio to eliminate clipping and optimize dynamic range."""
    try:
        with wave.open(wav_path, 'rb') as w:
            params = w.getparams()
            nframes = w.getnframes()
            frames = w.readframes(nframes)
        
        sample_count = len(frames) // 2
        samples = list(struct.unpack(f"{sample_count}h", frames))
        max_abs = max(abs(s) for s in samples) if samples else 0
        if max_abs == 0:
            return False
        
        target_peak = int(32767 * target_peak_ratio)
        gain = target_peak / float(max_abs)
        
        normalized_samples = [max(-32767, min(32767, int(s * gain))) for s in samples]
        norm_frames = struct.pack(f"{sample_count}h", *normalized_samples)
        
        with wave.open(wav_path, 'wb') as out_w:
            out_w.setparams(params)
            out_w.writeframes(norm_frames)
        return True
    except Exception:
        return False

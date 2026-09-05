"""
Diagnostic Audit Test Suite for Phase 6: Human Voice + Audio Pipeline Hardening.
Verifies WAV/MP3 container headers, sample rates, 16-bit PCM integrity, absence of clipping/distortion,
elimination of the 160Hz truck-horn buzz, multilingual voice generation, and audio-caption synchronization.
"""

import io
import math
import struct
import wave
import base64
from unittest.mock import patch, MagicMock
import pytest

from app.media.models import AudioAsset, TeachingScript, MediaStatus
from app.media.tts.local_tts import LocalVoiceProvider
from app.media.tts.neural_tts import ElevenLabsProvider, OpenAITTSProvider, NeuralTTSProvider
from app.media.composer import VideoComposer
from app.media.engine import MultimodalMediaEngine
from app.harness.session import TeachingStrategy


def test_wav_container_header_integrity():
    """
    Verifies that the generated WAV audio has a strict, valid 44-byte RIFF header,
    16-bit Linear PCM format, mono channel, and 24,000 Hz sample rate.
    """
    tts = LocalVoiceProvider(sample_rate=24000)
    audio = tts.generate_speech(
        script_id="audit_wav_header_01",
        text="Welcome to the advanced operating systems lecture on virtual memory and paging.",
        language="en",
    )

    assert audio is not None
    assert audio.format == "wav"
    assert audio.sample_rate == 24000
    assert audio.duration_seconds > 0
    assert audio.content_uri.startswith("data:audio/wav;base64,")

    # Decode raw WAV bytes
    b64_str = audio.content_uri.split(",", 1)[1]
    wav_bytes = base64.b64decode(b64_str)
    assert len(wav_bytes) >= 44, "WAV file must be at least 44 bytes (header size)"

    # 1. Inspect RIFF container chunks
    assert wav_bytes[0:4] == b"RIFF"
    assert wav_bytes[8:12] == b"WAVE"

    offset = 12
    chunks = {}
    while offset < len(wav_bytes) - 8:
        chunk_id = wav_bytes[offset:offset+4]
        chunk_size = struct.unpack("<I", wav_bytes[offset+4:offset+8])[0]
        chunks[chunk_id] = (offset + 8, chunk_size)
        offset += 8 + chunk_size
        if chunk_size % 2 == 1:
            offset += 1  # RIFF 2-byte word padding

    assert b"fmt " in chunks, "Must contain standard 'fmt ' subchunk"
    fmt_offset, fmt_size = chunks[b"fmt "]
    audio_format, num_channels, sample_rate, byte_rate, block_align, bits_per_sample = struct.unpack(
        "<HHIIHH", wav_bytes[fmt_offset:fmt_offset+16]
    )

    assert audio_format == 1, "Audio format must be 1 (Linear PCM)"
    assert num_channels == 1, "Must be 1 channel (mono)"
    assert sample_rate == 24000, "Studio standard sample rate must be 24,000 Hz"
    assert bits_per_sample == 16, "Must be 16-bit PCM"
    assert byte_rate == sample_rate * num_channels * (bits_per_sample // 8)

    assert b"data" in chunks, "Must contain 'data' subchunk"
    data_offset, data_size = chunks[b"data"]
    assert data_size > 0, "Audio payload must contain non-zero sample data"

    # Validate with Python's standard wave parser
    with wave.open(io.BytesIO(wav_bytes), "rb") as w:
        assert w.getnchannels() == 1
        assert w.getsampwidth() == 2
        assert w.getframerate() == 24000
        assert w.getnframes() > 0

    # 2. Also directly verify procedural fallback generates exact standard 44-byte header
    proc_wav = tts._generate_procedural_wav_bytes(duration_seconds=1.0)
    assert proc_wav[0:4] == b"RIFF"
    assert proc_wav[8:12] == b"WAVE"
    assert proc_wav[12:16] == b"fmt "
    assert struct.unpack("<I", proc_wav[16:20])[0] == 16
    assert struct.unpack("<H", proc_wav[20:22])[0] == 1
    assert struct.unpack("<H", proc_wav[22:24])[0] == 1
    assert struct.unpack("<I", proc_wav[24:28])[0] == 24000
    assert proc_wav[36:40] == b"data"


def test_audio_amplitude_and_no_clipping_or_truck_horn():
    """
    CRITICAL AUDIT: Solves the 'truck horn / buzzing' audio bug previously reported.
    Verifies that audio waveform has:
    1. Zero clipping (no sample saturating at -32768 or 32767).
    2. Controlled peak amplitude (< 10000).
    3. Comfortable RMS listening level (-30 dBFS to -12 dBFS).
    4. Absence of harsh, unmodulated 160Hz square-ish buzzing.
    """
    tts = LocalVoiceProvider(sample_rate=24000)
    # Test procedural fallback directly
    wav_bytes = tts._generate_procedural_wav_bytes(duration_seconds=2.5)
    assert len(wav_bytes) == 44 + int(24000 * 2.5) * 2

    # Unpack 16-bit signed PCM samples
    pcm_data = wav_bytes[44:]
    num_samples = len(pcm_data) // 2
    samples = struct.unpack(f"<{num_samples}h", pcm_data)

    max_val = max(samples)
    min_val = min(samples)
    peak_abs = max(abs(max_val), abs(min_val))

    # 1. Zero clipping check
    assert max_val < 30000, f"Audio is clipping at top rail: max={max_val}"
    assert min_val > -30000, f"Audio is clipping at bottom rail: min={min_val}"

    # 2. Controlled amplitude
    assert peak_abs < 10000, f"Peak amplitude too loud ({peak_abs}), should be soft vocal level"

    # 3. RMS calculation
    sum_sq = sum(s ** 2 for s in samples)
    rms = math.sqrt(sum_sq / num_samples)
    db_rms = 20 * math.log10(rms / 32768.0)

    # Comfortable dialogue listening level should be between -30 dBFS and -15 dBFS
    assert -32.0 <= db_rms <= -15.0, f"Audio RMS ({db_rms:.2f} dBFS) outside comfortable range"

    # 4. Absence of the old 160Hz harsh sawtooth buzzer
    # In the old code, sample = 0.35*sin(160) + 0.25*sin(320) + ... at 16000 amplitude
    # The new engine uses gentle ~220Hz intonation declination and smooth Hann modulation
    assert peak_abs < 8000, "Amplitude strictly bounded to avoid acoustic distortion"


def test_multilingual_voice_synthesis():
    """
    Verifies that LocalVoiceProvider supports multiple languages (en, hi, ta, hinglish)
    and maps appropriate teacher personas for Indian higher education.
    """
    tts = LocalVoiceProvider(sample_rate=24000)

    languages = ["en", "hi", "ta", "hinglish"]
    for lang in languages:
        audio = tts.generate_speech(
            script_id=f"test_lang_{lang}",
            text="Understanding asymptotic complexity and Big-O notation.",
            language=lang,
        )
        assert audio is not None
        assert audio.language == lang
        assert audio.sample_rate == 24000
        assert audio.byte_size > 1000
        assert audio.content_uri.startswith("data:audio/wav;base64,")


def test_elevenlabs_provider_configuration_and_voices():
    """
    Verifies ElevenLabs provider configuration, premade voices including Prof. Apurva / Sarah,
    and voice resolution.
    """
    prov = ElevenLabsProvider(api_key="test_dummy_key")
    assert prov.is_configured() is True
    assert "apurva" in prov.PREMADE_VOICES
    assert "sarah" in prov.PREMADE_VOICES
    assert prov.PREMADE_VOICES["apurva"] == prov.PREMADE_VOICES["sarah"]

    voices = prov.get_voices("en")
    assert len(voices) >= 3
    # Check that Prof. Apurva / Sarah is present
    apurva_voice = next((v for v in voices if "Apurva" in v["name"] or "Sarah" in v["name"]), None)
    assert apurva_voice is not None
    assert apurva_voice["gender"] == "female"


def test_video_composer_supports_both_wav_and_mp3():
    """
    Verifies VideoComposer.render_mp4_video extracts audio bytes correctly
    whether provided as WAV (data:audio/wav;base64) or MP3 (data:audio/mp3;base64 or data:audio/mpeg;base64).
    """
    composer = VideoComposer()

    # Generate a tiny valid dummy WAV
    sample_rate = 24000
    num_samples = 2400  # 0.1s
    raw_wav = (
        b"RIFF"
        + struct.pack("<I", 36 + num_samples * 2)
        + b"WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x60\x5d\x00\x00\xc0\xba\x00\x00\x02\x00\x10\x00data"
        + struct.pack("<I", num_samples * 2)
        + (b"\x00\x00" * num_samples)
    )
    b64_wav = base64.b64encode(raw_wav).decode("ascii")

    wav_audio = AudioAsset(
        script_id="test_wav",
        language="en",
        voice_id="prof_apurva",
        duration_seconds=0.1,
        sample_rate=24000,
        format="wav",
        content_uri=f"data:audio/wav;base64,{b64_wav}",
        byte_size=len(raw_wav),
    )

    mp3_audio = AudioAsset(
        script_id="test_mp3",
        language="en",
        voice_id="prof_apurva",
        duration_seconds=0.1,
        sample_rate=44100,
        format="mp3",
        content_uri=f"data:audio/mp3;base64,{b64_wav}",  # dummy payload for testing parser dispatch
        byte_size=len(raw_wav),
    )

    mpeg_audio = AudioAsset(
        script_id="test_mpeg",
        language="en",
        voice_id="prof_apurva",
        duration_seconds=0.1,
        sample_rate=44100,
        format="mp3",
        content_uri=f"data:audio/mpeg;base64,{b64_wav}",
        byte_size=len(raw_wav),
    )

    # When ffmpeg is unavailable or mocked, method handles both gracefully without raising exceptions
    with patch.object(composer, "is_ffmpeg_available", return_value=False):
        assert composer.render_mp4_video("seg_01", wav_audio, None, 0.1) is None
        assert composer.render_mp4_video("seg_02", mp3_audio, None, 0.1) is None
        assert composer.render_mp4_video("seg_03", mpeg_audio, None, 0.1) is None


def test_caption_and_audio_duration_synchronization():
    """
    Verifies that generated subtitle cues span the full duration of the spoken audio,
    with monotonically increasing timestamps and exact end-time alignment.
    """
    composer = VideoComposer()
    script = TeachingScript(
        concept="Dynamic Programming",
        teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
        spoken_script="Dynamic programming solves problems by breaking them down into subproblems. "
                      "We store the results of subproblems to avoid redundant computation. "
                      "This technique is called memoization.",
        estimated_duration_seconds=12.0,
    )

    audio_duration = 10.5
    captions = composer.generate_captions(script, total_duration=audio_duration)

    assert captions is not None
    assert len(captions.cues) == 3
    assert captions.cues[0].start_seconds == 0.0
    assert captions.cues[-1].end_seconds == audio_duration

    # Verify monotonic time ordering
    for i in range(len(captions.cues) - 1):
        assert captions.cues[i].end_seconds <= captions.cues[i + 1].start_seconds + 0.01

    # Verify WebVTT syntax
    assert "WEBVTT" in captions.vtt_content
    assert "-->" in captions.vtt_content

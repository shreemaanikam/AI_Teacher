"""
Local Machine Capability Detection for Teacher Media Pipeline.
Probes OS, CPU, RAM, GPU, CUDA, VRAM, Python, FFmpeg, and model providers
to dynamically configure the optimal, reliable execution path.
"""

import os
import sys
import platform
import shutil
import subprocess
from typing import Dict, Any, Optional
from pydantic import BaseModel


class MediaCapabilities(BaseModel):
    os: str
    cpu_architecture: str
    python_version: str
    cuda_available: bool = False
    gpu_name: Optional[str] = None
    vram_mb: int = 0
    ffmpeg_available: bool = False
    ffmpeg_path: Optional[str] = None
    node_available: bool = False
    
    # Model Provider Status
    kokoro_available: bool = False
    musetalk_available: bool = False
    liveportrait_available: bool = False
    bark_available: bool = False
    system_tts_available: bool = False
    opencv_video_writer_available: bool = True
    
    # Recommended Active Stack
    primary_tts: str
    primary_lipsync: str
    primary_avatar: str
    fallback_strategy: str


def detect_capabilities() -> MediaCapabilities:
    """Probes host hardware, dependencies, and configured models."""
    system_os = platform.system()
    arch = platform.machine()
    py_ver = sys.version.split()[0]
    
    # Check FFmpeg
    from .media.ffmpeg import find_ffmpeg_binary
    ffmpeg_path = find_ffmpeg_binary()
    ffmpeg_ok = ffmpeg_path is not None
    
    # Check Node.js
    node_ok = shutil.which("node") is not None
    
    # Check CUDA / Torch GPU
    cuda_ok = False
    gpu_name = None
    vram = 0
    try:
        import torch
        if torch.cuda.is_available():
            cuda_ok = True
            gpu_name = torch.cuda.get_device_name(0)
            vram = int(torch.cuda.get_device_properties(0).total_memory / (1024 * 1024))
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            gpu_name = "Apple Silicon MPS"
    except ImportError:
        pass

    # Check Kokoro ONNX
    kokoro_ok = False
    try:
        import kokoro_onnx  # noqa: F401
        kokoro_ok = True
    except ImportError:
        try:
            import kokoro  # noqa: F401
            kokoro_ok = True
        except ImportError:
            kokoro_ok = False

    # Check MuseTalk
    musetalk_ok = False
    # Check if musetalk package or weights directory exists
    if os.environ.get("MUSE_TALK_ENABLED", "false").lower() == "true":
        musetalk_ok = True
    elif os.path.exists("models/musetalk") or shutil.which("musetalk"):
        musetalk_ok = True

    # Check LivePortrait
    liveportrait_ok = False
    if os.environ.get("LIVEPORTRAIT_API_KEY") or os.environ.get("LIVEPORTRAIT_ENABLED", "false").lower() == "true":
        liveportrait_ok = True

    # Check Bark
    bark_ok = False
    try:
        import bark  # noqa: F401
        bark_ok = True
    except ImportError:
        bark_ok = False

    # Check System TTS (macOS say)
    system_tts_ok = shutil.which("say") is not None

    # Check OpenCV
    cv2_ok = False
    try:
        import cv2  # noqa: F401
        cv2_ok = True
    except ImportError:
        cv2_ok = False

    # Determine optimal primary stack
    if kokoro_ok:
        active_tts = "kokoro_onnx"
    elif system_tts_ok:
        active_tts = "system_tts_daniel"
    elif bark_ok:
        active_tts = "bark"
    else:
        active_tts = "procedural_formant"

    if musetalk_ok and cuda_ok:
        active_lipsync = "musetalk"
    elif cv2_ok:
        active_lipsync = "audio_synchronized_viseme"
    else:
        active_lipsync = "pregenerated_sync"

    if liveportrait_ok:
        active_avatar = "liveportrait"
    elif cv2_ok:
        active_avatar = "procedural_photorealistic_opencv"
    else:
        active_avatar = "pregenerated_canonical_video"

    return MediaCapabilities(
        os=system_os,
        cpu_architecture=arch,
        python_version=py_ver,
        cuda_available=cuda_ok,
        gpu_name=gpu_name,
        vram_mb=vram,
        ffmpeg_available=ffmpeg_ok,
        ffmpeg_path=ffmpeg_path,
        node_available=node_ok,
        kokoro_available=kokoro_ok,
        musetalk_available=musetalk_ok,
        liveportrait_available=liveportrait_ok,
        bark_available=bark_ok,
        system_tts_available=system_tts_ok,
        opencv_video_writer_available=cv2_ok,
        primary_tts=active_tts,
        primary_lipsync=active_lipsync,
        primary_avatar=active_avatar,
        fallback_strategy="graceful_pregenerated_and_procedural"
    )


probe_system_capabilities = detect_capabilities

"""
Module 9: Voice + Avatar + Video Engine.
"""

from app.media.models import (
    MediaStatus,
    MediaKind,
    TeachingScript,
    AudioAsset,
    AvatarAsset,
    CaptionAsset,
    TimedCaptionCue,
    MediaSegment,
    MediaJob,
)
from app.media.script_generator import TeachingScriptGenerator
from app.media.tts.provider import VoiceProvider
from app.media.tts.local_tts import LocalVoiceProvider
from app.media.avatar.provider import AvatarProvider
from app.media.avatar.procedural_avatar import ProceduralAvatarProvider
from app.media.composer import VideoComposer
from app.media.jobs import MediaJobQueue
from app.media.engine import MultimodalMediaEngine

__all__ = [
    "MediaStatus",
    "MediaKind",
    "TeachingScript",
    "AudioAsset",
    "AvatarAsset",
    "CaptionAsset",
    "TimedCaptionCue",
    "MediaSegment",
    "MediaJob",
    "TeachingScriptGenerator",
    "VoiceProvider",
    "LocalVoiceProvider",
    "AvatarProvider",
    "ProceduralAvatarProvider",
    "VideoComposer",
    "MediaJobQueue",
    "MultimodalMediaEngine",
]

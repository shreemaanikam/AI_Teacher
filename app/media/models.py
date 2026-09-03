"""
Data Models for Module 9 (Voice + Avatar + Video Engine).
"""

from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.harness.session import TeachingStrategy


class MediaStatus(str, Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"
    FALLBACK = "FALLBACK"


class MediaKind(str, Enum):
    AUDIO = "audio"
    AVATAR = "avatar"
    VISUAL = "visual"
    CAPTION = "caption"
    SEGMENT = "segment"
    TIMELINE = "timeline"


class TeachingScript(BaseModel):
    """Structured narration script tailored to pedagogical strategy and language."""
    script_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    concept: str
    teaching_strategy: TeachingStrategy
    language: str = "en"
    learner_level: str = "beginner"
    spoken_script: str
    on_screen_text: List[str] = Field(default_factory=list)
    visual_cues: List[str] = Field(default_factory=list)
    pause_points: List[float] = Field(default_factory=list)  # timestamps in seconds
    question_points: List[float] = Field(default_factory=list)
    estimated_duration_seconds: float = 20.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AudioAsset(BaseModel):
    """Synthesized speech audio file or data URI."""
    audio_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    script_id: str
    language: str
    voice_id: str
    duration_seconds: float
    format: str = "wav"  # wav, mp3
    content_uri: str  # local path, data URI or URL
    byte_size: int = 0
    is_fallback: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AvatarAsset(BaseModel):
    """Avatar presenter video, WebM stream, or interactive procedural SVG animation."""
    avatar_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    script_id: str
    audio_id: Optional[str] = None
    presenter_style: str = "academic_mentor"
    format: str = "svg_animation"  # mp4, webm, svg_animation
    content_uri: str
    duration_seconds: float
    is_fallback: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TimedCaptionCue(BaseModel):
    start_seconds: float
    end_seconds: float
    text: str


class CaptionAsset(BaseModel):
    caption_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    language: str
    vtt_content: str
    cues: List[TimedCaptionCue] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MediaSegment(BaseModel):
    """A fully synchronized, adaptive lesson video segment."""
    segment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    lesson_id: str
    session_id: Optional[str] = None
    concept: str
    teaching_strategy: TeachingStrategy
    language: str = "en"
    status: MediaStatus = MediaStatus.READY
    duration_seconds: float = 20.0
    script: TeachingScript
    audio: Optional[AudioAsset] = None
    avatar: Optional[AvatarAsset] = None
    visual_spec_id: Optional[str] = None
    visual_asset_id: Optional[str] = None
    captions: Optional[CaptionAsset] = None
    video_url: Optional[str] = None
    playback_manifest: Dict[str, Any] = Field(default_factory=dict)
    is_fallback_mode: bool = False
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MediaJob(BaseModel):
    """Asynchronous background rendering job."""
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    segment_id: str
    status: MediaStatus = MediaStatus.QUEUED
    progress_percent: int = 0
    result_segment: Optional[MediaSegment] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

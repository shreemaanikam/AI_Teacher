"""
Multimodal Media Engine for Module 9 (Voice + Avatar + Video Engine).
High-level service coordinating script generation, TTS, avatar animation, video assembly, and background job queuing.
"""

from __future__ import annotations
import logging
from typing import Dict, Optional

from app.media.models import (
    MediaSegment,
    MediaJob,
    MediaStatus,
    TeachingScript,
    AudioAsset,
    AvatarAsset,
)
from app.media.script_generator import TeachingScriptGenerator
from app.media.tts.provider import VoiceProvider
from app.media.tts.local_tts import LocalVoiceProvider
from app.media.avatar.provider import AvatarProvider
from app.media.avatar.procedural_avatar import ProceduralAvatarProvider
from app.media.composer import VideoComposer
from app.media.jobs import MediaJobQueue
from app.visuals.models import VisualAsset
from app.harness.session import TeachingStrategy
from app.assessment.models import MisconceptionRecord

logger = logging.getLogger(__name__)


class MultimodalMediaEngine:
    """
    Coordinates end-to-end multimodal teaching segment generation.
    Produces synchronized, multilingual audio/avatar/visual lesson segments.
    """

    def __init__(
        self,
        script_generator: Optional[TeachingScriptGenerator] = None,
        voice_provider: Optional[VoiceProvider] = None,
        avatar_provider: Optional[AvatarProvider] = None,
        composer: Optional[VideoComposer] = None,
        job_queue: Optional[MediaJobQueue] = None,
    ):
        self.script_generator = script_generator or TeachingScriptGenerator()
        self.voice_provider = voice_provider or LocalVoiceProvider()
        self.avatar_provider = avatar_provider or ProceduralAvatarProvider()
        self.composer = composer or VideoComposer()
        self.job_queue = job_queue or MediaJobQueue()
        self._segments_store: Dict[str, MediaSegment] = {}

    def generate_teaching_segment(
        self,
        lesson_id: str,
        concept: str,
        teaching_strategy: TeachingStrategy = TeachingStrategy.DIRECT_EXPLANATION,
        language: str = "en",
        learner_level: str = "beginner",
        misconception: Optional[MisconceptionRecord] = None,
        visual_asset: Optional[VisualAsset] = None,
        session_id: Optional[str] = None,
        async_mode: bool = False,
    ) -> MediaSegment | MediaJob:
        """
        Generates a synchronized teaching segment.
        If async_mode=True, immediately returns a MediaJob with status QUEUED/PROCESSING.
        """
        def _produce_segment() -> MediaSegment:
            # 1. Script Generation
            script = self.script_generator.generate_script(
                concept=concept,
                teaching_strategy=teaching_strategy,
                language=language,
                learner_level=learner_level,
                misconception=misconception,
            )

            # 2. Voice / TTS Generation with fallback
            audio: Optional[AudioAsset] = None
            try:
                audio = self.voice_provider.generate_speech(
                    script_id=script.script_id,
                    text=script.spoken_script,
                    language=language,
                )
            except Exception as e:
                logger.warning(f"Voice generation failed: {e}. Falling back to text/caption mode.")

            # 3. Avatar Generation with fallback
            avatar: Optional[AvatarAsset] = None
            try:
                avatar = self.avatar_provider.generate_avatar(
                    script=script,
                    audio=audio,
                )
            except Exception as e:
                logger.warning(f"Avatar generation failed: {e}. Falling back to visual+audio mode.")

            # 4. Assembly and Synchronization
            segment = self.composer.assemble_segment(
                lesson_id=lesson_id,
                script=script,
                audio=audio,
                avatar=avatar,
                visual_asset=visual_asset,
                session_id=session_id,
            )

            self._segments_store[segment.segment_id] = segment
            return segment

        if async_mode:
            import uuid
            seg_id = str(uuid.uuid4())
            return self.job_queue.submit_segment_job(seg_id, _produce_segment)

        return _produce_segment()

    def get_segment(self, segment_id: str) -> Optional[MediaSegment]:
        return self._segments_store.get(segment_id)

    def get_job(self, job_id: str) -> Optional[MediaJob]:
        return self.job_queue.get_job(job_id)

    def get_job_by_segment(self, segment_id: str) -> Optional[MediaJob]:
        return self.job_queue.get_job_by_segment(segment_id)

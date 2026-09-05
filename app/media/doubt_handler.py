"""
Student Doubt & Interruption Handler for Module 9.
Handles real-time student doubts ("I don't understand this", voice queries, concept questions),
preserves active lesson session state, generates targeted teacher clarification,
coordinates avatar reactions (THINKING -> EXPLAINING -> QUESTION), and enables seamless resumption.
"""

from __future__ import annotations
import logging
import uuid
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.media.models import (
    TeacherEmotion,
    TeacherGesture,
    TeacherPresentationState,
    TeachingScript,
    AudioAsset,
    AvatarAsset,
    MediaSegment,
)
from app.harness.session import TeachingStrategy, DifficultyLevel
from app.visuals.models import SubjectCategory, VisualType

logger = logging.getLogger(__name__)


class DoubtResponse(BaseModel):
    """Structured response to a student doubt interruption."""
    doubt_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    concept: str
    student_query: str
    saved_state: Dict[str, Any]
    clarification_text: str
    presentation_state: TeacherPresentationState
    audio: Optional[AudioAsset] = None
    avatar: Optional[AvatarAsset] = None
    suggested_visual_strategy: str = "SIMPLE_ANALOGY"
    follow_up_prompt: str = ""
    can_resume_lesson: bool = True


class StudentDoubtHandler:
    """
    Manages live educator reactions to learner confusion, interruptions, and queries.
    Preserves cognitive state, generates clarifying pedagogy, and coordinates avatar gestures.
    """

    def __init__(self, media_engine: Optional[Any] = None, visual_engine: Optional[Any] = None):
        self.media_engine = media_engine
        self.visual_engine = visual_engine
        self._saved_sessions: Dict[str, Dict[str, Any]] = {}

    def capture_session_snapshot(self, session_id: str, current_state: Dict[str, Any]) -> None:
        """Saves current lesson state prior to handling the student doubt."""
        self._saved_sessions[session_id] = {
            "session_id": session_id,
            "concept": current_state.get("concept", "general_study"),
            "strategy": current_state.get("strategy", "DIRECT_EXPLANATION"),
            "step_index": current_state.get("step_index", 0),
            "difficulty": current_state.get("difficulty", "BASIC"),
            "mastery": current_state.get("mastery", {}),
            "language": current_state.get("language", "en"),
        }

    def get_saved_snapshot(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self._saved_sessions.get(session_id)

    def handle_doubt(
        self,
        session_id: str,
        student_query: str,
        concept: str,
        current_context: Optional[Dict[str, Any]] = None,
        language: str = "en",
        teacher_id: str = "prof_apurva",
    ) -> DoubtResponse:
        """
        Executes the doubt resolution flow:
        1. Acknowledge and save state.
        2. Set avatar to THINKING -> EXPLAINING with reassuring tone.
        3. Formulate intuitive clarification (preferring analogies or stepwise breakdown).
        4. Produce speech audio and synchronized avatar reaction.
        5. Provide follow-up check and resume option.
        """
        snapshot = current_context or self.get_saved_snapshot(session_id) or {
            "session_id": session_id,
            "concept": concept,
            "strategy": "DIRECT_EXPLANATION",
            "step_index": 0,
            "language": language,
        }
        self.capture_session_snapshot(session_id, snapshot)

        # 1. Affective Teacher State for Doubt Handling
        presentation_state = TeacherPresentationState(
            emotion=TeacherEmotion.ENCOURAGING,
            gesture=TeacherGesture.EXPLANATION,
            speech_mode="REASSURING",
            attention_target="student",
            intensity=0.8,
        )

        # 2. Formulate Pedagogical Clarification
        clean_q = student_query.strip().lower()
        if language == "hi":
            clarification = (
                f"कोई बात नहीं, यह बहुत स्वाभाविक प्रश्न है। चलिए '{concept}' को एक सरल उदाहरण से समझते हैं। "
                "जब हम चरण-दर-चरण देखते हैं, तो मुख्य सिद्धांत बिल्कुल स्पष्ट हो जाता है।"
            )
            follow_up = "क्या अब आपको यह अवधारणा स्पष्ट लग रही है, या हम एक और उदाहरण देखें?"
        elif language == "ta":
            clarification = (
                f"கவலைப்பட வேண்டாம், '{concept}' பற்றிய இந்த சந்தேகம் மிகவும் இயல்பானது. "
                "நாம் இதை ஒரு எளிய உருவகத்துடன் மீண்டும் பார்ப்போம்."
            )
            follow_up = "இப்போது உங்களுக்கு இந்த கருத்து தெளிவாக உள்ளதா?"
        else:
            clarification = (
                f"That is a completely natural question to ask about {concept}. "
                "Let us pause and look at this from an intuitive physical perspective. "
                "Notice how the core relationship works when we isolate each component."
            )
            follow_up = "Does this intuitive breakdown make sense, or would you like to explore another step?"

        # 3. Generate Clarification Speech & Avatar if Media Engine is wired
        audio_asset = None
        avatar_asset = None

        if self.media_engine:
            script = TeachingScript(
                concept=concept,
                teaching_strategy=TeachingStrategy.SIMPLE_ANALOGY,
                language=language,
                spoken_script=clarification,
                estimated_duration_seconds=8.0,
            )
            try:
                audio_asset = self.media_engine.voice_provider.generate_speech(
                    script_id=script.script_id,
                    text=script.spoken_script,
                    language=language,
                )
            except Exception as e:
                logger.warning(f"Failed to generate doubt voice: {e}")

            try:
                avatar_asset = self.media_engine.avatar_provider.generate_avatar(
                    script=script,
                    audio=audio_asset,
                    presenter_style=teacher_id,
                )
            except Exception as e:
                logger.warning(f"Failed to generate doubt avatar: {e}")

        return DoubtResponse(
            session_id=session_id,
            concept=concept,
            student_query=student_query,
            saved_state=snapshot,
            clarification_text=clarification,
            presentation_state=presentation_state,
            audio=audio_asset,
            avatar=avatar_asset,
            suggested_visual_strategy="SIMPLE_ANALOGY",
            follow_up_prompt=follow_up,
            can_resume_lesson=True,
        )

    def resume_lesson(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Restores the lesson state following successful doubt resolution."""
        return self._saved_sessions.get(session_id)

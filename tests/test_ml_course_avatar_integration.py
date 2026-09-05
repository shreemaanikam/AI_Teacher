"""
Tests for STAGE ML-COURSE-26: Human AI Teacher Integration Engine.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.avatar_integration import MLAvatarIntegrationEngine
from app.ml_course.models import VerificationStatus
from app.media.models import TeacherGesture


class TestMLAvatarIntegrationEngine:
    """Test suite for human avatar, voice, and visual board pedagogical integration."""

    @pytest.fixture(autouse=True)
    def setup_engine(self):
        self.engine = MLAvatarIntegrationEngine.get_instance()

    def test_deliver_lesson_with_prof_apurva(self):
        exp = self.engine.deliver_concept_lesson("ml.u3.backpropagation", teacher_id="prof_apurva")
        assert exp.teacher_name == "Prof. Apurva Sharma, Ph.D."
        assert exp.concept_id == "ml.u3.backpropagation"
        assert exp.unit_number == 3

        # Approved script check
        assert exp.approved_script.is_approved is True
        assert exp.approved_script.status == VerificationStatus.VERIFIED

        # Visual board check
        assert exp.visual_payload.visual_type == "BACKPROPAGATION"
        assert "<svg" in exp.visual_payload.html_canvas_component

        # Presentation cues & gestures
        gestures = [c.gesture for c in exp.presentation_cues]
        assert TeacherGesture.POINT_TO_BOARD in gestures
        assert TeacherGesture.EXPLANATION in gestures
        assert TeacherGesture.QUESTION in gestures
        assert TeacherGesture.CONGRATULATE in gestures

        # Avatar asset
        assert exp.avatar_asset is not None
        assert exp.avatar_asset.aspect_ratio == "16:9"
        assert len(exp.source_refs) > 0
        assert exp.verification_status == VerificationStatus.VERIFIED

    def test_deliver_lesson_with_dr_vikram(self):
        exp = self.engine.deliver_concept_lesson("ml.u4.kmeans", teacher_id="dr_vikram")
        assert "Vikram" in exp.teacher_name
        assert exp.visual_payload.visual_type == "KMEANS_CLUSTERING"
        assert exp.approved_script.is_approved is True

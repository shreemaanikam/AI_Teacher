"""
Tests for STAGE ML-COURSE-35: Full Machine Learning Student Journey Engine.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.student_journey import MLStudentJourneyEngine
from app.ml_course.models import VerificationStatus


class TestMLStudentJourneyEngine:
    """Test suite for full end-to-end collegiate ML student journey."""

    @pytest.fixture(autouse=True)
    def setup_engine(self):
        self.engine = MLStudentJourneyEngine.get_instance()

    def test_complete_student_learning_journey(self):
        # 1. Initialize Profile
        state = self.engine.initialize_journey(
            student_id="cit_student_101",
            student_name="Aarav CIT Scholar",
        )
        assert state.student_id == "cit_student_101"
        assert "INITIALIZE_PROFILE" in state.steps_completed

        # 2. Select Concept from Unit 3
        exp = self.engine.select_concept(
            state=state,
            concept_id="ml.u3.backpropagation",
            teacher_id="prof_apurva",
        )
        assert state.current_unit == 3
        assert state.current_concept_id == "ml.u3.backpropagation"
        assert exp.approved_script.is_approved is True
        assert exp.visual_payload.visual_type == "BACKPROPAGATION"
        assert "AVATAR_NARRATION_READY" in state.steps_completed
        assert "DYNAMIC_VISUAL_MOUNTED" in state.steps_completed

        # 3. Generate Diagnostic Question
        q = self.engine.generate_concept_question(state)
        assert q.concept_id == "ml.u3.backpropagation"
        assert len(q.question_text) > 10
        assert "QUESTION_PRESENTED" in state.steps_completed

        # 4. Process Student Response - Incorrect Answer (Triggers Misconception Adaptation)
        res_incorrect = self.engine.process_student_response(
            state=state,
            student_answer="Backpropagation randomly guesses weights until the loss magically hits 0.",
        )
        assert res_incorrect["evaluation"].is_correct is False
        assert res_incorrect["remediation"] is not None
        assert "ml.u3.backpropagation" in state.weak_concepts
        assert "MISCONCEPTION_DIAGNOSED" in state.steps_completed
        assert "NEW_VISUAL_REMEDIATION" in state.steps_completed

        # 5. Process Student Response - Correct Answer (Achieves Mastery)
        res_correct = self.engine.process_student_response(
            state=state,
            student_answer="Backpropagation computes the gradient of the loss function with respect to weights using the chain rule and propagates error backward.",
        )
        assert res_correct["evaluation"].is_correct is True
        assert state.concept_mastery["ml.u3.backpropagation"] > 0.9
        assert "MASTERY_ACHIEVED" in state.steps_completed

        # 6. Generate 60-minute Exam Session Plan
        exam_plan = self.engine.create_exam_plan(state, duration_minutes=60)
        assert exam_plan.duration_minutes == 60
        assert len(exam_plan.questions) > 0
        assert "EXAM_PLAN_CONFIGURED" in state.steps_completed

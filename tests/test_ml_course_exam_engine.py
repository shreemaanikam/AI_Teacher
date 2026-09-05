"""
Tests for STAGE ML-COURSE-21: Machine Learning Exam Engine.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.exam_engine import MLExamEngine
from app.ml_course.models import VerificationStatus


class TestMLExamEngine:
    """Test suite for 5/20/60 minute exam sessions and 7-day revision plans."""

    @pytest.fixture(autouse=True)
    def setup_engine(self):
        self.engine = MLExamEngine.get_instance()

    def test_five_minute_quick_session(self):
        session = self.engine.generate_exam_session(5)
        assert session.duration_minutes == 5
        assert len(session.questions) == 2
        assert session.total_marks == 10
        assert session.verification_status == VerificationStatus.VERIFIED

    def test_twenty_minute_targeted_session(self):
        session = self.engine.generate_exam_session(20)
        assert session.duration_minutes == 20
        assert len(session.questions) == 4
        # Must include at least 1 numerical
        assert any(q.question_type == "NUMERICAL" for q in session.questions)
        assert session.total_marks == 25

    def test_sixty_minute_comprehensive_exam(self):
        session = self.engine.generate_exam_session(60)
        assert session.duration_minutes == 60
        # Must cover all 5 units
        assert set(session.units_covered) == {1, 2, 3, 4, 5}
        assert session.total_marks >= 70

    def test_prioritization_of_weak_concepts(self):
        weak = ["ml.u3.backpropagation", "ml.u5.q_learning"]
        session = self.engine.generate_exam_session(5, student_weak_concepts=weak)
        # Weak concept should be in the top questions
        q_concepts = [q.concept_id for q in session.questions]
        assert any(c in q_concepts for c in weak)

    def test_seven_day_revision_schedule(self):
        plan = self.engine.generate_7day_revision_schedule(
            target_score=95,
            available_hours_per_day=3.0,
            weak_units=[3],
        )
        assert len(plan.daily_schedules) == 7
        assert plan.target_score == 95
        # Day 3 (Unit 3, weak) should have 1.25x allocated hours
        day3 = plan.daily_schedules[2]
        assert day3.allocated_hours == 3.75
        # Day 7 has full mock exam
        assert plan.daily_schedules[6].mock_test_duration_minutes == 60

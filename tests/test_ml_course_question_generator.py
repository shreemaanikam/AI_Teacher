"""
Tests for STAGE ML-COURSE-22: Course-Grounded Question Generator.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.question_generator import MLQuestionGenerator
from app.ml_course.models import VerificationStatus


class TestMLQuestionGenerator:
    """Test suite for 8-type question generation grounded in course materials."""

    @pytest.fixture(autouse=True)
    def setup_gen(self):
        self.generator = MLQuestionGenerator.get_instance()

    def test_generate_all_eight_question_types(self):
        types = [
            "MCQ",
            "SHORT_ANSWER",
            "NUMERICAL",
            "ALGORITHM",
            "DERIVATION",
            "CONCEPTUAL",
            "APPLICATION",
            "VIVA",
        ]
        for t in types:
            q = self.generator.generate_question(unit=2, question_type=t)
            assert q.question_type == t
            assert q.unit == 2
            assert len(q.question_text) > 15
            assert len(q.expected_answer) > 0
            assert len(q.source_refs) > 0
            assert q.verification_status == VerificationStatus.VERIFIED

    def test_mcq_structure(self):
        q = self.generator.generate_question(unit=4, question_type="MCQ")
        assert q.options is not None
        assert len(q.options) == 4
        assert q.correct_option_index is not None
        assert 0 <= q.correct_option_index < 4
        assert q.expected_answer == q.options[q.correct_option_index]

    def test_numerical_question_grounding(self):
        q = self.generator.generate_question(unit=2, question_type="NUMERICAL")
        assert len(q.expected_answer) > 0
        assert any(r.filename.endswith(".pdf") for r in q.source_refs)

    def test_generate_multi_unit_question_set(self):
        q_set = self.generator.generate_question_set(count=10)
        assert len(q_set) == 10
        units_in_set = {q.unit for q in q_set}
        assert len(units_in_set) >= 4

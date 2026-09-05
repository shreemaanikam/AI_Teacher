"""
Tests for STAGE ML-COURSE-19: Concept Teaching Engine.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.concept_teaching_engine import MLConceptTeachingEngine
from app.ml_course.models import VerificationStatus


class TestMLConceptTeachingEngine:
    """Test suite for representative concept pedagogical modules across Units I through V."""

    @pytest.fixture(autouse=True)
    def setup_engine(self):
        self.engine = MLConceptTeachingEngine.get_instance()

    def test_teach_representative_concepts_across_all_units(self):
        test_concepts = [
            ("ml.u1.linear_regression", 1, "Linear Regression"),
            ("ml.u2.svm", 2, "Support Vector"),
            ("ml.u3.backpropagation", 3, "Backpropagation"),
            ("ml.u4.kmeans", 4, "K-Means"),
            ("ml.u5.q_learning", 5, "Q-Learning"),
        ]

        for cid, expected_unit, name_substr in test_concepts:
            module = self.engine.teach_concept(cid)
            assert module.concept_id == cid
            assert module.unit_number == expected_unit
            assert name_substr.lower() in module.canonical_name.lower()
            assert len(module.definition) > 10
            assert len(module.intuition) > 10
            assert "title" in module.example
            assert "visual_type" in module.visual_spec
            assert len(module.check_question) > 10
            assert len(module.expected_answer_rubric) > 10
            assert len(module.source_refs) > 0
            assert module.verification_status == VerificationStatus.VERIFIED

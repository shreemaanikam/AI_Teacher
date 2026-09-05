"""
Tests for STAGE ML-COURSE-18: Unit-by-Unit Teaching Engine.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.unit_teaching_engine import MLUnitTeachingEngine
from app.ml_course.models import VerificationStatus


class TestMLUnitTeachingEngine:
    """Test suite for unit lesson plan generation, visual mapping, and drift prevention."""

    @pytest.fixture(autouse=True)
    def setup_engine(self):
        self.engine = MLUnitTeachingEngine.get_instance()

    def test_teach_all_five_units_sequentially(self):
        for u_num in range(1, 6):
            plan = self.engine.generate_unit_lesson_plan(u_num)
            assert plan.unit_number == u_num
            assert plan.verification_status == VerificationStatus.VERIFIED
            assert len(plan.concept_ids) >= 10
            assert len(plan.concept_names) == len(plan.concept_ids)
            assert len(plan.source_refs) > 0
            assert "type" in plan.visual_plan
            assert "diagnostic_questions" in plan.assessment_plan

    def test_zero_cross_unit_drift(self):
        # Unit 1 must not contain neural networks, kmeans, or q-learning
        u1 = self.engine.generate_unit_lesson_plan(1)
        for cid in u1.concept_ids:
            assert cid.startswith("ml.u1.")
            assert "neural" not in cid
            assert "kmeans" not in cid
            assert "q_learning" not in cid

        # Unit 4 must contain only Unit 4 concepts (clustering, dim reduction)
        u4 = self.engine.generate_unit_lesson_plan(4)
        for cid in u4.concept_ids:
            assert cid.startswith("ml.u4.")
        assert "ml.u4.kmeans" in u4.concept_ids
        assert "ml.u4.pca" in u4.concept_ids

        # Unit 5 must contain only Unit 5 concepts
        u5 = self.engine.generate_unit_lesson_plan(5)
        for cid in u5.concept_ids:
            assert cid.startswith("ml.u5.")
        assert "ml.u5.reinforcement_learning" in u5.concept_ids
        assert "ml.u5.least_squares" in u5.concept_ids

    def test_unit_visual_blueprints(self):
        u1 = self.engine.generate_unit_lesson_plan(1)
        assert u1.visual_plan["type"] == "REGRESSION_RESIDUAL_PLOT"

        u3 = self.engine.generate_unit_lesson_plan(3)
        assert u3.visual_plan["type"] == "NEURAL_NETWORK_FLOW"

        u4 = self.engine.generate_unit_lesson_plan(4)
        assert u4.visual_plan["type"] == "CLUSTERING_SPACE"

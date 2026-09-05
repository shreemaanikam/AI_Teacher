"""
Tests for STAGE ML-COURSE-20: Numerical Teaching & Interactive Doubt Engine.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.numerical_teaching_engine import MLNumericalTeachingEngine
from app.ml_course.models import VerificationStatus


class TestMLNumericalTeachingEngine:
    """Test suite for step-by-step numerical lesson delivery and interactive doubt resolution."""

    @pytest.fixture(autouse=True)
    def setup_engine(self):
        self.engine = MLNumericalTeachingEngine.get_instance()

    def test_teach_numerical_problem_walkthrough(self):
        plan = self.engine.teach_numerical_problem("prob.ml.u4.kmeans_7points")
        assert plan.problem_id == "prob.ml.u4.kmeans_7points"
        assert len(plan.step_by_step_walkthrough) >= 3
        assert len(plan.final_answer) > 0
        assert len(plan.source_refs) > 0
        assert plan.verification_status == VerificationStatus.VERIFIED

    def test_answer_doubt_why_centroid_changed(self):
        resp = self.engine.answer_student_numerical_doubt(
            "prob.ml.u4.kmeans_7points",
            "Why did the centroid change after iteration 1?"
        )
        assert resp["doubt_category"] == "CENTROID_UPDATE_EXPLANATION"
        assert "mean" in resp["answer"].lower() or "average" in resp["answer"].lower()
        assert resp["is_grounded"] is True

    def test_answer_doubt_why_this_formula(self):
        resp = self.engine.answer_student_numerical_doubt(
            "prob.ml.u2.knn_angelina",
            "Why this formula?"
        )
        assert resp["doubt_category"] == "FORMULA_JUSTIFICATION"
        assert len(resp["answer"]) > 20

    def test_answer_doubt_how_did_you_calculate(self):
        resp = self.engine.answer_student_numerical_doubt(
            "prob.ml.u3.backpropagation_ex1",
            "How did you calculate this step?"
        )
        assert resp["doubt_category"] == "CALCULATION_STEP_EXPLANATION"
        assert "sequential" in resp["answer"].lower()

    def test_answer_doubt_why_value_used(self):
        resp = self.engine.answer_student_numerical_doubt(
            "prob.ml.u2.knn_angelina",
            "Why is this value used for k?"
        )
        assert resp["doubt_category"] == "PARAMETER_SOURCE_EXPLANATION"
        assert resp["is_grounded"] is True

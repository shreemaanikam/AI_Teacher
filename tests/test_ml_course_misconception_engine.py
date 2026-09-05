"""
Tests for STAGE ML-COURSE-24: Misconception Engine.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.misconception_engine import MLMisconceptionEngine
from app.ml_course.models import VerificationStatus


class TestMLMisconceptionEngine:
    """Test suite for closed-loop diagnosis, contrastive remediation, and retest generation."""

    @pytest.fixture(autouse=True)
    def setup_engine(self):
        self.engine = MLMisconceptionEngine.get_instance()

    def test_remediation_kmeans_supervised_misconception(self):
        error = "K-Means is a supervised algorithm that uses labels to optimize clusters."
        plan = self.engine.diagnose_and_remediate("ml.u4.kmeans", error)

        assert plan.concept_id == "ml.u4.kmeans"
        assert plan.unit_number == 4
        assert "Unsupervised" in plan.diagnosed_misconception or "Supervised" in plan.diagnosed_misconception
        assert "unlabelled" in plan.contrastive_explanation.lower()
        # Contrastive visual must be distinct
        assert plan.remediation_visual["type"] == "CONTRASTIVE_SCATTER"
        # Retest question must be attached
        assert plan.retest_question is not None
        assert plan.retest_question.unit == 4
        assert plan.verification_status == VerificationStatus.VERIFIED

    def test_remediation_sigmoid_range_misconception(self):
        error = "The output range of sigmoid function is from -1 to 1."
        plan = self.engine.diagnose_and_remediate("ml.u2.logistic_regression", error)

        assert plan.concept_id == "ml.u2.logistic_regression"
        assert plan.unit_number == 2
        assert "Tanh" in plan.contrastive_explanation or "(0, 1)" in plan.contrastive_explanation
        assert plan.remediation_visual["type"] == "ACTIVATION_CURVES_COMPARISON"
        assert plan.retest_question is not None

"""
Tests for STAGE ML-COURSE-14: Teaching Claim Verification Engine.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.claim_validator import MLClaimValidator
from app.ml_course.models import ClaimStatus, VerificationStatus


class TestMLClaimValidator:
    """Test suite for claim extraction, contradiction detection, and correction."""

    @pytest.fixture(autouse=True)
    def setup_validator(self):
        self.validator = MLClaimValidator.get_instance()

    def test_supported_script_validation(self):
        script = "Backpropagation calculates the gradient of the error function with respect to weights using the chain rule. The weights are then updated using gradient descent."
        res = self.validator.validate_script(script, unit=3, concept_id="ml.u3.backpropagation")
        assert res.is_approved is True
        assert res.status == VerificationStatus.VERIFIED
        assert any(c.status == ClaimStatus.SUPPORTED for c in res.claims)
        assert len(res.corrections_made) == 0

    def test_contradiction_detection_and_correction_kmeans(self):
        flawed_script = "In this lecture we discuss clustering. K-Means is a supervised algorithm that uses labeled targets to train."
        res = self.validator.validate_script(flawed_script, unit=4, concept_id="ml.u4.kmeans")
        assert len(res.corrections_made) >= 1
        assert "unsupervised" in res.approved_text
        assert "supervised algorithm that uses labeled" not in res.approved_text
        assert any(c.status == ClaimStatus.CONTRADICTED for c in res.claims)

    def test_contradiction_detection_sigmoid_range(self):
        flawed_script = "The logistic regression activation function is the sigmoid. Sigmoid outputs values between -1 and 1."
        res = self.validator.validate_script(flawed_script, unit=2, concept_id="ml.u2.logistic_regression")
        assert len(res.corrections_made) >= 1
        assert "(0, 1)" in res.approved_text
        assert any(c.status == ClaimStatus.CONTRADICTED for c in res.claims)

    def test_qlearning_model_free_validation(self):
        flawed_script = "Q-learning requires a model-based transition probability table."
        res = self.validator.validate_script(flawed_script, unit=5, concept_id="ml.u5.q_learning")
        assert len(res.corrections_made) >= 1
        assert "model-free" in res.approved_text

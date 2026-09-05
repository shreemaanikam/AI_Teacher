"""
Tests for STAGE ML-COURSE-17: Algorithm Verification Engine.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.algorithm_validator import MLAlgorithmValidator
from app.ml_course.models import VerificationStatus


class TestMLAlgorithmValidator:
    """Test suite for procedural algorithm step validation and ordering auditing."""

    @pytest.fixture(autouse=True)
    def setup_validator(self):
        self.validator = MLAlgorithmValidator.get_instance()

    def test_valid_kmeans_algorithm_steps_pass(self):
        steps = [
            "Step 1: Choose number of clusters K.",
            "Initialize K cluster centroids randomly or using K-Means++.",
            "Assign each data point to the nearest centroid using Euclidean distance.",
            "Recompute the centroids by taking the mean of all points assigned to each cluster.",
            "Repeat assignment and update steps until centroids no longer change or max iterations reached.",
        ]
        stopping = "Centroids no longer move or assignments do not change."
        res = self.validator.validate_algorithm_explanation(
            "algo.ml.u4.kmeans",
            steps,
            candidate_stopping_condition=stopping,
        )
        assert res.is_valid is True
        assert res.status == VerificationStatus.VERIFIED
        assert len(res.missing_steps) == 0
        assert len(res.ordering_violations) == 0

    def test_detect_reversed_order_in_kmeans(self):
        # Flawed: Recomputing before assigning
        flawed_steps = [
            "Initialize K cluster centroids.",
            "Recompute the centroids by taking the mean.",
            "Assign each data point to the nearest centroid.",
            "Repeat until convergence.",
        ]
        res = self.validator.validate_algorithm_explanation(
            "algo.ml.u4.kmeans",
            flawed_steps,
        )
        assert res.is_valid is False
        assert len(res.ordering_violations) >= 1
        assert "before point assignment" in res.ordering_violations[0]

    def test_detect_reversed_backprop_order(self):
        flawed_steps = [
            "Compute backward pass gradients using delta rule.",
            "Execute forward pass to calculate activations and outputs.",
            "Update weights using learning rate.",
        ]
        res = self.validator.validate_algorithm_explanation(
            "algo.ml.u3.backpropagation",
            flawed_steps,
        )
        assert res.is_valid is False
        assert len(res.ordering_violations) >= 1
        assert "before forward pass" in res.ordering_violations[0]

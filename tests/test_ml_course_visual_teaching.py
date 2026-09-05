"""
Tests for STAGE ML-COURSE-25: Dynamic Visual Teaching Engine.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.visual_teaching import MLDynamicVisualEngine
from app.ml_course.models import VerificationStatus


class TestMLDynamicVisualEngine:
    """Test suite for deterministic visual payloads across 6 core ML paradigms."""

    @pytest.fixture(autouse=True)
    def setup_engine(self):
        self.engine = MLDynamicVisualEngine.get_instance()

    def test_backpropagation_visual_payload(self):
        res = self.engine.generate_visual_payload("ml.u3.backpropagation")
        assert res.visual_type == "BACKPROPAGATION"
        assert res.unit == 3
        assert len(res.animation_steps) == 4
        assert "<svg" in res.html_canvas_component
        assert "Step Forward" in res.interactive_controls
        assert res.is_deterministic is True
        assert res.verification_status == VerificationStatus.VERIFIED

    def test_kmeans_clustering_visual_payload(self):
        res = self.engine.generate_visual_payload("ml.u4.kmeans")
        assert res.visual_type == "KMEANS_CLUSTERING"
        assert res.unit == 4
        assert any("Centroid" in s["action"] for s in res.animation_steps)
        assert "<svg" in res.html_canvas_component

    def test_gradient_descent_visual_payload(self):
        res = self.engine.generate_visual_payload("ml.u2.gradient_descent")
        assert res.visual_type == "GRADIENT_DESCENT"
        assert res.unit == 2
        assert any("Negative Gradient" in s["action"] for s in res.animation_steps)

    def test_decision_tree_visual_payload(self):
        res = self.engine.generate_visual_payload("ml.u2.decision_tree")
        assert res.visual_type == "DECISION_TREE"
        assert res.unit == 2
        assert any("Root Split" in s["action"] for s in res.animation_steps)

    def test_q_learning_visual_payload(self):
        res = self.engine.generate_visual_payload("ml.u5.q_learning")
        assert res.visual_type == "Q_LEARNING"
        assert res.unit == 5
        assert any("Bellman" in s["action"] for s in res.animation_steps)

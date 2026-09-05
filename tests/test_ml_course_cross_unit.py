"""
Tests for STAGE ML-COURSE-29: Cross-Unit Synthesis & Multi-Unit Query Engine.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.cross_unit import MLCrossUnitEngine
from app.ml_course.models import VerificationStatus


class TestMLCrossUnitEngine:
    """Test suite for cross-unit query handling and synthesis across Units I–V."""

    @pytest.fixture(autouse=True)
    def setup_engine(self):
        self.engine = MLCrossUnitEngine.get_instance()

    def test_detect_cross_unit_topics(self):
        units = self.engine.detect_units("Compare Perceptron with Backpropagation in deep neural networks")
        assert 2 in units
        assert 3 in units
        assert len(units) >= 2

    def test_cross_unit_synthesis_unit_2_and_3(self):
        query = "How does the single-layer Perceptron differ from Multilayer Networks and Backpropagation?"
        res = self.engine.answer_cross_unit_query(query)

        assert res.is_cross_unit is True
        assert 2 in res.units_involved
        assert 3 in res.units_involved
        assert 2 in res.unit_evidence_groups
        assert 3 in res.unit_evidence_groups

        # Both units must have evidence
        assert len(res.unit_evidence_groups[2].evidence_items) > 0
        assert len(res.unit_evidence_groups[3].evidence_items) > 0

        # Comparative synthesis text
        assert "Unit 2" in res.comparative_synthesis
        assert "Unit 3" in res.comparative_synthesis
        assert res.verification_status == VerificationStatus.VERIFIED

    def test_cross_unit_synthesis_unit_1_and_4(self):
        query = "How does PCA dimensionality reduction impact Linear Regression?"
        res = self.engine.answer_cross_unit_query(query)

        assert res.is_cross_unit is True
        assert 1 in res.units_involved
        assert 4 in res.units_involved
        assert len(res.unit_evidence_groups[1].evidence_items) > 0
        assert len(res.unit_evidence_groups[4].evidence_items) > 0

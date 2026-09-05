"""
Tests for STAGE ML-COURSE-33 & ML-COURSE-34: Adversarial Testing & Human Review Protocol.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.adversarial import MLAdversarialTester
from app.ml_course.human_review import MLHumanReviewEngine, InspectionVerdict


class TestMLAdversarialAndHumanReview:
    """Test suite for adversarial defense robustness and human inspection audit."""

    def test_adversarial_traps_intercepted(self):
        tester = MLAdversarialTester.get_instance()
        results = tester.run_all_tests()

        assert len(results) >= 5
        for r in results:
            assert r.trap_identified is True, f"Failed on attack {r.test_id}"
            assert r.passed is True
            assert r.action_taken in ["CORRECTED", "REJECTED", "ABSTAINED"]

    def test_human_review_protocol_passed(self):
        engine = MLHumanReviewEngine.get_instance()
        proto = engine.get_protocol()

        assert proto.total_checks_performed == 35
        assert proto.total_passed == 35
        assert proto.total_failed == 0
        assert proto.total_needs_review == 0
        assert proto.overall_certification_verdict == InspectionVerdict.PASS

        # Every unit must have passed all 7 criteria
        for u in range(1, 6):
            rec = proto.unit_records[u]
            assert rec.accuracy_verdict == InspectionVerdict.PASS
            assert rec.formula_verdict == InspectionVerdict.PASS
            assert rec.algorithm_verdict == InspectionVerdict.PASS
            assert rec.visual_verdict == InspectionVerdict.PASS
            assert rec.source_grounding_verdict == InspectionVerdict.PASS
            assert rec.teaching_clarity_verdict == InspectionVerdict.PASS
            assert rec.question_verdict == InspectionVerdict.PASS
            assert rec.overall_unit_verdict == InspectionVerdict.PASS

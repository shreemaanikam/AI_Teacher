"""
Tests for STAGE ML-COURSE-08: Problem Bank Assembly.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.problem_bank import MLProblemBank
from app.ml_course.models import ProblemType, VerificationStatus


class TestMLProblemBank:
    """Test suite for MLProblemBank assembly, indexing, retrieval, and validation."""

    def test_total_problem_count_and_units(self):
        problems = MLProblemBank.get_all_problems()
        assert len(problems) == 14, f"Expected 14 problems across 5 units, got {len(problems)}"

        # Check distribution per unit
        assert len(MLProblemBank.get_problems_by_unit(1)) == 4
        assert len(MLProblemBank.get_problems_by_unit(2)) == 3
        assert len(MLProblemBank.get_problems_by_unit(3)) == 3
        assert len(MLProblemBank.get_problems_by_unit(4)) == 2
        assert len(MLProblemBank.get_problems_by_unit(5)) == 2

    def test_all_problems_verified_and_grounded(self):
        audit = MLProblemBank.verify_all_problems()
        assert audit["verified"] is True, f"Audit failed: {audit}"
        assert len(audit["missing_steps"]) == 0
        assert len(audit["missing_answers"]) == 0
        assert len(audit["missing_refs"]) == 0
        assert len(audit["unverified"]) == 0

    def test_get_individual_problem_by_id(self):
        p1 = MLProblemBank.get_problem("prob.ml.u1.confusion_matrix_metrics")
        assert p1 is not None
        assert p1.unit == 1
        assert "Accuracy" in p1.question or "Precision" in p1.question
        assert len(p1.solution_steps) > 0
        assert p1.verification_status == VerificationStatus.VERIFIED

        p_pca = MLProblemBank.get_problem("prob.ml.u4.pca_numerical")
        assert p_pca is not None
        assert p_pca.unit == 4
        assert "PCA" in p_pca.topic or "Principal Component" in p_pca.topic

    def test_filter_by_concept_id(self):
        knn_problems = MLProblemBank.get_problems_by_concept("ml.u2.knn")
        assert len(knn_problems) >= 1
        assert any("Angelina" in p.question for p in knn_problems)

        scaling_problems = MLProblemBank.get_problems_by_concept("ml.u1.feature_scaling")
        assert len(scaling_problems) == 2
        assert any("min_max" in p.problem_id for p in scaling_problems)

    def test_filter_by_problem_type(self):
        numericals = MLProblemBank.get_problems_by_type(ProblemType.NUMERICAL)
        assert len(numericals) >= 8
        derivations = MLProblemBank.get_problems_by_type(ProblemType.DERIVATION)
        assert isinstance(derivations, list)

    def test_search_problems(self):
        results = MLProblemBank.search_problems("Backpropagation")
        assert len(results) >= 1
        assert results[0].problem_id == "prob.ml.u3.backpropagation_ex1"

        results_kmeans = MLProblemBank.search_problems("K-Means")
        assert len(results_kmeans) >= 1
        assert results_kmeans[0].problem_id == "prob.ml.u4.kmeans_7points"

        results_cg = MLProblemBank.search_problems("Conjugate Gradient")
        assert len(results_cg) >= 1
        assert results_cg[0].problem_id == "prob.ml.u5.cg_iteration"

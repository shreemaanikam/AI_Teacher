"""
Tests for STAGE ML-COURSE-04: Machine Learning Unit II Ingestion Engine.
Verifies all 11 concepts, dual-source grounding in all_units_combined.pdf (Pages 40-72)
and unit_2_problems.pdf (Pages 1-9), including solved problems for KNN, Perceptron, and Logistic Regression.
"""

import math
import pytest
from app.ml_course.unit2_ingestion import Unit2IngestionEngine
from app.ml_course.models import MachineLearningUnit, ProblemType, VerificationStatus


def test_unit2_ingestion_metadata():
    unit = Unit2IngestionEngine.ingest()
    assert isinstance(unit, MachineLearningUnit)
    assert unit.unit_number == 2
    assert unit.unit_code == "UNIT II"
    assert "Supervised Learning" in unit.title
    assert len(unit.source_pages) == 33
    assert unit.source_pages[0] == 40
    assert unit.source_pages[-1] == 72
    assert "all_units_combined.pdf" in unit.source_documents
    assert "unit_2_problems.pdf" in unit.source_documents


def test_unit2_concepts_grounding():
    unit = Unit2IngestionEngine.ingest()
    assert len(unit.concepts) == 11

    expected_ids = [
        "ml.u2.bayesian_regression",
        "ml.u2.gradient_descent",
        "ml.u2.perceptron",
        "ml.u2.logistic_regression",
        "ml.u2.naive_bayes",
        "ml.u2.svm",
        "ml.u2.decision_tree",
        "ml.u2.random_forest",
        "ml.u2.knn",
        "ml.u2.bagging_boosting",
        "ml.u2.hyperparameter_tuning",
    ]

    c_map = {c.concept_id: c for c in unit.concepts}
    for eid in expected_ids:
        assert eid in c_map, f"Missing Unit 2 concept: {eid}"

    # Verify concepts with problem sheet dual-sourcing
    dual_sourced = ["ml.u2.knn", "ml.u2.perceptron", "ml.u2.logistic_regression"]
    for cid in dual_sourced:
        refs = c_map[cid].source_refs
        filenames = {r.filename for r in refs}
        assert "all_units_combined.pdf" in filenames, f"{cid} missing theory ref"
        assert "unit_2_problems.pdf" in filenames, f"{cid} missing problem ref"


def test_unit2_definitions():
    unit = Unit2IngestionEngine.ingest()
    assert len(unit.definitions) >= 4

    terms = {d.term: d for d in unit.definitions}
    assert any("Perceptron" in t for t in terms.keys())
    assert any("Maximum Margin Hyperplane" in t for t in terms.keys())
    assert any("Conditional Independence" in t for t in terms.keys())
    assert any("Entropy" in t for t in terms.keys())


def test_unit2_formulas():
    unit = Unit2IngestionEngine.ingest()
    assert len(unit.formulas) >= 8

    f_map = {f.formula_id: f for f in unit.formulas}
    assert "form.ml.u2.gd_update" in f_map
    assert "form.ml.u2.perceptron_rule" in f_map
    assert "form.ml.u2.sigmoid" in f_map
    assert "form.ml.u2.log_loss" in f_map
    assert "form.ml.u2.bayes" in f_map
    assert "form.ml.u2.entropy" in f_map
    assert "form.ml.u2.info_gain" in f_map
    assert "form.ml.u2.svm_margin" in f_map
    assert "form.ml.u2.euclidean_dist" in f_map


def test_unit2_algorithms():
    unit = Unit2IngestionEngine.ingest()
    assert len(unit.algorithms) >= 3

    algo_ids = {a.algorithm_id: a for a in unit.algorithms}
    assert "algo.ml.u2.knn" in algo_ids
    assert "algo.ml.u2.perceptron" in algo_ids
    assert "algo.ml.u2.id3" in algo_ids

    # Verify ID3 algorithm steps
    id3 = algo_ids["algo.ml.u2.id3"]
    assert any("Information Gain" in s for s in id3.steps)
    assert id3.stopping_condition is not None


def test_unit2_solved_problems_mathematical_precision():
    unit = Unit2IngestionEngine.ingest()
    assert len(unit.problems) >= 3

    p_map = {p.problem_id: p for p in unit.problems}

    # 1. KNN Angelina
    p_knn = p_map["prob.ml.u2.knn_angelina"]
    assert p_knn.verification_status == VerificationStatus.VERIFIED
    assert "Cricket" in p_knn.final_answer
    # Recalculate distance to record 8 (Age: 15, Gender: 1) from Angelina (5, 1)
    d8 = math.sqrt((15 - 5) ** 2 + (1 - 1) ** 2)
    assert d8 == 10.0
    # Recalculate distance to record 10 (Age: 15, Gender: 0)
    d10 = math.sqrt((15 - 5) ** 2 + (0 - 1) ** 2)
    assert round(d10, 2) == 10.05

    # 2. Perceptron AND Gate
    p_perc = p_map["prob.ml.u2.perceptron_and_gate"]
    assert p_perc.verification_status == VerificationStatus.VERIFIED
    assert "0.7" in p_perc.final_answer
    assert "0.6" in p_perc.final_answer
    # Recalculate update: w1 = 1.2 + 0.5 * (0 - 1) * 1 = 0.7
    w1_new = 1.2 + 0.5 * (0 - 1) * 1
    assert w1_new == 0.7

    # 3. Logistic Regression Loan Default
    p_log = p_map["prob.ml.u2.logistic_loan_default"]
    assert p_log.verification_status == VerificationStatus.VERIFIED
    # Recalculate linear score and sigmoid:
    z = (-0.005 * 650) + (-0.04 * 50) + 4
    assert z == -1.25
    prob = 1.0 / (1.0 + math.exp(-z))
    assert round(prob, 4) == 0.2227
    assert "22.2" in p_log.final_answer
    assert "approved" in p_log.final_answer.lower() or "class 0" in p_log.final_answer.lower()


def test_unit2_source_grounding_audit():
    audit = Unit2IngestionEngine.verify_source_grounding()
    assert audit["verified"] is True
    assert audit["unit"] == 2
    assert audit["total_concepts"] == 11
    assert len(audit["invalid_citations"]) == 0
    assert len(audit["missing_source_refs"]) == 0

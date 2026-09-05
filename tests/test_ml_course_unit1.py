"""
Tests for STAGE ML-COURSE-03: Machine Learning Unit I Ingestion Engine.
Verifies all 12 concepts, definitions, formulas, algorithms, problems, exam topics,
and 100% source grounding in all_units_combined.pdf (Pages 1-39).
"""

import pytest
from app.ml_course.unit1_ingestion import Unit1IngestionEngine
from app.ml_course.models import MachineLearningUnit, ProblemType, VerificationStatus


def test_unit1_ingestion_basic_metadata():
    unit = Unit1IngestionEngine.ingest()
    assert isinstance(unit, MachineLearningUnit)
    assert unit.unit_number == 1
    assert unit.unit_code == "UNIT I"
    assert "Regression" in unit.title
    assert len(unit.source_pages) == 39
    assert unit.source_pages[0] == 1
    assert unit.source_pages[-1] == 39
    assert "all_units_combined.pdf" in unit.source_documents


def test_unit1_concepts_twelve_grounded():
    unit = Unit1IngestionEngine.ingest()
    assert len(unit.concepts) == 12

    expected_concept_ids = [
        "ml.u1.intro",
        "ml.u1.learning_types",
        "ml.u1.hypothesis_space",
        "ml.u1.inductive_bias",
        "ml.u1.train_test_split",
        "ml.u1.cross_validation",
        "ml.u1.underfitting_overfitting",
        "ml.u1.bias_variance_tradeoff",
        "ml.u1.linear_regression",
        "ml.u1.polynomial_regression",
        "ml.u1.evaluation_metrics",
        "ml.u1.feature_scaling",
    ]

    concept_ids = [c.concept_id for c in unit.concepts]
    for cid in expected_concept_ids:
        assert cid in concept_ids, f"Missing expected Unit 1 concept: {cid}"

    for c in unit.concepts:
        assert c.source_document == "all_units_combined.pdf"
        assert len(c.source_pages) >= 1
        for p in c.source_pages:
            assert 1 <= p <= 39
        assert len(c.source_refs) >= 1
        assert c.source_refs[0].document_id == "doc_ml_all_units"


def test_unit1_definitions():
    unit = Unit1IngestionEngine.ingest()
    assert len(unit.definitions) >= 4

    terms = {d.term: d for d in unit.definitions}
    assert any("Arthur Samuel" in t for t in terms.keys())
    assert any("Tom Mitchell" in t for t in terms.keys())
    assert any("Inductive Bias" in t for t in terms.keys())
    assert any("Hypothesis Space" in t for t in terms.keys())

    # Check Tom Mitchell definition contains T, P, E
    mitchell_def = [d for d in unit.definitions if "Tom Mitchell" in d.term][0]
    assert "Task T" in mitchell_def.definition_text or "tasks in T" in mitchell_def.definition_text
    assert "performance measure P" in mitchell_def.definition_text
    assert "experience E" in mitchell_def.definition_text


def test_unit1_formulas_mathematical_integrity():
    unit = Unit1IngestionEngine.ingest()
    assert len(unit.formulas) >= 9

    formula_ids = {f.formula_id: f for f in unit.formulas}
    assert "form.ml.u1.simple_linear" in formula_ids
    assert "form.ml.u1.multiple_linear" in formula_ids
    assert "form.ml.u1.accuracy" in formula_ids
    assert "form.ml.u1.precision" in formula_ids
    assert "form.ml.u1.recall" in formula_ids
    assert "form.ml.u1.f1_score" in formula_ids
    assert "form.ml.u1.mse" in formula_ids
    assert "form.ml.u1.min_max" in formula_ids
    assert "form.ml.u1.standardization" in formula_ids

    # Check variable definitions exist
    for fid, formula in formula_ids.items():
        assert len(formula.variables) > 0
        assert formula.source_document == "all_units_combined.pdf"
        assert 1 <= formula.page <= 39


def test_unit1_algorithms():
    unit = Unit1IngestionEngine.ingest()
    assert len(unit.algorithms) >= 2

    algo_ids = {a.algorithm_id: a for a in unit.algorithms}
    assert "algo.ml.u1.kfold_cv" in algo_ids
    assert "algo.ml.u1.batch_gradient_descent" in algo_ids

    kfold = algo_ids["algo.ml.u1.kfold_cv"]
    assert len(kfold.steps) >= 5
    assert kfold.stopping_condition is not None


def test_unit1_numerical_problems_solved():
    unit = Unit1IngestionEngine.ingest()
    assert len(unit.problems) >= 4

    # Test 5-fold CV problem calculation
    cv_prob = [p for p in unit.problems if p.problem_id == "prob.ml.u1.cross_validation_5fold"][0]
    accs = cv_prob.given_data["accuracies"]
    expected_mean = sum(accs) / len(accs)
    assert expected_mean == 93.0
    assert "93" in cv_prob.final_answer
    assert cv_prob.verification_status == VerificationStatus.VERIFIED

    # Test Min-Max scaling problem
    mm_prob = [p for p in unit.problems if p.problem_id == "prob.ml.u1.min_max_scaling"][0]
    vals = mm_prob.given_data["X_values"]
    target = mm_prob.given_data["target_x"]
    norm = (target - min(vals)) / (max(vals) - min(vals))
    assert norm == 0.5
    assert "0.5" in mm_prob.final_answer

    # Test Confusion matrix metrics
    cm_prob = [p for p in unit.problems if p.problem_id == "prob.ml.u1.confusion_matrix_metrics"][0]
    tp = cm_prob.given_data["TP"]
    fp = cm_prob.given_data["FP"]
    fn = cm_prob.given_data["FN"]
    tn = cm_prob.given_data["TN"]
    acc = (tp + tn) / (tp + tn + fp + fn)
    prec = tp / (tp + fp)
    rec = tp / (tp + fn)
    f1 = 2 * (prec * rec) / (prec + rec)
    assert acc == 0.85
    assert prec == 0.80
    assert round(rec, 4) == 0.8889
    assert round(f1, 4) == 0.8421


def test_unit1_source_grounding_audit():
    audit = Unit1IngestionEngine.verify_source_grounding()
    assert audit["verified"] is True
    assert audit["unit"] == 1
    assert audit["total_concepts"] == 12
    assert len(audit["invalid_citations"]) == 0
    assert len(audit["missing_source_refs"]) == 0

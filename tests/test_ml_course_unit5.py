"""
Tests for STAGE ML-COURSE-07: Machine Learning Unit V Ingestion Engine.
Verifies all 10 concepts, multi-source deduplication across all_units_combined.pdf (Pages 148-178),
unit_5_notes_v1.pdf (Pages 1-15), and unit_5_notes_v2.pdf (Pages 1-16).
"""

import pytest
from app.ml_course.unit5_ingestion import Unit5IngestionEngine
from app.ml_course.models import MachineLearningUnit, ProblemType, VerificationStatus


def test_unit5_ingestion_metadata():
    unit = Unit5IngestionEngine.ingest()
    assert isinstance(unit, MachineLearningUnit)
    assert unit.unit_number == 5
    assert unit.unit_code == "UNIT V"
    assert "Optimization, Reinforcement Learning" in unit.title
    assert len(unit.source_pages) == 31
    assert unit.source_pages[0] == 148
    assert unit.source_pages[-1] == 178
    assert "all_units_combined.pdf" in unit.source_documents
    assert "unit_5_notes_v1.pdf" in unit.source_documents
    assert "unit_5_notes_v2.pdf" in unit.source_documents


def test_unit5_concepts_zero_duplication_and_multi_source():
    unit = Unit5IngestionEngine.ingest()
    assert len(unit.concepts) == 10

    expected_ids = [
        "ml.u5.least_squares",
        "ml.u5.conjugate_gradient",
        "ml.u5.reinforcement_learning",
        "ml.u5.mdp",
        "ml.u5.q_learning",
        "ml.u5.exploration_exploitation",
        "ml.u5.responsible_ai",
        "ml.u5.shap_and_lime",
        "ml.u5.mlops",
        "ml.u5.federated_learning",
    ]

    c_map = {c.concept_id: c for c in unit.concepts}
    for eid in expected_ids:
        assert eid in c_map, f"Missing Unit 5 concept: {eid}"

    # Verify Least Squares and Conjugate Gradient cite both Set 1 and Set 2 notes
    ls_refs = {r.filename for r in c_map["ml.u5.least_squares"].source_refs}
    assert "all_units_combined.pdf" in ls_refs
    assert "unit_5_notes_v1.pdf" in ls_refs
    assert "unit_5_notes_v2.pdf" in ls_refs

    cg_refs = {r.filename for r in c_map["ml.u5.conjugate_gradient"].source_refs}
    assert "all_units_combined.pdf" in cg_refs
    assert "unit_5_notes_v1.pdf" in cg_refs
    assert "unit_5_notes_v2.pdf" in cg_refs


def test_unit5_definitions():
    unit = Unit5IngestionEngine.ingest()
    assert len(unit.definitions) >= 5

    terms = {d.term: d for d in unit.definitions}
    assert any("Normal Equations" in t for t in terms.keys())
    assert any("Conjugacy" in t for t in terms.keys())
    assert any("Markov Property" in t for t in terms.keys())
    assert any("Q-Learning" in t for t in terms.keys())
    assert any("Shapley Value" in t for t in terms.keys())


def test_unit5_formulas():
    unit = Unit5IngestionEngine.ingest()
    assert len(unit.formulas) >= 5

    f_map = {f.formula_id: f for f in unit.formulas}
    assert "form.ml.u5.normal_equations" in f_map
    assert "form.ml.u5.cg_step" in f_map
    assert "form.ml.u5.q_update" in f_map
    assert "form.ml.u5.shap_attribution" in f_map
    assert "form.ml.u5.fedavg" in f_map


def test_unit5_algorithms():
    unit = Unit5IngestionEngine.ingest()
    assert len(unit.algorithms) >= 2

    algo_ids = {a.algorithm_id: a for a in unit.algorithms}
    assert "algo.ml.u5.q_learning" in algo_ids
    assert "algo.ml.u5.conjugate_gradient" in algo_ids

    cg = algo_ids["algo.ml.u5.conjugate_gradient"]
    assert any("step size alpha_k" in s for s in cg.steps)
    assert any("beta_k" in s for s in cg.steps)


def test_unit5_solved_problems_mathematics():
    unit = Unit5IngestionEngine.ingest()
    assert len(unit.problems) >= 2

    p_map = {p.problem_id: p for p in unit.problems}

    # 1. Q-Learning TD Target calculation
    p_ql = p_map["prob.ml.u5.q_learning_td_target"]
    assert p_ql.verification_status == VerificationStatus.VERIFIED
    # Target = 5 + 0.9 * 6.0 = 10.4
    # Error = 10.4 - 2.0 = 8.4
    # Q_new = 2.0 + 0.5 * 8.4 = 6.2
    assert "6.2" in p_ql.final_answer
    assert "10.4" in p_ql.final_answer
    assert "8.4" in p_ql.final_answer

    # 2. Conjugate Gradient 2 iteration problem
    p_cg = p_map["prob.ml.u5.cg_iteration"]
    assert p_cg.verification_status == VerificationStatus.VERIFIED
    assert "0.0909" in p_cg.final_answer
    assert "0.6364" in p_cg.final_answer


def test_unit5_source_grounding_audit():
    audit = Unit5IngestionEngine.verify_source_grounding()
    assert audit["verified"] is True
    assert audit["unit"] == 5
    assert audit["total_concepts"] == 10
    assert len(audit["invalid_citations"]) == 0
    assert len(audit["missing_source_refs"]) == 0

"""
Tests for STAGE ML-COURSE-05: Machine Learning Unit III Ingestion Engine.
Verifies all 11 concepts, dual-source grounding in all_units_combined.pdf (Pages 73-110)
and unit_3_and_4_problems.pdf (Pages 1-21), including Backprop, CNN, and LSTM numericals.
"""

import math
import pytest
from app.ml_course.unit3_ingestion import Unit3IngestionEngine
from app.ml_course.models import MachineLearningUnit, ProblemType, VerificationStatus


def test_unit3_ingestion_metadata():
    unit = Unit3IngestionEngine.ingest()
    assert isinstance(unit, MachineLearningUnit)
    assert unit.unit_number == 3
    assert unit.unit_code == "UNIT III"
    assert "Neural Networks" in unit.title
    assert len(unit.source_pages) == 38
    assert unit.source_pages[0] == 73
    assert unit.source_pages[-1] == 110
    assert "all_units_combined.pdf" in unit.source_documents
    assert "unit_3_and_4_problems.pdf" in unit.source_documents


def test_unit3_concepts_grounding():
    unit = Unit3IngestionEngine.ingest()
    assert len(unit.concepts) == 11

    expected_ids = [
        "ml.u3.ann_intro",
        "ml.u3.ann_architectures",
        "ml.u3.ann_challenges",
        "ml.u3.perceptron_activations",
        "ml.u3.backpropagation",
        "ml.u3.cnn",
        "ml.u3.rnn",
        "ml.u3.lstm",
        "ml.u3.bert",
        "ml.u3.gans",
        "ml.u3.generative_models",
    ]

    c_map = {c.concept_id: c for c in unit.concepts}
    for eid in expected_ids:
        assert eid in c_map, f"Missing Unit 3 concept: {eid}"

    # Verify concepts dual-sourced with problem sheet
    problem_supported = ["ml.u3.backpropagation", "ml.u3.cnn", "ml.u3.lstm", "ml.u3.gans"]
    for cid in problem_supported:
        refs = c_map[cid].source_refs
        filenames = {r.filename for r in refs}
        assert "all_units_combined.pdf" in filenames, f"{cid} missing theory ref"
        assert "unit_3_and_4_problems.pdf" in filenames, f"{cid} missing problem ref"


def test_unit3_definitions():
    unit = Unit3IngestionEngine.ingest()
    assert len(unit.definitions) >= 5

    terms = {d.term: d for d in unit.definitions}
    assert any("McCulloch-Pitts" in t for t in terms.keys())
    assert any("Backpropagation" in t for t in terms.keys())
    assert any("Vanishing Gradient" in t for t in terms.keys())
    assert any("Convolution" in t for t in terms.keys())
    assert any("Generative Adversarial" in t for t in terms.keys())


def test_unit3_formulas():
    unit = Unit3IngestionEngine.ingest()
    assert len(unit.formulas) >= 7

    f_map = {f.formula_id: f for f in unit.formulas}
    assert "form.ml.u3.backprop_deltas" in f_map
    assert "form.ml.u3.cnn_dim" in f_map
    assert "form.ml.u3.rnn_hidden" in f_map
    assert "form.ml.u3.lstm_forget" in f_map
    assert "form.ml.u3.lstm_cell" in f_map
    assert "form.ml.u3.gan_objective" in f_map
    assert "form.ml.u3.softmax" in f_map


def test_unit3_algorithms():
    unit = Unit3IngestionEngine.ingest()
    assert len(unit.algorithms) >= 2

    algo_ids = {a.algorithm_id: a for a in unit.algorithms}
    assert "algo.ml.u3.backpropagation" in algo_ids
    assert "algo.ml.u3.cnn_forward" in algo_ids

    bp = algo_ids["algo.ml.u3.backpropagation"]
    assert any("Forward Pass" in s for s in bp.steps)
    assert any("Hidden Error" in s for s in bp.steps)


def test_unit3_solved_problems_mathematics():
    unit = Unit3IngestionEngine.ingest()
    assert len(unit.problems) >= 3

    p_map = {p.problem_id: p for p in unit.problems}

    # 1. Backpropagation Ex 1
    p_bp = p_map["prob.ml.u3.backpropagation_ex1"]
    assert p_bp.verification_status == VerificationStatus.VERIFIED
    assert "0.8731" in p_bp.final_answer or "0.8730" in p_bp.final_answer
    assert "0.3971" in p_bp.final_answer
    assert "0.0991" in p_bp.final_answer
    # Recalculate forward pass hidden node 3:
    a1 = 0.1 * 0.35 + 0.8 * 0.9  # 0.755
    y3 = 1.0 / (1.0 + math.exp(-a1))
    assert round(y3, 2) == 0.68

    # 2. CNN convolution dimension
    p_cnn = p_map["prob.ml.u3.cnn_convolution_pooling"]
    assert p_cnn.verification_status == VerificationStatus.VERIFIED
    # O = (N - F + 2P)/S + 1 = (5 - 3 + 0)/1 + 1 = 3
    assert "3x3" in p_cnn.final_answer

    # 3. LSTM Gate step
    p_lstm = p_map["prob.ml.u3.lstm_gate_step"]
    assert p_lstm.verification_status == VerificationStatus.VERIFIED
    assert "0.76" in p_lstm.final_answer
    assert "0.75" in p_lstm.final_answer
    assert "0.8045" in p_lstm.final_answer or "0.8077" in p_lstm.final_answer
    assert "0.70" in p_lstm.final_answer
    assert "0.47" in p_lstm.final_answer


def test_unit3_source_grounding_audit():
    audit = Unit3IngestionEngine.verify_source_grounding()
    assert audit["verified"] is True
    assert audit["unit"] == 3
    assert audit["total_concepts"] == 11
    assert len(audit["invalid_citations"]) == 0
    assert len(audit["missing_source_refs"]) == 0

"""
Flask API Blueprint for Module 7 (Assessment & Misconception Engine).
"""

from __future__ import annotations
from flask import Blueprint, jsonify, request, current_app
from app.assessment.engine import AssessmentEngine
from app.assessment.models import EvaluationVerdict
from app.harness.orchestrator import MasterTeachingOrchestrator
from app.harness.session import DifficultyLevel, ActiveMisconception, SessionState

assessment_blueprint = Blueprint("assessment", __name__)


def get_assessment_engine() -> AssessmentEngine:
    if "ASSESSMENT_ENGINE" not in current_app.config:
        current_app.config["ASSESSMENT_ENGINE"] = AssessmentEngine()
    return current_app.config["ASSESSMENT_ENGINE"]


def get_orchestrator() -> MasterTeachingOrchestrator:
    if "MASTER_ORCHESTRATOR" not in current_app.config:
        current_app.config["MASTER_ORCHESTRATOR"] = MasterTeachingOrchestrator()
    return current_app.config["MASTER_ORCHESTRATOR"]


@assessment_blueprint.route("/lessons/<lesson_id>/question", methods=["POST"])
def get_checkpoint_question(lesson_id: str):
    """Generates the appropriate checkpoint question for current concept."""
    engine = get_assessment_engine()
    orchestrator = get_orchestrator()

    data = request.get_json(silent=True) or {}
    concept = data.get("concept")
    diff_val = data.get("difficulty", 2)
    language = data.get("language", "en")

    session = None
    for s in orchestrator._sessions.values():
        if s.lesson_id == lesson_id:
            session = s
            break

    if session:
        concept = concept or session.current_concept
        diff_val = session.current_difficulty.value
        language = session.language

    concept = concept or "ohms_law"
    difficulty = DifficultyLevel(diff_val) if diff_val in (1, 2, 3, 4, 5) else DifficultyLevel.BASIC

    question = engine.generate_checkpoint_question(
        lesson_id=lesson_id,
        concept=concept,
        difficulty=difficulty,
        language=language,
    )

    # Advance state machine from TEACH -> QUESTION if session is active
    if session and session.current_state in (SessionState.TEACH, SessionState.REEXPLAIN):
        orchestrator.advance_to_question(session.session_id, question_id=question.question_id)

    return jsonify({
        "status": "success",
        "question": question.model_dump(mode="json"),
        "session_state": session.current_state.value if session else None,
    }), 200


@assessment_blueprint.route("/lessons/<lesson_id>/answer", methods=["POST"])
def evaluate_student_answer(lesson_id: str):
    """
    Submits student answer, evaluates semantic correctness, detects misconceptions,
    and drives the Teaching Harness adaptive decision.
    """
    engine = get_assessment_engine()
    orchestrator = get_orchestrator()

    data = request.get_json(silent=True) or {}
    question_id = data.get("question_id")
    student_answer = data.get("student_answer", "")
    student_id = data.get("student_id", "student_1")
    subject = data.get("subject", "physics")

    if not question_id:
        return jsonify({"error": "question_id is required."}), 400

    # 1. Evaluate Response in Assessment Engine
    eval_res = engine.evaluate_response(
        question_id=question_id,
        student_answer=student_answer,
        student_id=student_id,
        subject=subject,
    )

    # 2. Find matching session to update Harness
    session = None
    for s in orchestrator._sessions.values():
        if s.lesson_id == lesson_id:
            session = s
            break

    decision = None
    if session:
        # Ensure session is in QUESTION state before evaluating
        if session.current_state == SessionState.TEACH:
            orchestrator.advance_to_question(session.session_id, question_id=question_id)

        is_correct = eval_res.verdict == EvaluationVerdict.CORRECT
        active_misc = None
        if eval_res.misconception:
            active_misc = ActiveMisconception(
                concept=eval_res.misconception.concept,
                misconception_type=eval_res.misconception.misconception_type,
                belief=eval_res.misconception.belief,
                evidence_from_answer=eval_res.misconception.evidence_from_answer,
                confidence=eval_res.misconception.confidence,
                severity=eval_res.misconception.severity,
                prerequisite_gap=eval_res.misconception.prerequisite_gap,
                recommended_intervention=eval_res.misconception.recommended_intervention,
            )

        decision = orchestrator.process_evaluation_result(
            session_id=session.session_id,
            is_correct=is_correct,
            score=eval_res.score,
            confidence=eval_res.confidence,
            misconception=active_misc,
            evaluator_reason=eval_res.evaluator_reason,
            question_id=question_id,
            student_answer=student_answer,
        )

    return jsonify({
        "status": "success",
        "evaluation": eval_res.model_dump(mode="json"),
        "decision": decision.model_dump(mode="json") if decision else None,
        "session_state": session.current_state.value if session else None,
    }), 200


@assessment_blueprint.route("/lessons/<lesson_id>/assessment", methods=["POST"])
def run_final_assessment(lesson_id: str):
    """Executes final assessment and generates learning report."""
    orchestrator = get_orchestrator()
    session = None
    for s in orchestrator._sessions.values():
        if s.lesson_id == lesson_id:
            session = s
            break

    if not session:
        return jsonify({"error": f"Session for lesson '{lesson_id}' not found."}), 404

    data = request.get_json(silent=True) or {}
    final_score = float(data.get("score", 0.9))
    summary = data.get("summary", "Lesson completed with verified mastery.")

    completed_session = orchestrator.complete_assessment_and_report(
        session_id=session.session_id,
        final_score=final_score,
        summary=summary,
    )

    return jsonify({
        "status": "success",
        "session": completed_session.model_dump(mode="json"),
        "final_score": final_score,
        "mastery_summary": completed_session.concept_mastery,
    }), 200


@assessment_blueprint.route("/students/<student_id>/misconceptions", methods=["GET"])
def get_student_misconceptions(student_id: str):
    """Returns active and resolved misconceptions for the student."""
    orchestrator = get_orchestrator()
    active = []
    resolved = []
    for s in orchestrator._sessions.values():
        if s.student_id == student_id:
            active.extend([m.model_dump(mode="json") for m in s.active_misconceptions])
            resolved.extend([m.model_dump(mode="json") for m in s.resolved_misconceptions])

    return jsonify({
        "status": "success",
        "student_id": student_id,
        "active_misconceptions": active,
        "resolved_misconceptions": resolved,
    }), 200


@assessment_blueprint.route("/students/<student_id>/misconceptions/analyze", methods=["POST"])
def analyze_misconceptions(student_id: str):
    """Analyzes student input text directly against the misconception taxonomy."""
    engine = get_assessment_engine()
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    subject = data.get("subject", "physics")
    concept = data.get("concept", "ohms_law")

    dummy_q = engine.generate_checkpoint_question("temp", concept)
    detector = engine.evaluator.detector
    misc = detector.detect_misconception(dummy_q, text, subject=subject)

    return jsonify({
        "status": "success",
        "misconception_detected": misc is not None,
        "misconception": misc.model_dump(mode="json") if misc else None,
    }), 200

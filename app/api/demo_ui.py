"""
Demo UI Blueprint and API Proxy for interactive hackathon demonstration.
"""

from __future__ import annotations
import json
from flask import Blueprint, render_template, jsonify, request

from app.harness.orchestrator import MasterTeachingOrchestrator
from app.harness.session import SessionState, TeachingStrategy, DifficultyLevel, ActiveMisconception
from app.assessment.engine import AssessmentEngine
from app.assessment.models import EvaluationVerdict, MisconceptionRecord
from app.visuals.engine import VisualIntelligenceEngine
from app.media.engine import MultimodalMediaEngine

demo_ui_bp = Blueprint("demo_ui", __name__, template_folder="../templates", static_folder="../static")

_orchestrator = MasterTeachingOrchestrator()
_assessment_engine = AssessmentEngine()
_visual_engine = VisualIntelligenceEngine()
_media_engine = MultimodalMediaEngine()


@demo_ui_bp.route("/", methods=["GET"])
@demo_ui_bp.route("/demo", methods=["GET"])
def render_demo():
    """Renders the single-page interactive AI Teacher demo application."""
    return render_template("demo.html")


@demo_ui_bp.route("/api/v1/demo/run-ohms-law", methods=["POST"])
def execute_ohms_law_flow():
    """
    Executes the full Ohm's Law adaptive teaching cycle and returns
    all step payloads for live visualization in the demo UI.
    """
    data = request.get_json(silent=True) or {}
    language = data.get("language", "en")
    student_id = data.get("student_id", "student_judge_01")
    lesson_id = f"lesson_ohms_{language}"

    # Step 1: Session Init & Lesson Plan
    session = _orchestrator.start_session(
        student_id=student_id,
        lesson_id=lesson_id,
        topic="Ohm's Law",
        subject="physics",
        language=language,
        learner_level="beginner",
        concepts_list=["ohms_law_basics", "voltage_current_resistance_relation"],
        time_minutes=10,
    )

    # Step 2: Segment 1 (Direct Explanation + Circuit Diagram)
    visual_1 = _visual_engine.generate_visual(
        subject="physics",
        concept=session.current_concept,
        teaching_strategy=session.current_strategy,
    )
    segment_1 = _media_engine.generate_teaching_segment(
        lesson_id=lesson_id,
        concept=session.current_concept,
        teaching_strategy=session.current_strategy,
        language=language,
        visual_asset=visual_1,
        session_id=session.session_id,
    )

    # Step 3: Checkpoint Question
    question_1 = _assessment_engine.generate_checkpoint_question(
        lesson_id=lesson_id,
        concept=session.current_concept,
        difficulty=session.current_difficulty,
        language=language,
    )
    _orchestrator.advance_to_question(session.session_id, question_id=question_1.question_id)

    # Step 4: Misconception Submission & Evaluation
    wrong_answer = "If resistance increases, the current will also increase and double because more resistance pushes more electrons."
    eval_1 = _assessment_engine.evaluate_response(
        question_id=question_1.question_id,
        student_answer=wrong_answer,
        student_id=student_id,
        subject="physics",
    )

    # Step 5: Pedagogical Adaptation
    active_misc = None
    if eval_1.misconception:
        active_misc = ActiveMisconception(
            concept=eval_1.misconception.concept,
            misconception_type=eval_1.misconception.misconception_type,
            belief=eval_1.misconception.belief,
            evidence_from_answer=eval_1.misconception.evidence_from_answer,
            confidence=eval_1.misconception.confidence,
            severity=eval_1.misconception.severity,
            recommended_intervention=eval_1.misconception.recommended_intervention,
        )

    decision_1 = _orchestrator.process_evaluation_result(
        session_id=session.session_id,
        is_correct=False,
        score=eval_1.score,
        confidence=eval_1.confidence,
        misconception=active_misc,
        question_id=question_1.question_id,
        student_answer=wrong_answer,
    )

    # Step 6: Segment 2 (Remediated Water Pipe Analogy)
    visual_2 = _visual_engine.generate_visual(
        subject="physics",
        concept=session.current_concept,
        teaching_strategy=session.current_strategy,
        misconception=eval_1.misconception,
    )
    segment_2 = _media_engine.generate_teaching_segment(
        lesson_id=lesson_id,
        concept=session.current_concept,
        teaching_strategy=session.current_strategy,
        language=language,
        misconception=eval_1.misconception,
        visual_asset=visual_2,
        session_id=session.session_id,
    )

    # Step 7: Re-check Question & Correct Answer
    recheck_q = _assessment_engine.generate_recheck_question(
        lesson_id=lesson_id,
        concept=session.current_concept,
        misconception=eval_1.misconception,
        difficulty=session.current_difficulty,
        language=language,
    )
    from app.harness.state_machine import TeachingStateMachine
    from app.harness.session import ActionType
    TeachingStateMachine.transition(session, SessionState.REEXPLAIN, ActionType.REEXPLAIN_CONCEPT)
    _orchestrator.advance_to_question(session.session_id, question_id=recheck_q.question_id)

    correct_answer = "A"  # Option A: The current decreases
    eval_2 = _assessment_engine.evaluate_response(
        question_id=recheck_q.question_id,
        student_answer=correct_answer,
        student_id=student_id,
        subject="physics",
    )

    decision_2 = _orchestrator.process_evaluation_result(
        session_id=session.session_id,
        is_correct=True,
        score=eval_2.score,
        confidence=eval_2.confidence,
        question_id=recheck_q.question_id,
        student_answer="Option A: The current decreases",
    )

    # Step 8: Final Assessment & Report
    completed_session = _orchestrator.complete_assessment_and_report(
        session_id=session.session_id,
        final_score=0.95,
        summary="Learner successfully resolved inverse-relationship misconception in Ohm's Law via hydraulic analogy.",
    )

    # Step 9: AI Teaching Trace
    traces = [t.model_dump() for t in _orchestrator.trace_logger.get_session_traces(session.session_id)]
    trace_summary = _orchestrator.trace_logger.render_session_trace_summary(session.session_id)

    return jsonify({
        "success": True,
        "session_id": session.session_id,
        "step_1_plan": {
            "topic": "Ohm's Law",
            "concepts": session.concepts_list,
            "duration_minutes": 10,
            "difficulty": session.current_difficulty.value,
        },
        "step_2_segment_1": {
            "duration": segment_1.duration_seconds,
            "script": segment_1.script.spoken_script,
            "audio_track": segment_1.audio.content_uri if segment_1.audio else None,
            "avatar_track": segment_1.avatar.content_uri if segment_1.avatar else None,
            "visual_svg": visual_1.content,
            "visual_type": visual_1.visual_type.value,
            "captions": segment_1.captions.vtt_content if segment_1.captions else "",
        },
        "step_3_question_1": {
            "question_id": question_1.question_id,
            "prompt": question_1.prompt,
            "options": [o.model_dump() for o in question_1.options] if question_1.options else [],
        },
        "step_4_misconception_evaluation": {
            "submitted_answer": wrong_answer,
            "verdict": eval_1.verdict.value,
            "score": eval_1.score,
            "confidence": eval_1.confidence,
            "misconception": eval_1.misconception.model_dump() if eval_1.misconception else None,
        },
        "step_5_adaptive_decision": {
            "action": decision_1.action.value,
            "previous_strategy": decision_1.metadata.get("previous_strategy"),
            "new_strategy": decision_1.teaching_strategy.value,
            "visual_strategy": decision_1.visual_strategy,
        },
        "step_6_segment_2": {
            "duration": segment_2.duration_seconds,
            "script": segment_2.script.spoken_script,
            "audio_track": segment_2.audio.content_uri if segment_2.audio else None,
            "avatar_track": segment_2.avatar.content_uri if segment_2.avatar else None,
            "visual_svg": visual_2.content,
            "visual_type": visual_2.visual_type.value,
            "captions": segment_2.captions.vtt_content if segment_2.captions else "",
        },
        "step_7_recheck": {
            "question_id": recheck_q.question_id,
            "prompt": recheck_q.prompt,
            "options": [o.model_dump() for o in recheck_q.options] if recheck_q.options else [],
            "submitted_answer": "Option A: The current decreases",
            "verdict": eval_2.verdict.value,
            "score": eval_2.score,
        },
        "step_8_final_report": {
            "final_score": 0.95,
            "concept_mastery": completed_session.concept_mastery,
            "resolved_misconceptions": [m.misconception_type for m in completed_session.resolved_misconceptions],
            "strengths": ["Understands voltage as potential difference", "Mastered inverse relationship in Ohm's Law (I = V/R)"],
            "recommended_topics": ["Joule's Heating Law", "Resistors in Series and Parallel"],
        },
        "step_9_traces": traces,
        "trace_summary_ascii": trace_summary,
    })

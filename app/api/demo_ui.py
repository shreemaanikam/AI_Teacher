"""
Demo UI Blueprint and API Proxy for interactive hackathon demonstration.
"""

from __future__ import annotations
import os
import json
from flask import Blueprint, render_template, jsonify, request, send_from_directory, abort

from app.harness.orchestrator import MasterTeachingOrchestrator
from app.harness.session import SessionState, TeachingStrategy, DifficultyLevel, ActiveMisconception
from app.assessment.engine import AssessmentEngine
from app.assessment.models import EvaluationVerdict, MisconceptionRecord
from app.visuals.engine import VisualIntelligenceEngine
from app.media.engine import MultimodalMediaEngine

demo_ui_bp = Blueprint("demo_ui", __name__, template_folder="../templates", static_folder="../static")

FRONTEND_DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))
ASSETS_DIR = os.path.join(FRONTEND_DIST_DIR, "assets")

_orchestrator = MasterTeachingOrchestrator()
_assessment_engine = AssessmentEngine()
_visual_engine = VisualIntelligenceEngine()
_media_engine = MultimodalMediaEngine()


@demo_ui_bp.route("/assets/<path:filename>", methods=["GET"])
def serve_frontend_assets(filename: str):
    """Serves compiled frontend static assets (JS, CSS, SVGs, etc.)."""
    if os.path.exists(os.path.join(ASSETS_DIR, filename)):
        return send_from_directory(ASSETS_DIR, filename)
    # Fallback to app/static/assets if present
    static_assets = os.path.abspath(os.path.join(os.path.dirname(__file__), "../static/assets"))
    if os.path.exists(os.path.join(static_assets, filename)):
        return send_from_directory(static_assets, filename)
    abort(404)


@demo_ui_bp.route("/teacher/<path:filename>", methods=["GET"])
def serve_root_teacher(filename: str):
    """Serves teacher media assets from frontend dist or static/teacher."""
    dist_teacher = os.path.join(FRONTEND_DIST_DIR, "teacher")
    if os.path.exists(os.path.join(dist_teacher, filename)):
        return send_from_directory(dist_teacher, filename)
    static_teacher = os.path.abspath(os.path.join(os.path.dirname(__file__), "../static/teacher"))
    if os.path.exists(os.path.join(static_teacher, filename)):
        return send_from_directory(static_teacher, filename)
    data_teacher = os.path.abspath("data/media/teacher")
    if os.path.exists(os.path.join(data_teacher, filename)):
        return send_from_directory(data_teacher, filename)
    abort(404)


@demo_ui_bp.route("/robots.txt", methods=["GET"])
def serve_robots_txt():
    """Serves robots.txt from the compiled frontend distribution."""
    if os.path.exists(os.path.join(FRONTEND_DIST_DIR, "robots.txt")):
        return send_from_directory(FRONTEND_DIST_DIR, "robots.txt")
    return "User-agent: *\nDisallow: /", 200, {"Content-Type": "text/plain"}


@demo_ui_bp.route("/", methods=["GET"])
@demo_ui_bp.route("/demo", methods=["GET"])
@demo_ui_bp.route("/app", methods=["GET"])
def render_demo():
    """Renders the official single-page interactive AI Teacher prototype frontend."""
    if os.path.exists(os.path.join(FRONTEND_DIST_DIR, "index.html")):
        return send_from_directory(FRONTEND_DIST_DIR, "index.html")
    return render_template("demo.html")


# Register client-side SPA routes
SPA_ROUTES = [
    "/landing",
    "/onboarding",
    "/dashboard",
    "/create-lesson",
    "/document-processing",
    "/lesson-plan",
    "/lesson-player",
    "/learning-path",
    "/analytics",
    "/profile",
    "/documents",
]

for _spa_route in SPA_ROUTES:
    demo_ui_bp.add_url_rule(_spa_route, endpoint=f"spa_{_spa_route.strip('/')}", view_func=render_demo, methods=["GET"])



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

    # Step 9: Module 10 Analytics & Recommendations
    from app.analytics.recommendations import RevisionRecommendationEngine
    from app.analytics.learning_path import LearningPathEngine
    recs = RevisionRecommendationEngine.generate_recommendations(student_id)
    lpath = LearningPathEngine.compute_learning_path(student_id, subject="physics")

    # Step 10: AI Teaching Trace
    traces = [t.model_dump() for t in _orchestrator.trace_logger.get_session_traces(session.session_id)]
    trace_summary = _orchestrator.trace_logger.render_session_trace_summary(session.session_id)

    return jsonify({
        "success": True,
        "session_id": session.session_id,
        "step_1_plan": {
            "topic": "Ohm's Law: Voltage, Current, and Resistance",
            "concepts": session.concepts_list,
            "duration_minutes": 10,
            "difficulty": session.current_difficulty.value,
            "language": language,
        },
        "step_2_segment_1": {
            "duration": segment_1.duration_seconds,
            "script": segment_1.script.spoken_script,
            "audio_track": segment_1.audio.content_uri if segment_1.audio else None,
            "audio_provider": segment_1.audio.provider_used if segment_1.audio else "procedural_wav",
            "avatar_track": segment_1.avatar.content_uri if segment_1.avatar else None,
            "avatar_provider": segment_1.avatar.provider_used if segment_1.avatar else "procedural_svg",
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
            "previous_strategy": decision_1.metadata.get("previous_strategy", "DIRECT_EXPLANATION"),
            "new_strategy": decision_1.teaching_strategy.value,
            "visual_strategy": decision_1.visual_strategy,
        },
        "step_6_segment_2": {
            "duration": segment_2.duration_seconds,
            "script": segment_2.script.spoken_script,
            "audio_track": segment_2.audio.content_uri if segment_2.audio else None,
            "audio_provider": segment_2.audio.provider_used if segment_2.audio else "procedural_wav",
            "avatar_track": segment_2.avatar.content_uri if segment_2.avatar else None,
            "avatar_provider": segment_2.avatar.provider_used if segment_2.avatar else "procedural_svg",
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
            "weak_concepts": [],
            "recommendations": [r.model_dump() for r in recs],
            "learning_path": lpath.model_dump(),
        },
        "step_9_traces": traces,
        "trace_summary_ascii": trace_summary,
    })


def _get_avatar_svg(avatar_asset):
    if not avatar_asset or not avatar_asset.content_uri:
        return None
    if avatar_asset.content_uri.strip().startswith("<svg"):
        return avatar_asset.content_uri
    if os.path.exists(avatar_asset.content_uri):
        try:
            with open(avatar_asset.content_uri, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass
    return None


@demo_ui_bp.route("/api/v1/demo/run-topic", methods=["POST"])
def execute_topic_flow():
    """
    Executes a complete adaptive teaching flow for ANY college topic or uploaded document,
    generating dynamic, step-by-step whiteboard visuals and synchronized pedagogy.
    """
    import uuid
    data = request.get_json(silent=True) or {}
    topic = data.get("topic", "Binary Search")
    subject = data.get("subject", "computer_science")
    language = data.get("language", "en")
    document_id = data.get("document_id")
    student_id = data.get("student_id", "student_college_01")
    lesson_id = f"lesson_{subject}_{uuid.uuid4().hex[:6]}"

    # Step 1: Session Init & Lesson Plan
    session = _orchestrator.start_session(
        student_id=student_id,
        lesson_id=lesson_id,
        topic=topic,
        subject=subject,
        language=language,
        learner_level="beginner",
        concepts_list=[topic.lower().replace(" ", "_")],
        time_minutes=10,
    )

    # Step 2: Segment 1 with Dynamic Whiteboard
    visual_plan_1 = _visual_engine.plan_visual_teaching(
        concept=topic,
        subject_hint=subject,
        teaching_strategy=session.current_strategy,
        document_id=document_id,
        language=language,
    )
    visual_1 = _visual_engine.render_teaching_visual(visual_plan_1, step_index=0)

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

    # Step 4: Misconception Evaluation
    sample_wrong_answers = {
        "computer_science": "Binary search checks every element from index 0 to N sequentially.",
        "mathematics": "In a quadratic equation, we can just take the square root of each term separately.",
        "engineering": "Increasing circuit resistance allows twice as much electrical current to flow.",
        "physics": "Heavier objects fall significantly faster in a vacuum than light objects.",
    }
    wrong_answer = sample_wrong_answers.get(subject, f"Incorrect initial hypothesis regarding {topic}.")

    eval_1 = _assessment_engine.evaluate_response(
        question_id=question_1.question_id,
        student_answer=wrong_answer,
        student_id=student_id,
        subject=subject,
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

    # Step 6: Segment 2 (Remediated Visual with Different Strategy)
    visual_plan_2 = _visual_engine.plan_visual_teaching(
        concept=topic,
        subject_hint=subject,
        teaching_strategy=session.current_strategy,
        misconception=eval_1.misconception,
        document_id=document_id,
        language=language,
    )
    visual_2 = _visual_engine.render_teaching_visual(visual_plan_2, step_index=0)

    segment_2 = _media_engine.generate_teaching_segment(
        lesson_id=lesson_id,
        concept=session.current_concept,
        teaching_strategy=session.current_strategy,
        language=language,
        misconception=eval_1.misconception,
        visual_asset=visual_2,
        session_id=session.session_id,
    )

    # Step 7: Recheck & Final Report
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

    eval_2 = _assessment_engine.evaluate_response(
        question_id=recheck_q.question_id,
        student_answer="Correct principle successfully demonstrated",
        student_id=student_id,
        subject=subject,
    )

    decision_2 = _orchestrator.process_evaluation_result(
        session_id=session.session_id,
        is_correct=True,
        score=0.92,
        confidence=0.95,
        question_id=recheck_q.question_id,
        student_answer="Correct principle applied",
    )

    completed_session = _orchestrator.complete_assessment_and_report(
        session_id=session.session_id,
        final_score=0.92,
        summary=f"Learner mastered {topic} across progressive whiteboard visualizations and formative checkpoints.",
    )

    traces = [t.model_dump() for t in _orchestrator.trace_logger.get_session_traces(session.session_id)]
    trace_summary = _orchestrator.trace_logger.render_session_trace_summary(session.session_id)

    return jsonify({
        "success": True,
        "session_id": session.session_id,
        "topic": topic,
        "subject": subject,
        "step_1_plan": {
            "topic": topic,
            "subject": subject,
            "concepts": session.concepts_list,
            "duration_minutes": 10,
            "difficulty": session.current_difficulty.value,
            "language": language,
            "visual_plan_id": visual_plan_1.visual_id,
        },
        "step_2_segment_1": {
            "duration": segment_1.duration_seconds,
            "script": segment_1.script.spoken_script,
            "audio_track": segment_1.audio.content_uri if segment_1.audio else None,
            "audio_provider": segment_1.audio.provider_used if segment_1.audio else "procedural_wav",
            "avatar_track": segment_1.avatar.content_uri if segment_1.avatar else None,
            "avatar_provider": segment_1.avatar.provider_used if segment_1.avatar else "human_avatar",
            "avatar_svg": _get_avatar_svg(segment_1.avatar),
            "teacher_profile": segment_1.avatar.teacher_profile.model_dump() if (segment_1.avatar and segment_1.avatar.teacher_profile) else None,
            "presentation_state": segment_1.avatar.presentation_state.model_dump() if (segment_1.avatar and segment_1.avatar.presentation_state) else None,
            "visual_svg": visual_1.content,
            "visual_id": visual_1.asset_id,
            "visual_type": visual_1.visual_type.value,
            "steps_count": visual_1.steps_count,
            "active_step": visual_1.active_step,
            "captions": segment_1.captions.vtt_content if segment_1.captions else "",
            "source_trace": _visual_engine.get_source_trace(visual_1.asset_id),
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
            "previous_strategy": decision_1.metadata.get("previous_strategy", "DIRECT_EXPLANATION"),
            "new_strategy": decision_1.teaching_strategy.value,
            "original_visual_id": visual_plan_1.visual_id,
            "remediation_visual_id": visual_plan_2.visual_id,
            "visual_strategy_changed": visual_plan_1.visual_id != visual_plan_2.visual_id,
        },
        "step_6_segment_2": {
            "duration": segment_2.duration_seconds,
            "script": segment_2.script.spoken_script,
            "audio_track": segment_2.audio.content_uri if segment_2.audio else None,
            "audio_provider": segment_2.audio.provider_used if segment_2.audio else "procedural_wav",
            "avatar_track": segment_2.avatar.content_uri if segment_2.avatar else None,
            "avatar_provider": segment_2.avatar.provider_used if segment_2.avatar else "human_avatar",
            "avatar_svg": _get_avatar_svg(segment_2.avatar),
            "teacher_profile": segment_2.avatar.teacher_profile.model_dump() if (segment_2.avatar and segment_2.avatar.teacher_profile) else None,
            "presentation_state": segment_2.avatar.presentation_state.model_dump() if (segment_2.avatar and segment_2.avatar.presentation_state) else None,
            "visual_svg": visual_2.content,
            "visual_id": visual_2.asset_id,
            "visual_type": visual_2.visual_type.value,
            "steps_count": visual_2.steps_count,
            "active_step": visual_2.active_step,
            "captions": segment_2.captions.vtt_content if segment_2.captions else "",
        },
        "step_7_recheck": {
            "question_id": recheck_q.question_id,
            "prompt": recheck_q.prompt,
            "options": [o.model_dump() for o in recheck_q.options] if recheck_q.options else [],
            "submitted_answer": "Correct principle applied",
            "verdict": "CORRECT",
            "score": 0.92,
        },
        "step_8_final_report": {
            "final_score": 0.92,
            "concept_mastery": completed_session.concept_mastery,
            "resolved_misconceptions": [m.misconception_type for m in completed_session.resolved_misconceptions],
            "strengths": [f"Mastered core principles of {topic}"],
            "weak_concepts": [],
        },
        "step_9_traces": traces,
        "trace_summary_ascii": trace_summary,
    })


@demo_ui_bp.route("/api/v1/demo/run-ml-course", methods=["POST"])
def execute_ml_course_flow():
    """
    Executes the full Machine Learning college course student journey (AD5305 / CS4403).
    Grounded in actual 5-unit college materials from Chennai Institute of Technology.
    """
    from app.ml_course.student_journey import MLStudentJourneyEngine
    from app.ml_course.knowledge import CourseKnowledgeBase

    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id", "student_aditya_cit")
    concept_id = data.get("concept_id", "ml.u3.backpropagation")
    teacher_id = data.get("teacher_id", "prof_apurva")
    language = data.get("language", "en")

    engine = MLStudentJourneyEngine.get_instance()
    kb = CourseKnowledgeBase.get_instance()

    # Step 1: Initialize Journey & Profile
    state = engine.initialize_journey(student_id=student_id, student_name="Aditya Rao (CIT AI & DS)")

    # Step 2: Select Concept & Deliver Verified Lesson
    experience = engine.select_concept(
        state=state,
        concept_id=concept_id,
        teacher_id=teacher_id,
        language=language,
    )

    # Step 3: Diagnostic Question
    q = engine.generate_concept_question(state)

    # Step 4: Misconception Simulation & Adaptation
    res_wrong = engine.process_student_response(
        state=state,
        student_answer="Backpropagation randomly guesses weights until loss reaches zero.",
    )

    # Step 5: Retest & Mastery
    res_correct = engine.process_student_response(
        state=state,
        student_answer="Backpropagation computes the loss gradient with respect to weights using multivariable chain rule to update weights.",
    )

    # Step 6: 60-Minute Exam Session Plan
    exam_plan = engine.create_exam_plan(state, duration_minutes=60)

    return jsonify({
        "success": True,
        "course_code": "AD5305 / CS4403",
        "course_name": "Machine Learning",
        "institution": "Chennai Institute of Technology (Autonomous)",
        "unit": experience.unit_number,
        "concept_id": experience.concept_id,
        "concept_name": experience.concept_name,
        "teacher": {
            "name": experience.teacher_name,
            "profile_id": teacher_id,
            "cues_count": len(experience.presentation_cues),
        },
        "lesson": {
            "approved_script": experience.approved_script.approved_text,
            "is_verified": experience.approved_script.is_approved,
            "claims_count": len(experience.approved_script.claims),
            "sources": [s.model_dump() for s in experience.source_refs],
        },
        "visual_canvas": {
            "title": experience.visual_payload.title,
            "visual_type": experience.visual_payload.visual_type,
            "svg_html": experience.visual_payload.html_canvas_component,
        },
        "question": {
            "question_id": q.question_id,
            "type": q.question_type,
            "text": q.question_text,
            "expected": q.expected_answer,
        },
        "misconception_remediation": {
            "diagnosed": res_wrong["remediation"].diagnosed_misconception if res_wrong.get("remediation") else None,
            "contrastive_explanation": res_wrong["remediation"].contrastive_explanation if res_wrong.get("remediation") else None,
            "remediation_visual": res_wrong["remediation"].remediation_visual if res_wrong.get("remediation") else None,
        },
        "mastery_result": {
            "verdict": res_correct["evaluation"].evaluation_status,
            "score": res_correct["evaluation"].score,
            "concept_mastery": state.concept_mastery.get(concept_id, 0.95),
        },
        "exam_plan": {
            "duration_minutes": exam_plan.duration_minutes,
            "total_marks": exam_plan.total_marks,
            "questions_count": len(exam_plan.questions),
        },
        "steps_completed": state.steps_completed,
    })


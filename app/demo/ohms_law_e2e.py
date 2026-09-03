"""
End-to-End Demo: Closed-Loop Adaptive Cognitive AI Teacher (Ohm's Law).
Demonstrates the full closed-loop teaching flow:
Understand -> Plan -> Teach -> Question -> Misconception -> Adapt -> Re-explain -> Re-question -> Mastery -> Assessment -> Report.
"""

from __future__ import annotations
import json
import logging
from typing import Dict, Any

from app.harness.orchestrator import MasterTeachingOrchestrator
from app.harness.session import SessionState, TeachingStrategy, DifficultyLevel
from app.assessment.engine import AssessmentEngine
from app.assessment.models import EvaluationVerdict
from app.visuals.engine import VisualIntelligenceEngine
from app.media.engine import MultimodalMediaEngine

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("OhmsLawDemo")


def run_ohms_law_adaptive_demo(language: str = "en") -> Dict[str, Any]:
    """
    Executes the complete Ohm's Law adaptive teaching demonstration.
    """
    print("=" * 70)
    print("  AI TEACHER — ADAPTIVE COGNITIVE TEACHING DEMO (OHM'S LAW)")
    print("=" * 70)

    orchestrator = MasterTeachingOrchestrator()
    assessment_engine = AssessmentEngine()
    visual_engine = VisualIntelligenceEngine()
    media_engine = MultimodalMediaEngine()

    student_id = "student_apurva_01"
    lesson_id = "lesson_physics_ohms_law"
    topic = "Ohm's Law"
    subject = "physics"

    # -------------------------------------------------------------
    # STEP 1: Understand Learner & Initialize Session (START -> TEACH)
    # -------------------------------------------------------------
    print("\n[STEP 1] Initializing Teaching Session...")
    session = orchestrator.start_session(
        student_id=student_id,
        lesson_id=lesson_id,
        topic=topic,
        subject=subject,
        language=language,
        learner_level="beginner",
        concepts_list=["ohms_law_basics", "voltage_current_resistance_relation"],
        time_minutes=10,
    )
    print(f"✓ Session Started: {session.session_id}")
    print(f"✓ State: {session.current_state.value} | Strategy: {session.current_strategy.value}")

    # -------------------------------------------------------------
    # STEP 2: Deliver Initial Teaching Segment (Direct Explanation)
    # -------------------------------------------------------------
    print("\n[STEP 2] Generating Initial Teaching Segment (Direct Explanation + Circuit Diagram)...")
    visual_1 = visual_engine.generate_visual(
        subject=subject,
        concept=session.current_concept,
        teaching_strategy=session.current_strategy,
    )
    segment_1 = media_engine.generate_teaching_segment(
        lesson_id=lesson_id,
        concept=session.current_concept,
        teaching_strategy=session.current_strategy,
        language=language,
        visual_asset=visual_1,
        session_id=session.session_id,
    )
    print(f"✓ Segment 1 Created (Duration: {segment_1.duration_seconds}s)")
    print(f"  Teacher Script: \"{segment_1.script.spoken_script[:90]}...\"")
    print(f"  Visual Asset: {visual_1.visual_type.value} ({visual_1.format.value.upper()})")

    # -------------------------------------------------------------
    # STEP 3: Ask Checkpoint Question (TEACH -> QUESTION)
    # -------------------------------------------------------------
    print("\n[STEP 3] Posing Checkpoint Question to Learner...")
    question_1 = assessment_engine.generate_checkpoint_question(
        lesson_id=lesson_id,
        concept=session.current_concept,
        difficulty=session.current_difficulty,
        language=language,
    )
    orchestrator.advance_to_question(session.session_id, question_id=question_1.question_id)
    print(f"✓ Teacher asks: \"{question_1.prompt}\"")

    # -------------------------------------------------------------
    # STEP 4: Student Submits Common Misconception Answer
    # -------------------------------------------------------------
    print("\n[STEP 4] Student Answers with a Common Misconception...")
    student_ans_1 = "If resistance increases, the current will also increase and double because more resistance pushes more electrons."
    print(f"  Student Response: \"{student_ans_1}\"")

    # -------------------------------------------------------------
    # STEP 5: Evaluate Answer & Diagnose Misconception
    # -------------------------------------------------------------
    print("\n[STEP 5] Diagnosing Cognitive Misconception...")
    eval_1 = assessment_engine.evaluate_response(
        question_id=question_1.question_id,
        student_answer=student_ans_1,
        student_id=student_id,
        subject=subject,
    )
    print(f"✓ Evaluation Verdict: {eval_1.verdict.value} (Score: {eval_1.score})")
    if eval_1.misconception:
        print(f"  Diagnosed Misconception: {eval_1.misconception.misconception_type}")
        print(f"  Underlying Belief: \"{eval_1.misconception.belief}\"")
        print(f"  Confidence: {eval_1.misconception.confidence:.2f}")

    # -------------------------------------------------------------
    # STEP 6: Teaching Harness Policy Adaptation (EVALUATE -> ADAPT)
    # -------------------------------------------------------------
    print("\n[STEP 6] Triggering Pedagogical Adaptation in Harness...")
    active_misc = None
    if eval_1.misconception:
        from app.harness.session import ActiveMisconception
        active_misc = ActiveMisconception(
            concept=eval_1.misconception.concept,
            misconception_type=eval_1.misconception.misconception_type,
            belief=eval_1.misconception.belief,
            evidence_from_answer=eval_1.misconception.evidence_from_answer,
            confidence=eval_1.misconception.confidence,
            severity=eval_1.misconception.severity,
            recommended_intervention=eval_1.misconception.recommended_intervention,
        )

    decision_1 = orchestrator.process_evaluation_result(
        session_id=session.session_id,
        is_correct=False,
        score=eval_1.score,
        confidence=eval_1.confidence,
        misconception=active_misc,
        question_id=question_1.question_id,
        student_answer=student_ans_1,
    )
    print(f"✓ Adaptive Decision: {decision_1.action.value}")
    print(f"  Strategy Switch: {decision_1.metadata.get('previous_strategy')} -> {decision_1.teaching_strategy.value}")
    print(f"  Visual Strategy Adapted to: {decision_1.visual_strategy}")

    # -------------------------------------------------------------
    # STEP 7: Generate Remediated Segment (Water-Pipe Analogy)
    # -------------------------------------------------------------
    print("\n[STEP 7] Generating Remediated Multimodal Lesson Segment (Water Pipe Analogy)...")
    visual_2 = visual_engine.generate_visual(
        subject=subject,
        concept=session.current_concept,
        teaching_strategy=session.current_strategy,
        misconception=eval_1.misconception,
    )
    segment_2 = media_engine.generate_teaching_segment(
        lesson_id=lesson_id,
        concept=session.current_concept,
        teaching_strategy=session.current_strategy,
        language=language,
        misconception=eval_1.misconception,
        visual_asset=visual_2,
        session_id=session.session_id,
    )
    from app.harness.state_machine import TeachingStateMachine
    from app.harness.session import ActionType
    TeachingStateMachine.transition(session, SessionState.REEXPLAIN, ActionType.REEXPLAIN_CONCEPT)
    orchestrator.save_session(session)

    print(f"✓ Segment 2 Created (Duration: {segment_2.duration_seconds}s)")
    print(f"  Remediated Script: \"{segment_2.script.spoken_script[:120]}...\"")
    print(f"  Adapted Visual: {visual_2.visual_type.value} ({visual_2.format.value.upper()})")

    # -------------------------------------------------------------
    # STEP 8: Ask Targeted Re-check Question (ADAPT -> REQUESTION)
    # -------------------------------------------------------------
    print("\n[STEP 8] Asking Targeted Re-Check Question...")
    recheck_q = assessment_engine.generate_recheck_question(
        lesson_id=lesson_id,
        concept=session.current_concept,
        misconception=eval_1.misconception,
        difficulty=session.current_difficulty,
        language=language,
    )
    orchestrator.advance_to_question(session.session_id, question_id=recheck_q.question_id)
    print(f"✓ Re-check Question: \"{recheck_q.prompt}\"")

    # -------------------------------------------------------------
    # STEP 9: Student Answers Correctly After Analogy
    # -------------------------------------------------------------
    print("\n[STEP 9] Student Re-Attempts After Water Pipe Explanation...")
    student_ans_2 = "A"  # Option A: The current decreases
    print(f"  Student Selects Option: {student_ans_2} ('The current decreases')")

    eval_2 = assessment_engine.evaluate_response(
        question_id=recheck_q.question_id,
        student_answer=student_ans_2,
        student_id=student_id,
        subject=subject,
    )
    print(f"✓ Re-check Verdict: {eval_2.verdict.value} (Score: {eval_2.score})")

    decision_2 = orchestrator.process_evaluation_result(
        session_id=session.session_id,
        is_correct=True,
        score=eval_2.score,
        confidence=eval_2.confidence,
        question_id=recheck_q.question_id,
        student_answer="Option A: The current decreases",
    )
    print(f"✓ Harness Advances: {decision_2.action.value}")
    print(f"✓ Concept Mastery Updated: {session.concept_mastery}")

    # -------------------------------------------------------------
    # STEP 10: Final Assessment & Comprehensive Learning Report
    # -------------------------------------------------------------
    print("\n[STEP 10] Final Assessment & Learning Report...")
    completed_session = orchestrator.complete_assessment_and_report(
        session_id=session.session_id,
        final_score=0.95,
        summary="Learner successfully resolved inverse-relationship misconception in Ohm's Law via hydraulic analogy.",
    )
    print(f"✓ Final Session State: {completed_session.current_state.value}")
    print(f"✓ Final Mastery Scores: {completed_session.concept_mastery}")
    print(f"✓ Resolved Misconceptions: {[m.misconception_type for m in completed_session.resolved_misconceptions]}")

    # -------------------------------------------------------------
    # STEP 11: Display AI Teaching Trace
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print("  AI TEACHING TRACE (OBSERVABILITY LOG)")
    print("=" * 70)
    trace_text = orchestrator.trace_logger.render_session_trace_summary(session.session_id)
    print(trace_text)

    return {
        "session_id": session.session_id,
        "completed_state": completed_session.current_state.value,
        "initial_strategy": TeachingStrategy.DIRECT_EXPLANATION.value,
        "adapted_strategy": TeachingStrategy.SIMPLE_ANALOGY.value,
        "misconception_resolved": True,
        "final_mastery": completed_session.concept_mastery,
    }


if __name__ == "__main__":
    run_ohms_law_adaptive_demo()

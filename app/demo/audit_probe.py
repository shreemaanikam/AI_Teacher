"""
Live Real-Implementation Verification Script for AI Teacher Audit.
Executes unmocked runtime calls across Modules 5, 7, 8, and 9 and prints exact data structures.
"""

from __future__ import annotations
import os
import json
import time
from typing import Dict, Any

from app.harness.session import (
    SessionState,
    TeachingStrategy,
    ActionType,
    DifficultyLevel,
    TeachingSessionState,
    TeachingDecision,
    ActiveMisconception,
)
from app.harness.state_machine import TeachingStateMachine
from app.harness.policies import TeachingPolicyEngine, PolicyConfig
from app.harness.orchestrator import MasterTeachingOrchestrator
from app.assessment.engine import AssessmentEngine
from app.assessment.models import (
    Question,
    QuestionType,
    AnswerRubric,
    MisconceptionTarget,
    EvaluationVerdict,
    MisconceptionRecord,
)
from app.visuals.engine import VisualIntelligenceEngine
from app.visuals.models import VisualSpec, VisualType, RenderFormat
from app.media.engine import MultimodalMediaEngine
from app.media.models import MediaStatus


def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def verify_module_5_real_state_machine():
    print_header("VERIFICATION 2: REAL MODULE 5 STATE MACHINE EXECUTION")
    orchestrator = MasterTeachingOrchestrator()
    session = orchestrator.start_session(
        student_id="live_student_101",
        lesson_id="lesson_ohms_live",
        topic="Ohm's Law",
        subject="physics",
        concepts_list=["ohms_law_core"],
        time_minutes=10,
    )
    print(f"1. START -> UNDERSTAND -> PLAN -> TEACH | Current State: {session.current_state.value} (Ver: {session.version})")

    # TEACH -> QUESTION
    orchestrator.advance_to_question(session.session_id, question_id="q_live_1")
    print(f"2. TEACH -> QUESTION | Current State: {session.current_state.value} (Ver: {session.version})")

    # QUESTION -> EVALUATE -> ADAPT (via misconception submission)
    misc = ActiveMisconception(
        concept="ohms_law_core",
        misconception_type="inverse_relationship_confusion",
        belief="higher resistance increases current",
        evidence_from_answer="current will increase",
        confidence=0.92,
    )
    dec_adapt = orchestrator.process_evaluation_result(
        session_id=session.session_id,
        is_correct=False,
        score=0.1,
        confidence=0.92,
        misconception=misc,
        question_id="q_live_1",
        student_answer="current will increase",
    )
    print(f"3. QUESTION -> EVALUATE -> ADAPT | Current State: {session.current_state.value} | Action: {dec_adapt.action.value} | Strategy: {session.current_strategy.value}")

    # ADAPT -> REEXPLAIN
    TeachingStateMachine.transition(session, SessionState.REEXPLAIN, ActionType.REEXPLAIN_CONCEPT)
    print(f"4. ADAPT -> REEXPLAIN | Current State: {session.current_state.value} (Ver: {session.version})")

    # REEXPLAIN -> REQUESTION
    orchestrator.advance_to_question(session.session_id, question_id="q_live_recheck")
    print(f"5. REEXPLAIN -> REQUESTION | Current State: {session.current_state.value} (Ver: {session.version})")

    # REQUESTION -> EVALUATE -> TEACH/ADVANCE (via correct submission)
    dec_correct = orchestrator.process_evaluation_result(
        session_id=session.session_id,
        is_correct=True,
        score=1.0,
        confidence=0.95,
        question_id="q_live_recheck",
        student_answer="current decreases",
    )
    print(f"6. REQUESTION -> EVALUATE -> TEACH | Current State: {session.current_state.value} | Action: {dec_correct.action.value} | Mastery: {session.concept_mastery}")

    # TEACH -> ASSESSMENT -> REPORT -> COMPLETE
    comp_session = orchestrator.complete_assessment_and_report(session.session_id, final_score=0.95)
    print(f"7. ASSESSMENT -> REPORT -> COMPLETE | Current State: {comp_session.current_state.value} | Completed At: {comp_session.completed_at}")


def verify_module_7_exact_evaluation():
    print_header("VERIFICATION 3: REAL MODULE 7 ANSWER EVALUATION & MISCONCEPTION")
    assessment_engine = AssessmentEngine()

    raw_answer = "If resistance increases, current also increases because more resistance pushes more electrons."
    question = assessment_engine.generate_checkpoint_question("live_lesson", "ohms_law")

    norm_answer = assessment_engine.evaluator.normalize_text(raw_answer)
    eval_res = assessment_engine.evaluate_response(
        question_id=question.question_id,
        student_answer=raw_answer,
        student_id="live_student_101",
        subject="physics",
    )

    intervention = None
    if eval_res.misconception:
        intervention = assessment_engine.create_intervention(
            eval_res.misconception,
            current_strategy=TeachingStrategy.DIRECT_EXPLANATION,
        )

    output = {
        "raw_answer": raw_answer,
        "normalized_answer": norm_answer,
        "question_prompt": question.prompt,
        "expected_answer": question.expected_answer,
        "verdict": eval_res.verdict.value,
        "score": eval_res.score,
        "confidence": eval_res.confidence,
        "misconception_type": eval_res.misconception.misconception_type if eval_res.misconception else None,
        "misconception_belief": eval_res.misconception.belief if eval_res.misconception else None,
        "misconception_severity": eval_res.misconception.severity if eval_res.misconception else None,
        "recommended_strategy": eval_res.misconception.recommended_strategy.value if eval_res.misconception else None,
        "intervention_plan": {
            "previous_strategy": intervention.previous_strategy.value,
            "new_strategy": intervention.new_strategy.value,
            "reason_for_change": intervention.reason_for_change,
            "analogy_prompt": intervention.analogy_prompt,
            "visual_type": intervention.visual_type,
            "steps": intervention.steps,
        } if intervention else None,
    }
    print(json.dumps(output, indent=2))


def verify_misconception_reusability_across_subjects():
    print_header("VERIFICATION 4: MISCONCEPTION REUSABILITY ACROSS OTHER SUBJECTS")
    assessment_engine = AssessmentEngine()

    # 1. Physics: Force and Motion (Newton's 1st Law misconception)
    q_force = Question(
        question_id="q_force_test",
        lesson_id="l_force",
        concept="force_motion",
        prompt="Why does a hockey puck keep moving across smooth ice after being hit?",
        expected_answer="Due to inertia; no net force is required to maintain constant velocity.",
        rubric=AnswerRubric(key_terms=["inertia", "constant velocity", "no net force"]),
        misconception_targets=[
            MisconceptionTarget(
                misconception_type="force_velocity_confusion",
                trigger_patterns=["needs force to move", "force is required to keep moving", "constant force"],
                explanation="Student believes an object in motion must continuously have a net force acting on it.",
                remediation_strategy=TeachingStrategy.CONTRASTIVE_EXPLANATION,
            )
        ],
    )
    assessment_engine.store_question(q_force)

    student_force_ans = "The puck keeps moving because there is a force required to keep moving it forward."
    eval_force = assessment_engine.evaluate_response(
        question_id="q_force_test",
        student_answer=student_force_ans,
        subject="physics",
    )
    print(f"A. Physics (Force/Motion):")
    print(f"   Student Answer: \"{student_force_ans}\"")
    print(f"   Verdict: {eval_force.verdict.value} | Diagnosed: {eval_force.misconception.misconception_type if eval_force.misconception else 'None'}")
    print(f"   Belief: {eval_force.misconception.belief if eval_force.misconception else 'None'}")
    print(f"   Remediation Strategy: {eval_force.misconception.recommended_strategy.value if eval_force.misconception else 'None'}")

    # 2. Programming: Assignment vs Equality in Python
    q_prog = Question(
        question_id="q_prog_test",
        lesson_id="l_prog",
        concept="python_basics",
        prompt="Write the condition to check if variable x equals 5 in Python.",
        expected_answer="if x == 5:",
        rubric=AnswerRubric(key_terms=["=="]),
        misconception_targets=[
            MisconceptionTarget(
                misconception_type="assignment_vs_equality",
                trigger_patterns=["if x = 5", "x = 5", "single equal"],
                explanation="Student confuses assignment operator '=' with comparison operator '=='.",
                remediation_strategy=TeachingStrategy.DIRECT_EXPLANATION,
            )
        ],
    )
    assessment_engine.store_question(q_prog)

    student_prog_ans = "You write: if x = 5:"
    eval_prog = assessment_engine.evaluate_response(
        question_id="q_prog_test",
        student_answer=student_prog_ans,
        subject="programming",
    )
    print(f"\nB. Programming (Assignment vs Equality):")
    print(f"   Student Answer: \"{student_prog_ans}\"")
    print(f"   Verdict: {eval_prog.verdict.value} | Diagnosed: {eval_prog.misconception.misconception_type if eval_prog.misconception else 'None'}")
    print(f"   Belief: {eval_prog.misconception.belief if eval_prog.misconception else 'None'}")
    print(f"   Remediation Strategy: {eval_prog.misconception.recommended_strategy.value if eval_prog.misconception else 'None'}")


def verify_real_adaptation_student_a_vs_student_b():
    print_header("VERIFICATION 5: ADAPTATION PROOF (STUDENT A vs STUDENT B)")
    orchestrator = MasterTeachingOrchestrator()

    # Student A: Correct Answer
    sess_a = orchestrator.start_session(
        student_id="student_A_correct",
        lesson_id="lesson_adaptation_test_A",
        topic="Ohm's Law",
        concepts_list=["ohms_law", "circuit_analysis"],
    )
    orchestrator.advance_to_question(sess_a.session_id, question_id="q_ohms_1")
    dec_a = orchestrator.process_evaluation_result(
        session_id=sess_a.session_id,
        is_correct=True,
        score=1.0,
        confidence=0.95,
        question_id="q_ohms_1",
        student_answer="Current decreases inversely with resistance.",
    )

    # Student B: Misconception Answer
    sess_b = orchestrator.start_session(
        student_id="student_B_misconception",
        lesson_id="lesson_adaptation_test_B",
        topic="Ohm's Law",
        concepts_list=["ohms_law", "circuit_analysis"],
    )
    orchestrator.advance_to_question(sess_b.session_id, question_id="q_ohms_1")
    misc_b = ActiveMisconception(
        concept="ohms_law",
        misconception_type="inverse_relationship_confusion",
        belief="higher resistance increases current",
        evidence_from_answer="Current increases",
        confidence=0.92,
    )
    dec_b = orchestrator.process_evaluation_result(
        session_id=sess_b.session_id,
        is_correct=False,
        score=0.1,
        confidence=0.92,
        misconception=misc_b,
        question_id="q_ohms_1",
        student_answer="Current increases when resistance increases.",
    )

    print("Student A (Correct Answer):")
    print(f"  Decision Action: {dec_a.action.value}")
    print(f"  Next State: {dec_a.next_state.value}")
    print(f"  Teaching Strategy: {dec_a.teaching_strategy.value}")
    print(f"  Visual Strategy: {dec_a.visual_strategy}")
    print(f"  Mastery: {sess_a.concept_mastery['ohms_law']}")

    print("\nStudent B (Misconception Answer):")
    print(f"  Decision Action: {dec_b.action.value}")
    print(f"  Next State: {dec_b.next_state.value}")
    print(f"  Teaching Strategy: {dec_b.teaching_strategy.value} (Switched from {dec_b.metadata.get('previous_strategy')})")
    print(f"  Visual Strategy: {dec_b.visual_strategy}")
    print(f"  Mastery: {sess_b.concept_mastery['ohms_law']}")


def verify_module_8_real_visual_files():
    print_header("VERIFICATION 6 & 7: REAL VISUAL FILE GENERATION & ADAPTIVE SPECS")
    engine = VisualIntelligenceEngine()
    out_dir = "/tmp/ai_teacher_rendered_visuals"
    os.makedirs(out_dir, exist_ok=True)

    test_cases = [
        ("physics", "ohms_law", TeachingStrategy.DIRECT_EXPLANATION, None, "01_physics_ohms_law_circuit.svg"),
        ("physics", "ohms_law", TeachingStrategy.SIMPLE_ANALOGY, MisconceptionRecord(
            concept="ohms_law",
            misconception_type="inverse_relationship_confusion",
            belief="higher resistance increases current",
            evidence_from_answer="current doubles",
        ), "02_physics_ohms_law_analogy.svg"),
        ("mathematics", "algebra_equations", TeachingStrategy.STEP_BY_STEP, None, "03_math_algebra_equations.html"),
        ("programming", "python_basics", TeachingStrategy.DIRECT_EXPLANATION, None, "04_programming_python.html"),
        ("biology", "cellular_respiration", TeachingStrategy.DIRECT_EXPLANATION, None, "05_biology_respiration.mermaid"),
    ]

    for subj, concept, strat, misc, filename in test_cases:
        spec = engine.plan_visual(subj, concept, strat, misconception=misc)
        asset = engine.render_visual(spec)

        filepath = os.path.join(out_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(asset.content)

        file_size = os.path.getsize(filepath)
        print(f"✓ Generated: {filename}")
        print(f"  VisualSpec Type: {spec.visual_type.value} | Format: {asset.format.value}")
        print(f"  File Path: {filepath} ({file_size} bytes)")
        print(f"  Renderer: {spec.renderer}")


def verify_module_9_audio_avatar_and_multilingual():
    print_header("VERIFICATION 8, 9, 10, 11: TTS, AVATAR, VIDEO PIPELINE & MULTILINGUAL")
    media_engine = MultimodalMediaEngine()
    out_dir = "/tmp/ai_teacher_media"
    os.makedirs(out_dir, exist_ok=True)

    # 1. Test Multilingual Scripts and Audio
    for lang in ["en", "hi", "ta", "hinglish"]:
        segment = media_engine.generate_teaching_segment(
            lesson_id=f"lesson_lang_{lang}",
            concept="Ohm's Law",
            teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
            language=lang,
        )
        print(f"Language [{lang.upper()}]:")
        print(f"  Script ({segment.script.estimated_duration_seconds}s): \"{segment.script.spoken_script[:80]}...\"")
        print(f"  Audio Track: format={segment.audio.format}, size={segment.audio.byte_size} bytes, is_fallback={segment.audio.is_fallback}")
        print(f"  Avatar Track: format={segment.avatar.format}, style={segment.avatar.presenter_style}")
        print(f"  Captions: {len(segment.captions.cues)} timed cues")


def verify_performance_benchmarks():
    print_header("VERIFICATION 14: PERFORMANCE MEASUREMENT BENCHMARKS")
    orchestrator = MasterTeachingOrchestrator()
    assessment_engine = AssessmentEngine()
    visual_engine = VisualIntelligenceEngine()
    media_engine = MultimodalMediaEngine()

    # 1. State Machine Transition
    t0 = time.perf_counter()
    sess = orchestrator.start_session("p_user", "p_lesson", "Ohm's Law", concepts_list=["ohms_law"])
    TeachingStateMachine.transition(sess, SessionState.QUESTION, ActionType.ASK_QUESTION)
    t_sm = (time.perf_counter() - t0) * 1000

    # 2. Assessment & Misconception Evaluation
    q = assessment_engine.generate_checkpoint_question("p_lesson", "ohms_law")
    t0 = time.perf_counter()
    eval_res = assessment_engine.evaluate_response(q.question_id, "If resistance increases current increases.", subject="physics")
    t_eval = (time.perf_counter() - t0) * 1000

    # 3. Visual SVG Generation
    t0 = time.perf_counter()
    vis = visual_engine.generate_visual("physics", "ohms_law", TeachingStrategy.SIMPLE_ANALOGY, misconception=eval_res.misconception)
    t_vis = (time.perf_counter() - t0) * 1000

    # 4. Multimodal Segment (Script + TTS WAV + Procedural Avatar SVG + Captions)
    t0 = time.perf_counter()
    seg = media_engine.generate_teaching_segment("p_lesson", "ohms_law", TeachingStrategy.SIMPLE_ANALOGY, visual_asset=vis)
    t_media = (time.perf_counter() - t0) * 1000

    print(f"1. State Machine Transitions (START -> TEACH -> QUESTION): {t_sm:.3f} ms")
    print(f"2. Assessment & Misconception Detection Engine:            {t_eval:.3f} ms")
    print(f"3. Subject-Aware SVG Visual Generation:                     {t_vis:.3f} ms")
    print(f"4. Multimodal Segment Assembly (Script + Audio + Avatar):   {t_media:.3f} ms")
    print(f"5. Total Synchronous Adaptive Loop Latency:                 {t_sm + t_eval + t_vis + t_media:.3f} ms")


if __name__ == "__main__":
    verify_module_5_real_state_machine()
    verify_module_7_exact_evaluation()
    verify_misconception_reusability_across_subjects()
    verify_real_adaptation_student_a_vs_student_b()
    verify_module_8_real_visual_files()
    verify_module_9_audio_avatar_and_multilingual()
    verify_performance_benchmarks()

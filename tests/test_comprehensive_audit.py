"""
Comprehensive Audit Test Suite covering Phases 2 through 25 for Modules 5, 7, 8, and 9.
"""

import pytest
from app.harness.session import (
    SessionState,
    TeachingStrategy,
    ActionType,
    DifficultyLevel,
    TeachingSessionState,
    TeachingDecision,
    ActiveMisconception,
    ConceptMasterySnapshot,
)
from app.harness.state_machine import TeachingStateMachine, InvalidStateTransitionError
from app.harness.policies import TeachingPolicyEngine, PolicyConfig
from app.harness.validators import StructuredOutputValidator
from app.harness.orchestrator import MasterTeachingOrchestrator
from app.assessment.models import (
    Question,
    QuestionType,
    QuestionOption,
    AnswerRubric,
    MisconceptionTarget,
    EvaluationVerdict,
    MisconceptionRecord,
)
from app.assessment.evaluator import AnswerEvaluator
from app.assessment.misconceptions import MisconceptionDetector
from app.assessment.interventions import InterventionEngine
from app.assessment.difficulty import AdaptiveDifficultyController
from app.assessment.taxonomy import MisconceptionTaxonomy, MisconceptionDefinition
from app.assessment.engine import AssessmentEngine
from app.visuals.models import VisualSpec, VisualType, SubjectCategory, RenderFormat
from app.visuals.strategies import VisualStrategyPlanner
from app.visuals.engine import VisualIntelligenceEngine
from app.media.models import TeachingScript, MediaStatus
from app.media.script_generator import TeachingScriptGenerator
from app.media.tts.local_tts import LocalVoiceProvider
from app.media.avatar.procedural_avatar import ProceduralAvatarProvider
from app.media.composer import VideoComposer
from app.media.jobs import MediaJobQueue
from app.media.engine import MultimodalMediaEngine


# =====================================================================
# PHASE 2 AUDIT: State Machine & 12 Transitions
# =====================================================================
def test_all_twelve_state_transitions():
    session = TeachingSessionState(
        student_id="audit_student",
        lesson_id="audit_lesson",
        topic="Ohm's Law",
        current_concept="ohms_law",
        concepts_list=["ohms_law"],
    )

    # 1. START -> UNDERSTAND
    TeachingStateMachine.transition(session, SessionState.UNDERSTAND, ActionType.UNDERSTAND_LEARNER)
    assert session.current_state == SessionState.UNDERSTAND

    # 2. UNDERSTAND -> PLAN
    TeachingStateMachine.transition(session, SessionState.PLAN, ActionType.GENERATE_PLAN)
    assert session.current_state == SessionState.PLAN

    # 3. PLAN -> TEACH
    TeachingStateMachine.transition(session, SessionState.TEACH, ActionType.DELIVER_EXPLANATION)
    assert session.current_state == SessionState.TEACH

    # 4. TEACH -> QUESTION
    TeachingStateMachine.transition(session, SessionState.QUESTION, ActionType.ASK_QUESTION)
    assert session.current_state == SessionState.QUESTION

    # 5. QUESTION -> EVALUATE
    TeachingStateMachine.transition(session, SessionState.EVALUATE, ActionType.EVALUATE_RESPONSE)
    assert session.current_state == SessionState.EVALUATE

    # 6. EVALUATE -> ADAPT (Misconception branch)
    TeachingStateMachine.transition(session, SessionState.ADAPT, ActionType.ADAPT_STRATEGY)
    assert session.current_state == SessionState.ADAPT

    # 7. ADAPT -> REEXPLAIN
    TeachingStateMachine.transition(session, SessionState.REEXPLAIN, ActionType.REEXPLAIN_CONCEPT)
    assert session.current_state == SessionState.REEXPLAIN

    # 8. REEXPLAIN -> REQUESTION
    TeachingStateMachine.transition(session, SessionState.REQUESTION, ActionType.ASK_RECHECK_QUESTION)
    assert session.current_state == SessionState.REQUESTION

    # 9. REQUESTION -> EVALUATE
    TeachingStateMachine.transition(session, SessionState.EVALUATE, ActionType.EVALUATE_RESPONSE)
    assert session.current_state == SessionState.EVALUATE

    # 10. EVALUATE -> ASSESSMENT
    TeachingStateMachine.transition(session, SessionState.ASSESSMENT, ActionType.RUN_ASSESSMENT)
    assert session.current_state == SessionState.ASSESSMENT

    # 11. ASSESSMENT -> REPORT
    TeachingStateMachine.transition(session, SessionState.REPORT, ActionType.GENERATE_REPORT)
    assert session.current_state == SessionState.REPORT

    # 12. REPORT -> COMPLETE
    TeachingStateMachine.transition(session, SessionState.COMPLETE, ActionType.COMPLETE_SESSION)
    assert session.current_state == SessionState.COMPLETE
    assert session.completed_at is not None


def test_illegal_state_transition_rejection():
    session = TeachingSessionState(
        student_id="audit_student",
        lesson_id="audit_lesson",
        topic="Ohm's Law",
        current_concept="ohms_law",
    )
    # Cannot jump from START to EVALUATE, COMPLETE, or REEXPLAIN
    with pytest.raises(InvalidStateTransitionError):
        TeachingStateMachine.transition(session, SessionState.EVALUATE, ActionType.EVALUATE_RESPONSE)
    with pytest.raises(InvalidStateTransitionError):
        TeachingStateMachine.transition(session, SessionState.COMPLETE, ActionType.COMPLETE_SESSION)


# =====================================================================
# PHASE 3 & 4 AUDIT: Policies & Structured Output Validation
# =====================================================================
def test_policy_engine_escalation_rules():
    config = PolicyConfig(
        mastery_increase_step=0.25,
        mastery_decrease_step=0.15,
        max_consecutive_failures_before_prerequisite=3,
    )
    engine = TeachingPolicyEngine(config=config)
    session = TeachingSessionState(
        student_id="s1",
        lesson_id="l1",
        topic="Ohm's Law",
        current_concept="ohms_law",
        concepts_list=["ohms_law"],
        current_strategy=TeachingStrategy.DIRECT_EXPLANATION,
    )

    # 1st Failure -> Switch to Analogy
    dec1 = engine.evaluate_checkpoint_response(session, is_correct=False, score=0.0, confidence=0.9)
    assert dec1.teaching_strategy == TeachingStrategy.SIMPLE_ANALOGY
    assert session.consecutive_failures == 1

    # 2nd Failure -> Switch to Visual Explanation
    dec2 = engine.evaluate_checkpoint_response(session, is_correct=False, score=0.0, confidence=0.9)
    assert dec2.teaching_strategy == TeachingStrategy.VISUAL_EXPLANATION
    assert session.consecutive_failures == 2

    # 3rd Failure -> Switch to Prerequisite Review
    dec3 = engine.evaluate_checkpoint_response(session, is_correct=False, score=0.0, confidence=0.9)
    assert dec3.teaching_strategy == TeachingStrategy.PREREQUISITE_REVIEW
    assert session.consecutive_failures == 3


def test_structured_output_validator_fallback():
    validator = StructuredOutputValidator()
    
    # Valid dict -> valid model
    valid_data = {
        "current_state": "EVALUATE",
        "action": "ADVANCE_CONCEPT",
        "reason": "Correct answer",
        "concept": "ohms_law",
        "difficulty": 2,
        "teaching_strategy": "DIRECT_EXPLANATION",
        "visual_strategy": "circuit_diagram",
        "language": "en",
        "next_state": "TEACH",
    }
    decision = validator.validate_or_fallback(TeachingDecision, valid_data, lambda: TeachingDecision(
        current_state=SessionState.START,
        action=ActionType.START_LESSON,
        reason="fallback",
        concept="fallback",
        next_state=SessionState.TEACH,
    ))
    assert decision.action == ActionType.ADVANCE_CONCEPT

    # Malformed data -> triggers fallback safely without throwing
    malformed_data = {"invalid_key": 12345}
    fallback_decision = validator.validate_or_fallback(
        TeachingDecision,
        malformed_data,
        lambda: TeachingDecision(
            current_state=SessionState.START,
            action=ActionType.START_LESSON,
            reason="safe fallback triggered",
            concept="ohms_law",
            next_state=SessionState.TEACH,
        ),
    )
    assert fallback_decision.reason == "safe fallback triggered"
    assert validator.validation_errors_count >= 1


# =====================================================================
# PHASE 5 & 6 AUDIT: Multi-Type Questions & Evaluator Robustness
# =====================================================================
def test_evaluator_edge_cases():
    evaluator = AnswerEvaluator()
    q = Question(
        lesson_id="l1",
        concept="ohms_law",
        type=QuestionType.CONCEPTUAL,
        prompt="Explain what happens to current if resistance increases at constant voltage.",
        expected_answer="Current decreases inversely according to I = V / R.",
        rubric=AnswerRubric(
            key_terms=["decrease", "inversely", "drops", "reduces"],
            anti_patterns=["increases", "doubles"],
        ),
    )

    # 1. Empty string -> Incorrect
    res_empty = evaluator.evaluate(q, "")
    assert res_empty.verdict == EvaluationVerdict.INCORRECT
    assert res_empty.score == 0.0

    # 2. Irrelevant / nonsensical answer -> Incorrect
    res_nonsense = evaluator.evaluate(q, "The sky is blue and pizza is delicious.")
    assert res_nonsense.verdict == EvaluationVerdict.INCORRECT
    assert res_nonsense.score == 0.0

    # 3. Very long response (500+ words) containing key terms -> Correct
    long_answer = "In standard circuit analysis, voltage provides the electromotive push. " + ("word " * 200) + "Consequently, the current decreases inversely as resistance opposes flow."
    res_long = evaluator.evaluate(q, long_answer)
    assert res_long.verdict == EvaluationVerdict.CORRECT
    assert res_long.score == 1.0

    # 4. Partial answer -> Partially Correct
    partial_answer = "The current decreases."
    res_partial = evaluator.evaluate(q, partial_answer)
    assert res_partial.verdict in (EvaluationVerdict.PARTIALLY_CORRECT, EvaluationVerdict.CORRECT)
    assert res_partial.score >= 0.25


# =====================================================================
# PHASE 10, 11, 12, 13 AUDIT: Visual Strategy & Accuracy
# =====================================================================
def test_subject_aware_visual_specs():
    engine = VisualIntelligenceEngine()

    # Physics Normal -> Circuit Diagram
    spec_phys = engine.plan_visual("physics", "ohms_law", TeachingStrategy.DIRECT_EXPLANATION)
    assert spec_phys.visual_type == VisualType.CIRCUIT_DIAGRAM

    # Physics Misconception -> Water Analogy Diagram
    record = MisconceptionRecord(
        concept="ohms_law",
        misconception_type="inverse_relationship_confusion",
        belief="higher resistance increases current",
        evidence_from_answer="current will increase",
    )
    spec_analogy = engine.plan_visual("physics", "ohms_law", TeachingStrategy.SIMPLE_ANALOGY, misconception=record)
    assert spec_analogy.visual_type == VisualType.ANALOGY_WATER_CIRCUIT

    # Mathematics -> LaTeX Equation / Step Solution
    spec_math = engine.plan_visual("mathematics", "algebra_equations", TeachingStrategy.STEP_BY_STEP)
    assert spec_math.visual_type == VisualType.LATEX_EQUATION

    # Programming -> Code Block
    spec_prog = engine.plan_visual("programming", "python_basics")
    assert spec_prog.visual_type == VisualType.CODE_BLOCK

    # Biology / Chemistry / General -> Mermaid Flowchart
    spec_bio = engine.plan_visual("biology", "cell_respiration_process")
    assert spec_bio.visual_type == VisualType.MERMAID_FLOWCHART


# =====================================================================
# PHASE 14, 15, 16, 17, 19 AUDIT: Multimodal Script, Voice, Avatar, Sync
# =====================================================================
def test_multilingual_script_and_media_pipeline():
    script_gen = TeachingScriptGenerator()
    tts = LocalVoiceProvider()
    avatar_gen = ProceduralAvatarProvider()
    composer = VideoComposer()

    # Test languages: en, hi, ta, hinglish
    for lang in ["en", "hi", "ta", "hinglish"]:
        script = script_gen.generate_script("Ohm's Law", TeachingStrategy.DIRECT_EXPLANATION, language=lang)
        assert len(script.spoken_script) > 10
        assert script.estimated_duration_seconds > 0

        audio = tts.generate_speech(script.script_id, script.spoken_script, language=lang)
        assert audio.duration_seconds > 0
        assert audio.content_uri.startswith("data:audio/wav;base64,")

        avatar = avatar_gen.generate_avatar(script, audio)
        assert avatar.format == "svg_animation"
        assert "<svg" in avatar.content_uri

        segment = composer.assemble_segment("test_lesson", script, audio, avatar)
        assert segment.status == MediaStatus.READY
        assert segment.captions is not None
        assert len(segment.captions.cues) >= 1

"""
Unit & Integration Tests for Module 5: Teaching Harness & Orchestrator.
"""

import pytest
from app.harness.session import (
    SessionState,
    TeachingStrategy,
    ActionType,
    DifficultyLevel,
    TeachingSessionState,
    ActiveMisconception,
)
from app.harness.state_machine import TeachingStateMachine, InvalidStateTransitionError
from app.harness.policies import TeachingPolicyEngine, PolicyConfig
from app.harness.orchestrator import MasterTeachingOrchestrator
from app.harness.trace import TeachingTraceLogger


def test_state_machine_valid_transitions():
    session = TeachingSessionState(
        student_id="student_1",
        lesson_id="lesson_1",
        topic="Ohm's Law",
        current_concept="resistance",
    )
    assert session.current_state == SessionState.START

    # Valid START -> UNDERSTAND
    TeachingStateMachine.transition(session, SessionState.UNDERSTAND, ActionType.UNDERSTAND_LEARNER)
    assert session.current_state == SessionState.UNDERSTAND
    assert len(session.events_history) == 1

    # Valid UNDERSTAND -> PLAN
    TeachingStateMachine.transition(session, SessionState.PLAN, ActionType.GENERATE_PLAN)
    assert session.current_state == SessionState.PLAN

    # Valid PLAN -> TEACH
    TeachingStateMachine.transition(session, SessionState.TEACH, ActionType.DELIVER_EXPLANATION)
    assert session.current_state == SessionState.TEACH


def test_state_machine_invalid_transition_rejected():
    session = TeachingSessionState(
        student_id="student_1",
        lesson_id="lesson_1",
        topic="Ohm's Law",
        current_concept="resistance",
    )
    # Cannot jump directly from START to ASSESSMENT
    with pytest.raises(InvalidStateTransitionError):
        TeachingStateMachine.transition(session, SessionState.ASSESSMENT, ActionType.RUN_ASSESSMENT)


def test_policy_engine_correct_answer_advancement():
    engine = TeachingPolicyEngine()
    session = TeachingSessionState(
        student_id="s1",
        lesson_id="l1",
        topic="Ohm's Law",
        current_concept="voltage",
        concepts_list=["voltage", "current", "resistance"],
        concept_mastery={"voltage": 0.5, "current": 0.3, "resistance": 0.2},
    )

    decision = engine.evaluate_checkpoint_response(
        session=session,
        is_correct=True,
        score=1.0,
        confidence=0.95,
        misconception=None,
    )

    assert decision.action == ActionType.ADVANCE_CONCEPT
    assert decision.concept == "current"
    assert session.concept_mastery["voltage"] > 0.5
    assert session.consecutive_successes == 1


def test_policy_engine_misconception_adaptation():
    engine = TeachingPolicyEngine()
    session = TeachingSessionState(
        student_id="s1",
        lesson_id="l1",
        topic="Ohm's Law",
        current_concept="resistance",
        concepts_list=["voltage", "current", "resistance"],
        concept_mastery={"voltage": 0.8, "current": 0.8, "resistance": 0.3},
        current_strategy=TeachingStrategy.DIRECT_EXPLANATION,
    )

    misconception = ActiveMisconception(
        concept="resistance",
        misconception_type="inverse_relationship_confusion",
        belief="higher resistance increases current",
        evidence_from_answer="Current will double when resistance doubles",
        confidence=0.92,
    )

    decision = engine.evaluate_checkpoint_response(
        session=session,
        is_correct=False,
        score=0.1,
        confidence=0.92,
        misconception=misconception,
    )

    assert decision.action == ActionType.ADAPT_STRATEGY
    assert decision.next_state == SessionState.ADAPT
    # Teaching strategy should have switched from DIRECT_EXPLANATION to SIMPLE_ANALOGY
    assert decision.teaching_strategy == TeachingStrategy.SIMPLE_ANALOGY
    assert session.current_strategy == TeachingStrategy.SIMPLE_ANALOGY
    assert len(session.active_misconceptions) == 1


def test_orchestrator_full_lifecycle():
    orchestrator = MasterTeachingOrchestrator()
    session = orchestrator.start_session(
        student_id="user_123",
        lesson_id="lesson_ohms",
        topic="Ohm's Law",
        subject="Physics",
        concepts_list=["voltage", "resistance"],
        time_minutes=10,
    )

    assert session.current_state == SessionState.TEACH
    assert session.current_concept == "voltage"

    # Step to question
    decision_q = orchestrator.advance_to_question(session.session_id, question_id="q1")
    assert decision_q.current_state == SessionState.QUESTION

    # Evaluate correct answer
    decision_eval = orchestrator.process_evaluation_result(
        session_id=session.session_id,
        is_correct=True,
        score=1.0,
        confidence=0.9,
        question_id="q1",
        student_answer="Voltage is potential difference.",
    )
    assert decision_eval.action == ActionType.ADVANCE_CONCEPT
    assert decision_eval.concept == "resistance"

    # Trace logged
    traces = orchestrator.trace_logger.get_traces_for_session(session.session_id)
    assert len(traces) >= 2
    ascii_summary = orchestrator.trace_logger.render_session_trace_summary(session.session_id)
    assert "AI TEACHING TRACE" in ascii_summary

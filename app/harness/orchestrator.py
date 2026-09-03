"""
Master Teaching Orchestrator for Module 5 (Teaching Harness).
The central coordinator enforcing deterministic state progression, policy execution, and tool orchestration.
"""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import uuid

from app.harness.session import (
    SessionState,
    TeachingStrategy,
    ActionType,
    DifficultyLevel,
    TeachingDecision,
    TeachingSessionState,
    ActiveMisconception,
    ConceptMasterySnapshot,
)
from app.harness.state_machine import TeachingStateMachine
from app.harness.policies import TeachingPolicyEngine, PolicyConfig
from app.harness.validators import StructuredOutputValidator
from app.harness.tools import ToolRegistry
from app.harness.trace import TeachingTraceLogger, TeachingTraceEntry

logger = logging.getLogger(__name__)


class MasterTeachingOrchestrator:
    """
    Master Teaching Orchestrator implementing the full adaptive teaching loop:
    UNDERSTAND -> PLAN -> TEACH -> QUESTION -> EVALUATE -> (CORRECT | MISCONCEPTION) -> ADAPT -> REEXPLAIN -> REQUESTION -> ASSESSMENT -> REPORT
    """

    def __init__(
        self,
        policy_engine: Optional[TeachingPolicyEngine] = None,
        tool_registry: Optional[ToolRegistry] = None,
        trace_logger: Optional[TeachingTraceLogger] = None,
    ):
        self.policy_engine = policy_engine or TeachingPolicyEngine()
        self.tool_registry = tool_registry or ToolRegistry()
        self.trace_logger = trace_logger or TeachingTraceLogger()
        self.validator = StructuredOutputValidator()
        self._sessions: Dict[str, TeachingSessionState] = {}

    def get_session(self, session_id: str) -> TeachingSessionState:
        if session_id not in self._sessions:
            raise KeyError(f"Teaching session '{session_id}' not found.")
        return self._sessions[session_id]

    def save_session(self, session: TeachingSessionState) -> None:
        self._sessions[session.session_id] = session

    def start_session(
        self,
        student_id: str,
        lesson_id: str,
        topic: str,
        subject: str = "physics",
        language: str = "en",
        learner_level: str = "beginner",
        concepts_list: Optional[List[str]] = None,
        time_minutes: int = 10,
    ) -> TeachingSessionState:
        """Initializes a new teaching session and transitions through START -> UNDERSTAND -> PLAN -> TEACH."""
        concepts = concepts_list or [topic]
        initial_mastery = {c: 0.3 for c in concepts}
        initial_snapshots = {
            c: ConceptMasterySnapshot(concept=c, mastery=0.3, confidence=0.5)
            for c in concepts
        }

        session = TeachingSessionState(
            student_id=student_id,
            lesson_id=lesson_id,
            topic=topic,
            subject=subject,
            language=language,
            learner_level=learner_level,
            current_state=SessionState.START,
            current_concept=concepts[0],
            current_concept_index=0,
            concepts_list=concepts,
            concept_mastery=initial_mastery,
            concept_snapshots=initial_snapshots,
            current_strategy=TeachingStrategy.DIRECT_EXPLANATION,
            current_difficulty=DifficultyLevel.BASIC,
            time_remaining_minutes=time_minutes,
            total_time_minutes=time_minutes,
        )

        # 1. Transition START -> UNDERSTAND
        TeachingStateMachine.transition(session, SessionState.UNDERSTAND, ActionType.UNDERSTAND_LEARNER)

        # 2. Transition UNDERSTAND -> PLAN
        TeachingStateMachine.transition(session, SessionState.PLAN, ActionType.GENERATE_PLAN)

        # 3. Transition PLAN -> TEACH
        TeachingStateMachine.transition(
            session,
            SessionState.TEACH,
            ActionType.DELIVER_EXPLANATION,
            payload={"concept": session.current_concept, "strategy": session.current_strategy.value},
        )

        self.save_session(session)

        # Log initial trace
        self.trace_logger.log_entry(
            TeachingTraceEntry(
                session_id=session.session_id,
                student_id=session.student_id,
                concept=session.current_concept,
                learner_level=session.learner_level,
                current_state="START",
                next_state="TEACH",
                previous_strategy="None",
                new_strategy=session.current_strategy.value,
                visual_strategy=self.policy_engine.select_visual_strategy(
                    session.subject, session.current_concept, session.current_strategy
                ),
                next_action=ActionType.DELIVER_EXPLANATION.value,
            )
        )

        return session

    def advance_to_question(self, session_id: str, question_id: Optional[str] = None) -> TeachingDecision:
        """Transitions state from TEACH or REEXPLAIN to QUESTION or REQUESTION."""
        session = self.get_session(session_id)

        if session.current_state == SessionState.TEACH:
            target_state = SessionState.QUESTION
            action = ActionType.ASK_QUESTION
        elif session.current_state in (SessionState.REEXPLAIN, SessionState.ADAPT):
            target_state = SessionState.REQUESTION
            action = ActionType.ASK_RECHECK_QUESTION
        else:
            target_state = SessionState.QUESTION
            action = ActionType.ASK_QUESTION

        TeachingStateMachine.transition(
            session,
            target_state,
            action,
            payload={"concept": session.current_concept, "question_id": question_id},
        )
        session.current_question_id = question_id
        self.save_session(session)

        decision = TeachingDecision(
            current_state=target_state,
            action=action,
            reason=f"Transitioned to {target_state.value} for concept '{session.current_concept}'",
            concept=session.current_concept,
            difficulty=session.current_difficulty,
            teaching_strategy=session.current_strategy,
            visual_strategy=self.policy_engine.select_visual_strategy(
                session.subject, session.current_concept, session.current_strategy
            ),
            language=session.language,
            next_state=SessionState.EVALUATE,
            requires_video=False,
            requires_question=True,
        )
        return decision

    def process_evaluation_result(
        self,
        session_id: str,
        is_correct: bool,
        score: float,
        confidence: float,
        misconception: Optional[ActiveMisconception] = None,
        evaluator_reason: str = "",
        question_id: Optional[str] = None,
        student_answer: Optional[str] = None,
        latency_ms: float = 0.0,
    ) -> TeachingDecision:
        """
        Receives an evaluation from Module 7, applies Policy Engine rules, transitions state,
        updates cognitive model, and creates an AI Teaching Trace.
        """
        session = self.get_session(session_id)
        prev_strategy = session.current_strategy.value

        # Ensure state machine is in QUESTION or REQUESTION before EVALUATE
        if session.current_state == SessionState.TEACH:
            TeachingStateMachine.transition(
                session, SessionState.QUESTION, ActionType.ASK_QUESTION, payload={"question_id": question_id}
            )
        elif session.current_state in (SessionState.REEXPLAIN, SessionState.ADAPT):
            TeachingStateMachine.transition(
                session, SessionState.REQUESTION, ActionType.ASK_RECHECK_QUESTION, payload={"question_id": question_id}
            )

        # First transition state machine into EVALUATE
        TeachingStateMachine.transition(
            session,
            SessionState.EVALUATE,
            ActionType.EVALUATE_RESPONSE,
            payload={
                "is_correct": is_correct,
                "score": score,
                "confidence": confidence,
                "misconception": misconception.model_dump() if misconception else None,
            },
        )

        # Policy Engine evaluates the next decision
        decision = self.policy_engine.evaluate_checkpoint_response(
            session=session,
            is_correct=is_correct,
            score=score,
            confidence=confidence,
            misconception=misconception,
            evaluator_reason=evaluator_reason,
        )

        session.decisions_history.append(decision)

        # Transition to next state prescribed by the policy decision
        TeachingStateMachine.transition(
            session,
            decision.next_state,
            decision.action,
            payload={"decision_id": decision.decision_id, "reason": decision.reason},
        )

        self.save_session(session)

        # Record structured trace
        eval_label = "Correct" if is_correct else ("Misconception" if misconception else "Incorrect")
        trace = TeachingTraceEntry(
            session_id=session.session_id,
            student_id=session.student_id,
            concept=decision.concept,
            learner_level=session.learner_level,
            current_state=SessionState.EVALUATE.value,
            next_state=decision.next_state.value,
            question_id=question_id or session.current_question_id,
            student_answer=student_answer,
            evaluation_result=eval_label,
            evaluation_score=score,
            misconception_type=misconception.misconception_type if misconception else None,
            misconception_belief=misconception.belief if misconception else None,
            confidence=confidence,
            previous_strategy=prev_strategy,
            new_strategy=decision.teaching_strategy.value,
            visual_strategy=decision.visual_strategy,
            next_action=decision.action.value,
            latency_ms=latency_ms,
        )
        self.trace_logger.log_entry(trace)

        return decision

    def complete_assessment_and_report(
        self, session_id: str, final_score: float, summary: str = ""
    ) -> TeachingSessionState:
        """Transitions through ASSESSMENT -> REPORT -> COMPLETE."""
        session = self.get_session(session_id)

        if session.current_state != SessionState.ASSESSMENT:
            TeachingStateMachine.transition(session, SessionState.ASSESSMENT, ActionType.RUN_ASSESSMENT)

        TeachingStateMachine.transition(
            session,
            SessionState.REPORT,
            ActionType.GENERATE_REPORT,
            payload={"final_score": final_score, "summary": summary},
        )

        TeachingStateMachine.transition(
            session,
            SessionState.COMPLETE,
            ActionType.COMPLETE_SESSION,
            payload={"completed_at": datetime.now(timezone.utc).isoformat()},
        )

        self.save_session(session)

        self.trace_logger.log_entry(
            TeachingTraceEntry(
                session_id=session.session_id,
                student_id=session.student_id,
                concept=session.topic,
                learner_level=session.learner_level,
                current_state="REPORT",
                next_state="COMPLETE",
                evaluation_result="Completed",
                evaluation_score=final_score,
                next_action=ActionType.COMPLETE_SESSION.value,
            )
        )

        return session

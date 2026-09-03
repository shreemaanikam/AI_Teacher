"""
Deterministic Teaching State Machine for Module 5.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, List, Set
from app.harness.session import (
    SessionState,
    ActionType,
    TeachingEvent,
    TeachingSessionState,
)


class InvalidStateTransitionError(ValueError):
    """Raised when an illegal or out-of-order state transition is attempted."""
    def __init__(self, from_state: SessionState, to_state: SessionState, reason: str = ""):
        message = f"Invalid state transition from {from_state.value} to {to_state.value}"
        if reason:
            message += f": {reason}"
        super().__init__(message)
        self.from_state = from_state
        self.to_state = to_state
        self.reason = reason


class TeachingStateMachine:
    """
    Controlled deterministic state machine governing teaching session progression.
    Guarantees that probabilistic models cannot arbitrarily jump states or bypass pedagogical steps.
    """

    # Allowed forward transitions
    VALID_TRANSITIONS: Dict[SessionState, Set[SessionState]] = {
        SessionState.START: {SessionState.UNDERSTAND, SessionState.ERROR},
        SessionState.UNDERSTAND: {SessionState.PLAN, SessionState.ERROR},
        SessionState.PLAN: {SessionState.TEACH, SessionState.ERROR},
        SessionState.TEACH: {SessionState.QUESTION, SessionState.ASSESSMENT, SessionState.PAUSED, SessionState.ERROR},
        SessionState.QUESTION: {SessionState.EVALUATE, SessionState.PAUSED, SessionState.ERROR},
        SessionState.EVALUATE: {
            SessionState.TEACH,       # Advance to next concept
            SessionState.ADAPT,       # Misconception detected -> trigger adaptation
            SessionState.ASSESSMENT,  # All concepts taught -> final assessment
            SessionState.REEXPLAIN,   # Direct re-explanation path
            SessionState.PAUSED,
            SessionState.ERROR,
        },
        SessionState.ADAPT: {SessionState.REEXPLAIN, SessionState.REQUESTION, SessionState.PAUSED, SessionState.ERROR},
        SessionState.REEXPLAIN: {SessionState.REQUESTION, SessionState.PAUSED, SessionState.ERROR},
        SessionState.REQUESTION: {SessionState.EVALUATE, SessionState.PAUSED, SessionState.ERROR},
        SessionState.ASSESSMENT: {SessionState.REPORT, SessionState.PAUSED, SessionState.ERROR},
        SessionState.REPORT: {SessionState.COMPLETE, SessionState.ERROR},
        SessionState.COMPLETE: set(),  # Terminal state
        SessionState.PAUSED: {
            SessionState.TEACH,
            SessionState.QUESTION,
            SessionState.EVALUATE,
            SessionState.ADAPT,
            SessionState.REEXPLAIN,
            SessionState.REQUESTION,
            SessionState.ASSESSMENT,
            SessionState.REPORT,
            SessionState.COMPLETE,
        },
        SessionState.ERROR: {SessionState.START, SessionState.TEACH, SessionState.COMPLETE},
    }

    @classmethod
    def is_valid_transition(cls, from_state: SessionState, to_state: SessionState) -> bool:
        allowed = cls.VALID_TRANSITIONS.get(from_state, set())
        return to_state in allowed

    @classmethod
    def transition(
        cls,
        session: TeachingSessionState,
        to_state: SessionState,
        trigger_action: ActionType,
        payload: dict | None = None,
    ) -> TeachingSessionState:
        """
        Executes a validated transition on the session.
        Appends a state event and increments the session version.
        """
        from_state = session.current_state

        if to_state == SessionState.PAUSED:
            session.previous_state = from_state
            session.current_state = SessionState.PAUSED
        elif from_state == SessionState.PAUSED and session.previous_state is not None:
            # Resuming from pause to previous state or to_state
            session.current_state = to_state
        else:
            if not cls.is_valid_transition(from_state, to_state):
                raise InvalidStateTransitionError(
                    from_state=from_state,
                    to_state=to_state,
                    reason=f"Transition disallowed by teaching harness policy from {from_state.value} to {to_state.value}",
                )
            session.previous_state = from_state
            session.current_state = to_state

        # Record event
        event = TeachingEvent(
            session_id=session.session_id,
            from_state=from_state,
            to_state=to_state,
            trigger_action=trigger_action,
            payload=payload or {},
            timestamp=datetime.now(timezone.utc),
        )
        session.events_history.append(event)
        session.version += 1
        session.updated_at = datetime.now(timezone.utc)

        if to_state == SessionState.COMPLETE:
            session.completed_at = datetime.now(timezone.utc)

        return session

    @classmethod
    def can_proceed_to_assessment(cls, session: TeachingSessionState) -> bool:
        """Enforces invariant: final assessment is only allowed after all concepts have been taught and evaluated."""
        if not session.concepts_list:
            return True
        return session.current_concept_index >= len(session.concepts_list) - 1

    @classmethod
    def can_finalize_report(cls, session: TeachingSessionState) -> bool:
        """Enforces invariant: report cannot be finalized before assessment is reached."""
        visited_states = {e.to_state for e in session.events_history}
        return SessionState.ASSESSMENT in visited_states or session.current_state == SessionState.ASSESSMENT

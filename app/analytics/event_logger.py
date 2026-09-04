"""
Central Learning Event Logger for Module 10: Learning Analytics.
"""

from __future__ import annotations
from typing import List, Dict, Optional
from datetime import datetime, timezone

from app.analytics.models import LearningEvent, LearningEventType
from app.harness.session import TeachingStrategy


class LearningEventLogger:
    """Records real-time telemetry events from across the teaching platform."""

    def __init__(self):
        self._events: List[LearningEvent] = []

    def log_event(
        self,
        learner_id: str,
        concept_id: str,
        event_type: LearningEventType,
        session_id: Optional[str] = None,
        score: Optional[float] = None,
        difficulty: int = 2,
        strategy: Optional[TeachingStrategy] = None,
        language: str = "en",
        duration_seconds: float = 0.0,
        payload: Optional[Dict] = None,
    ) -> LearningEvent:
        evt = LearningEvent(
            learner_id=learner_id,
            session_id=session_id,
            concept_id=concept_id,
            event_type=event_type,
            score=score,
            difficulty=difficulty,
            strategy=strategy,
            language=language,
            duration_seconds=duration_seconds,
            payload=payload or {},
        )
        self._events.append(evt)
        return evt

    def get_learner_events(self, learner_id: str) -> List[LearningEvent]:
        return [e for e in self._events if e.learner_id == learner_id]

    def get_session_events(self, session_id: str) -> List[LearningEvent]:
        return [e for e in self._events if e.session_id == session_id]


# Global singleton
_GLOBAL_EVENT_LOGGER = LearningEventLogger()


def get_event_logger() -> LearningEventLogger:
    return _GLOBAL_EVENT_LOGGER

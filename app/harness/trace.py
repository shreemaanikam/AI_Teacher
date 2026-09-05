"""
AI Teaching Trace and Observability for Module 5 (Teaching Harness).
Provides auditable step-by-step traces of cognitive state, evaluation, misconception detection, and teaching decisions.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class TeachingTraceEntry(BaseModel):
    """Structured record of an adaptive teaching decision event."""
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    student_id: str
    step_index: int = 0
    concept: str
    learner_level: str = "beginner"
    current_state: str
    next_state: str
    question_id: Optional[str] = None
    student_answer: Optional[str] = None
    evaluation_result: Optional[str] = None  # Correct, Incorrect, Misconception
    evaluation_score: Optional[float] = None
    misconception_type: Optional[str] = None
    misconception_belief: Optional[str] = None
    confidence: float = 1.0
    previous_strategy: str = "DIRECT_EXPLANATION"
    new_strategy: str = "DIRECT_EXPLANATION"
    visual_strategy: str = "diagram"
    selected_model: str = "local-llama"
    next_action: str = "CONTINUE"
    latency_ms: float = 0.0
    media_status: str = "READY"
    evidence_refs: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def render_ascii_box(self) -> str:
        """Renders an ASCII trace box suitable for CLI logs and judge presentations."""
        lines = [
            "┌" + "─" * 46 + "┐",
            "│" + " AI TEACHING TRACE".center(46) + "│",
            "├" + "─" * 46 + "┤",
            f"│ Concept: {self.concept[:35]:<35} │",
            f"│ Student: {self.learner_level[:35]:<35} │",
            f"│ State: {self.current_state} -> {self.next_state:<28} │"[:47] + " │",
            f"│ Question ID: {(self.question_id or 'N/A')[:31]:<31} │",
            f"│ Result: {(self.evaluation_result or 'N/A')[:36]:<36} │",
            f"│ Misconception: {(self.misconception_type or 'None')[:29]:<29} │",
            f"│ Confidence: {self.confidence:<32.2f} │",
            f"│ Prev Strategy: {self.previous_strategy[:29]:<29} │",
            f"│ New Strategy: {self.new_strategy[:30]:<30} │",
            f"│ Visual Strategy: {self.visual_strategy[:27]:<27} │",
            f"│ Next Action: {self.next_action[:31]:<31} │",
            f"│ Media Status: {self.media_status[:30]:<30} │",
            "└" + "─" * 46 + "┘",
        ]
        return "\n".join(lines)


class TeachingTraceLogger:
    """Stores and formats teaching traces for observability and evaluation."""

    def __init__(self):
        self._traces: Dict[str, List[TeachingTraceEntry]] = {}

    def log_entry(self, entry: TeachingTraceEntry) -> None:
        if entry.session_id not in self._traces:
            self._traces[entry.session_id] = []
        entry.step_index = len(self._traces[entry.session_id]) + 1
        self._traces[entry.session_id].append(entry)

    def get_traces_for_session(self, session_id: str) -> List[TeachingTraceEntry]:
        return self._traces.get(session_id, [])

    def get_session_traces(self, session_id: str) -> List[TeachingTraceEntry]:
        """Alias for get_traces_for_session."""
        return self.get_traces_for_session(session_id)

    def get_latest_trace(self, session_id: str) -> Optional[TeachingTraceEntry]:
        traces = self._traces.get(session_id, [])
        return traces[-1] if traces else None

    def render_session_trace_summary(self, session_id: str) -> str:
        traces = self.get_traces_for_session(session_id)
        if not traces:
            return f"No trace entries recorded for session {session_id}."
        return "\n\n".join([t.render_ascii_box() for t in traces])

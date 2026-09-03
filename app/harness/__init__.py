"""
Module 5: Teaching Harness / Orchestrator
Deterministic orchestration layer for adaptive cognitive teaching.
"""

from app.harness.session import (
    SessionState,
    TeachingStrategy,
    ActionType,
    DifficultyLevel,
    TeachingDecision,
    TeachingSessionState,
    TeachingEvent,
)
from app.harness.state_machine import TeachingStateMachine, InvalidStateTransitionError
from app.harness.policies import TeachingPolicyEngine, PolicyConfig
from app.harness.validators import StructuredOutputValidator
from app.harness.tools import ToolRegistry
from app.harness.trace import TeachingTraceLogger, TeachingTraceEntry
from app.harness.orchestrator import MasterTeachingOrchestrator

__all__ = [
    "SessionState",
    "TeachingStrategy",
    "ActionType",
    "DifficultyLevel",
    "TeachingDecision",
    "TeachingSessionState",
    "TeachingEvent",
    "TeachingStateMachine",
    "InvalidStateTransitionError",
    "TeachingPolicyEngine",
    "PolicyConfig",
    "StructuredOutputValidator",
    "ToolRegistry",
    "TeachingTraceLogger",
    "TeachingTraceEntry",
    "MasterTeachingOrchestrator",
]

"""
Learner Cognitive Model Adapter for Member 2 Integration.
"""

from __future__ import annotations
from typing import Dict, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class LearnerProfileData(BaseModel):
    student_id: str
    display_name: str = "Learner"
    education_level: str = "beginner"
    preferred_language: str = "en"
    goals: List[str] = Field(default_factory=list)
    mastery_scores: Dict[str, float] = Field(default_factory=dict)
    known_misconceptions: List[str] = Field(default_factory=list)


from app.learner.cognitive_service import LearnerCognitiveService, get_learner_service


class LearnerCognitiveModelAdapter:
    """Interacts with Module 3's persistent learner profile and mastery tracking services."""

    def __init__(self, service: Optional[LearnerCognitiveService] = None):
        self.service = service or get_learner_service()

    def get_learner_profile(self, student_id: str) -> LearnerProfileData:
        state = self.service.get_or_create_learner(student_id)
        return LearnerProfileData(
            student_id=state.learner_id,
            display_name=state.display_name,
            education_level=state.educational_level,
            preferred_language=state.language,
            goals=[state.learning_objective],
            mastery_scores=state.concept_mastery,
            known_misconceptions=[m.misconception_type for m in state.misconceptions],
        )

    def update_concept_mastery(self, student_id: str, concept: str, mastery: float) -> None:
        state = self.service.get_or_create_learner(student_id)
        state.concept_mastery[concept] = mastery
        state.current_concept = concept
        state.current_mastery = mastery

    def record_misconception(self, student_id: str, misconception_type: str) -> None:
        state = self.service.get_or_create_learner(student_id)
        from app.learner.models import MisconceptionMemory
        if not any(m.misconception_type == misconception_type for m in state.misconceptions):
            state.misconceptions.append(
                MisconceptionMemory(
                    misconception_type=misconception_type,
                    concept=state.current_concept or "general",
                    severity="high",
                    resolved=False,
                )
            )

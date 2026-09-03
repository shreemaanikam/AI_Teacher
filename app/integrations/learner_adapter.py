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


class LearnerCognitiveModelAdapter:
    """Interacts with Member 2's persistent learner profile and mastery tracking services."""

    def __init__(self):
        self._profiles: Dict[str, LearnerProfileData] = {}

    def get_learner_profile(self, student_id: str) -> LearnerProfileData:
        if student_id not in self._profiles:
            self._profiles[student_id] = LearnerProfileData(
                student_id=student_id,
                display_name=f"Student_{student_id}",
                education_level="beginner",
                preferred_language="en",
            )
        return self._profiles[student_id]

    def update_concept_mastery(self, student_id: str, concept: str, mastery: float) -> None:
        profile = self.get_learner_profile(student_id)
        profile.mastery_scores[concept] = mastery

    def record_misconception(self, student_id: str, misconception_type: str) -> None:
        profile = self.get_learner_profile(student_id)
        if misconception_type not in profile.known_misconceptions:
            profile.known_misconceptions.append(misconception_type)

"""
Adaptive Difficulty Controller for Module 7 (Assessment & Misconception Engine).
Adjusts question and lesson difficulty based on a rolling history of learner responses and cognitive mastery.
"""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field
from app.harness.session import DifficultyLevel


class ResponseAttemptRecord(BaseModel):
    is_correct: bool
    score: float
    confidence: float
    has_misconception: bool
    difficulty_level: DifficultyLevel
    time_taken_seconds: Optional[float] = None


class AdaptiveDifficultyController:
    """
    Computes dynamic difficulty progression using rolling history, misconception severity,
    and response performance.
    """

    def __init__(self, window_size: int = 4):
        self.window_size = window_size
        self._history: List[ResponseAttemptRecord] = []

    def record_attempt(
        self,
        is_correct: bool,
        score: float,
        confidence: float,
        has_misconception: bool,
        difficulty_level: DifficultyLevel,
        time_taken_seconds: Optional[float] = None,
    ) -> None:
        self._history.append(
            ResponseAttemptRecord(
                is_correct=is_correct,
                score=score,
                confidence=confidence,
                has_misconception=has_misconception,
                difficulty_level=difficulty_level,
                time_taken_seconds=time_taken_seconds,
            )
        )
        if len(self._history) > self.window_size * 2:
            self._history = self._history[-self.window_size * 2 :]

    def compute_next_difficulty(self, current_level: DifficultyLevel, current_mastery: float) -> DifficultyLevel:
        """
        Determines the appropriate next difficulty level.
        Requires consistent multi-step success to promote and immediate mitigation on severe struggle.
        """
        if not self._history:
            return current_level

        recent = self._history[-self.window_size :]
        correct_count = sum(1 for r in recent if r.is_correct and r.score >= 0.8)
        misconception_count = sum(1 for r in recent if r.has_misconception)
        avg_score = sum(r.score for r in recent) / len(recent)

        current_val = current_level.value

        # Demote if multiple misconceptions or very low score
        if misconception_count >= 2 or (len(recent) >= 2 and avg_score < 0.35):
            new_val = max(DifficultyLevel.FOUNDATION.value, current_val - 1)
            return DifficultyLevel(new_val)

        # Promote if strong rolling record (at least 2 consecutive high scores, mastery > 0.75)
        if len(recent) >= 2 and correct_count >= 2 and avg_score >= 0.85 and current_mastery >= 0.75:
            new_val = min(DifficultyLevel.ADVANCED.value, current_val + 1)
            return DifficultyLevel(new_val)

        return current_level

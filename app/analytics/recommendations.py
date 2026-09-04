"""
Personalized Revision and Action Recommendation Engine for Module 10.
"""

from __future__ import annotations
from typing import List
from app.analytics.models import RevisionRecommendation
from app.learner.cognitive_service import get_learner_service
from app.harness.session import TeachingStrategy


class RevisionRecommendationEngine:
    """
    Generates prioritized revision schedules based on low mastery, repeated errors, and misconception memory.
    """

    @classmethod
    def generate_recommendations(cls, learner_id: str) -> List[RevisionRecommendation]:
        learner_svc = get_learner_service()
        learner = learner_svc.get_or_create_learner(learner_id)
        recommendations: List[RevisionRecommendation] = []

        # 1. Unresolved misconceptions -> HIGH priority revision
        for m in learner.misconceptions:
            if not m.resolved or m.frequency >= 2:
                recommendations.append(
                    RevisionRecommendation(
                        concept=m.concept,
                        priority="HIGH",
                        reason=f"Targeted remediation for diagnosed misconception: '{m.misconception_type}' (Frequency: {m.frequency}).",
                        recommended_duration_minutes=10,
                        recommended_strategy=TeachingStrategy.SIMPLE_ANALOGY,
                        question_count=2,
                    )
                )

        # 2. Low mastery concepts -> MEDIUM priority revision
        for concept, mastery in learner.concept_mastery.items():
            if mastery < 0.50 and not any(r.concept == concept for r in recommendations):
                recommendations.append(
                    RevisionRecommendation(
                        concept=concept,
                        priority="MEDIUM",
                        reason=f"Foundational mastery is developing ({mastery:.2f}). Practice step-by-step problems.",
                        recommended_duration_minutes=8,
                        recommended_strategy=TeachingStrategy.STEP_BY_STEP,
                        question_count=3,
                    )
                )

        # 3. If everything is well mastered, recommend high-yield practice
        if not recommendations:
            for concept, mastery in learner.concept_mastery.items():
                if mastery >= 0.70:
                    recommendations.append(
                        RevisionRecommendation(
                            concept=concept,
                            priority="LOW",
                            reason=f"High proficiency ({mastery:.2f}). Ready for advanced extension and timed exam challenge.",
                            recommended_duration_minutes=5,
                            recommended_strategy=TeachingStrategy.DIRECT_EXPLANATION,
                            question_count=2,
                        )
                    )
                    break

        return recommendations

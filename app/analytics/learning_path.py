"""
Prerequisite-Aware Curriculum Graph & Learning Path Engine for Module 10.
"""

from __future__ import annotations
from typing import Dict, List, Optional
from app.analytics.models import LearningPath
from app.learner.cognitive_service import get_learner_service

# Prerequisite curriculum DAGs
CURRICULUM_GRAPHS: Dict[str, Dict[str, List[str]]] = {
    "physics": {
        "electric_charge_basics": [],
        "voltage_current_basics": ["electric_charge_basics"],
        "ohms_law": ["voltage_current_basics"],
        "resistors_series_parallel": ["ohms_law"],
        "kirchhoffs_laws": ["resistors_series_parallel"],
        "joules_heating": ["ohms_law"],
    },
    "programming": {
        "python_variables": [],
        "python_conditionals": ["python_variables"],
        "python_loops": ["python_conditionals"],
        "python_functions": ["python_loops"],
        "python_data_structures": ["python_functions"],
        "python_oop": ["python_data_structures"],
    },
    "mathematics": {
        "arithmetic_operations": [],
        "linear_equations": ["arithmetic_operations"],
        "quadratic_equations": ["linear_equations"],
        "polynomial_functions": ["quadratic_equations"],
        "calculus_derivatives": ["polynomial_functions"],
    },
    "biology": {
        "cell_organelles": [],
        "cellular_respiration": ["cell_organelles"],
        "photosynthesis": ["cell_organelles"],
        "dna_and_genetics": ["cell_organelles"],
    },
}


class LearningPathEngine:
    """Computes personalized sequential roadmaps respecting strict prerequisite mastery gates."""

    @classmethod
    def compute_learning_path(cls, learner_id: str, subject: str = "physics") -> LearningPath:
        learner_svc = get_learner_service()
        learner = learner_svc.get_or_create_learner(learner_id)
        graph = CURRICULUM_GRAPHS.get(subject.lower(), CURRICULUM_GRAPHS["physics"])

        completed = []
        blocked = []
        next_available = []
        recommended = []

        for topic, prereqs in graph.items():
            topic_mastery = learner.concept_mastery.get(topic, 0.0)

            # Check if all prerequisites meet mastery threshold (>= 0.60)
            prereqs_met = True
            for p in prereqs:
                p_mastery = learner.concept_mastery.get(p, 0.0)
                if p_mastery < 0.60:
                    prereqs_met = False
                    break

            if topic_mastery >= 0.75:
                completed.append(topic)
            elif prereqs_met:
                next_available.append(topic)
                if not recommended:
                    recommended.append(topic)
            else:
                blocked.append(topic)

        current = recommended[0] if recommended else (next_available[0] if next_available else list(graph.keys())[0])

        return LearningPath(
            learner_id=learner_id,
            subject=subject,
            goal=f"Master full {subject.title()} curriculum",
            current_topic=current,
            completed_topics=completed,
            next_topics=next_available,
            blocked_topics=blocked,
            recommended_topics=recommended or next_available[:2],
        )

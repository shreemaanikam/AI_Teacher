"""
Machine Learning Course Grounding & Pedagogical Correctness Engine.
Dedicated module providing high-fidelity syllabus extraction, knowledge representation,
claim verification, and pedagogical validation for College Machine Learning (Units 1-5).
"""

from app.ml_course.models import (
    MachineLearningCourse,
    MachineLearningUnit,
    ConceptDetail,
    GoldDefinition,
    GoldFormula,
    GoldAlgorithm,
    GoldExample,
    ExamTopic,
    TeachingClaim,
    ClaimStatus,
    ClaimValidationResult,
)

__all__ = [
    "MachineLearningCourse",
    "MachineLearningUnit",
    "ConceptDetail",
    "GoldDefinition",
    "GoldFormula",
    "GoldAlgorithm",
    "GoldExample",
    "ExamTopic",
    "TeachingClaim",
    "ClaimStatus",
    "ClaimValidationResult",
]

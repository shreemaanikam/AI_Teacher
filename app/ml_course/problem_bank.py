"""
STAGE ML-COURSE-08: Problem Bank Assembly Engine.
Course: AD5305 / CS4403 - Machine Learning
Institution: Chennai Institute of Technology (Autonomous)
Department: Artificial Intelligence and Data Science

Assembles, indexes, and validates all solved problems and numericals across all 5 units
from all_units_combined.pdf, unit_2_problems.pdf, unit_3_and_4_problems.pdf, and unit_5 notes.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any
from app.ml_course.models import (
    ProblemItem,
    ProblemType,
    VerificationStatus,
    SourceRef,
)
from app.ml_course.unit1_ingestion import Unit1IngestionEngine
from app.ml_course.unit2_ingestion import Unit2IngestionEngine
from app.ml_course.unit3_ingestion import Unit3IngestionEngine
from app.ml_course.unit4_ingestion import Unit4IngestionEngine
from app.ml_course.unit5_ingestion import Unit5IngestionEngine


class MLProblemBank:
    """
    Unified Problem Bank indexing every numerical problem, calculation step, formula,
    and solution across Units I through V with full source traceability.
    """

    _cache: Optional[Dict[str, ProblemItem]] = None

    @classmethod
    def get_all_problems(cls) -> List[ProblemItem]:
        if cls._cache is None:
            cls._initialize()
        return list(cls._cache.values())

    @classmethod
    def get_problem(cls, problem_id: str) -> Optional[ProblemItem]:
        if cls._cache is None:
            cls._initialize()
        return cls._cache.get(problem_id)

    @classmethod
    def get_problems_by_unit(cls, unit: int) -> List[ProblemItem]:
        if cls._cache is None:
            cls._initialize()
        return [p for p in cls._cache.values() if p.unit == unit]

    @classmethod
    def get_problems_by_concept(cls, concept_id: str) -> List[ProblemItem]:
        if cls._cache is None:
            cls._initialize()
        return [p for p in cls._cache.values() if p.concept_id == concept_id]

    @classmethod
    def get_problems_by_type(cls, problem_type: ProblemType) -> List[ProblemItem]:
        if cls._cache is None:
            cls._initialize()
        return [p for p in cls._cache.values() if p.problem_type == problem_type]

    @classmethod
    def search_problems(cls, query: str) -> List[ProblemItem]:
        if cls._cache is None:
            cls._initialize()
        q = query.lower()
        results = []
        for p in cls._cache.values():
            if (
                q in p.problem_id.lower()
                or q in p.topic.lower()
                or q in p.concept.lower()
                or q in p.question.lower()
                or q in p.final_answer.lower()
            ):
                results.append(p)
        return results

    @classmethod
    def _initialize(cls) -> None:
        cls._cache = {}
        # Aggregate problems from all 5 units
        units_engine = [
            Unit1IngestionEngine,
            Unit2IngestionEngine,
            Unit3IngestionEngine,
            Unit4IngestionEngine,
            Unit5IngestionEngine,
        ]
        for engine in units_engine:
            unit = engine.ingest()
            for p in unit.problems:
                cls._cache[p.problem_id] = p

    @classmethod
    def verify_all_problems(cls) -> Dict[str, Any]:
        """
        Verify that all indexed problems have:
        1. Valid question and non-empty solution steps.
        2. Non-empty final answer.
        3. At least one source reference with valid page > 0.
        4. VERIFIED status.
        """
        problems = cls.get_all_problems()
        audit = {
            "total_problems": len(problems),
            "by_unit": {u: len(cls.get_problems_by_unit(u)) for u in range(1, 6)},
            "missing_steps": [],
            "missing_answers": [],
            "missing_refs": [],
            "unverified": [],
            "verified": True,
        }

        for p in problems:
            if not p.solution_steps:
                audit["missing_steps"].append(p.problem_id)
            if not p.final_answer:
                audit["missing_answers"].append(p.problem_id)
            if not p.source_refs or any(r.page <= 0 for r in p.source_refs):
                audit["missing_refs"].append(p.problem_id)
            if p.verification_status != VerificationStatus.VERIFIED:
                audit["unverified"].append(p.problem_id)

        if (
            audit["missing_steps"]
            or audit["missing_answers"]
            or audit["missing_refs"]
            or audit["unverified"]
        ):
            audit["verified"] = False

        return audit

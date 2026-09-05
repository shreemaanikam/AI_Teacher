"""
STAGE ML-COURSE-10: Canonical Course Knowledge Base Engine.
Course: AD5305 / CS4403 - Machine Learning
Institution: Chennai Institute of Technology (Autonomous)
Department: Artificial Intelligence and Data Science

Unified in-memory knowledge base offering high-performance, typed lookups
for concepts, formulas, algorithms, problems, and step-by-step solutions
grounded directly in college materials.
"""

from __future__ import annotations
import json
from typing import Dict, List, Optional, Any, Union
from app.ml_course.models import (
    MachineLearningCourse,
    ConceptDetail,
    GoldFormula,
    GoldAlgorithm,
    ProblemItem,
)
from app.ml_course.canonical import CanonicalCourseBuilder
from app.ml_course.problem_bank import MLProblemBank
from app.ml_course.traceability import MLSourceTraceabilityMatrix


class CourseKnowledgeBase:
    """
    Centralized canonical knowledge repository for the Machine Learning course.
    Provides fast indexed queries by topic, ID, unit, and educational entity type.
    """

    _instance: Optional[CourseKnowledgeBase] = None

    def __init__(self):
        self._course: MachineLearningCourse = CanonicalCourseBuilder.build_canonical_course()
        self._concepts: Dict[str, ConceptDetail] = {}
        self._formulas: Dict[str, GoldFormula] = {}
        self._algorithms: Dict[str, GoldAlgorithm] = {}
        self._problems: Dict[str, ProblemItem] = {}
        self._traceability: MLSourceTraceabilityMatrix = MLSourceTraceabilityMatrix.get_instance()
        self._build_indices()

    @classmethod
    def get_instance(cls) -> CourseKnowledgeBase:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _build_indices(self) -> None:
        for unit in self._course.units.values():
            for c in unit.concepts:
                self._concepts[c.concept_id] = c
                for f in c.formulas:
                    self._formulas[f.formula_id] = f
                for a in c.algorithms:
                    self._algorithms[a.algorithm_id] = a

            for f in unit.formulas:
                self._formulas[f.formula_id] = f

            for a in unit.algorithms:
                self._algorithms[a.algorithm_id] = a

        for p in MLProblemBank.get_all_problems():
            self._problems[p.problem_id] = p

    @property
    def course(self) -> MachineLearningCourse:
        return self._course

    def get_concept(self, concept_id: str) -> Optional[ConceptDetail]:
        return self._concepts.get(concept_id)

    def get_formula(self, formula_id: str) -> Optional[GoldFormula]:
        return self._formulas.get(formula_id)

    def get_algorithm(self, algorithm_id: str) -> Optional[GoldAlgorithm]:
        return self._algorithms.get(algorithm_id)

    def get_problem(self, problem_id: str) -> Optional[ProblemItem]:
        return self._problems.get(problem_id)

    def get_solution_steps(self, problem_id: str) -> Optional[List[str]]:
        prob = self._problems.get(problem_id)
        if prob:
            return prob.solution_steps
        return None

    def get_unit_summary(self, unit: int) -> Dict[str, Any]:
        if unit not in self._course.units:
            return {}
        u = self._course.units[unit]
        probs = MLProblemBank.get_problems_by_unit(unit)
        return {
            "unit_number": u.unit_number,
            "unit_code": u.unit_code,
            "title": u.title,
            "total_concepts": len(u.concepts),
            "concept_names": [c.name for c in u.concepts],
            "total_formulas": len(u.formulas),
            "total_algorithms": len(u.algorithms),
            "total_problems": len(probs),
            "source_files": list({r.filename for r in u.source_refs}),
        }

    def get_course_overview(self) -> Dict[str, Any]:
        return {
            "course_name": self._course.course_name,
            "course_code": self._course.course_code,
            "institution": self._course.institution,
            "department": self._course.department,
            "total_units": len(self._course.units),
            "total_concepts": len(self._concepts),
            "total_formulas": len(self._formulas),
            "total_algorithms": len(self._algorithms),
            "total_problems": len(self._problems),
            "units": [self.get_unit_summary(u) for u in range(1, 6)],
        }

    def query_by_topic(self, topic: str, unit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search concepts, formulas, algorithms, and problems matching topic string.
        Optionally filter by unit.
        """
        q = topic.lower()
        results = []

        # Search concepts
        for cid, c in self._concepts.items():
            if unit is not None and c.unit_number != unit:
                continue
            if q in c.name.lower() or any(q in alias.lower() for alias in c.aliases) or q in c.summary.lower():
                results.append({
                    "entity_type": "concept",
                    "id": cid,
                    "unit": c.unit_number,
                    "title": c.name,
                    "snippet": c.summary,
                    "sources": [r.model_dump() for r in c.source_refs],
                })

        # Search formulas
        for fid, f in self._formulas.items():
            # Check unit via concept or formula
            f_unit = None
            if f.concept_id and f.concept_id in self._concepts:
                f_unit = self._concepts[f.concept_id].unit_number
            if unit is not None and f_unit is not None and f_unit != unit:
                continue
            if q in f.name.lower() or q in f.expression.lower() or q in f.context.lower():
                results.append({
                    "entity_type": "formula",
                    "id": fid,
                    "unit": f_unit,
                    "title": f.name,
                    "snippet": f.expression,
                    "sources": [r.model_dump() for r in f.source_refs],
                })

        # Search algorithms
        for aid, a in self._algorithms.items():
            a_unit = None
            if a.concept_id and a.concept_id in self._concepts:
                a_unit = self._concepts[a.concept_id].unit_number
            if unit is not None and a_unit is not None and a_unit != unit:
                continue
            if q in a.name.lower() or q in a.purpose.lower():
                results.append({
                    "entity_type": "algorithm",
                    "id": aid,
                    "unit": a_unit,
                    "title": a.name,
                    "snippet": a.purpose,
                    "sources": [r.model_dump() for r in a.source_refs],
                })

        # Search problems
        for pid, p in self._problems.items():
            if unit is not None and p.unit != unit:
                continue
            if q in p.topic.lower() or q in p.question.lower() or q in p.concept.lower():
                results.append({
                    "entity_type": "problem",
                    "id": pid,
                    "unit": p.unit,
                    "title": p.topic,
                    "snippet": p.question[:150] + "...",
                    "sources": [r.model_dump() for r in p.source_refs],
                })

        return results

    def export_canonical_json(self) -> str:
        """Export the full course structure and problems as a formatted JSON document."""
        return self._course.model_dump_json(indent=2)

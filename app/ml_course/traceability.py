"""
STAGE ML-COURSE-09: Source Traceability Matrix Engine.
Course: AD5305 / CS4403 - Machine Learning
Institution: Chennai Institute of Technology (Autonomous)
Department: Artificial Intelligence and Data Science

Maintains bidirectional, verifiable mapping between every pedagogical artifact
(concepts, formulas, algorithms, problems) and the source documents:
- all_units_combined.pdf
- unit_2_problems.pdf
- unit_3_and_4_problems.pdf
- unit_4_notes.pdf
- unit_5_notes_v1.pdf
- unit_5_notes_v2.pdf
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel, Field
from app.ml_course.models import SourceRef, VerificationStatus
from app.ml_course.canonical import CanonicalCourseBuilder
from app.ml_course.problem_bank import MLProblemBank


class TraceabilityEntry(BaseModel):
    entity_id: str
    entity_type: str  # 'concept', 'formula', 'algorithm', 'problem'
    title: str
    unit: int
    source_refs: List[SourceRef] = Field(default_factory=list)
    verification_status: VerificationStatus = VerificationStatus.VERIFIED


class MLSourceTraceabilityMatrix:
    """
    Bidirectional Traceability Matrix mapping all canonical ML syllabus entities
    to exact page numbers, document files, and chunk references.
    """

    _instance: Optional[MLSourceTraceabilityMatrix] = None

    def __init__(self):
        self._entries: Dict[str, TraceabilityEntry] = {}
        self._by_unit: Dict[int, List[str]] = {1: [], 2: [], 3: [], 4: [], 5: []}
        self._by_file: Dict[str, List[str]] = {}
        self._by_type: Dict[str, List[str]] = {
            "concept": [],
            "formula": [],
            "algorithm": [],
            "problem": [],
        }
        self._build_index()

    @classmethod
    def get_instance(cls) -> MLSourceTraceabilityMatrix:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _build_index(self) -> None:
        course = CanonicalCourseBuilder.build_canonical_course()

        # 1. Index concepts, formulas, algorithms from canonical course
        for unit in course.units.values():
            u_num = unit.unit_number

            for concept in unit.concepts:
                entry = TraceabilityEntry(
                    entity_id=concept.concept_id,
                    entity_type="concept",
                    title=concept.name,
                    unit=u_num,
                    source_refs=concept.source_refs,
                    verification_status=VerificationStatus.VERIFIED if concept.source_refs else VerificationStatus.NEEDS_VERIFICATION,
                )
                self._add_entry(entry)

            for formula in unit.formulas:
                entry = TraceabilityEntry(
                    entity_id=formula.formula_id,
                    entity_type="formula",
                    title=formula.name,
                    unit=u_num,
                    source_refs=formula.source_refs,
                    verification_status=VerificationStatus.VERIFIED if formula.source_refs else VerificationStatus.NEEDS_VERIFICATION,
                )
                self._add_entry(entry)

            for algo in unit.algorithms:
                entry = TraceabilityEntry(
                    entity_id=algo.algorithm_id,
                    entity_type="algorithm",
                    title=algo.name,
                    unit=u_num,
                    source_refs=algo.source_refs,
                    verification_status=VerificationStatus.VERIFIED if algo.source_refs else VerificationStatus.NEEDS_VERIFICATION,
                )
                self._add_entry(entry)

        # 2. Index problems from ProblemBank
        problems = MLProblemBank.get_all_problems()
        for prob in problems:
            entry = TraceabilityEntry(
                entity_id=prob.problem_id,
                entity_type="problem",
                title=prob.topic,
                unit=prob.unit,
                source_refs=prob.source_refs,
                verification_status=prob.verification_status,
            )
            self._add_entry(entry)

    def _add_entry(self, entry: TraceabilityEntry) -> None:
        self._entries[entry.entity_id] = entry
        if entry.unit in self._by_unit:
            self._by_unit[entry.unit].append(entry.entity_id)
        if entry.entity_type in self._by_type:
            self._by_type[entry.entity_type].append(entry.entity_id)

        for ref in entry.source_refs:
            fn = ref.filename
            if fn not in self._by_file:
                self._by_file[fn] = []
            if entry.entity_id not in self._by_file[fn]:
                self._by_file[fn].append(entry.entity_id)

    def get_entry(self, entity_id: str) -> Optional[TraceabilityEntry]:
        return self._entries.get(entity_id)

    def get_by_unit(self, unit: int) -> List[TraceabilityEntry]:
        ids = self._by_unit.get(unit, [])
        return [self._entries[eid] for eid in ids]

    def get_by_type(self, entity_type: str) -> List[TraceabilityEntry]:
        ids = self._by_type.get(entity_type, [])
        return [self._entries[eid] for eid in ids]

    def get_by_file(self, filename: str) -> List[TraceabilityEntry]:
        ids = self._by_file.get(filename, [])
        return [self._entries[eid] for eid in ids]

    def get_by_page(self, filename: str, page: int) -> List[TraceabilityEntry]:
        matches = []
        for entry in self._entries.values():
            for ref in entry.source_refs:
                if ref.filename == filename and ref.page == page:
                    matches.append(entry)
                    break
        return matches

    def get_coverage_statistics(self) -> Dict[str, Any]:
        """Compute full traceability coverage across the ML curriculum."""
        total = len(self._entries)
        by_type_counts = {t: len(eids) for t, eids in self._by_type.items()}
        by_unit_counts = {u: len(eids) for u, eids in self._by_unit.items()}
        all_files = list(self._by_file.keys())

        return {
            "total_entities_indexed": total,
            "by_type": by_type_counts,
            "by_unit": by_unit_counts,
            "source_files_indexed": all_files,
            "total_source_files": len(all_files),
        }

    def verify_complete_coverage(self) -> Dict[str, Any]:
        """
        Verify that 100% of canonical entities have valid source references with
        valid filenames and positive page numbers.
        """
        missing_refs = []
        invalid_pages = []
        unverified_entities = []

        for eid, entry in self._entries.items():
            if not entry.source_refs:
                missing_refs.append(eid)
                continue
            for ref in entry.source_refs:
                if ref.page <= 0:
                    invalid_pages.append((eid, ref.filename, ref.page))
            if entry.verification_status != VerificationStatus.VERIFIED:
                unverified_entities.append(eid)

        passed = (
            len(missing_refs) == 0
            and len(invalid_pages) == 0
            and len(unverified_entities) == 0
        )

        return {
            "passed": passed,
            "total_checked": len(self._entries),
            "missing_refs": missing_refs,
            "invalid_pages": invalid_pages,
            "unverified_entities": unverified_entities,
        }

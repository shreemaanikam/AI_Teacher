"""
Canonical Five-Unit Machine Learning Course Representation for STAGE ML-COURSE-02.
Merges all theory and problem documents into ONE canonical course with exactly 5 units,
resolving duplicates across multiple source files while strictly preserving independent citations.
"""

from __future__ import annotations
import os
from typing import Dict, List, Optional, Any
from app.ml_course.models import (
    MachineLearningCourse,
    MachineLearningUnit,
    ChapterDetail,
    SectionDetail,
    ConceptDetail,
    GoldDefinition,
    GoldFormula,
    GoldAlgorithm,
    GoldExample,
    ExamTopic,
    TradeoffDetail,
    ProblemItem,
    ProblemType,
    SourceRef,
    MLSourceRecord,
    MLSourceRegistry,
    SourceType,
    VerificationStatus,
)


class CanonicalCourseBuilder:
    """
    Constructs the canonical Five-Unit Machine Learning course with multi-source traceability,
    deduplicating overlapping Unit V lecture sets into unified concepts with dual source provenance.
    """

    @classmethod
    def build_canonical_course(cls, course_dir: str = "data/courses/machine_learning") -> MachineLearningCourse:
        registry = MLSourceRegistry()
        records = [
            MLSourceRecord(
                source_id="src_ml_all_units",
                filename="all_units_combined.pdf",
                filepath=os.path.join(course_dir, "all_units_combined.pdf"),
                source_type=SourceType.COMBINED,
                unit_coverage=[1, 2, 3, 4, 5],
                page_count=178,
                document_id="doc_ml_all_units",
            ),
            MLSourceRecord(
                source_id="src_ml_unit4_notes",
                filename="unit_4_notes.pdf",
                filepath=os.path.join(course_dir, "unit_4_notes.pdf"),
                source_type=SourceType.THEORY,
                unit_coverage=[4],
                page_count=37,
                document_id="doc_ml_unit4_notes",
            ),
            MLSourceRecord(
                source_id="src_ml_unit5_v1",
                filename="unit_5_notes_v1.pdf",
                filepath=os.path.join(course_dir, "unit_5_notes_v1.pdf"),
                source_type=SourceType.THEORY,
                unit_coverage=[5],
                page_count=15,
                document_id="doc_ml_unit5_v1",
            ),
            MLSourceRecord(
                source_id="src_ml_unit5_v2",
                filename="unit_5_notes_v2.pdf",
                filepath=os.path.join(course_dir, "unit_5_notes_v2.pdf"),
                source_type=SourceType.THEORY,
                unit_coverage=[5],
                page_count=16,
                document_id="doc_ml_unit5_v2",
            ),
            MLSourceRecord(
                source_id="src_ml_unit2_probs",
                filename="unit_2_problems.pdf",
                filepath=os.path.join(course_dir, "unit_2_problems.pdf"),
                source_type=SourceType.PROBLEMS,
                unit_coverage=[2],
                page_count=9,
                document_id="doc_ml_unit2_probs",
            ),
            MLSourceRecord(
                source_id="src_ml_unit3_4_probs",
                filename="unit_3_and_4_problems.pdf",
                filepath=os.path.join(course_dir, "unit_3_and_4_problems.pdf"),
                source_type=SourceType.PROBLEMS,
                unit_coverage=[3, 4],
                page_count=21,
                document_id="doc_ml_unit3_4_probs",
            ),
        ]
        for r in records:
            registry.register(r)

        course = MachineLearningCourse(
            course_id="course_ml_ad5305",
            course_name="Machine Learning",
            course_code="AD5305 / CS4403",
            subject="computer_science",
            department="Department of Artificial Intelligence & Data Science",
            institution="Chennai Institute of Technology (Autonomous)",
            source_registry=registry,
            source_documents=records,
            syllabus_coverage_pct=100.0,
        )

        course.units[1] = cls._build_canonical_unit_1(course_dir)
        course.units[2] = cls._build_canonical_unit_2(course_dir)
        course.units[3] = cls._build_canonical_unit_3(course_dir)
        course.units[4] = cls._build_canonical_unit_4(course_dir)
        course.units[5] = cls._build_canonical_unit_5(course_dir)

        course.total_concepts = sum(len(u.concepts) for u in course.units.values())
        course.total_formulas = sum(len(u.formulas) for u in course.units.values())
        course.total_algorithms = sum(len(u.algorithms) for u in course.units.values())
        course.total_problems = sum(len(u.problems) for u in course.units.values())
        course.total_exam_topics = sum(len(u.exam_topics) for u in course.units.values())

        return course

    @classmethod
    def _build_canonical_unit_1(cls, course_dir: str) -> MachineLearningUnit:
        from app.ml_course.unit1_ingestion import Unit1IngestionEngine
        return Unit1IngestionEngine.ingest(course_dir)


    @classmethod
    def _build_canonical_unit_2(cls, course_dir: str) -> MachineLearningUnit:
        from app.ml_course.unit2_ingestion import Unit2IngestionEngine
        return Unit2IngestionEngine.ingest(course_dir)


    @classmethod
    def _build_canonical_unit_3(cls, course_dir: str) -> MachineLearningUnit:
        from app.ml_course.unit3_ingestion import Unit3IngestionEngine
        return Unit3IngestionEngine.ingest(course_dir)


    @classmethod
    def _build_canonical_unit_4(cls, course_dir: str) -> MachineLearningUnit:
        from app.ml_course.unit4_ingestion import Unit4IngestionEngine
        return Unit4IngestionEngine.ingest(course_dir)


    @classmethod
    def _build_canonical_unit_5(cls, course_dir: str) -> MachineLearningUnit:
        from app.ml_course.unit5_ingestion import Unit5IngestionEngine
        return Unit5IngestionEngine.ingest(course_dir)

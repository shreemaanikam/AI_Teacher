"""
Data models and schemas for College Machine Learning Subject Grounding (Units 1-5).
Ensures strict typed representations, source provenance, mathematical rigor, and claim validation.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional, Any, Union
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class SourceType(str, Enum):
    THEORY = "THEORY"
    PROBLEMS = "PROBLEMS"
    NUMERICAL = "NUMERICAL"
    HANDWRITTEN = "HANDWRITTEN"
    LECTURE_NOTES = "LECTURE_NOTES"
    SUPPLEMENTARY = "SUPPLEMENTARY"
    COMBINED = "COMBINED"


class ClaimStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    UNCERTAIN = "UNCERTAIN"


class ProblemType(str, Enum):
    DEFINITION = "definition"
    CONCEPTUAL = "conceptual"
    NUMERICAL = "numerical"
    ALGORITHM = "algorithm"
    DERIVATION = "derivation"
    COMPARISON = "comparison"
    APPLICATION = "application"
    CODING = "coding"
    DIAGRAM = "diagram"
    EXAM_QUESTION = "exam_question"
    VIVA = "viva"


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"


class SourceRef(BaseModel):
    source_id: str
    document_id: str
    filename: str
    page: int
    section: Optional[str] = None
    chunk_id: Optional[str] = None


class MLSourceRecord(BaseModel):
    source_id: str = ""
    filename: str
    filepath: str
    source_type: SourceType = SourceType.THEORY
    unit_coverage: List[int] = Field(default_factory=list)
    page_count: int = 1
    total_pages: Optional[int] = None
    document_id: str = ""
    course_id: str = "course_ml_ad5305"
    institution: str = "Chennai Institute of Technology (Autonomous)"
    department: str = "Dept. of AI&DS"

    def model_post_init(self, __context: Any) -> None:
        if not self.source_id and self.document_id:
            self.source_id = f"src_{self.document_id}"
        elif not self.document_id and self.source_id:
            self.document_id = self.source_id.replace("src_", "doc_")
        if self.total_pages is not None:
            self.page_count = self.total_pages
        elif self.page_count:
            self.total_pages = self.page_count



class MLSourceRegistry(BaseModel):
    course_id: str = "course_ml_ad5305"
    sources: Dict[str, MLSourceRecord] = Field(default_factory=dict)

    def register(self, record: MLSourceRecord) -> None:
        self.sources[record.source_id] = record

    def get_sources_for_unit(self, unit_number: int) -> List[MLSourceRecord]:
        return [s for s in self.sources.values() if unit_number in s.unit_coverage]


class GoldDefinition(BaseModel):
    def_id: str = Field(default_factory=lambda: f"def_{uuid.uuid4().hex[:8]}")
    term: str
    definition_text: str
    author_or_source: Optional[str] = None
    source_document: str
    page: int
    chunk_id: Optional[str] = None
    source_refs: List[SourceRef] = Field(default_factory=list)


class GoldFormula(BaseModel):
    formula_id: str = Field(default_factory=lambda: f"form_{uuid.uuid4().hex[:8]}")
    concept_id: str = ""
    name: str
    expression: str
    variables: Dict[str, str] = Field(default_factory=dict)
    context: str = ""
    source_document: str
    page: int
    chunk_id: Optional[str] = None
    source_refs: List[SourceRef] = Field(default_factory=list)


class GoldAlgorithm(BaseModel):
    algorithm_id: str = Field(default_factory=lambda: f"algo_{uuid.uuid4().hex[:8]}")
    concept_id: str = ""
    name: str
    purpose: str
    inputs: List[str] = Field(default_factory=list)
    steps: List[str] = Field(default_factory=list)
    stopping_condition: Optional[str] = None
    output: str = ""
    complexity: Optional[str] = None
    source_document: str
    page: int
    chunk_id: Optional[str] = None
    source_refs: List[SourceRef] = Field(default_factory=list)


class GoldExample(BaseModel):
    example_id: str
    concept_id: str = ""
    title: str
    problem_statement: str
    solution_steps: List[str] = Field(default_factory=list)
    final_answer: Optional[str] = None
    source_document: str
    page: int
    chunk_id: Optional[str] = None
    source_refs: List[SourceRef] = Field(default_factory=list)


class TradeoffDetail(BaseModel):
    concept: str
    advantages: List[str] = Field(default_factory=list)
    disadvantages_or_limitations: List[str] = Field(default_factory=list)
    applications: List[str] = Field(default_factory=list)
    source_document: str
    page: int
    source_refs: List[SourceRef] = Field(default_factory=list)


class ExamTopic(BaseModel):
    topic_id: str = Field(default_factory=lambda: f"exam_{uuid.uuid4().hex[:8]}")
    concept: str
    concept_id: str = ""
    unit: int
    importance: str = "HIGH"  # EXAM_CRITICAL, HIGH, MEDIUM
    question_types: List[str] = Field(default_factory=list)
    revision_priority: int = 1
    source: str = ""
    page: int = 1
    is_inferred: bool = False
    source_refs: List[SourceRef] = Field(default_factory=list)


class ConceptDetail(BaseModel):
    concept_id: str
    name: str
    aliases: List[str] = Field(default_factory=list)
    unit_number: int
    chapter: str
    section: str = ""
    summary: str = ""
    definitions: List[GoldDefinition] = Field(default_factory=list)
    formulas: List[GoldFormula] = Field(default_factory=list)
    algorithms: List[GoldAlgorithm] = Field(default_factory=list)
    examples: List[GoldExample] = Field(default_factory=list)
    tradeoffs: Optional[TradeoffDetail] = None
    source_document: str
    source_pages: List[int] = Field(default_factory=list)
    source_chunk_ids: List[str] = Field(default_factory=list)
    source_refs: List[SourceRef] = Field(default_factory=list)
    importance: str = "CORE_FOUNDATION"


class SectionDetail(BaseModel):
    section_id: str
    title: str
    page_number: int = 1
    concepts: List[ConceptDetail] = Field(default_factory=list)


class ChapterDetail(BaseModel):
    chapter_id: str
    number: Optional[str] = None
    title: str
    sections: List[SectionDetail] = Field(default_factory=list)


class ProblemItem(BaseModel):
    problem_id: str = Field(default_factory=lambda: f"prob_{uuid.uuid4().hex[:8]}")
    course_id: str = "course_ml_ad5305"
    unit: int
    topic: str
    concept: str
    concept_id: str = ""
    problem_type: ProblemType = ProblemType.NUMERICAL
    difficulty: str = "intermediate"  # beginner, intermediate, advanced
    source_document: str
    source_page: int
    question: str
    given_data: Dict[str, Any] = Field(default_factory=dict)
    formula: Optional[str] = None
    solution_steps: List[str] = Field(default_factory=list)
    final_answer: str = ""
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    source_refs: List[SourceRef] = Field(default_factory=list)


class MachineLearningUnit(BaseModel):
    unit_id: str = ""
    unit_number: int  # 1 to 5
    unit_code: str = ""    # "UNIT I", "UNIT II", etc.
    title: str = ""
    unit_title: Optional[str] = None

    def model_post_init(self, __context: Any) -> None:
        if not self.unit_id:
            self.unit_id = f"unit_ml_{self.unit_number}"
        if not self.title and self.unit_title:
            self.title = self.unit_title
        elif not self.unit_title and self.title:
            self.unit_title = self.title
    syllabus_topics: List[str] = Field(default_factory=list)
    chapters: List[ChapterDetail] = Field(default_factory=list)
    sections: List[SectionDetail] = Field(default_factory=list)
    concepts: List[ConceptDetail] = Field(default_factory=list)
    definitions: List[GoldDefinition] = Field(default_factory=list)
    formulas: List[GoldFormula] = Field(default_factory=list)
    algorithms: List[GoldAlgorithm] = Field(default_factory=list)
    examples: List[GoldExample] = Field(default_factory=list)
    problems: List[ProblemItem] = Field(default_factory=list)
    tradeoffs: List[TradeoffDetail] = Field(default_factory=list)
    problem_types: List[str] = Field(default_factory=list)
    exam_topics: List[ExamTopic] = Field(default_factory=list)
    practical_topics: List[str] = Field(default_factory=list)
    source_pages: List[int] = Field(default_factory=list)
    source_documents: List[str] = Field(default_factory=list)
    source_refs: List[SourceRef] = Field(default_factory=list)


class MachineLearningCourse(BaseModel):
    course_id: str = "course_ml_ad5305"
    course_name: str = "Machine Learning"
    course_code: str = "AD5305 / CS4403"
    subject: str = "computer_science"
    department: str = "Department of Artificial Intelligence & Data Science"
    institution: str = "Chennai Institute of Technology (Autonomous)"
    units: Dict[int, MachineLearningUnit] = Field(default_factory=dict)
    source_registry: MLSourceRegistry = Field(default_factory=MLSourceRegistry)
    source_documents: List[MLSourceRecord] = Field(default_factory=list)
    total_concepts: int = 0
    total_formulas: int = 0
    total_algorithms: int = 0
    total_problems: int = 0
    total_exam_topics: int = 0
    syllabus_coverage_pct: float = 100.0

    def get_course_tree(self) -> Dict[str, Any]:
        return {
            "course_id": self.course_id,
            "course_name": self.course_name,
            "course_code": self.course_code,
            "institution": self.institution,
            "department": self.department,
            "units": [
                {
                    "unit_id": u.unit_id,
                    "unit_number": u.unit_number,
                    "code": u.unit_code,
                    "title": u.title,
                    "topics": u.syllabus_topics,
                    "concept_count": len(u.concepts),
                    "formula_count": len(u.formulas),
                    "algorithm_count": len(u.algorithms),
                    "problem_count": len(u.problems),
                    "exam_topic_count": len(u.exam_topics),
                    "sources": [s.filename for s in u.source_refs],
                }
                for u in sorted(self.units.values(), key=lambda x: x.unit_number)
            ],
            "total_concepts": self.total_concepts,
            "total_formulas": self.total_formulas,
            "total_algorithms": self.total_algorithms,
            "total_problems": self.total_problems,
            "total_exam_topics": self.total_exam_topics,
        }


class TeachingClaim(BaseModel):
    claim_id: str = Field(default_factory=lambda: f"claim_{uuid.uuid4().hex[:8]}")
    text: str
    concept_id: str
    evidence_chunk_ids: List[str] = Field(default_factory=list)
    source_citations: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    status: ClaimStatus = ClaimStatus.SUPPORTED


class ClaimValidationResult(BaseModel):
    passed: bool
    claims: List[TeachingClaim] = Field(default_factory=list)
    approved_script: str
    rejected_claims: List[TeachingClaim] = Field(default_factory=list)
    explanations: List[str] = Field(default_factory=list)
    limitation_notes: Optional[str] = None


# Backward compatibility alias
SourceDocument = MLSourceRecord

"""
STAGE ML-COURSE-35: Full Machine Learning Student Journey Engine.
Course: AD5305 / CS4403 - Machine Learning
Institution: Chennai Institute of Technology (Autonomous)
Department: Artificial Intelligence and Data Science

Implements the end-to-end collegiate student learning journey:
Student -> Machine Learning -> Units I-V -> Select Unit -> Select Concept
-> RAG -> Verified Script -> Dynamic Visual -> Human AI Teacher Avatar
-> Question -> Answer Evaluation -> Misconception -> Adaptation -> Retest
-> Mastery -> Assignment -> Feedback -> Exam Plan -> Progress Tracking.
"""

from __future__ import annotations
import uuid
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from app.ml_course.models import VerificationStatus
from app.ml_course.knowledge import CourseKnowledgeBase
from app.ml_course.rag_service import MLCourseRAGService
from app.ml_course.claim_validator import MLClaimValidator, ApprovedTeachingScript
from app.ml_course.visual_teaching import MLDynamicVisualEngine, DynamicVisualPayload
from app.ml_course.avatar_integration import MLAvatarIntegrationEngine, IntegratedTeacherExperience
from app.ml_course.question_generator import MLQuestionGenerator, GeneratedQuestion
from app.ml_course.answer_evaluator import MLAnswerEvaluator, AnswerEvaluationResult
from app.ml_course.misconception_engine import MLMisconceptionEngine, MisconceptionRemediationPlan
from app.ml_course.exam_engine import MLExamEngine, ExamSession


class StudentJourneyState(BaseModel):
    journey_id: str = Field(default_factory=lambda: f"jny_{uuid.uuid4().hex[:8]}")
    student_id: str
    student_name: str
    course_id: str = "course_ml_ad5305"
    current_unit: Optional[int] = None
    current_concept_id: Optional[str] = None
    active_lesson: Optional[IntegratedTeacherExperience] = None
    active_question: Optional[GeneratedQuestion] = None
    last_evaluation: Optional[AnswerEvaluationResult] = None
    active_remediation: Optional[MisconceptionRemediationPlan] = None
    concept_mastery: Dict[str, float] = Field(default_factory=dict)
    weak_concepts: List[str] = Field(default_factory=list)
    active_exam_plan: Optional[ExamSession] = None
    steps_completed: List[str] = Field(default_factory=list)


class MLStudentJourneyEngine:
    """
    Orchestrates the entire student journey from concept discovery to exam readiness.
    """

    _instance: Optional[MLStudentJourneyEngine] = None

    def __init__(self):
        self._kb = CourseKnowledgeBase.get_instance()
        self._rag = MLCourseRAGService.get_instance()
        self._validator = MLClaimValidator.get_instance()
        self._visual = MLDynamicVisualEngine.get_instance()
        self._avatar = MLAvatarIntegrationEngine.get_instance()
        self._questions = MLQuestionGenerator.get_instance()
        self._evaluator = MLAnswerEvaluator.get_instance()
        self._misconceptions = MLMisconceptionEngine.get_instance()
        self._exam = MLExamEngine.get_instance()

    @classmethod
    def get_instance(cls) -> MLStudentJourneyEngine:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def initialize_journey(
        self,
        student_id: str,
        student_name: str = "College Scholar",
    ) -> StudentJourneyState:
        state = StudentJourneyState(
            student_id=student_id,
            student_name=student_name,
            steps_completed=["INITIALIZE_PROFILE", "SELECT_ML_COURSE"],
        )
        return state

    def select_concept(
        self,
        state: StudentJourneyState,
        concept_id: str,
        teacher_id: str = "prof_apurva",
        language: str = "en",
    ) -> IntegratedTeacherExperience:
        concept = self._kb.get_concept(concept_id)
        if not concept:
            raise ValueError(f"Concept '{concept_id}' not found in course knowledge base.")

        state.current_unit = concept.unit_number
        state.current_concept_id = concept_id

        # 1. Deliver Verified Lesson with Avatar and Visual Board
        experience = self._avatar.deliver_concept_lesson(
            concept_id=concept_id,
            teacher_id=teacher_id,
            language=language,
        )
        state.active_lesson = experience
        state.steps_completed.extend([
            f"SELECT_UNIT_{concept.unit_number}",
            f"SELECT_CONCEPT_{concept_id}",
            "RAG_RETRIEVAL",
            "CLAIM_VERIFICATION",
            "AVATAR_NARRATION_READY",
            "DYNAMIC_VISUAL_MOUNTED",
        ])
        return experience

    def generate_concept_question(
        self,
        state: StudentJourneyState,
    ) -> GeneratedQuestion:
        if not state.current_concept_id:
            raise ValueError("No active concept selected.")
        q = self._questions.generate_question(
            concept_id=state.current_concept_id,
            unit=state.current_unit or 1,
            question_type="conceptual",
        )
        state.active_question = q
        state.steps_completed.append("QUESTION_PRESENTED")
        return q

    def process_student_response(
        self,
        state: StudentJourneyState,
        student_answer: str,
    ) -> Dict[str, Any]:
        if not state.active_question:
            raise ValueError("No active question to evaluate.")

        q = state.active_question
        eval_res = self._evaluator.evaluate_answer(
            question_text=q.question_text,
            expected_answer=q.expected_answer,
            student_response=student_answer,
            concept_id=q.concept_id,
            unit=q.unit,
            question_type=q.question_type,
        )
        state.last_evaluation = eval_res
        state.steps_completed.append("ANSWER_EVALUATED")

        remediation = None
        if not eval_res.is_correct:
            # Trigger Misconception Remediation
            rem_plan = self._misconceptions.diagnose_and_remediate(
                concept_id=q.concept_id,
                student_error=student_answer,
            )
            state.active_remediation = rem_plan
            state.weak_concepts.append(q.concept_id)
            state.concept_mastery[q.concept_id] = 0.4
            state.steps_completed.extend([
                "MISCONCEPTION_DIAGNOSED",
                "ADAPTIVE_REEXPLANATION_GENERATED",
                "NEW_VISUAL_REMEDIATION",
            ])
            remediation = rem_plan
        else:
            state.concept_mastery[q.concept_id] = 0.95
            if q.concept_id in state.weak_concepts:
                state.weak_concepts.remove(q.concept_id)
            state.steps_completed.append("MASTERY_ACHIEVED")

        return {
            "evaluation": eval_res,
            "remediation": remediation,
            "current_mastery": state.concept_mastery.get(q.concept_id, 0.5),
        }

    def create_exam_plan(
        self,
        state: StudentJourneyState,
        duration_minutes: int = 60,
    ) -> ExamSession:
        plan = self._exam.generate_exam_session(
            duration_minutes=duration_minutes,
            student_weak_concepts=state.weak_concepts,
        )
        state.active_exam_plan = plan
        state.steps_completed.append("EXAM_PLAN_CONFIGURED")
        return plan

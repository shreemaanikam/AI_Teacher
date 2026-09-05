"""
Repository pattern for AI Teacher persistence.
Provides common interface across SQLAlchemy PostgreSQL/SQLite and in-memory fallback.
"""

from __future__ import annotations
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

from app.harness.session import (
    TeachingSessionState,
    TeachingEvent,
    SessionState,
    TeachingStrategy,
    ActionType,
    DifficultyLevel,
    ActiveMisconception,
)
from app.assessment.models import (
    Question,
    QuestionType,
    QuestionOption,
    AnswerRubric,
    MisconceptionTarget,
    AnswerEvaluation,
    EvaluationVerdict,
    MisconceptionRecord,
)
from app.harness.trace import TeachingTraceEntry

logger = logging.getLogger("TeachingRepository")


class TeachingRepository(ABC):
    """Abstract interface for all teaching and assessment persistence."""

    # Sessions
    @abstractmethod
    def save_session(self, session: TeachingSessionState) -> TeachingSessionState:
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> Optional[TeachingSessionState]:
        pass

    @abstractmethod
    def list_user_sessions(self, user_id: str) -> List[TeachingSessionState]:
        pass

    # Questions & Evaluations
    @abstractmethod
    def save_question(self, question: Question) -> Question:
        pass

    @abstractmethod
    def get_question(self, question_id: str) -> Optional[Question]:
        pass

    @abstractmethod
    def save_response(self, session_id: str, evaluation: AnswerEvaluation) -> AnswerEvaluation:
        pass

    # Mastery & Misconceptions
    @abstractmethod
    def update_concept_mastery(self, user_id: str, concept_id: str, mastery: float, confidence: float = 0.8) -> float:
        pass

    @abstractmethod
    def get_user_mastery(self, user_id: str) -> Dict[str, float]:
        pass

    # Traces
    @abstractmethod
    def save_trace_entry(self, entry: TeachingTraceEntry) -> TeachingTraceEntry:
        pass

    @abstractmethod
    def get_session_traces(self, session_id: str) -> List[TeachingTraceEntry]:
        pass

    # Documents
    @abstractmethod
    def save_document(self, doc_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def list_student_documents(self, student_id: Optional[str] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def update_document_processing_state(
        self, doc_id: str, state: str, progress: Optional[int] = None, extra: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def delete_document(self, doc_id: str, student_id: Optional[str] = None) -> bool:
        pass


    # Learner Profiles
    @abstractmethod
    def save_learner_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_learner_profile(self, learner_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def list_learner_profiles(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def delete_learner_profile(self, learner_id: str) -> bool:
        pass

    # Courses
    @abstractmethod
    def save_course(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_course(self, course_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def list_student_courses(self, student_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def delete_course(self, course_id: str) -> bool:
        pass




class SQLAlchemyTeachingRepository(TeachingRepository):
    """Production database repository using SQLAlchemy (PostgreSQL / SQLite)."""

    def __init__(self):
        from app.db.session import init_db, get_session_factory
        init_db()
        self.session_factory = get_session_factory()

    def _session_to_model(self, session: TeachingSessionState):
        from app.db.models import TeachingSessionModel, TeachingStateEventModel

        model = TeachingSessionModel(
            id=session.session_id,
            user_id=session.student_id,
            lesson_id=session.lesson_id,
            topic=session.topic,
            subject=session.subject,
            current_state=session.current_state.value,
            previous_state=session.previous_state.value if session.previous_state else None,
            current_concept=session.current_concept,
            current_strategy=session.current_strategy.value,
            current_difficulty=session.current_difficulty.value if hasattr(session.current_difficulty, "value") else int(session.current_difficulty),
            language=session.language,
            consecutive_failures=session.consecutive_failures,
            consecutive_successes=session.consecutive_successes,
            version=session.version,
            concepts_list_json=json.dumps(session.concepts_list, default=str),
            concept_mastery_json=json.dumps(session.concept_mastery, default=str),
            active_misconceptions_json=json.dumps([m.model_dump(mode='json') if hasattr(m, 'model_dump') else dict(m) for m in session.active_misconceptions], default=str),
            resolved_misconceptions_json=json.dumps([m.model_dump(mode='json') if hasattr(m, 'model_dump') else dict(m) for m in session.resolved_misconceptions], default=str),
            metadata_json=json.dumps(session.metadata, default=str),
            started_at=session.started_at,
            last_activity_at=session.updated_at,
            completed_at=session.completed_at,
        )
        return model

    def _model_to_session(self, model) -> TeachingSessionState:
        active_misc = [ActiveMisconception(**m) for m in json.loads(model.active_misconceptions_json)]
        resolved_misc = [ActiveMisconception(**m) for m in json.loads(model.resolved_misconceptions_json)]

        session = TeachingSessionState(
            session_id=model.id,
            student_id=model.user_id,
            lesson_id=model.lesson_id,
            topic=model.topic,
            subject=model.subject,
            current_state=SessionState(model.current_state),
            previous_state=SessionState(model.previous_state) if model.previous_state else None,
            current_concept=model.current_concept,
            current_strategy=TeachingStrategy(model.current_strategy),
            current_difficulty=DifficultyLevel(model.current_difficulty),
            language=model.language,
            concepts_list=json.loads(model.concepts_list_json),
            concept_mastery=json.loads(model.concept_mastery_json),
            active_misconceptions=active_misc,
            resolved_misconceptions=resolved_misc,
            consecutive_failures=model.consecutive_failures,
            consecutive_successes=model.consecutive_successes,
            version=model.version,
            started_at=model.started_at,
            updated_at=model.last_activity_at,
            completed_at=model.completed_at,
            metadata=json.loads(model.metadata_json),
        )
        return session

    def save_session(self, session: TeachingSessionState) -> TeachingSessionState:
        from app.db.models import TeachingSessionModel, TeachingStateEventModel

        db = self.session_factory()
        try:
            existing = db.query(TeachingSessionModel).filter_by(id=session.session_id).first()
            if existing:
                # Update existing row
                existing.current_state = session.current_state.value
                existing.previous_state = session.previous_state.value if session.previous_state else None
                existing.current_concept = session.current_concept
                existing.current_strategy = session.current_strategy.value
                existing.current_difficulty = session.current_difficulty.value if hasattr(session.current_difficulty, "value") else int(session.current_difficulty)
                existing.language = session.language
                existing.consecutive_failures = session.consecutive_failures
                existing.consecutive_successes = session.consecutive_successes
                existing.version = session.version
                existing.concepts_list_json = json.dumps(session.concepts_list, default=str)
                existing.concept_mastery_json = json.dumps(session.concept_mastery, default=str)
                existing.active_misconceptions_json = json.dumps([m.model_dump(mode='json') if hasattr(m, 'model_dump') else dict(m) for m in session.active_misconceptions], default=str)
                existing.resolved_misconceptions_json = json.dumps([m.model_dump(mode='json') if hasattr(m, 'model_dump') else dict(m) for m in session.resolved_misconceptions], default=str)
                existing.metadata_json = json.dumps(session.metadata, default=str)
                existing.last_activity_at = session.updated_at
                existing.completed_at = session.completed_at
            else:
                new_model = self._session_to_model(session)
                db.add(new_model)

            # Record latest state event if present
            if session.events_history:
                latest_event = session.events_history[-1]
                event_model = TeachingStateEventModel(
                    session_id=session.session_id,
                    from_state=latest_event.from_state.value,
                    to_state=latest_event.to_state.value,
                    trigger_action=latest_event.trigger_action.value,
                    payload_json=json.dumps(latest_event.payload, default=str) if latest_event.payload else None,
                    timestamp=latest_event.timestamp,
                )
                db.add(event_model)

            db.commit()
            return session
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save session to database: {e}")
            raise
        finally:
            db.close()

    def get_session(self, session_id: str) -> Optional[TeachingSessionState]:
        from app.db.models import TeachingSessionModel
        db = self.session_factory()
        try:
            model = db.query(TeachingSessionModel).filter_by(id=session_id).first()
            if not model:
                return None
            return self._model_to_session(model)
        finally:
            db.close()

    def list_user_sessions(self, user_id: str) -> List[TeachingSessionState]:
        from app.db.models import TeachingSessionModel
        db = self.session_factory()
        try:
            models = db.query(TeachingSessionModel).filter_by(user_id=user_id).all()
            return [self._model_to_session(m) for m in models]
        finally:
            db.close()

    def save_question(self, question: Question) -> Question:
        from app.db.models import QuestionModel
        db = self.session_factory()
        try:
            existing = db.query(QuestionModel).filter_by(id=question.question_id).first()
            if not existing:
                model = QuestionModel(
                    id=question.question_id,
                    lesson_id=question.lesson_id,
                    concept=question.concept,
                    type=question.type.value if hasattr(question.type, "value") else str(question.type),
                    prompt=question.prompt,
                    expected_answer=question.expected_answer,
                    difficulty=question.difficulty.value if hasattr(question.difficulty, "value") else int(question.difficulty),
                    language=question.language,
                    is_final=getattr(question, "is_checkpoint", True),
                    options_json=json.dumps([o.model_dump() for o in question.options]) if question.options else None,
                    rubric_json=json.dumps(question.rubric.model_dump()),
                    misconception_targets_json=json.dumps([m.model_dump() for m in question.misconception_targets]) if question.misconception_targets else None,
                    prerequisite_concepts_json=json.dumps(question.prerequisite_concepts) if question.prerequisite_concepts else None,
                )
                db.add(model)
                db.commit()
            return question
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save question: {e}")
            raise
        finally:
            db.close()

    def get_question(self, question_id: str) -> Optional[Question]:
        from app.db.models import QuestionModel
        db = self.session_factory()
        try:
            m = db.query(QuestionModel).filter_by(id=question_id).first()
            if not m:
                return None
            options = [QuestionOption(**o) for o in json.loads(m.options_json)] if m.options_json else []
            rubric = AnswerRubric(**json.loads(m.rubric_json))
            misc_targets = [MisconceptionTarget(**t) for t in json.loads(m.misconception_targets_json)] if m.misconception_targets_json else []
            prereqs = json.loads(m.prerequisite_concepts_json) if m.prerequisite_concepts_json else []

            return Question(
                question_id=m.id,
                lesson_id=m.lesson_id,
                concept=m.concept,
                type=QuestionType(m.type),
                prompt=m.prompt,
                expected_answer=m.expected_answer,
                difficulty=DifficultyLevel(m.difficulty),
                language=m.language,
                options=options,
                rubric=rubric,
                misconception_targets=misc_targets,
                prerequisite_concepts=prereqs,
                is_checkpoint=m.is_final,
            )
        finally:
            db.close()

    def save_response(self, session_id: str, evaluation: AnswerEvaluation) -> AnswerEvaluation:
        from app.db.models import ResponseModel
        import uuid

        db = self.session_factory()
        try:
            resp_id = str(uuid.uuid4())
            model = ResponseModel(
                id=resp_id,
                session_id=session_id,
                question_id=evaluation.question_id,
                student_id=evaluation.student_id,
                student_answer=evaluation.student_answer,
                verdict=evaluation.verdict.value,
                score=evaluation.score,
                confidence=evaluation.confidence,
                feedback=evaluation.feedback,
                misconception_code=evaluation.misconception.misconception_type if evaluation.misconception else None,
                misconception_belief=evaluation.misconception.belief if evaluation.misconception else None,
                deterministic_validation=evaluation.deterministic_validation,
                evaluator_reason=evaluation.evaluator_reason,
                rubric_matches_json=json.dumps(evaluation.rubric_matches),
                rubric_misses_json=json.dumps(evaluation.rubric_misses),
            )
            db.add(model)
            db.commit()
            return evaluation
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save response: {e}")
            raise
        finally:
            db.close()

    def update_concept_mastery(self, user_id: str, concept_id: str, mastery: float, confidence: float = 0.8) -> float:
        from app.db.models import MasteryRecordModel, LearnerProfileModel
        db = self.session_factory()
        try:
            clamped_mastery = max(0.0, min(1.0, mastery))
            record = db.query(MasteryRecordModel).filter_by(user_id=user_id, concept_id=concept_id).first()
            if record:
                record.mastery = clamped_mastery
                record.confidence = confidence
                record.evidence_count += 1
            else:
                record = MasteryRecordModel(
                    user_id=user_id,
                    concept_id=concept_id,
                    mastery=clamped_mastery,
                    confidence=confidence,
                    evidence_count=1,
                )
                db.add(record)

            # Also synchronize with learner profile if exists
            prof = db.query(LearnerProfileModel).filter_by(id=user_id).first()
            if prof:
                k_map = json.loads(prof.knowledge_json) if prof.knowledge_json else {}
                k_map[concept_id] = clamped_mastery
                prof.knowledge_json = json.dumps(k_map)
                # If student mastered concept, remove from weak_concepts
                if clamped_mastery >= 0.7 and prof.weak_concepts_json:
                    wc = json.loads(prof.weak_concepts_json)
                    wc = [w for w in wc if (w if isinstance(w, str) else w.get("concept")) != concept_id]
                    prof.weak_concepts_json = json.dumps(wc)

            db.commit()
            return clamped_mastery
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update concept mastery: {e}")
            raise
        finally:
            db.close()

    def get_user_mastery(self, user_id: str) -> Dict[str, float]:
        from app.db.models import MasteryRecordModel
        db = self.session_factory()
        try:
            records = db.query(MasteryRecordModel).filter_by(user_id=user_id).all()
            return {r.concept_id: r.mastery for r in records}
        finally:
            db.close()

    def save_trace_entry(self, entry: TeachingTraceEntry) -> TeachingTraceEntry:
        from app.db.models import TeachingTraceModel
        db = self.session_factory()
        try:
            model = TeachingTraceModel(
                session_id=entry.session_id,
                trace_id=entry.trace_id,
                concept=entry.concept,
                learner_level=entry.learner_level,
                from_state=entry.from_state,
                to_state=entry.to_state,
                question_id=entry.question_id,
                student_response=entry.student_response,
                evaluation_result=entry.evaluation_result,
                misconception_type=entry.misconception_type,
                confidence=entry.confidence,
                previous_strategy=entry.previous_strategy,
                new_strategy=entry.new_strategy,
                visual_strategy=entry.visual_strategy,
                next_action=entry.next_action,
                media_status=entry.media_status,
                timestamp=entry.timestamp,
            )
            db.add(model)
            db.commit()
            return entry
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save trace entry: {e}")
            raise
        finally:
            db.close()

    def get_session_traces(self, session_id: str) -> List[TeachingTraceEntry]:
        from app.db.models import TeachingTraceModel
        db = self.session_factory()
        try:
            models = db.query(TeachingTraceModel).filter_by(session_id=session_id).order_by(TeachingTraceModel.timestamp.asc()).all()
            traces = []
            for m in models:
                traces.append(TeachingTraceEntry(
                    trace_id=m.trace_id,
                    session_id=m.session_id,
                    concept=m.concept,
                    learner_level=m.learner_level,
                    from_state=m.from_state,
                    to_state=m.to_state,
                    question_id=m.question_id,
                    student_response=m.student_response,
                    evaluation_result=m.evaluation_result,
                    misconception_type=m.misconception_type,
                    confidence=m.confidence,
                    previous_strategy=m.previous_strategy,
                    new_strategy=m.new_strategy,
                    visual_strategy=m.visual_strategy,
                    next_action=m.next_action,
                    media_status=m.media_status,
                    timestamp=m.timestamp,
                ))
            return traces
        finally:
            db.close()

    def _doc_model_to_dict(self, m) -> Dict[str, Any]:
        return {
            "id": m.id,
            "document_id": m.id,
            "student_id": m.student_id,
            "original_filename": m.original_filename,
            "file_path": m.file_path,
            "mime_type": m.mime_type,
            "extension": m.extension,
            "file_size_bytes": m.file_size_bytes,
            "sha256_checksum": m.sha256_checksum,
            "detected_language": m.detected_language,
            "detected_title": m.detected_title,
            "detected_subject": m.detected_subject,
            "course": m.course,
            "chapter": m.chapter,
            "page_count": m.page_count,
            "ocr_provider_used": m.ocr_provider_used,
            "processing_state": m.processing_state,
            "concepts": json.loads(m.concepts_json) if m.concepts_json else [],
            "structure": json.loads(m.structure_json) if m.structure_json else None,
            "understanding": json.loads(m.understanding_json) if m.understanding_json else None,
            "uploaded_at": m.uploaded_at.isoformat() if m.uploaded_at else None,
        }

    def save_document(self, doc_data: Dict[str, Any]) -> Dict[str, Any]:
        from app.db.models import UploadedDocumentModel
        db = self.session_factory()
        try:
            doc_id = doc_data.get("id") or doc_data.get("document_id")
            existing = db.query(UploadedDocumentModel).filter_by(id=doc_id).first()
            if existing:
                for k, v in doc_data.items():
                    if hasattr(existing, k) and k not in ("id", "uploaded_at"):
                        setattr(existing, k, v)
                db.commit()
                return self._doc_model_to_dict(existing)
            else:
                model = UploadedDocumentModel(
                    id=doc_id,
                    student_id=doc_data.get("student_id", "default_student"),
                    original_filename=doc_data.get("original_filename", "untitled"),
                    file_path=doc_data.get("file_path", ""),
                    mime_type=doc_data.get("mime_type", "application/octet-stream"),
                    extension=doc_data.get("extension", ""),
                    file_size_bytes=doc_data.get("file_size_bytes", 0),
                    sha256_checksum=doc_data.get("sha256_checksum", ""),
                    detected_language=doc_data.get("detected_language", "en"),
                    detected_title=doc_data.get("detected_title"),
                    detected_subject=doc_data.get("detected_subject"),
                    course=doc_data.get("course"),
                    chapter=doc_data.get("chapter"),
                    page_count=doc_data.get("page_count", 1),
                    ocr_provider_used=doc_data.get("ocr_provider_used", "native_extractor"),
                    processing_state=doc_data.get("processing_state", "READY"),
                    concepts_json=doc_data.get("concepts_json", "[]"),
                    structure_json=doc_data.get("structure_json"),
                    understanding_json=doc_data.get("understanding_json"),
                )
                db.add(model)
                db.commit()
                return self._doc_model_to_dict(model)
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save document {doc_data.get('id')}: {e}")
            raise
        finally:
            db.close()

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        from app.db.models import UploadedDocumentModel
        db = self.session_factory()
        try:
            model = db.query(UploadedDocumentModel).filter_by(id=doc_id).first()
            if not model:
                return None
            return self._doc_model_to_dict(model)
        finally:
            db.close()

    def list_student_documents(self, student_id: Optional[str] = None) -> List[Dict[str, Any]]:
        from app.db.models import UploadedDocumentModel
        db = self.session_factory()
        try:
            query = db.query(UploadedDocumentModel)
            if student_id and student_id != "all":
                query = query.filter_by(student_id=student_id)
            models = query.order_by(UploadedDocumentModel.uploaded_at.desc()).all()
            return [self._doc_model_to_dict(m) for m in models]
        finally:
            db.close()

    def update_document_processing_state(
        self, doc_id: str, state: str, progress: Optional[int] = None, extra: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        from app.db.models import UploadedDocumentModel
        db = self.session_factory()
        try:
            model = db.query(UploadedDocumentModel).filter_by(id=doc_id).first()
            if not model:
                return None
            model.processing_state = state
            if extra:
                for k, v in extra.items():
                    if hasattr(model, k):
                        setattr(model, k, v)
            db.commit()
            return self._doc_model_to_dict(model)
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update document processing state: {e}")
            raise
        finally:
            db.close()

    def delete_document(self, doc_id: str, student_id: Optional[str] = None) -> bool:
        from app.db.models import UploadedDocumentModel
        import os
        db = self.session_factory()
        try:
            query = db.query(UploadedDocumentModel).filter_by(id=doc_id)
            if student_id and student_id != "all":
                query = query.filter_by(student_id=student_id)
            model = query.first()
            if model:
                if model.file_path and os.path.exists(model.file_path):
                    try:
                        os.remove(model.file_path)
                    except Exception:
                        pass
                db.delete(model)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False
        finally:
            db.close()

    def _profile_model_to_dict(self, m) -> Dict[str, Any]:
        exam_dates = {}
        if getattr(m, "exam_dates_json", None):
            try:
                exam_dates = json.loads(m.exam_dates_json)
            except Exception:
                exam_dates = {}
        elif getattr(m, "exam_date", None):
            exam_dates = {getattr(m, "subject", "General") or "General": m.exam_date}

        courses = []
        if getattr(m, "courses_json", None):
            try:
                courses = json.loads(m.courses_json)
            except Exception:
                courses = []

        return {
            "id": m.id,
            "learner_id": m.id,
            "student_id": m.id,
            "name": m.display_name,
            "display_name": m.display_name,
            "college": getattr(m, "college", None) or getattr(m, "college_grade", None),
            "department": getattr(m, "department", None),
            "degree": getattr(m, "degree", None),
            "year": getattr(m, "year", 1) or 1,
            "semester": getattr(m, "semester", 1) or 1,
            "available_study_hours": getattr(m, "available_study_hours", 10.0) or 10.0,
            "educational_level": m.educational_level,
            "preferred_language": m.preferred_language,
            "material_language": m.material_language,
            "teaching_style": m.teaching_style,
            "learning_style": m.preferred_teaching_style or m.teaching_style,
            "available_time": m.available_time,
            "custom_time_minutes": m.custom_time_minutes,
            "desired_depth": m.desired_depth,
            "subject": m.subject,
            "college_grade": m.college_grade,
            "target_exam": m.target_exam,
            "exam_date": m.exam_date,
            "exam_dates": exam_dates,
            "courses": courses,
            "target_score": m.target_score,
            "learning_speed": m.learning_speed,
            "preferred_teaching_style": m.preferred_teaching_style,
            "knowledge": json.loads(m.knowledge_json) if m.knowledge_json else {},
            "weak_concepts": json.loads(m.weak_concepts_json) if m.weak_concepts_json else [],
            "strengths": json.loads(m.strengths_json) if m.strengths_json else [],
            "misconceptions": json.loads(m.misconceptions_json) if m.misconceptions_json else [],
            "study_history": json.loads(m.study_history_json) if m.study_history_json else {},
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "updated_at": m.updated_at.isoformat() if m.updated_at else None,
        }

    def save_learner_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        from app.db.models import LearnerProfileModel
        db = self.session_factory()
        try:
            lid = profile_data.get("id") or profile_data.get("learner_id") or profile_data.get("student_id")
            existing = db.query(LearnerProfileModel).filter_by(id=lid).first()

            disp_name = profile_data.get("name") or profile_data.get("display_name")
            college = profile_data.get("college")
            department = profile_data.get("department")
            degree = profile_data.get("degree")
            year = profile_data.get("year")
            semester = profile_data.get("semester")
            study_hours = profile_data.get("available_study_hours") or profile_data.get("study_hours")
            learning_style = profile_data.get("learning_style") or profile_data.get("preferred_teaching_style")
            exam_dates_val = profile_data.get("exam_dates")
            courses_val = profile_data.get("courses") or profile_data.get("enrolled_courses")

            exam_dates_json = json.dumps(exam_dates_val, default=str) if isinstance(exam_dates_val, dict) else (str(exam_dates_val) if exam_dates_val else "{}")
            courses_json = json.dumps(courses_val, default=str) if isinstance(courses_val, list) else (str(courses_val) if courses_val else "[]")

            weak_json = json.dumps(profile_data.get("weak_concepts", []), default=str) if isinstance(profile_data.get("weak_concepts"), list) else profile_data.get("weak_concepts_json", "[]")
            strengths_json = json.dumps(profile_data.get("strengths", []), default=str) if isinstance(profile_data.get("strengths"), list) else profile_data.get("strengths_json", "[]")
            misc_json = json.dumps(profile_data.get("misconceptions", []), default=str) if isinstance(profile_data.get("misconceptions"), list) else profile_data.get("misconceptions_json", "[]")
            know_json = json.dumps(profile_data.get("knowledge", {}), default=str) if isinstance(profile_data.get("knowledge"), dict) else profile_data.get("knowledge_json", "{}")
            hist_json = json.dumps(profile_data.get("study_history", {}), default=str) if isinstance(profile_data.get("study_history"), dict) else profile_data.get("study_history_json", "{}")

            if existing:
                if disp_name:
                    existing.display_name = disp_name
                if college:
                    existing.college = college
                if department:
                    existing.department = department
                if degree:
                    existing.degree = degree
                if year is not None:
                    existing.year = int(year)
                if semester is not None:
                    existing.semester = int(semester)
                if study_hours is not None:
                    existing.available_study_hours = float(study_hours)
                if learning_style:
                    existing.preferred_teaching_style = learning_style

                existing.educational_level = profile_data.get("educational_level", existing.educational_level)
                existing.preferred_language = profile_data.get("preferred_language", existing.preferred_language)
                existing.material_language = profile_data.get("material_language", existing.material_language)
                existing.teaching_style = profile_data.get("teaching_style", existing.teaching_style)
                existing.available_time = profile_data.get("available_time", existing.available_time)
                existing.custom_time_minutes = profile_data.get("custom_time_minutes", existing.custom_time_minutes)
                existing.desired_depth = profile_data.get("desired_depth", existing.desired_depth)
                existing.subject = profile_data.get("subject", existing.subject)
                existing.college_grade = profile_data.get("college_grade", existing.college_grade)
                existing.target_exam = profile_data.get("target_exam", existing.target_exam)
                existing.exam_date = profile_data.get("exam_date", existing.exam_date)
                if exam_dates_val is not None:
                    existing.exam_dates_json = exam_dates_json
                if courses_val is not None:
                    existing.courses_json = courses_json
                existing.target_score = str(profile_data.get("target_score", existing.target_score or ""))
                existing.learning_speed = profile_data.get("learning_speed", existing.learning_speed)
                existing.knowledge_json = know_json
                existing.weak_concepts_json = weak_json
                existing.strengths_json = strengths_json
                existing.misconceptions_json = misc_json
                existing.study_history_json = hist_json
                db.commit()
                return self._profile_model_to_dict(existing)
            else:
                model = LearnerProfileModel(
                    id=lid,
                    display_name=disp_name or "Learner",
                    college=college,
                    department=department,
                    degree=degree,
                    year=int(year) if year is not None else 1,
                    semester=int(semester) if semester is not None else 1,
                    available_study_hours=float(study_hours) if study_hours is not None else 10.0,
                    exam_dates_json=exam_dates_json,
                    courses_json=courses_json,
                    educational_level=profile_data.get("educational_level", "beginner"),
                    preferred_language=profile_data.get("preferred_language", "en"),
                    material_language=profile_data.get("material_language", "en"),
                    teaching_style=profile_data.get("teaching_style", "SIMPLE"),
                    available_time=profile_data.get("available_time", "20_MIN"),
                    custom_time_minutes=profile_data.get("custom_time_minutes", 20),
                    desired_depth=profile_data.get("desired_depth", "foundation"),
                    subject=profile_data.get("subject", "physics"),
                    college_grade=profile_data.get("college_grade"),
                    target_exam=profile_data.get("target_exam"),
                    exam_date=profile_data.get("exam_date"),
                    target_score=str(profile_data.get("target_score", "")),
                    learning_speed=profile_data.get("learning_speed", "moderate"),
                    preferred_teaching_style=learning_style or "FORMAL_RIGOROUS",
                    knowledge_json=know_json,
                    weak_concepts_json=weak_json,
                    strengths_json=strengths_json,
                    misconceptions_json=misc_json,
                    study_history_json=hist_json,
                )
                db.add(model)
                db.commit()
                return self._profile_model_to_dict(model)
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save learner profile {profile_data.get('id')}: {e}")
            raise
        finally:
            db.close()

    def get_learner_profile(self, learner_id: str) -> Optional[Dict[str, Any]]:
        from app.db.models import LearnerProfileModel
        db = self.session_factory()
        try:
            model = db.query(LearnerProfileModel).filter_by(id=learner_id).first()
            if not model:
                return None
            return self._profile_model_to_dict(model)
        finally:
            db.close()

    def list_learner_profiles(self) -> List[Dict[str, Any]]:
        from app.db.models import LearnerProfileModel
        db = self.session_factory()
        try:
            models = db.query(LearnerProfileModel).order_by(LearnerProfileModel.created_at.desc()).all()
            return [self._profile_model_to_dict(m) for m in models]
        finally:
            db.close()

    def delete_learner_profile(self, learner_id: str) -> bool:
        from app.db.models import LearnerProfileModel
        db = self.session_factory()
        try:
            model = db.query(LearnerProfileModel).filter_by(id=learner_id).first()
            if model:
                db.delete(model)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete learner profile {learner_id}: {e}")
            return False
        finally:
            db.close()

    def _course_model_to_dict(self, m) -> Dict[str, Any]:
        units = []
        if getattr(m, "units_json", None):
            try:
                units = json.loads(m.units_json)
            except Exception:
                units = []
        concepts = []
        if getattr(m, "concepts_json", None):
            try:
                concepts = json.loads(m.concepts_json)
            except Exception:
                concepts = []

        return {
            "id": m.id,
            "course_id": m.id,
            "student_id": m.student_id,
            "code": m.code,
            "name": m.name,
            "department": m.department,
            "semester": m.semester,
            "description": m.description,
            "exam_date": m.exam_date,
            "target_score": m.target_score,
            "status": m.status,
            "units": units,
            "concepts": concepts,
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "updated_at": m.updated_at.isoformat() if m.updated_at else None,
        }

    def save_course(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        from app.db.models import CourseModel
        import uuid
        db = self.session_factory()
        try:
            cid = course_data.get("id") or course_data.get("course_id") or f"crs_{uuid.uuid4().hex[:8]}"
            student_id = course_data.get("student_id") or "default_student"
            existing = db.query(CourseModel).filter_by(id=cid).first()

            units_val = course_data.get("units", [])
            concepts_val = course_data.get("concepts", [])
            units_json = json.dumps(units_val, default=str) if isinstance(units_val, list) else str(units_val)
            concepts_json = json.dumps(concepts_val, default=str) if isinstance(concepts_val, list) else str(concepts_val)

            if existing:
                existing.student_id = course_data.get("student_id", existing.student_id)
                existing.code = course_data.get("code", existing.code)
                existing.name = course_data.get("name", existing.name)
                existing.department = course_data.get("department", existing.department)
                existing.semester = int(course_data.get("semester", existing.semester))
                existing.description = course_data.get("description", existing.description)
                existing.exam_date = course_data.get("exam_date", existing.exam_date)
                existing.target_score = course_data.get("target_score", existing.target_score)
                existing.status = course_data.get("status", existing.status)
                if "units" in course_data:
                    existing.units_json = units_json
                if "concepts" in course_data:
                    existing.concepts_json = concepts_json
                db.commit()
                return self._course_model_to_dict(existing)
            else:
                model = CourseModel(
                    id=cid,
                    student_id=student_id,
                    code=course_data.get("code") or "GEN101",
                    name=course_data.get("name") or "General Course",
                    department=course_data.get("department"),
                    semester=int(course_data.get("semester", 1)),
                    description=course_data.get("description"),
                    exam_date=course_data.get("exam_date"),
                    target_score=course_data.get("target_score", "90%"),
                    status=course_data.get("status", "ACTIVE"),
                    units_json=units_json,
                    concepts_json=concepts_json,
                )
                db.add(model)
                db.commit()
                return self._course_model_to_dict(model)
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save course {course_data.get('id')}: {e}")
            raise
        finally:
            db.close()

    def get_course(self, course_id: str) -> Optional[Dict[str, Any]]:
        from app.db.models import CourseModel
        db = self.session_factory()
        try:
            m = db.query(CourseModel).filter_by(id=course_id).first()
            return self._course_model_to_dict(m) if m else None
        finally:
            db.close()

    def list_student_courses(self, student_id: str) -> List[Dict[str, Any]]:
        from app.db.models import CourseModel
        db = self.session_factory()
        try:
            models = db.query(CourseModel).filter_by(student_id=student_id).order_by(CourseModel.created_at.asc()).all()
            return [self._course_model_to_dict(m) for m in models]
        finally:
            db.close()

    def delete_course(self, course_id: str) -> bool:
        from app.db.models import CourseModel
        db = self.session_factory()
        try:
            m = db.query(CourseModel).filter_by(id=course_id).first()
            if m:
                db.delete(m)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete course {course_id}: {e}")
            return False
        finally:
            db.close()





class MemoryTeachingRepository(TeachingRepository):
    """In-memory dictionary fallback repository."""

    def __init__(self):
        self._sessions: Dict[str, TeachingSessionState] = {}
        self._questions: Dict[str, Question] = {}
        self._responses: List[Dict[str, Any]] = []
        self._mastery: Dict[str, Dict[str, float]] = {}
        self._traces: Dict[str, List[TeachingTraceEntry]] = {}
        self._documents: Dict[str, Dict[str, Any]] = {}

    def save_session(self, session: TeachingSessionState) -> TeachingSessionState:
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[TeachingSessionState]:
        return self._sessions.get(session_id)

    def list_user_sessions(self, user_id: str) -> List[TeachingSessionState]:
        return [s for s in self._sessions.values() if s.student_id == user_id]

    def save_question(self, question: Question) -> Question:
        self._questions[question.question_id] = question
        return question

    def get_question(self, question_id: str) -> Optional[Question]:
        return self._questions.get(question_id)

    def save_response(self, session_id: str, evaluation: AnswerEvaluation) -> AnswerEvaluation:
        self._responses.append({"session_id": session_id, "evaluation": evaluation})
        return evaluation

    def update_concept_mastery(self, user_id: str, concept_id: str, mastery: float, confidence: float = 0.8) -> float:
        if user_id not in self._mastery:
            self._mastery[user_id] = {}
        clamped = max(0.0, min(1.0, mastery))
        self._mastery[user_id][concept_id] = clamped
        if user_id in self._learner_profiles:
            prof = self._learner_profiles[user_id]
            if "knowledge" not in prof:
                prof["knowledge"] = {}
            prof["knowledge"][concept_id] = clamped
        return clamped

    def get_user_mastery(self, user_id: str) -> Dict[str, float]:
        return self._mastery.get(user_id, {})

    def save_trace_entry(self, entry: TeachingTraceEntry) -> TeachingTraceEntry:
        if entry.session_id not in self._traces:
            self._traces[entry.session_id] = []
        self._traces[entry.session_id].append(entry)
        return entry

    def get_session_traces(self, session_id: str) -> List[TeachingTraceEntry]:
        return self._traces.get(session_id, [])

    def save_document(self, doc_data: Dict[str, Any]) -> Dict[str, Any]:
        doc_id = doc_data.get("id") or doc_data.get("document_id")
        record = dict(doc_data)
        record["id"] = doc_id
        record["document_id"] = doc_id
        if "concepts_json" in record and "concepts" not in record:
            try:
                record["concepts"] = json.loads(record["concepts_json"])
            except Exception:
                record["concepts"] = []
        if "structure_json" in record and "structure" not in record and record["structure_json"]:
            try:
                record["structure"] = json.loads(record["structure_json"])
            except Exception:
                pass
        if "understanding_json" in record and "understanding" not in record and record["understanding_json"]:
            try:
                record["understanding"] = json.loads(record["understanding_json"])
            except Exception:
                pass
        self._documents[doc_id] = record
        return record

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        return self._documents.get(doc_id)

    def list_student_documents(self, student_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if not student_id or student_id == "all":
            return list(self._documents.values())
        return [d for d in self._documents.values() if d.get("student_id") == student_id]

    def update_document_processing_state(
        self, doc_id: str, state: str, progress: Optional[int] = None, extra: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        if doc_id in self._documents:
            self._documents[doc_id]["processing_state"] = state
            if extra:
                self._documents[doc_id].update(extra)
            return self._documents[doc_id]
        return None

    def delete_document(self, doc_id: str, student_id: Optional[str] = None) -> bool:
        if not hasattr(self, "_documents"):
            self._documents = {}
        if doc_id in self._documents:
            if student_id and student_id != "all" and self._documents[doc_id].get("student_id") != student_id:
                return False
            del self._documents[doc_id]
            return True
        return False


    def save_learner_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        lid = profile_data.get("id") or profile_data.get("learner_id") or profile_data.get("student_id")
        record = dict(profile_data)
        record["id"] = lid
        record["learner_id"] = lid
        record["student_id"] = lid
        if not hasattr(self, "_learner_profiles"):
            self._learner_profiles = {}
        self._learner_profiles[lid] = record
        return record

    def get_learner_profile(self, learner_id: str) -> Optional[Dict[str, Any]]:
        if not hasattr(self, "_learner_profiles"):
            self._learner_profiles = {}
        return self._learner_profiles.get(learner_id)

    def list_learner_profiles(self) -> List[Dict[str, Any]]:
        if not hasattr(self, "_learner_profiles"):
            self._learner_profiles = {}
        return list(self._learner_profiles.values())

    def delete_learner_profile(self, learner_id: str) -> bool:
        if not hasattr(self, "_learner_profiles"):
            self._learner_profiles = {}
        if learner_id in self._learner_profiles:
            del self._learner_profiles[learner_id]
            return True
        return False

    def save_course(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        if not hasattr(self, "_courses"):
            self._courses = {}
        import uuid
        cid = course_data.get("id") or course_data.get("course_id") or f"crs_{uuid.uuid4().hex[:8]}"
        record = dict(course_data)
        record["id"] = cid
        record["course_id"] = cid
        self._courses[cid] = record
        return record

    def get_course(self, course_id: str) -> Optional[Dict[str, Any]]:
        if not hasattr(self, "_courses"):
            self._courses = {}
        return self._courses.get(course_id)

    def list_student_courses(self, student_id: str) -> List[Dict[str, Any]]:
        if not hasattr(self, "_courses"):
            self._courses = {}
        return [c for c in self._courses.values() if c.get("student_id") == student_id]

    def delete_course(self, course_id: str) -> bool:
        if not hasattr(self, "_courses"):
            self._courses = {}
        if course_id in self._courses:
            del self._courses[course_id]
            return True
        return False






# Singleton repository instance
_REPOSITORY: Optional[TeachingRepository] = None


def get_teaching_repository() -> TeachingRepository:
    """
    Returns the production database repository, or falls back to in-memory on failure.
    """
    global _REPOSITORY
    if _REPOSITORY is None:
        try:
            _REPOSITORY = SQLAlchemyTeachingRepository()
            logger.info("Initialized SQLAlchemyTeachingRepository successfully.")
        except Exception as e:
            logger.warning(f"Failed to initialize database repository, using MemoryTeachingRepository fallback: {e}")
            _REPOSITORY = MemoryTeachingRepository()
    return _REPOSITORY

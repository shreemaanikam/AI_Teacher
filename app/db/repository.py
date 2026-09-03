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
            concepts_list_json=json.dumps(session.concepts_list),
            concept_mastery_json=json.dumps(session.concept_mastery),
            active_misconceptions_json=json.dumps([m.model_dump() for m in session.active_misconceptions]),
            resolved_misconceptions_json=json.dumps([m.model_dump() for m in session.resolved_misconceptions]),
            metadata_json=json.dumps(session.metadata),
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
                existing.concepts_list_json = json.dumps(session.concepts_list)
                existing.concept_mastery_json = json.dumps(session.concept_mastery)
                existing.active_misconceptions_json = json.dumps([m.model_dump() for m in session.active_misconceptions])
                existing.resolved_misconceptions_json = json.dumps([m.model_dump() for m in session.resolved_misconceptions])
                existing.metadata_json = json.dumps(session.metadata)
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
                    payload_json=json.dumps(latest_event.payload) if latest_event.payload else None,
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
        from app.db.models import MasteryRecordModel
        db = self.session_factory()
        try:
            record = db.query(MasteryRecordModel).filter_by(user_id=user_id, concept_id=concept_id).first()
            if record:
                record.mastery = max(0.0, min(1.0, mastery))
                record.confidence = confidence
                record.evidence_count += 1
            else:
                record = MasteryRecordModel(
                    user_id=user_id,
                    concept_id=concept_id,
                    mastery=max(0.0, min(1.0, mastery)),
                    confidence=confidence,
                    evidence_count=1,
                )
                db.add(record)
            db.commit()
            return record.mastery
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


class MemoryTeachingRepository(TeachingRepository):
    """In-memory dictionary fallback repository."""

    def __init__(self):
        self._sessions: Dict[str, TeachingSessionState] = {}
        self._questions: Dict[str, Question] = {}
        self._responses: List[Dict[str, Any]] = []
        self._mastery: Dict[str, Dict[str, float]] = {}
        self._traces: Dict[str, List[TeachingTraceEntry]] = {}

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
        self._mastery[user_id][concept_id] = max(0.0, min(1.0, mastery))
        return self._mastery[user_id][concept_id]

    def get_user_mastery(self, user_id: str) -> Dict[str, float]:
        return self._mastery.get(user_id, {})

    def save_trace_entry(self, entry: TeachingTraceEntry) -> TeachingTraceEntry:
        if entry.session_id not in self._traces:
            self._traces[entry.session_id] = []
        self._traces[entry.session_id].append(entry)
        return entry

    def get_session_traces(self, session_id: str) -> List[TeachingTraceEntry]:
        return self._traces.get(session_id, [])


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

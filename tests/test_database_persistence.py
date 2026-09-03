"""
Tests for SQLAlchemy Database Persistence and Repository Layer.
"""

import os
import pytest
from app.db.session import init_db, get_engine
from app.db.repository import SQLAlchemyTeachingRepository, MemoryTeachingRepository
from app.harness.session import TeachingSessionState, SessionState, TeachingStrategy, DifficultyLevel
from app.harness.state_machine import TeachingStateMachine
from app.harness.orchestrator import MasterTeachingOrchestrator
from app.assessment.models import Question, QuestionType, AnswerRubric


def test_sqlite_database_initialization():
    engine = get_engine()
    assert engine is not None
    init_db()


def test_sqlalchemy_session_save_and_reload():
    repo = SQLAlchemyTeachingRepository()
    
    session = TeachingSessionState(
        student_id="student_db_test_01",
        lesson_id="lesson_db_test_01",
        topic="Electromagnetism",
        current_concept="magnetic_flux",
        concepts_list=["magnetic_flux", "faradays_law"],
        current_strategy=TeachingStrategy.DIRECT_EXPLANATION,
        current_difficulty=DifficultyLevel.BASIC,
    )
    
    # Save session
    saved = repo.save_session(session)
    assert saved.session_id == session.session_id

    # Reload from fresh DB query
    reloaded = repo.get_session(session.session_id)
    assert reloaded is not None
    assert reloaded.student_id == "student_db_test_01"
    assert reloaded.topic == "Electromagnetism"
    assert reloaded.current_concept == "magnetic_flux"
    assert reloaded.concepts_list == ["magnetic_flux", "faradays_law"]
    assert reloaded.current_strategy == TeachingStrategy.DIRECT_EXPLANATION


def test_mastery_persistence_across_sessions():
    repo = SQLAlchemyTeachingRepository()
    user_id = "student_mastery_test_01"
    
    # Update mastery
    mastery_1 = repo.update_concept_mastery(user_id, "ohms_law", 0.75, confidence=0.9)
    assert mastery_1 == 0.75

    # Retrieve mastery map
    mastery_map = repo.get_user_mastery(user_id)
    assert "ohms_law" in mastery_map
    assert mastery_map["ohms_law"] == 0.75


def test_question_persistence():
    repo = SQLAlchemyTeachingRepository()
    q = Question(
        question_id="q_db_test_01",
        lesson_id="lesson_db_test_01",
        concept="magnetic_flux",
        type=QuestionType.CONCEPTUAL,
        prompt="Define magnetic flux through a closed surface.",
        expected_answer="The net magnetic flux through any closed surface is zero (Gauss's law for magnetism).",
        rubric=AnswerRubric(key_terms=["zero", "closed surface"]),
    )
    
    repo.save_question(q)
    fetched_q = repo.get_question("q_db_test_01")
    assert fetched_q is not None
    assert fetched_q.concept == "magnetic_flux"
    assert fetched_q.expected_answer == q.expected_answer

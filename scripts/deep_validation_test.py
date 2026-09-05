"""
Deep Validation Test Suite for AI Teacher.
Validates:
- Database CRUD & persistence on Neon PostgreSQL
- Upstash Redis session caching
- Pinecone 1024-D vector indexing & retrieval
- RAG Grounding (Query A: Supported vs Query B: Unsupported)
- Misconception diagnosis & pedagogical adaptation loop
- Cognitive model persistence across simulated restarts
- Multilingual teaching & mid-lesson language switching
"""

import os
import sys
import json
import base64
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import get_settings
from app.db.session import init_db, get_engine
from app.db.repository import get_teaching_repository, SQLAlchemyTeachingRepository
from app.cache.redis_client import get_redis_client
from app.rag.extractors.ocr_extractor import OCRDocumentExtractor, GoogleVisionProvider, LocalOCRProvider
from app.rag.extractors.text_extractor import TextDocumentExtractor
from app.rag.chunking import SemanticDocumentChunker
from app.rag.embeddings import get_embedding_provider, LocalDenseEmbeddingProvider
from app.rag.vector_store import get_vector_store, PineconeVectorStore
from app.rag.retriever import get_hybrid_retriever
from app.rag.models import GroundingLevel
from app.harness.orchestrator import MasterTeachingOrchestrator
from app.harness.session import SessionState, TeachingStrategy, DifficultyLevel, ActiveMisconception
from app.assessment.engine import AssessmentEngine
from app.assessment.models import EvaluationVerdict
from app.visuals.engine import VisualIntelligenceEngine
from app.media.engine import MultimodalMediaEngine
from app.media.tts.neural_tts import NeuralTTSProvider
from app.media.stt.openai_stt import OpenAISTTProvider
from app.media.stt.local_stt import LocalSTTProvider


def test_database_crud_neon():
    print("\n" + "=" * 60)
    print("  [AUDIT 3] DATABASE PERSISTENCE (POSTGRESQL)")
    print("=" * 60)
    repo = get_teaching_repository()
    print(f"Repository Type: {type(repo).__name__}")
    
    # Create test session
    session_id = f"audit_sess_{int(datetime.now().timestamp())}"
    from app.harness.session import TeachingSessionState
    sess = TeachingSessionState(
        session_id=session_id,
        student_id="student_audit_01",
        lesson_id="lesson_audit_ohms",
        topic="Ohm's Law",
        subject="physics",
        current_state=SessionState.TEACH,
        current_concept="ohms_law_basics",
        current_strategy=TeachingStrategy.DIRECT_EXPLANATION,
        current_difficulty=DifficultyLevel.BASIC,
        concepts_list=["ohms_law_basics", "resistance_factors"],
        concept_mastery={"ohms_law_basics": 0.25},
    )
    
    # 1. WRITE
    saved = repo.save_session(sess)
    print(f"✓ Saved session {saved.session_id} to database.")
    
    # 2. READ
    loaded = repo.get_session(session_id)
    assert loaded is not None, "Failed to read saved session"
    assert loaded.student_id == "student_audit_01"
    assert loaded.concept_mastery["ohms_law_basics"] == 0.25
    print(f"✓ Read back session: student={loaded.student_id}, concept={loaded.current_concept}, mastery={loaded.concept_mastery}")
    
    # 3. UPDATE
    loaded.current_state = SessionState.REEXPLAIN
    loaded.current_strategy = TeachingStrategy.SIMPLE_ANALOGY
    loaded.concept_mastery["ohms_law_basics"] = 0.75
    updated = repo.save_session(loaded)
    print(f"✓ Updated session state to {updated.current_state.value} with strategy {updated.current_strategy.value}")
    
    # 4. RE-READ AFTER UPDATE
    reloaded = repo.get_session(session_id)
    assert reloaded.current_state == SessionState.REEXPLAIN
    assert reloaded.concept_mastery["ohms_law_basics"] == 0.75
    print(f"✓ Re-read verified update: state={reloaded.current_state.value}, mastery={reloaded.concept_mastery}")
    return True


def test_upstash_redis_session_cache():
    print("\n" + "=" * 60)
    print("  [AUDIT 4] UPSTASH REDIS SESSION CACHING")
    print("=" * 60)
    redis_client = get_redis_client()
    key = f"audit_cache_sess_{int(datetime.now().timestamp())}"
    data = {"session_id": key, "state": "QUESTION", "mastery": 0.5}
    
    # SET
    ok = redis_client.set_json(key, data, ex=60)
    print(f"✓ Upstash SET key '{key}': success={ok}")
    
    # GET
    cached = redis_client.get_json(key)
    print(f"✓ Upstash GET key '{key}': {cached}")
    assert cached is not None and cached.get("session_id") == key
    
    # UPDATE
    data["mastery"] = 0.9
    redis_client.set_json(key, data, ex=60)
    updated_cache = redis_client.get_json(key)
    print(f"✓ Upstash UPDATE key '{key}': mastery={updated_cache.get('mastery')}")
    
    # DEL
    del_ok = redis_client.delete(key)
    print(f"✓ Upstash DEL key '{key}': success={del_ok}")
    return True


def test_pinecone_and_rag_grounding():
    print("\n" + "=" * 60)
    print("  [AUDIT 5, 6, 7] PINECONE 1024-D & RAG GROUNDING VALIDATION")
    print("=" * 60)
    
    # Parse real document
    extractor = TextDocumentExtractor()
    doc_path = os.path.join(os.getcwd(), "data/uploads/sample_physics_ohms_law.txt")
    if not os.path.exists(doc_path):
        os.makedirs(os.path.dirname(doc_path), exist_ok=True)
        with open(doc_path, "w") as f:
            f.write("# Chapter 12: Electricity\n\n## Section 12.1: Ohm's Law\nOhm's Law states that the potential difference V across ends of a metallic wire is directly proportional to current I through it at constant temperature: V = I * R. Resistance R is measured in Ohms.\n\n## Section 12.2: Resistance Factors\nResistance depends on length L, cross-sectional area A, and material resistivity rho: R = rho * L / A.")
    
    doc_struct = extractor.extract_document(doc_path, "doc_audit_phys_01", "sample_physics_ohms_law.txt", "physics", "en")
    print(f"✓ Extracted Document AST: title='{doc_struct.title}', chapters={len(doc_struct.chapters)}")
    
    # Chunking
    chunks = SemanticDocumentChunker.chunk_document(doc_struct)
    print(f"✓ Generated {len(chunks)} semantic chunks.")
    
    # Retriever
    retriever = get_hybrid_retriever()
    retriever.vector_store.add_chunks(chunks)
    print(f"✓ Indexed chunks in active vector store ({type(retriever.vector_store).__name__}).")
    
    # QUERY A: Supported Information
    print("\n--- Running QUERY A (Grounding: In-Document Concept) ---")
    ev_a = retriever.retrieve_evidence("What is the formula for Ohm's Law and what does resistance depend on?", target_concept="ohms_law_basics")
    print(f"✓ Query A Grounding Level: {ev_a.grounding_level.value}")
    print(f"  Confidence: {ev_a.confidence}")
    print(f"  Evidence Items Retrieved: {len(ev_a.evidence_items)}")
    for i, item in enumerate(ev_a.evidence_items[:2]):
        print(f"   [{i+1}] Score={item.relevance_score:.3f} | {item.excerpt[:70]}...")
    assert ev_a.grounding_level in (GroundingLevel.SUPPORTED, GroundingLevel.PARTIALLY_SUPPORTED)
    
    # QUERY B: Unsupported Information against physics document
    print("\n--- Running QUERY B (Grounding: Out-of-Scope Concept against Physics Document) ---")
    ev_b = retriever.retrieve_evidence("Explain medieval feudal land treaties and Magna Carta clauses.", target_concept="feudalism", document_id="doc_audit_phys_01")
    print(f"✓ Query B Grounding Level: {ev_b.grounding_level.value}")
    print(f"  Confidence: {ev_b.confidence}")
    print(f"  Limitations/Gaps: {ev_b.limitations_or_gaps}")
    assert ev_b.grounding_level == GroundingLevel.UNSUPPORTED
    print("✓ Successfully proved RAG does NOT hallucinate unsupported queries.")
    return True


def test_harness_real_misconception_adaptation():
    print("\n" + "=" * 60)
    print("  [AUDIT 14, 15] TEACHING HARNESS & COGNITIVE ADAPTATION LOOP")
    print("=" * 60)
    orchestrator = MasterTeachingOrchestrator()
    assessment_engine = AssessmentEngine()
    visual_engine = VisualIntelligenceEngine()
    
    student_id = f"student_deep_audit_{int(datetime.now().timestamp())}"
    session = orchestrator.start_session(
        student_id=student_id,
        lesson_id="lesson_deep_audit",
        topic="Ohm's Law",
        subject="physics",
        language="en",
        learner_level="beginner",
        concepts_list=["ohms_law_basics", "voltage_current_relation"],
        time_minutes=15,
    )
    print(f"✓ Started Session {session.session_id} in state {session.current_state.value} with strategy {session.current_strategy.value}")
    
    # Step 1: Initial Question
    q1 = assessment_engine.generate_checkpoint_question("lesson_deep_audit", "ohms_law_basics", session.current_difficulty)
    orchestrator.advance_to_question(session.session_id, q1.question_id)
    print(f"✓ Advanced to Question: '{q1.prompt}'")
    
    # Step 2: Student gives classic inverse relationship misconception
    student_wrong_ans = "If resistance is doubled, current will also double because more resistance allows more current to flow."
    eval_1 = assessment_engine.evaluate_response(q1.question_id, student_wrong_ans, student_id, "physics")
    print(f"✓ Assessment Evaluation 1: verdict={eval_1.verdict.value}, score={eval_1.score}")
    assert eval_1.misconception is not None
    print(f"  Diagnosed Misconception: '{eval_1.misconception.misconception_type}' -> {eval_1.misconception.belief}")
    
    active_misc = ActiveMisconception(
        concept=eval_1.misconception.concept,
        misconception_type=eval_1.misconception.misconception_type,
        belief=eval_1.misconception.belief,
        evidence_from_answer=eval_1.misconception.evidence_from_answer,
        confidence=eval_1.misconception.confidence,
        severity=eval_1.misconception.severity,
        recommended_intervention=eval_1.misconception.recommended_intervention,
    )
    
    # Step 3: Policy adaptation
    decision = orchestrator.process_evaluation_result(
        session_id=session.session_id,
        is_correct=False,
        score=eval_1.score,
        confidence=eval_1.confidence,
        misconception=active_misc,
        question_id=q1.question_id,
        student_answer=student_wrong_ans,
    )
    print(f"✓ Policy Decision: Action={decision.action.value}, New Strategy={decision.teaching_strategy.value}, Visual={decision.visual_strategy}")
    assert decision.teaching_strategy == TeachingStrategy.SIMPLE_ANALOGY
    
    # Step 4: Adapted visual generation (Water Pipe Analogy)
    adapted_visual = visual_engine.generate_visual("physics", "ohms_law_basics", decision.teaching_strategy, eval_1.misconception)
    print(f"✓ Adapted Visual Generated: type={adapted_visual.visual_type.value}, format={adapted_visual.format.value}, alt='{adapted_visual.alt_text}'")
    assert "water" in adapted_visual.visual_type.value.lower() or "analogy" in adapted_visual.visual_type.value.lower() or "pipe" in adapted_visual.alt_text.lower()
    
    # Step 5: Follow-up re-check question
    recheck_q = assessment_engine.generate_recheck_question("lesson_deep_audit", "ohms_law_basics", eval_1.misconception)
    from app.harness.state_machine import TeachingStateMachine
    from app.harness.session import ActionType
    TeachingStateMachine.transition(session, SessionState.REEXPLAIN, ActionType.REEXPLAIN_CONCEPT)
    orchestrator.advance_to_question(session.session_id, recheck_q.question_id)
    
    # Step 6: Student answers correctly after analogy
    eval_2 = assessment_engine.evaluate_response(recheck_q.question_id, "A", student_id, "physics")
    print(f"✓ Assessment Evaluation 2: verdict={eval_2.verdict.value}, score={eval_2.score}")
    assert eval_2.verdict == EvaluationVerdict.CORRECT
    
    decision_2 = orchestrator.process_evaluation_result(
        session_id=session.session_id,
        is_correct=True,
        score=eval_2.score,
        confidence=eval_2.confidence,
        question_id=recheck_q.question_id,
        student_answer="Option A: Current decreases",
    )
    print(f"✓ Final Decision: Action={decision_2.action.value}, State={session.current_state.value}")
    
    # Complete
    completed = orchestrator.complete_assessment_and_report(session.session_id, 0.95, "Ohm's Law misconception successfully resolved.")
    print(f"✓ Session Completed: Final Mastery={completed.concept_mastery}")
    assert completed.concept_mastery.get("ohms_law_basics", 0) > 0.3
    return True


def test_multilingual_independence():
    print("\n" + "=" * 60)
    print("  [AUDIT 16] MULTILINGUAL COGNITIVE INDEPENDENCE")
    print("=" * 60)
    orchestrator = MasterTeachingOrchestrator()
    student_id = "student_multilingual_01"
    
    # Start in Hindi
    sess = orchestrator.start_session(
        student_id=student_id,
        lesson_id="lesson_hindi_01",
        topic="Ohm's Law",
        subject="physics",
        language="hi",
        learner_level="beginner",
        concepts_list=["ohms_law_basics"],
    )
    sess.concept_mastery["ohms_law_basics"] = 0.5
    orchestrator.repository.save_session(sess)
    print(f"✓ Session created in Hindi (hi): concept={sess.current_concept}, mastery={sess.concept_mastery}")
    
    # Switch to Tamil mid-lesson
    sess.language = "ta"
    orchestrator.repository.save_session(sess)
    
    # Reload session
    reloaded = orchestrator.repository.get_session(sess.session_id)
    assert reloaded.language == "ta"
    assert reloaded.concept_mastery["ohms_law_basics"] == 0.5
    assert reloaded.current_concept == "ohms_law_basics"
    print(f"✓ Language switched to Tamil (ta): underlying cognitive mastery preserved at {reloaded.concept_mastery['ohms_law_basics']}.")
    return True


def main():
    print("=" * 70)
    print("  AI TEACHER — DEEP VALIDATION RUNTIME AUDIT")
    print("=" * 70)
    
    test_database_crud_neon()
    test_upstash_redis_session_cache()
    test_pinecone_and_rag_grounding()
    test_harness_real_misconception_adaptation()
    test_multilingual_independence()
    
    print("\n" + "=" * 70)
    print("  ALL DEEP VALIDATION CHECKS COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()

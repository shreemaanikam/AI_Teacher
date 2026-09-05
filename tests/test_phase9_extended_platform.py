"""
Test Suite for Phase 9 Extended Collegiate Platform:
- Phase 9O: Practical Learning (Code debugging, SQL queries, DSA traversals, Physics circuits)
- Phase 9P: Ask Teacher with Multi-Turn Contextual Memory
- Phase 9Q: Doubt Vault & Review Status
- Phase 9R: Video Interruption & Seamless Resume at Exact Timestamp
- Phase 9S: Personalized Pedagogical Teaching Controls
- Phase 9K: Cross-Course Knowledge Graph
- Phase 9L & 9N: Learning Analytics & Formal Academic Mentor Report
- Phase 9Y: Multi-Student Personalization Comparison (Beginner vs Intermediate, 7-day vs 30-day)
- Phase 9AG: Multi-Subject Verification (ML, DSA, DBMS, Physics)
- REST API Endpoints Verification
"""

import uuid
import pytest
from app import create_app
from app.student.service import get_student_platform_service
from app.db.repository import get_teaching_repository



@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def service():
    return get_student_platform_service()


@pytest.fixture
def repo():
    return get_teaching_repository()


# -----------------------------------------------------------------------------
# 1. PRACTICAL LEARNING ENGINE (Phase 9O)
# -----------------------------------------------------------------------------
def test_practical_tasks_generation_and_evaluation(service):
    student_id = "std_test_practical_01"

    # 1. Machine Learning Task
    ml_task = service.generate_practical_task(
        student_id=student_id,
        subject="Machine Learning",
        topic="Gradient Descent",
        difficulty="INTERMEDIATE",
    )
    assert ml_task["task_id"].startswith("ptask_")
    assert "gradient_descent_step" in ml_task["starter_code"]
    assert ml_task["subject"] == "Machine Learning"

    # Evaluate ML Task with correct implementation
    correct_ml_code = (
        "def gradient_descent_step(w, grad, lr):\n"
        "    return [w[i] - lr * grad[i] for i in range(len(w))]\n"
    )
    eval_res = service.evaluate_practical_submission(
        student_id=student_id,
        task_id=ml_task["task_id"],
        code_submission=correct_ml_code,
    )
    assert eval_res["verdict"] == "PASS"
    assert eval_res["score"] == 100.0
    assert eval_res["tests_passed"] > 0

    # Evaluate ML Task with wrong implementation (missing minus sign)
    wrong_ml_code = (
        "def gradient_descent_step(w, grad, lr):\n"
        "    return [w[i] + lr * grad[i] for i in range(len(w))]\n"
    )
    eval_wrong = service.evaluate_practical_submission(
        student_id=student_id,
        task_id=ml_task["task_id"],
        code_submission=wrong_ml_code,
    )
    assert eval_wrong["score"] < 100.0

    # 2. DBMS SQL Task
    dbms_task = service.generate_practical_task(
        student_id=student_id,
        subject="DBMS",
        topic="SQL Aggregation",
    )
    assert "SELECT" in dbms_task["starter_code"]
    assert "GROUP BY" in dbms_task["expected_output_or_rubric"]

    sql_eval = service.evaluate_practical_submission(
        student_id=student_id,
        task_id=dbms_task["task_id"],
        code_submission="SELECT dept_name, AVG(salary) FROM employees GROUP BY dept_name HAVING COUNT(*) > 5;",
    )
    assert sql_eval["verdict"] == "PASS"

    # 3. DSA Task
    dsa_task = service.generate_practical_task(
        student_id=student_id,
        subject="Data Structures",
        topic="Binary Search Tree",
    )
    assert "inorder_traversal" in dsa_task["starter_code"]

    # 4. Physics / Circuits Task
    phys_task = service.generate_practical_task(
        student_id=student_id,
        subject="Physics",
        topic="Circuit Analysis",
    )
    assert "calculate_circuit" in phys_task["starter_code"]

    tasks_list = service.list_practical_tasks(student_id)
    assert len(tasks_list) >= 4


# -----------------------------------------------------------------------------
# 2. ASK TEACHER & CONTEXTUAL MEMORY (Phase 9P & 9Q)
# -----------------------------------------------------------------------------
def test_ask_teacher_and_contextual_memory(service):
    student_id = "std_test_doubt_01"

    # Turn 1: Ask specific technical question
    ans1 = service.ask_teacher(
        student_id=student_id,
        doubt_text="How does Gradient Descent minimize loss in neural networks?",
        context={"concept": "Gradient Descent", "course_name": "Machine Learning"},
    )
    assert ans1["status"] == "RESOLVED"
    assert ans1["doubt_id"].startswith("dbt_")
    assert "gradient" in ans1["teacher_explanation"].lower()
    assert ans1["avatar_presentation"]["script"]

    # Turn 2: Contextual doubt ("Explain that again with a simpler analogy")
    ans2 = service.ask_teacher(
        student_id=student_id,
        doubt_text="Can you explain that again more simply?",
    )
    assert "Gradient Descent" in ans2["resolved_context"]
    assert "valley" in ans2["teacher_explanation"].lower() or "foggy" in ans2["teacher_explanation"].lower()
    assert ans2["avatar_presentation"]["gesture"] == "EXPLAINING"

    # Turn 3: Contextual reference ("Why is there a minus sign?")
    ans3 = service.ask_teacher(
        student_id=student_id,
        doubt_text="Why was that negative?",
    )
    assert "steepest ascent" in ans3["teacher_explanation"].lower() or "opposite direction" in ans3["teacher_explanation"].lower()

    # Verify Doubt Vault
    doubts = service.list_doubts(student_id)
    assert len(doubts) >= 3

    # Update doubt status to MASTERED
    updated = service.update_doubt_status(ans1["doubt_id"], "MASTERED")
    assert updated["status"] == "MASTERED"


# -----------------------------------------------------------------------------
# 3. VIDEO INTERRUPTION & RESUME (Phase 9R)
# -----------------------------------------------------------------------------
def test_video_interruption_and_resume(service):
    student_id = "std_test_interrupt_01"
    session_id = "sess_video_active_42"

    # Student pauses video at 74.5 seconds to ask a doubt
    interruption = service.interrupt_session(
        student_id=student_id,
        session_id=session_id,
        paused_timestamp=74.5,
        current_concept="K-Means Clustering",
        doubt_text="Why do the centroids recompute at each iteration?",
    )
    assert interruption["state"] == "INTERRUPTED_DOUBT"
    assert interruption["paused_timestamp"] == 74.5
    assert interruption["can_resume"] is True
    assert interruption["doubt_answer"]["status"] == "RESOLVED"

    # Student clears doubt and clicks Resume
    resumption = service.resume_session(
        student_id=student_id,
        session_id=session_id,
    )
    assert resumption["state"] == "TEACHING"
    assert resumption["resumed_timestamp"] == 74.5
    assert resumption["concept"] == "K-Means Clustering"
    assert "1:14" in resumption["transition_script"]
    assert resumption["avatar_presentation"]["action"] == "RESUME_VIDEO"


# -----------------------------------------------------------------------------
# 4. PERSONALIZED TEACHING CONTROLS (Phase 9S)
# -----------------------------------------------------------------------------
def test_personalized_teaching_controls(service):
    student_id = "std_test_controls_01"
    concept = "Decision Tree Splitting & Entropy"

    # 1. Explain Simpler
    simpler = service.execute_teaching_control(student_id, "explain_simpler", concept)
    assert "books" in simpler["explanation"].lower() or "simple" in simpler["avatar_script"].lower()

    # 2. Another Example
    example = service.execute_teaching_control(student_id, "another_example", concept)
    assert "application" in example["explanation"].lower() or "spotify" in example["avatar_script"].lower()

    # 3. Show Visually
    visual = service.execute_teaching_control(student_id, "show_visually", concept)
    assert visual["visual_action"]["type"] == "DYNAMIC_SVG_BOARD"

    # 4. Give Hint
    hint = service.execute_teaching_control(student_id, "give_hint", concept)
    assert "invariant" in hint["explanation"].lower() or "hint" in hint["avatar_script"].lower()

    # 5. Slow Down
    slow = service.execute_teaching_control(student_id, "slow_down", concept)
    assert "Step 1" in slow["explanation"]
    assert "Step 2" in slow["explanation"]

    # 6. Practice This
    drill = service.execute_teaching_control(student_id, "practice_this", concept)
    assert drill["exercise"]["type"] == "QUICK_CHECK"

    # 7. Switch Language to Hindi
    hindi = service.execute_teaching_control(
        student_id, "switch_language", concept, context={"target_language": "hi"}
    )
    assert "हिंदी" in hindi["avatar_script"] or "सिद्धांत" in hindi["explanation"]

    # 8. Switch Language to Tamil
    tamil = service.execute_teaching_control(
        student_id, "switch_language", concept, context={"target_language": "ta"}
    )
    assert "தமிழில்" in tamil["avatar_script"] or "நோக்கம்" in tamil["explanation"]


# -----------------------------------------------------------------------------
# 5. CROSS-COURSE GRAPH, ANALYTICS & MENTOR REPORT (Phase 9K, 9L, 9N)
# -----------------------------------------------------------------------------
def test_cross_course_graph_and_mentor_report(service):
    student_id = "std_aditya"

    # Cross-course knowledge graph
    graph = service.get_cross_course_graph(student_id)
    assert graph["total_nodes"] >= 10
    assert graph["total_edges"] >= 4
    rel_types = [e["relationship"] for e in graph["edges"]]
    assert "PREREQUISITE" in rel_types
    assert "GENERALIZED_TO" in rel_types

    # Analytics
    analytics = service.get_student_analytics(student_id)
    assert analytics["student_id"] == student_id
    assert analytics["overall_mastery"] > 0.0
    assert "strong_concepts" in analytics
    assert "weak_concepts" in analytics

    # Mentor Report
    report = service.generate_mentor_report(student_id)
    assert report["report_id"].startswith("rpt_")
    assert report["student_name"] == "Aditya Rao"
    assert report["academic_standing"] in ("EXCELLENT", "GOOD")
    assert len(report["mentor_recommendations"]) > 0


# -----------------------------------------------------------------------------
# 6. MULTI-STUDENT PERSONALIZATION COMPARISON (Phase 9Y)
# -----------------------------------------------------------------------------
def test_multi_student_personalization_comparison(service, repo):
    """
    Validates that:
    Student A (Beginner, exam in 7 days, weak Unit 3, Hindi)
    vs
    Student B (Intermediate, exam in 30 days, strong Unit 1, English)
    produce distinctly adapted plans, difficulty, and teacher behavior.
    """
    today_str = "2026-09-11"

    # Setup Student A
    repo.save_learner_profile({
        "id": "std_student_a",
        "name": "Aarav Gupta",
        "college": "NIT Delhi",
        "degree": "B.Tech",
        "year": 2,
        "semester": 3,
        "available_study_hours": 2.0,
        "preferred_language": "hi",
        "learning_style": "STEP_BY_STEP",
        "weak_concepts": ["Unit 3 Neural Networks & Backprop"],
        "knowledge": {"Unit 3 Neural Networks & Backprop": 0.35, "Unit 1 Foundations": 0.60},
    })
    cA = repo.save_course({
        "student_id": "std_student_a",
        "name": "Machine Learning",
        "code": "CS401",
        "exam_date": today_str,
        "target_score": "80%",
        "units": [{"title": "Unit 1"}, {"title": "Unit 2"}, {"title": "Unit 3"}],
        "concepts": ["Unit 3 Neural Networks & Backprop"],
    })

    # Setup Student B
    repo.save_learner_profile({
        "id": "std_student_b",
        "name": "Bhavya Nair",
        "college": "BITS Pilani",
        "degree": "B.Tech",
        "year": 3,
        "semester": 6,
        "available_study_hours": 4.5,
        "preferred_language": "en",
        "learning_style": "FIRST_PRINCIPLES",
        "weak_concepts": [],
        "knowledge": {"Unit 1 Foundations": 0.95, "Unit 2 Classifiers": 0.90},
    })
    cB = repo.save_course({
        "student_id": "std_student_b",
        "name": "Machine Learning",
        "code": "CS401",
        "exam_date": "2026-10-04",
        "target_score": "98%",
        "units": [{"title": "Unit 1"}, {"title": "Unit 2"}, {"title": "Unit 3"}, {"title": "Unit 4"}, {"title": "Unit 5"}],
        "concepts": ["Unit 1 Foundations", "Unit 2 Classifiers"],
    })

    # Dashboards
    dash_a = service.get_student_dashboard("std_student_a")
    dash_b = service.get_student_dashboard("std_student_b")

    # Verify differentiated study action
    assert "Exam in" in dash_a["what_should_i_study_now"] or "Unit 3" in dash_a["what_should_i_study_now"]
    assert dash_a["exam_readiness_percentage"] < dash_b["exam_readiness_percentage"]

    # Exam Plans
    plan_a = service.generate_exam_plan(
        student_id="std_student_a",
        course_id=cA["id"],
        exam_date=today_str,
        target_score="80%",
        available_hours_per_day=2.0,
    )
    plan_b = service.generate_exam_plan(
        student_id="std_student_b",
        course_id=cB["id"],
        exam_date="2026-10-04",
        target_score="98%",
        available_hours_per_day=4.5,
    )

    assert plan_a["total_days"] <= 7
    assert plan_b["total_days"] >= 20
    assert plan_a["available_hours_per_day"] == 2.0
    assert plan_b["available_hours_per_day"] == 4.5

    # Differentiated Teacher Language Response
    ctrl_a = service.execute_teaching_control(
        "std_student_a", "switch_language", "Backpropagation", context={"target_language": "hi"}
    )
    ctrl_b = service.execute_teaching_control(
        "std_student_b", "switch_language", "Backpropagation", context={"target_language": "en"}
    )
    assert "हिंदी" in ctrl_a["avatar_script"]
    assert "English" in ctrl_b["avatar_script"]


# -----------------------------------------------------------------------------
# 7. MULTI-SUBJECT VERIFICATION (Phase 9AG)
# -----------------------------------------------------------------------------
def test_multi_subject_verification(service, repo):
    student_id = f"std_polymath_{uuid.uuid4().hex[:6]}"


    subjects = [
        ("Machine Learning", "CS4403", ["Linear Regression", "Gradient Descent", "Decision Trees"]),
        ("Data Structures & Algorithms", "CS201", ["AVL Trees", "Red-Black Trees", "Dijkstra"]),
        ("Database Management Systems", "CS301", ["Relational Algebra", "B-Tree Indexing", "ACID Transactions"]),
        ("Physics & Circuit Theory", "PH101", ["Ohm's Law", "Kirchhoff Laws", "RC Transient Response"]),
    ]

    for subj_name, code, concepts in subjects:
        c = repo.save_course({
            "student_id": student_id,
            "name": subj_name,
            "code": code,
            "exam_date": "2026-10-15",
            "target_score": "90%",
            "units": [{"title": f"Unit 1: {concepts[0]}"}, {"title": f"Unit 2: {concepts[1]}"}],
            "concepts": concepts,
        })
        assert c["id"].startswith("crs_")

        asgn = service.generate_assignment(
            student_id=student_id,
            course_name=subj_name,
            concept=concepts[0],
        )
        assert asgn["id"].startswith("asgn_")
        assert len(asgn["questions"]) > 0

    enrolled = repo.list_student_courses(student_id)
    assert len(enrolled) == 4


# -----------------------------------------------------------------------------
# 8. REST API EXTENDED PLATFORM VERIFICATION
# -----------------------------------------------------------------------------
def test_rest_api_extended_student_platform(client):
    student_id = "std_aditya"

    # Practical Tasks API
    pt_resp = client.post(
        f"/api/v1/students/{student_id}/practical-tasks",
        json={"subject": "Machine Learning", "topic": "Gradient Descent"},
    )
    assert pt_resp.status_code == 201
    pt_data = pt_resp.get_json()["practical_task"]
    task_id = pt_data["task_id"]

    pt_list = client.get(f"/api/v1/students/{student_id}/practical-tasks")
    assert pt_list.status_code == 200
    assert pt_list.get_json()["count"] >= 1

    eval_resp = client.post(
        f"/api/v1/students/{student_id}/practical-tasks/{task_id}/evaluate",
        json={"code_submission": "def gradient_descent_step(w, grad, lr): return [w[i] - lr*grad[i] for i in range(len(w))]"},
    )
    assert eval_resp.status_code == 200
    assert eval_resp.get_json()["result"]["verdict"] == "PASS"

    # Ask Teacher API
    ask_resp = client.post(
        f"/api/v1/students/{student_id}/ask-teacher",
        json={"doubt_text": "Why does gradient descent require learning rate?"},
    )
    assert ask_resp.status_code == 200
    d_id = ask_resp.get_json()["response"]["doubt_id"]

    # Doubt Vault API
    doubts_resp = client.get(f"/api/v1/students/{student_id}/doubts")
    assert doubts_resp.status_code == 200
    assert doubts_resp.get_json()["count"] >= 1

    status_resp = client.put(
        f"/api/v1/doubts/{d_id}/status",
        json={"status": "BOOKMARKED"},
    )
    assert status_resp.status_code == 200
    assert status_resp.get_json()["doubt"]["status"] == "BOOKMARKED"

    # Video Interruption & Resume API
    inter_resp = client.post(
        f"/api/v1/students/{student_id}/teaching-session/interrupt",
        json={
            "session_id": "sess_api_99",
            "paused_timestamp": 52.0,
            "current_concept": "B-Tree Indexing",
            "doubt_text": "Why must nodes split at the median?",
        },
    )
    assert inter_resp.status_code == 200
    assert inter_resp.get_json()["interruption"]["can_resume"] is True

    resume_resp = client.post(
        f"/api/v1/students/{student_id}/teaching-session/resume",
        json={"session_id": "sess_api_99"},
    )
    assert resume_resp.status_code == 200
    assert resume_resp.get_json()["resumption"]["state"] == "TEACHING"

    # Teaching Control API
    ctrl_resp = client.post(
        f"/api/v1/students/{student_id}/teaching-session/control",
        json={"action": "give_hint", "concept": "B-Tree Indexing"},
    )
    assert ctrl_resp.status_code == 200
    assert "hint" in ctrl_resp.get_json()["control_result"]["explanation"].lower()

    # Cross-Course Graph API
    graph_resp = client.get(f"/api/v1/students/{student_id}/cross-course-graph")
    assert graph_resp.status_code == 200
    assert graph_resp.get_json()["knowledge_graph"]["total_nodes"] > 0

    # Analytics API
    ana_resp = client.get(f"/api/v1/students/{student_id}/analytics")
    assert ana_resp.status_code == 200
    assert ana_resp.get_json()["analytics"]["student_id"] == student_id

    # Mentor Report API
    rep_resp = client.get(f"/api/v1/students/{student_id}/mentor-report")
    assert rep_resp.status_code == 200
    assert rep_resp.get_json()["mentor_report"]["academic_standing"] in ("EXCELLENT", "GOOD")

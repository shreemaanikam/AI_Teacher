"""
Unit and integration tests for Phase 9 Student Platform:
- Home Dashboard ("What should I study now?", countdown, weak concepts, exam readiness)
- Exam Study Planner & Dynamic Replanning (re-allocating study time when falling behind)
- Task Deadlines & State Transitions (TODO, IN_PROGRESS, COMPLETED, OVERDUE)
- Adaptive Assignment Generation, Rubric Evaluation, and Mastery Updates
- Course-Level Dashboard
"""

import uuid
from datetime import datetime, timezone, timedelta
import pytest
from app import create_app
from app.db.repository import get_teaching_repository


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_student_dashboard_computation(client):
    """Verifies student home dashboard responds to student profile, weak areas, and countdown."""
    student_id = f"std_{uuid.uuid4().hex[:6]}"
    repo = get_teaching_repository()

    # 1. Setup Student Profile with upcoming exam and weak concept
    repo.save_learner_profile({
        "id": student_id,
        "name": "Ananya Sharma",
        "college": "IIT Madras",
        "department": "Computer Science & Engineering",
        "degree": "B.Tech",
        "year": 3,
        "semester": 5,
        "available_study_hours": 4.0,
        "weak_concepts": ["B-Tree Indexing", "Deadlock Prevention"],
        "knowledge": {"B-Tree Indexing": 0.35, "Relational Algebra": 0.85},
    })

    # 2. Enroll in Course with Exam Date 5 days away (Urgent!)
    today = datetime.now(timezone.utc).date()
    exam_date_str = (today + timedelta(days=5)).strftime("%Y-%m-%d")
    course_resp = client.post("/api/v1/courses", json={
        "student_id": student_id,
        "name": "Database Management Systems",
        "code": "CS302",
        "exam_date": exam_date_str,
    })
    assert course_resp.status_code == 201

    # 3. Fetch Dashboard
    dash_resp = client.get(f"/api/v1/students/{student_id}/dashboard")
    assert dash_resp.status_code == 200
    data = dash_resp.get_json()["dashboard"]

    assert data["student_id"] == student_id
    assert data["name"] == "Ananya Sharma"
    assert data["college"] == "IIT Madras"
    assert len(data["enrolled_courses"]) >= 1

    # Verify Exam Countdown & Urgency
    assert len(data["exam_countdown"]) >= 1
    assert data["exam_countdown"][0]["days_remaining"] <= 5
    assert data["exam_countdown"][0]["is_urgent"] is True

    # Verify "What should I study now?" prioritizes the urgent exam & weak concept
    study_recommendation = data["what_should_i_study_now"]
    assert "Exam in" in study_recommendation or "Revise weak concept" in study_recommendation or "Priority" in study_recommendation

    # Verify Exam Readiness is calculated as a numeric percentage
    assert 15.0 <= data["exam_readiness_percentage"] <= 100.0

    # Verify Weak Concepts list
    weak_concepts = [w["concept"] for w in data["weak_concepts"]]
    assert "B-Tree Indexing" in weak_concepts


def test_exam_planner_and_dynamic_replanning(client):
    """Verifies exam study schedule generation and dynamic replanning when conditions change."""
    student_id = f"std_{uuid.uuid4().hex[:6]}"
    repo = get_teaching_repository()

    # 1. Setup Student & Course
    repo.save_learner_profile({
        "id": student_id,
        "name": "Rohan Verma",
        "weak_concepts": ["Red-Black Tree Rotations"],
    })
    course_resp = client.post("/api/v1/courses", json={
        "student_id": student_id,
        "name": "Data Structures & Algorithms",
        "code": "CS201",
        "units": [
            {"title": "Unit 1: Trees and Balanced Search Trees"},
            {"title": "Unit 2: Graph Algorithms & Shortest Path"},
            {"title": "Unit 3: Dynamic Programming"},
        ]
    })
    assert course_resp.status_code == 201
    course_id = course_resp.get_json()["course"]["id"]

    # 2. Generate Exam Plan (Exam in 10 days)
    today = datetime.now(timezone.utc).date()
    exam_date = (today + timedelta(days=10)).strftime("%Y-%m-%d")

    plan_resp = client.post(f"/api/v1/students/{student_id}/exam-plans", json={
        "course_id": course_id,
        "exam_date": exam_date,
        "target_score": "95%",
        "available_hours_per_day": 3.0,
    })
    assert plan_resp.status_code == 201
    plan = plan_resp.get_json()["exam_plan"]
    plan_id = plan["id"]

    assert plan["student_id"] == student_id
    assert plan["total_days"] >= 7
    assert len(plan["schedule"]) >= 7
    assert plan["version"] == 1
    assert plan["status"] == "ACTIVE"

    # Schedule should conclude with Mock Assessment and Final Review
    schedule = plan["schedule"]
    assert schedule[-1]["focus_type"] == "FINAL_REVIEW"
    assert schedule[-2]["focus_type"] == "MOCK_TEST"

    # 3. Dynamic Replanning: Student completed Day 1 & 2, discovered new weak concept, hours increased to 4.5
    replan_resp = client.post(f"/api/v1/exam-plans/{plan_id}/replan", json={
        "reason": "FELL_BEHIND_ON_TREES",
        "completed_days": [1, 2],
        "new_weak_concepts": ["AVL Deletion", "Red-Black Rotations"],
        "new_available_hours": 4.5,
    })
    assert replan_resp.status_code == 200
    replanned = replan_resp.get_json()["exam_plan"]

    assert replanned["version"] == 2
    assert replanned["status"] == "REPLANNED"
    assert replanned["available_hours_per_day"] == 4.5

    # Check that day 1 and 2 are marked completed
    assert replanned["schedule"][0]["completed"] is True
    assert replanned["schedule"][1]["completed"] is True

    # 4. Fetch plan details via GET
    fetch_resp = client.get(f"/api/v1/exam-plans/{plan_id}")
    assert fetch_resp.status_code == 200
    assert fetch_resp.get_json()["exam_plan"]["version"] == 2


def test_task_deadlines_lifecycle(client):
    """Verifies task creation, listing with filters, and state transition to COMPLETED."""
    student_id = f"std_{uuid.uuid4().hex[:6]}"

    # 1. Create a task
    create_resp = client.post("/api/v1/tasks", json={
        "student_id": student_id,
        "course_name": "Operating Systems",
        "title": "Implement Semaphores Practice Lab",
        "concept": "Concurrency & Mutex",
        "priority": "HIGH",
        "deadline": "2026-09-15",
        "estimated_duration_minutes": 45,
    })
    assert create_resp.status_code == 201
    task = create_resp.get_json()["task"]
    task_id = task["id"]
    assert task["status"] == "TODO"

    # 2. List tasks for student
    list_resp = client.get(f"/api/v1/tasks?student_id={student_id}")
    assert list_resp.status_code == 200
    tasks = list_resp.get_json()["tasks"]
    assert len(tasks) == 1
    assert tasks[0]["id"] == task_id

    # 3. Update task status to COMPLETED
    update_resp = client.put(f"/api/v1/tasks/{task_id}/status", json={"status": "COMPLETED"})
    assert update_resp.status_code == 200
    updated = update_resp.get_json()["task"]
    assert updated["status"] == "COMPLETED"
    assert updated["completed_at"] is not None

    # 4. Filter by status
    filter_resp = client.get(f"/api/v1/tasks?student_id={student_id}&status=COMPLETED")
    assert filter_resp.status_code == 200
    assert len(filter_resp.get_json()["tasks"]) == 1

    filter_todo = client.get(f"/api/v1/tasks?student_id={student_id}&status=TODO")
    assert filter_todo.status_code == 200
    assert len(filter_todo.get_json()["tasks"]) == 0


def test_assignment_generation_and_rubric_evaluation(client):
    """Verifies assignment generation, rubric scoring, and mastery updating."""
    student_id = f"std_{uuid.uuid4().hex[:6]}"
    repo = get_teaching_repository()

    # Initial profile
    repo.save_learner_profile({
        "id": student_id,
        "name": "Priya Patel",
        "knowledge": {"Binary Search": 0.40},
    })

    # 1. Generate assignment for Binary Search
    gen_resp = client.post("/api/v1/assignments/generate", json={
        "student_id": student_id,
        "course_name": "Data Structures",
        "concept": "Binary Search",
        "difficulty": "INTERMEDIATE",
    })
    assert gen_resp.status_code == 201
    asgn = gen_resp.get_json()["assignment"]
    asgn_id = asgn["id"]
    assert asgn["concept"] == "Binary Search"
    assert len(asgn["questions"]) >= 2
    q1_id = asgn["questions"][0]["question_id"]
    q2_id = asgn["questions"][1]["question_id"]

    # 2. Submit responses matching rubric
    submit_resp = client.post(f"/api/v1/assignments/{asgn_id}/submit", json={
        "student_id": student_id,
        "answers": {
            q1_id: "Binary search requires sorted array because it relies on the monotonicity invariant to eliminate half the search space. Unsorted input discards the target.",
            q2_id: "Iteration 1: low=0, high=9, mid=4. Iteration 2: low=5, high=9, mid=7. Iteration 3: low=5, high=6, mid=5 found target.",
        }
    })
    assert submit_resp.status_code == 200
    result = submit_resp.get_json()["result"]

    assert result["score"] >= 80.0
    assert result["verdict"] in ("EXCELLENT", "PROFICIENT")
    assert "submission_id" in result

    # 3. Verify concept mastery was updated in repository
    profile = repo.get_learner_profile(student_id)
    updated_mastery = profile.get("knowledge", {}).get("Binary Search", 0.0)
    assert updated_mastery >= 0.80  # Upgraded from 0.40!


def test_course_dashboard(client):
    """Verifies course dashboard provides syllabus coverage and linked materials."""
    student_id = f"std_{uuid.uuid4().hex[:6]}"
    repo = get_teaching_repository()

    # Create course with units
    course_resp = client.post("/api/v1/courses", json={
        "student_id": student_id,
        "name": "Computer Networks",
        "code": "CS304",
        "units": [
            {"title": "Unit 1: Physical & Data Link Layer"},
            {"title": "Unit 2: Network Layer & IP Routing"},
            {"title": "Unit 3: Transport Layer & TCP Congestion Control"},
        ]
    })
    assert course_resp.status_code == 201
    course_id = course_resp.get_json()["course"]["id"]

    # Fetch Course Dashboard
    dash_resp = client.get(f"/api/v1/courses/{course_id}/dashboard")
    assert dash_resp.status_code == 200
    dash = dash_resp.get_json()

    assert dash["course_id"] == course_id
    assert dash["course"]["name"] == "Computer Networks"
    assert len(dash["units"]) == 3
    assert "syllabus_coverage_percentage" in dash

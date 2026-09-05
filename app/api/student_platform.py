"""
Student Platform REST API Blueprint for Phase 9.
Exposes endpoints for:
- Student Home Dashboard ("What should I study now?", readiness %, countdown)
- Exam Study Planner & Dynamic Replanning
- Study Tasks & Deadlines (TODO, IN_PROGRESS, COMPLETED, OVERDUE)
- Adaptive Assignments Generation, Rubric Evaluation & Mastery Updates
- Course-Level Dashboard
"""

from __future__ import annotations
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify

from app.student.service import get_student_platform_service
from app.db.repository import get_teaching_repository
from app.auth.token_manager import (
    extract_token_from_request,
    get_session_token_manager,
    verify_student_ownership,
)

student_platform_blueprint = Blueprint("student_platform_api", __name__)


def _check_student_access(target_student_id: str):
    """Verifies that the authenticated caller has permission to access target_student_id data."""
    token = extract_token_from_request()
    if token:
        mgr = get_session_token_manager()
        is_val, payload, err = mgr.verify_token(token)
        if not is_val:
            return jsonify({"success": False, "error": f"Unauthorized: {err}", "status": 401}), 401
        caller_id = payload.get("sub") or payload.get("student_id")
        if caller_id and target_student_id and caller_id != target_student_id and payload.get("role") != "admin":
            return jsonify({
                "success": False,
                "error": f"Forbidden: You do not have permission to access student '{target_student_id}' data.",
                "status": 403,
            }), 403
    return None



# -----------------------------------------------------------------------------
# 1. PERSONALIZED HOME DASHBOARD (Phase 9H & 9V)
# -----------------------------------------------------------------------------
@student_platform_blueprint.route("/students/<student_id>/dashboard", methods=["GET"])
def get_student_dashboard(student_id: str):
    """
    Returns personalized student dashboard answering:
    - What should I study now?
    - Continue learning item
    - Today's plan
    - Upcoming deadlines & Exam countdown
    - Weak concepts requiring revision
    - Exam readiness percentage (0-100%)
    - Enrolled courses
    """
    denied = _check_student_access(student_id)
    if denied:
        return denied

    svc = get_student_platform_service()
    try:
        dashboard = svc.get_student_dashboard(student_id)
        return jsonify({"success": True, "dashboard": dashboard}), 200
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


# -----------------------------------------------------------------------------
# 2. EXAM PLANNER & DYNAMIC REPLANNING (Phase 9J & 9K)
# -----------------------------------------------------------------------------
@student_platform_blueprint.route("/students/<student_id>/exam-plans", methods=["POST"])
def generate_student_exam_plan(student_id: str):
    """Generates a dependency-aware multi-day study schedule for an upcoming exam."""
    denied = _check_student_access(student_id)
    if denied:
        return denied

    data = request.get_json(silent=True) or {}
    course_id = data.get("course_id")
    exam_date = data.get("exam_date")

    if not course_id or not exam_date:
        return jsonify({"error": "Fields 'course_id' and 'exam_date' are required."}), 400

    target_score = data.get("target_score", "90%")
    available_hours = float(data.get("available_hours_per_day", 2.0))

    svc = get_student_platform_service()
    try:
        plan = svc.generate_exam_plan(
            student_id=student_id,
            course_id=course_id,
            exam_date=exam_date,
            target_score=target_score,
            available_hours_per_day=available_hours,
        )
        return jsonify({"success": True, "exam_plan": plan}), 201
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@student_platform_blueprint.route("/students/<student_id>/exam-plans", methods=["GET"])
def list_student_exam_plans(student_id: str):
    """Lists all exam plans for a student."""
    denied = _check_student_access(student_id)
    if denied:
        return denied

    svc = get_student_platform_service()
    plans = svc.list_exam_plans(student_id)
    return jsonify({"success": True, "count": len(plans), "exam_plans": plans}), 200


@student_platform_blueprint.route("/exam-plans/<plan_id>", methods=["GET"])
def get_exam_plan_detail(plan_id: str):
    """Returns details of a single exam plan."""
    svc = get_student_platform_service()
    plan = svc.get_exam_plan(plan_id)
    if not plan:
        return jsonify({"error": f"Exam plan '{plan_id}' not found."}), 404

    denied = _check_student_access(plan.get("student_id"))
    if denied:
        return denied

    return jsonify({"success": True, "exam_plan": plan}), 200


@student_platform_blueprint.route("/exam-plans/<plan_id>/replan", methods=["POST"])
def replan_student_exam(plan_id: str):
    """
    Dynamically replans an existing study schedule when circumstances change
    (e.g., student falls behind, new weak concepts, changed study hours or exam date).
    """
    svc = get_student_platform_service()
    plan = svc.get_exam_plan(plan_id)
    if not plan:
        return jsonify({"error": f"Exam plan '{plan_id}' not found."}), 404

    denied = _check_student_access(plan.get("student_id"))
    if denied:
        return denied

    data = request.get_json(silent=True) or {}
    reason = data.get("reason", "SCHEDULE_UPDATE")
    completed_days = data.get("completed_days")
    new_weak_concepts = data.get("new_weak_concepts")
    new_available_hours = data.get("new_available_hours")
    if new_available_hours is not None:
        new_available_hours = float(new_available_hours)
    new_exam_date = data.get("new_exam_date")

    try:
        updated = svc.replan_exam(
            plan_id=plan_id,
            reason=reason,
            completed_days=completed_days,
            new_weak_concepts=new_weak_concepts,
            new_available_hours=new_available_hours,
            new_exam_date=new_exam_date,
        )
        return jsonify({"success": True, "exam_plan": updated}), 200
    except ValueError as val_err:
        return jsonify({"error": str(val_err)}), 404
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


# -----------------------------------------------------------------------------
# 3. DEADLINES & TASKS TRACKER (Phase 9L)
# -----------------------------------------------------------------------------
@student_platform_blueprint.route("/tasks", methods=["GET"])
def list_tasks():
    """Lists study tasks for a student, optionally filtered by status."""
    student_id = request.args.get("student_id")
    if not student_id:
        return jsonify({"error": "Query parameter 'student_id' is required."}), 400

    denied = _check_student_access(student_id)
    if denied:
        return denied

    status = request.args.get("status")
    svc = get_student_platform_service()
    tasks = svc.list_tasks(student_id=student_id, status_filter=status)
    return jsonify({
        "success": True,
        "count": len(tasks),
        "student_id": student_id,
        "status_filter": status,
        "tasks": tasks,
    }), 200


@student_platform_blueprint.route("/tasks", methods=["POST"])
def create_task():
    """Creates a new study task or deadline."""
    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id")
    title = data.get("title")

    if not student_id or not title:
        return jsonify({"error": "Fields 'student_id' and 'title' are required."}), 400

    denied = _check_student_access(student_id)
    if denied:
        return denied

    svc = get_student_platform_service()
    try:
        created = svc.create_task(data)
        return jsonify({"success": True, "task": created}), 201
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@student_platform_blueprint.route("/tasks/<task_id>/status", methods=["PUT"])
def update_task_status(task_id: str):
    """Updates status of a task ('TODO', 'IN_PROGRESS', 'COMPLETED', 'OVERDUE')."""
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    if not new_status:
        return jsonify({"error": "Field 'status' is required."}), 400

    valid_statuses = {"TODO", "IN_PROGRESS", "COMPLETED", "OVERDUE"}
    if new_status not in valid_statuses:
        return jsonify({"error": f"Invalid status '{new_status}'. Must be one of {valid_statuses}."}), 400

    from app.db.models import TaskModel
    from app.db.session import get_db_session
    with get_db_session() as session:
        t_model = session.query(TaskModel).filter_by(id=task_id).first()
        if not t_model:
            return jsonify({"error": f"Task '{task_id}' not found."}), 404
        denied = _check_student_access(t_model.student_id)
        if denied:
            return denied

    svc = get_student_platform_service()
    updated = svc.update_task_status(task_id, new_status)
    return jsonify({"success": True, "task": updated}), 200


# -----------------------------------------------------------------------------
# 4. ASSIGNMENTS & RUBRIC EVALUATION (Phase 9M & 9N)
# -----------------------------------------------------------------------------
@student_platform_blueprint.route("/assignments/generate", methods=["POST"])
def generate_assignment():
    """Generates structured college practice assignment adapted to student mastery."""
    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id")
    course_name = data.get("course_name")
    concept = data.get("concept")

    if not student_id or not course_name or not concept:
        return jsonify({"error": "Fields 'student_id', 'course_name', and 'concept' are required."}), 400

    assignment_type = data.get("assignment_type", "PRACTICE_SET")
    difficulty = data.get("difficulty", "INTERMEDIATE")
    course_id = data.get("course_id")

    svc = get_student_platform_service()
    try:
        asgn = svc.generate_assignment(
            student_id=student_id,
            course_name=course_name,
            concept=concept,
            assignment_type=assignment_type,
            difficulty=difficulty,
            course_id=course_id,
        )
        return jsonify({"success": True, "assignment": asgn}), 201
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@student_platform_blueprint.route("/assignments", methods=["GET"])
def list_assignments():
    """Lists assignments for a student."""
    student_id = request.args.get("student_id")
    if not student_id:
        return jsonify({"error": "Query parameter 'student_id' is required."}), 400

    svc = get_student_platform_service()
    assignments = svc.list_assignments(student_id)
    return jsonify({
        "success": True,
        "count": len(assignments),
        "student_id": student_id,
        "assignments": assignments,
    }), 200


@student_platform_blueprint.route("/assignments/<assignment_id>/submit", methods=["POST"])
def submit_assignment(assignment_id: str):
    """
    Submits student responses to an assignment.
    Evaluates against rubrics, provides detailed feedback, and updates student concept mastery.
    """
    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id")
    answers = data.get("answers", {})

    if not student_id:
        return jsonify({"error": "Field 'student_id' is required."}), 400

    svc = get_student_platform_service()
    try:
        result = svc.submit_assignment(
            assignment_id=assignment_id,
            student_id=student_id,
            answers=answers,
        )
        return jsonify({"success": True, "result": result}), 200
    except ValueError as val_err:
        return jsonify({"error": str(val_err)}), 404
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


# -----------------------------------------------------------------------------
# 5. COURSE-LEVEL DASHBOARD
# -----------------------------------------------------------------------------
@student_platform_blueprint.route("/courses/<course_id>/dashboard", methods=["GET"])
def get_course_dashboard(course_id: str):
    """Returns course dashboard with units, materials, syllabus status, and student progress."""
    repo = get_teaching_repository()
    course = repo.get_course(course_id)
    if not course:
        return jsonify({"error": f"Course '{course_id}' not found."}), 404

    student_id = course.get("student_id", "default_student")
    docs = repo.list_student_documents(student_id)
    course_docs = [d for d in docs if d.get("course") == course["name"] or d.get("course_id") == course_id]

    # Calculate syllabus coverage based on documents and units
    units = course.get("units", [])
    total_units = len(units) or 1
    covered_units = min(total_units, len(course_docs))
    coverage_pct = round((covered_units / total_units) * 100, 1)

    return jsonify({
        "success": True,
        "course_id": course_id,
        "course": course,
        "materials_count": len(course_docs),
        "materials": course_docs,
        "syllabus_coverage_percentage": coverage_pct,
        "units": units,
    }), 200


# -----------------------------------------------------------------------------
# 6. PRACTICAL LEARNING (Phase 9O)
# -----------------------------------------------------------------------------
@student_platform_blueprint.route("/students/<student_id>/practical-tasks", methods=["POST"])
def generate_practical_task(student_id: str):
    """Generates subject-specific practical task (code debugging, SQL query, etc.)."""
    denied = _check_student_access(student_id)
    if denied:
        return denied

    data = request.get_json(silent=True) or {}
    subject = data.get("subject", "Machine Learning")
    topic = data.get("topic", "Gradient Descent")
    difficulty = data.get("difficulty", "INTERMEDIATE")
    course_id = data.get("course_id")

    svc = get_student_platform_service()
    try:
        task = svc.generate_practical_task(
            student_id=student_id,
            subject=subject,
            topic=topic,
            difficulty=difficulty,
            course_id=course_id,
        )
        return jsonify({"success": True, "practical_task": task}), 201
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@student_platform_blueprint.route("/students/<student_id>/practical-tasks", methods=["GET"])
def list_practical_tasks(student_id: str):
    """Lists practical tasks for a student."""
    denied = _check_student_access(student_id)
    if denied:
        return denied

    svc = get_student_platform_service()
    tasks = svc.list_practical_tasks(student_id)
    return jsonify({"success": True, "count": len(tasks), "practical_tasks": tasks}), 200


@student_platform_blueprint.route("/students/<student_id>/practical-tasks/<task_id>/evaluate", methods=["POST"])
def evaluate_practical_submission(student_id: str, task_id: str):
    """Evaluates student code/SQL submission against practical task test cases."""
    denied = _check_student_access(student_id)
    if denied:
        return denied

    data = request.get_json(silent=True) or {}
    code_submission = data.get("code_submission") or data.get("code", "")

    svc = get_student_platform_service()
    try:
        res = svc.evaluate_practical_submission(
            student_id=student_id,
            task_id=task_id,
            code_submission=code_submission,
        )
        return jsonify({"success": True, "result": res}), 200
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


# -----------------------------------------------------------------------------
# 7. ASK TEACHER & DOUBT VAULT (Phase 9P & 9Q)
# -----------------------------------------------------------------------------
@student_platform_blueprint.route("/students/<student_id>/ask-teacher", methods=["POST"])
def ask_teacher(student_id: str):
    """Answers student doubts with multi-turn contextual memory and avatar cues."""
    denied = _check_student_access(student_id)
    if denied:
        return denied

    data = request.get_json(silent=True) or {}
    doubt_text = data.get("doubt_text") or data.get("question")
    if not doubt_text:
        return jsonify({"error": "Field 'doubt_text' (or 'question') is required."}), 400

    context = data.get("context")
    svc = get_student_platform_service()
    try:
        response = svc.ask_teacher(
            student_id=student_id,
            doubt_text=doubt_text,
            context=context,
        )
        return jsonify({"success": True, "response": response}), 200
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@student_platform_blueprint.route("/students/<student_id>/doubts", methods=["GET"])
def list_doubts(student_id: str):
    """Lists doubts in student's Doubt Vault."""
    denied = _check_student_access(student_id)
    if denied:
        return denied

    svc = get_student_platform_service()
    doubts = svc.list_doubts(student_id)
    return jsonify({"success": True, "count": len(doubts), "doubts": doubts}), 200


@student_platform_blueprint.route("/doubts/<doubt_id>/status", methods=["PUT"])
def update_doubt_status(doubt_id: str):
    """Updates status of a doubt (RESOLVED, BOOKMARKED, MASTERED)."""
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    if not new_status:
        return jsonify({"error": "Field 'status' is required."}), 400

    token = extract_token_from_request()
    caller_id = None
    if token:
        mgr = get_session_token_manager()
        is_val, payload, err = mgr.verify_token(token)
        if not is_val:
            return jsonify({"success": False, "error": f"Unauthorized: {err}", "status": 401}), 401
        caller_id = payload.get("sub") or payload.get("student_id")

    svc = get_student_platform_service()
    updated = svc.update_doubt_status(doubt_id, new_status, student_id=caller_id)
    if not updated:
        if caller_id and svc.update_doubt_status(doubt_id, new_status):
            return jsonify({"success": False, "error": "Forbidden: You cannot modify another student's doubt.", "status": 403}), 403
        return jsonify({"error": f"Doubt '{doubt_id}' not found."}), 404
    return jsonify({"success": True, "doubt": updated}), 200


# -----------------------------------------------------------------------------
# 8. VIDEO INTERRUPTION & RESUME (Phase 9R)
# -----------------------------------------------------------------------------
@student_platform_blueprint.route("/students/<student_id>/teaching-session/interrupt", methods=["POST"])
def interrupt_session(student_id: str):
    """Pauses video lesson and provides immediate grounded explanation for student doubt."""
    denied = _check_student_access(student_id)
    if denied:
        return denied

    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id") or data.get("lesson_id") or f"session_{student_id}"
    paused_timestamp = float(data.get("paused_timestamp") if data.get("paused_timestamp") is not None else data.get("timestamp_seconds", 0.0))
    current_concept = data.get("current_concept") or data.get("topic", "Core Concept")
    doubt_text = data.get("doubt_text") or data.get("question", "Student interrupted lesson to clarify concept.")

    if not session_id or not doubt_text:
        return jsonify({"error": "Fields 'session_id' and 'doubt_text' are required."}), 400

    svc = get_student_platform_service()
    try:
        interrupted = svc.interrupt_session(
            student_id=student_id,
            session_id=session_id,
            paused_timestamp=paused_timestamp,
            current_concept=current_concept,
            doubt_text=doubt_text,
        )
        return jsonify({"success": True, "interruption": interrupted}), 200
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@student_platform_blueprint.route("/students/<student_id>/teaching-session/resume", methods=["POST"])
def resume_session(student_id: str):
    """Resumes teaching session right at the exact interrupted timestamp."""
    denied = _check_student_access(student_id)
    if denied:
        return denied

    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id") or data.get("lesson_id") or f"session_{student_id}"
    if not session_id:
        return jsonify({"error": "Field 'session_id' is required."}), 400

    svc = get_student_platform_service()
    try:
        resumed = svc.resume_session(student_id=student_id, session_id=session_id)
        return jsonify({"success": True, "resumption": resumed}), 200
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


# -----------------------------------------------------------------------------
# 9. TEACHING CONTROLS (Phase 9S)
# -----------------------------------------------------------------------------
@student_platform_blueprint.route("/students/<student_id>/teaching-session/control", methods=["POST"])
def execute_teaching_control(student_id: str):
    """Executes live pedagogical control actions (simpler, another example, visual, hint, slow down, switch language)."""
    data = request.get_json(silent=True) or {}
    params = data.get("params") or {}
    action = data.get("action")
    concept = data.get("concept") or params.get("concept", "Machine Learning Optimization")
    context = data.get("context") or params.get("context")

    if not action:
        return jsonify({"error": "Field 'action' is required."}), 400

    svc = get_student_platform_service()
    try:
        result = svc.execute_teaching_control(
            student_id=student_id,
            control_action=action,
            current_concept=concept,
            context=context,
        )
        return jsonify({"success": True, "control_result": result}), 200
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


# -----------------------------------------------------------------------------
# 10. CROSS-COURSE GRAPH, ANALYTICS & MENTOR REPORT (Phase 9K, 9L, 9N)
# -----------------------------------------------------------------------------
@student_platform_blueprint.route("/students/<student_id>/cross-course-graph", methods=["GET"])
def get_cross_course_graph(student_id: str):
    """Returns cross-course knowledge graph showing conceptual linkages across college subjects."""
    denied = _check_student_access(student_id)
    if denied:
        return denied

    svc = get_student_platform_service()
    graph = svc.get_cross_course_graph(student_id)
    return jsonify({"success": True, "knowledge_graph": graph}), 200


@student_platform_blueprint.route("/students/<student_id>/analytics", methods=["GET"])
def get_student_analytics(student_id: str):
    """Returns comprehensive learning analytics for the student."""
    denied = _check_student_access(student_id)
    if denied:
        return denied

    svc = get_student_platform_service()
    analytics = svc.get_student_analytics(student_id)
    return jsonify({"success": True, "analytics": analytics}), 200


@student_platform_blueprint.route("/students/<student_id>/mentor-report", methods=["GET"])
def get_mentor_report(student_id: str):
    """Generates collegiate progress and advisory report for mentors and parents."""
    denied = _check_student_access(student_id)
    if denied:
        return denied

    svc = get_student_platform_service()
    report = svc.generate_mentor_report(student_id)
    return jsonify({"success": True, "mentor_report": report}), 200


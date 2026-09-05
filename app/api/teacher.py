"""
Teacher Media API Blueprint.
Provides endpoints for audio synthesis, video generation, lesson segmentation,
live doubt interruption, and hardware/provider capability reporting.
"""

import os
from flask import Blueprint, request, jsonify, send_from_directory, abort
from backend.services.teacher_media.service import TeacherMediaService
from backend.services.teacher_media.profile import TeacherState

teacher_bp = Blueprint("teacher_api", __name__)
_service = TeacherMediaService.get_instance()

MEDIA_ROOT = os.path.abspath("data/media/teacher")


@teacher_bp.route("/teacher/status", methods=["GET"])
def get_teacher_status():
    """Returns active male professor profile and media service health."""
    profile = _service.get_profile()
    caps = _service.get_capabilities()
    return jsonify({
        "success": True,
        "teacher": profile.model_dump(),
        "capabilities": caps.model_dump(),
        "status": "OPERATIONAL"
    })


@teacher_bp.route("/teacher/media/capabilities", methods=["GET"])
def get_media_capabilities():
    """Returns detailed host capability probe results."""
    caps = _service.get_capabilities()
    return jsonify({
        "success": True,
        "capabilities": caps.model_dump()
    })


@teacher_bp.route("/teacher/media/diagnostics", methods=["GET"])
def get_media_diagnostics():
    """Detailed stream diagnostics for audio and video media files."""
    from backend.services.teacher_media.media.ffmpeg import FFmpegExecutor
    executor = FFmpegExecutor()

    target_file = request.args.get("file", "").strip()
    if not target_file:
        target_file = "app/static/teacher/teacher_video_audio_test.mp4"
    elif not os.path.isabs(target_file):
        for prefix in ["app/static/teacher/segments", "app/static/teacher", "data/media/teacher/segments", "data/media/teacher"]:
            cand = os.path.join(prefix, target_file)
            if os.path.exists(cand):
                target_file = cand
                break

    probe = executor.probe_media(target_file) if executor.is_available() else {}
    browser_url = f"/static/teacher/{os.path.basename(target_file)}"

    return jsonify({
        "success": True,
        "audio_present": probe.get("audio_present", False),
        "video_present": probe.get("video_present", False),
        "audio_duration": probe.get("audio_duration", 0.0),
        "video_duration": probe.get("video_duration", 0.0),
        "codec": probe.get("codec", {}),
        "sample_rate": probe.get("sample_rate", 0),
        "channels": probe.get("channels", 0),
        "browser_url": browser_url,
        "media_ready": probe.get("audio_present", False) and probe.get("video_present", False),
        "provider": _service.get_capabilities().primary_tts,
        "error": probe.get("error", None)
    })


@teacher_bp.route("/teacher/audio", methods=["POST"])
def synthesize_audio():
    """Synthesizes high-quality audio for a given script."""
    data = request.get_json(silent=True) or {}
    script = data.get("script", "").strip()
    if not script:
        return jsonify({"success": False, "error": "script is required"}), 400
        
    voice_id = data.get("voice_id")
    language = data.get("language", "en")
    speed = float(data.get("speed", 1.0))
    
    meta = _service.generate_teacher_audio(
        script=script,
        voice_id=voice_id,
        language=language,
        speed=speed
    )
    rel_path = os.path.relpath(meta.file_path, MEDIA_ROOT).replace(os.sep, "/")
    return jsonify({
        "success": True,
        "audio": meta.model_dump(),
        "media_url": f"/media/teacher/{rel_path}"
    })


@teacher_bp.route("/teacher/video", methods=["POST"])
def synthesize_video():
    """Generates a photorealistic male professor video segment."""
    data = request.get_json(silent=True) or {}
    script = data.get("script", "").strip()
    if not script:
        return jsonify({"success": False, "error": "script is required"}), 400
        
    state_str = data.get("teacher_state", "EXPLAINING")
    try:
        t_state = TeacherState(state_str)
    except ValueError:
        t_state = TeacherState.EXPLAINING
        
    video_meta = _service.generate_teacher_video(
        script=script,
        teacher_state=t_state
    )
    rel_path = os.path.relpath(video_meta.video_path, MEDIA_ROOT).replace(os.sep, "/")
    return jsonify({
        "success": True,
        "video": video_meta.model_dump(),
        "media_url": f"/media/teacher/{rel_path}"
    })


@teacher_bp.route("/teacher/lesson-segment", methods=["POST"])
def get_or_create_lesson_segment():
    """Creates or returns a cached teaching segment with whiteboard metadata."""
    data = request.get_json(silent=True) or {}
    course_id = data.get("course_id", "physics_101")
    lesson_id = data.get("lesson_id", "ohms_law_master")
    segment_id = data.get("segment_id", "seg_01")
    title = data.get("title", "Teaching Segment")
    script = data.get("script", "").strip()
    state_str = data.get("teacher_state", "EXPLAINING")
    
    try:
        t_state = TeacherState(state_str)
    except ValueError:
        t_state = TeacherState.EXPLAINING

    seg = _service.get_or_create_segment(
        course_id=course_id,
        lesson_id=lesson_id,
        segment_id=segment_id,
        title=title,
        script=script,
        teacher_state=t_state,
        whiteboard_data=data.get("whiteboard_data")
    )
    
    vid_rel = os.path.relpath(seg.video_path, MEDIA_ROOT).replace(os.sep, "/") if seg.video_path else None
    aud_rel = os.path.relpath(seg.audio_path, MEDIA_ROOT).replace(os.sep, "/") if seg.audio_path else None
    
    return jsonify({
        "success": True,
        "segment": seg.model_dump(),
        "video_url": f"/media/teacher/{vid_rel}" if vid_rel else None,
        "audio_url": f"/media/teacher/{aud_rel}" if aud_rel else None,
    })


@teacher_bp.route("/teacher/doubt", methods=["POST"])
def handle_doubt():
    """Handles live doubt interruption with exact timestamp resumption."""
    data = request.get_json(silent=True) or {}
    lesson_id = data.get("lesson_id", "ohms_law_master")
    timestamp = float(data.get("timestamp", 0.0))
    doubt_text = data.get("doubt", "").strip()
    
    if not doubt_text:
        return jsonify({"success": False, "error": "doubt text is required"}), 400
        
    res = _service.handle_doubt_interruption(
        lesson_id=lesson_id,
        current_timestamp=timestamp,
        student_doubt=doubt_text
    )
    
    vid_rel = os.path.relpath(res.video_path, MEDIA_ROOT).replace(os.sep, "/") if res.video_path else None
    aud_rel = os.path.relpath(res.audio_path, MEDIA_ROOT).replace(os.sep, "/") if res.audio_path else None
    
    return jsonify({
        "success": True,
        "doubt_response": res.model_dump(),
        "video_url": f"/media/teacher/{vid_rel}" if vid_rel else None,
        "audio_url": f"/media/teacher/{aud_rel}" if aud_rel else None,
    })


PHYSICS_VISUAL_PLAN = {
    "subject": "physics",
    "course_id": "physics_101",
    "lesson_id": "ohms_law_master",
    "title": "Ohm's Law: Fundamental Circuit Theory",
    "target_grade": "Undergraduate Physics / Engineering",
    "teacher_voice_id": "Daniel",
    "canonical_avatar": "/teacher-avatar/male_teacher.mp4",
    "segments": [
        {
            "segment_id": "seg_01_intro",
            "title": "Welcome & Electric Potential",
            "teacher_state": "INTRODUCING",
            "teacher_action": "introducing",
            "duration": 6.2,
            "video_url": "/static/teacher-avatar/generated/physics/seg_01_intro.mp4",
            "audio_url": "/static/teacher-avatar/generated/physics/seg_01_intro.wav",
            "script": "Good morning class. Today we will explore Ohm's Law, which forms the cornerstone of circuit theory.",
            "latex_formula": "V = I \\cdot R",
            "rag_citation": "Halliday, Resnick & Walker, Fundamentals of Physics (10th ed.), Chapter 26: Current and Resistance",
            "timeline_events": [
                {"timestamp": 0.0, "event_type": "SHOW_TITLE", "content": "Ohm's Law: Circuit Dynamics"},
                {"timestamp": 1.5, "event_type": "SHOW_DEFINITION", "content": "Electric potential difference drives charge through a conducting loop."},
                {"timestamp": 3.2, "event_type": "SHOW_FORMULA", "latex": "V = I \\cdot R"},
                {"timestamp": 4.8, "event_type": "HIGHLIGHT", "target": "voltage_source"}
            ],
            "whiteboard_state": {"voltage": 9, "resistance": 3, "current": 3.0, "highlight": "voltage"}
        },
        {
            "segment_id": "seg_02_voltage",
            "title": "Understanding Voltage (Potential Difference)",
            "teacher_state": "EXPLAINING",
            "teacher_action": "explain_example",
            "duration": 7.87,
            "video_url": "/static/teacher-avatar/generated/physics/seg_02_voltage.mp4",
            "audio_url": "/static/teacher-avatar/generated/physics/seg_02_voltage.wav",
            "script": "Voltage, or electric potential difference, is the electrical pressure from a power source that pushes electrons through a conducting loop.",
            "latex_formula": "V = \\frac{W}{Q} \\quad (1\\text{ Volt} = 1\\text{ J/C})",
            "rag_citation": "Serway & Jewett, Physics for Scientists and Engineers, Chapter 28: Direct-Current Circuits",
            "timeline_events": [
                {"timestamp": 0.0, "event_type": "SHOW_TITLE", "content": "Voltage: Energy per Unit Charge"},
                {"timestamp": 2.0, "event_type": "SHOW_DEFINITION", "content": "Electrical potential difference creating the internal electric field."},
                {"timestamp": 4.5, "event_type": "SHOW_FORMULA", "latex": "V = \\frac{\\Delta U}{q} = \\frac{W}{Q}"},
                {"timestamp": 6.0, "event_type": "HIGHLIGHT", "target": "battery_terminals"}
            ],
            "whiteboard_state": {"voltage": 12, "resistance": 3, "current": 4.0, "highlight": "voltage"}
        },
        {
            "segment_id": "seg_03_current",
            "title": "Understanding Current (Flow of Charge)",
            "teacher_state": "EXPLAINING",
            "teacher_action": "explain_example",
            "duration": 8.41,
            "video_url": "/static/teacher-avatar/generated/physics/seg_03_current.mp4",
            "audio_url": "/static/teacher-avatar/generated/physics/seg_03_current.wav",
            "script": "Current is the rate at which electric charge flows past a point in a circuit, measured in amperes, where one ampere equals one coulomb per second.",
            "latex_formula": "I = \\frac{dQ}{dt} = n q v_d A",
            "rag_citation": "Purcell & Morin, Electricity and Magnetism (Cambridge Univ. Press), Chapter 4: Electric Currents",
            "timeline_events": [
                {"timestamp": 0.0, "event_type": "SHOW_TITLE", "content": "Current: Net Drift of Electrons"},
                {"timestamp": 2.2, "event_type": "SHOW_DEFINITION", "content": "Rate of electric charge transport through cross-sectional area A."},
                {"timestamp": 4.8, "event_type": "SHOW_FORMULA", "latex": "I = \\frac{dQ}{dt} \\quad (1\\text{ A} = 1\\text{ C/s})"},
                {"timestamp": 6.8, "event_type": "HIGHLIGHT", "target": "drift_velocity"}
            ],
            "whiteboard_state": {"voltage": 9, "resistance": 3, "current": 3.0, "highlight": "current"}
        },
        {
            "segment_id": "seg_04_resistance",
            "title": "Understanding Electrical Resistance",
            "teacher_state": "EXPLAINING",
            "teacher_action": "point_to_formula",
            "duration": 7.62,
            "video_url": "/static/teacher-avatar/generated/physics/seg_04_resistance.mp4",
            "audio_url": "/static/teacher-avatar/generated/physics/seg_04_resistance.wav",
            "script": "Resistance is the opposition to the flow of electrical charge. When electrons drift through a conductor, they collide with lattice ions.",
            "latex_formula": "R = \\rho \\frac{L}{A}",
            "rag_citation": "Griffiths, Introduction to Electrodynamics (4th ed.), Chapter 7: Electrodynamics and Ohm's Law",
            "timeline_events": [
                {"timestamp": 0.0, "event_type": "SHOW_TITLE", "content": "Electrical Resistance & Lattice Scattering"},
                {"timestamp": 2.4, "event_type": "SHOW_DEFINITION", "content": "Scattering impedes drift, converting electrical potential energy into thermal dissipation."},
                {"timestamp": 5.0, "event_type": "SHOW_FORMULA", "latex": "R = \\rho \\frac{L}{A}"},
                {"timestamp": 6.5, "event_type": "HIGHLIGHT", "target": "resistor_element"}
            ],
            "whiteboard_state": {"voltage": 9, "resistance": 6, "current": 1.5, "highlight": "resistance"}
        },
        {
            "segment_id": "seg_05_formula",
            "title": "The Master Equation: I = V / R",
            "teacher_state": "POINTING",
            "teacher_action": "point_to_formula",
            "duration": 9.86,
            "video_url": "/static/teacher-avatar/generated/physics/seg_05_formula.mp4",
            "audio_url": "/static/teacher-avatar/generated/physics/seg_05_formula.wav",
            "script": "Using Ohm's Law, the current I in amperes equals voltage V divided by resistance R. Notice the direct proportionality to voltage and inverse relationship with resistance.",
            "latex_formula": "I = \\frac{V}{R} \\iff V = I \\cdot R \\iff R = \\frac{V}{I}",
            "rag_citation": "Ohm, Georg Simon (1827), Die galvanische Kette, mathematisch bearbeitet, Berlin",
            "timeline_events": [
                {"timestamp": 0.0, "event_type": "SHOW_TITLE", "content": "The Ohm's Law Triangle"},
                {"timestamp": 2.0, "event_type": "SHOW_FORMULA", "latex": "I = \\frac{V}{R}"},
                {"timestamp": 4.5, "event_type": "HIGHLIGHT", "target": "formula_triangle"},
                {"timestamp": 7.0, "event_type": "SHOW_DEFINITION", "content": "I is directly proportional to V and inversely proportional to R."}
            ],
            "whiteboard_state": {"voltage": 9, "resistance": 3, "current": 3.0, "highlight": "formula"}
        },
        {
            "segment_id": "seg_06_example",
            "title": "Worked Numerical Circuit Example",
            "teacher_state": "EXPLAINING",
            "teacher_action": "explain_example",
            "duration": 7.69,
            "video_url": "/static/teacher-avatar/generated/physics/seg_06_example.mp4",
            "audio_url": "/static/teacher-avatar/generated/physics/seg_06_example.wav",
            "script": "For example, if our battery supplies nine volts across a three ohm resistor, the resulting current is exactly three amperes.",
            "latex_formula": "I = \\frac{9\\text{ V}}{3\\ \\Omega} = 3.0\\text{ Amperes}",
            "rag_citation": "MIT OpenCourseWare 8.02: Electricity and Magnetism, DC Circuits Lab",
            "timeline_events": [
                {"timestamp": 0.0, "event_type": "SHOW_TITLE", "content": "Numerical Circuit Calculation"},
                {"timestamp": 2.0, "event_type": "SHOW_EXAMPLE", "content": "Battery: 9 Volts | Resistor: 3 Ohms"},
                {"timestamp": 4.5, "event_type": "SHOW_FORMULA", "latex": "I = \\frac{9\\text{V}}{3\\ \\Omega} = 3\\text{A}"},
                {"timestamp": 6.8, "event_type": "HIGHLIGHT", "target": "ammeter_readout"}
            ],
            "whiteboard_state": {"voltage": 9, "resistance": 3, "current": 3.0, "highlight": "calculation"}
        }
    ]
}

ML_VISUAL_PLAN = {
    "subject": "machine-learning",
    "course_id": "ml_501",
    "lesson_id": "gradient_descent_master",
    "title": "Gradient Descent: First-Order Optimization in ML",
    "target_grade": "Graduate Machine Learning / Deep Learning",
    "teacher_voice_id": "Daniel",
    "canonical_avatar": "/teacher-avatar/male_teacher.mp4",
    "segments": [
        {
            "segment_id": "seg_01_intro",
            "title": "Welcome & Optimization Foundations",
            "teacher_state": "INTRODUCING",
            "teacher_action": "introducing",
            "duration": 8.18,
            "video_url": "/static/teacher-avatar/generated/machine-learning/seg_01_intro.mp4",
            "audio_url": "/static/teacher-avatar/generated/machine-learning/seg_01_intro.wav",
            "script": "Welcome back. Today we examine Gradient Descent, the foundational first-order optimization algorithm that powers modern machine learning.",
            "latex_formula": "\\min_{\\theta} \\mathcal{L}(\\theta)",
            "rag_citation": "Goodfellow, Bengio & Courville, Deep Learning (MIT Press), Chapter 4.3: Gradient-Based Optimization",
            "timeline_events": [
                {"timestamp": 0.0, "event_type": "SHOW_TITLE", "content": "Optimization in Machine Learning"},
                {"timestamp": 1.8, "event_type": "SHOW_DEFINITION", "content": "Iterative parameter adjustment to minimize an empirical loss objective."},
                {"timestamp": 3.8, "event_type": "SHOW_FORMULA", "latex": "\\min_{\\theta \\in \\mathbb{R}^d} \\mathcal{L}(\\theta)"},
                {"timestamp": 5.8, "event_type": "HIGHLIGHT", "target": "loss_bowl"}
            ],
            "whiteboard_state": {"learning_rate": 0.1, "step_index": 0, "weight": 2.0, "loss": 4.0, "highlight": "loss_surface"}
        },
        {
            "segment_id": "seg_02_loss_surface",
            "title": "The Objective & Loss Surface J(w)",
            "teacher_state": "EXPLAINING",
            "teacher_action": "explain_example",
            "duration": 9.42,
            "video_url": "/static/teacher-avatar/generated/machine-learning/seg_02_loss_surface.mp4",
            "audio_url": "/static/teacher-avatar/generated/machine-learning/seg_02_loss_surface.wav",
            "script": "Our objective is to minimize a loss function J of theta, which measures the difference between model predictions and true ground truth targets across parameter space.",
            "latex_formula": "J(w) = \\frac{1}{2m}\\sum_{i=1}^m (h_w(x^{(i)}) - y^{(i)})^2",
            "rag_citation": "Bishop, Pattern Recognition and Machine Learning, Chapter 3.1: Linear Basis Function Models",
            "timeline_events": [
                {"timestamp": 0.0, "event_type": "SHOW_TITLE", "content": "The Convex Loss Landscape"},
                {"timestamp": 2.2, "event_type": "SHOW_DEFINITION", "content": "Mean squared error defines a convex parabolic bowl with a unique global minimum."},
                {"timestamp": 4.8, "event_type": "SHOW_FORMULA", "latex": "J(w) = \\frac{1}{2m}\\sum_{i=1}^m (w^T x^{(i)} - y^{(i)})^2"},
                {"timestamp": 6.8, "event_type": "HIGHLIGHT", "target": "global_minimum"}
            ],
            "whiteboard_state": {"learning_rate": 0.1, "step_index": 1, "weight": 1.6, "loss": 2.56, "highlight": "loss_surface"}
        },
        {
            "segment_id": "seg_03_learning_rate",
            "title": "Learning Rate (Step Size Alpha)",
            "teacher_state": "EXPLAINING",
            "teacher_action": "explain_example",
            "duration": 9.74,
            "video_url": "/static/teacher-avatar/generated/machine-learning/seg_03_learning_rate.mp4",
            "audio_url": "/static/teacher-avatar/generated/machine-learning/seg_03_learning_rate.wav",
            "script": "The learning rate alpha controls our step size. If alpha is too small, convergence takes forever; if too large, the updates will oscillate or diverge.",
            "latex_formula": "0 < \\alpha < \\frac{2}{L} \\quad (L\\text{-Lipschitz smoothness})",
            "rag_citation": "Boyd & Vandenberghe, Convex Optimization (Cambridge Univ. Press), Chapter 9.3: Gradient Descent Method",
            "timeline_events": [
                {"timestamp": 0.0, "event_type": "SHOW_TITLE", "content": "Hyperparameter: Step Size \\alpha"},
                {"timestamp": 2.5, "event_type": "SHOW_DEFINITION", "content": "Controls trajectory pace: small alpha converges slowly; excessive alpha diverges."},
                {"timestamp": 5.0, "event_type": "SHOW_FORMULA", "latex": "\\alpha \\in (0, 2/L)"},
                {"timestamp": 7.0, "event_type": "HIGHLIGHT", "target": "step_tuning"}
            ],
            "whiteboard_state": {"learning_rate": 0.1, "step_index": 2, "weight": 1.28, "loss": 1.64, "highlight": "learning_rate"}
        },
        {
            "segment_id": "seg_04_gradient_direction",
            "title": "Gradient Vector & Steepest Descent",
            "teacher_state": "POINTING",
            "teacher_action": "point_to_formula",
            "duration": 9.44,
            "video_url": "/static/teacher-avatar/generated/machine-learning/seg_04_gradient_direction.mp4",
            "audio_url": "/static/teacher-avatar/generated/machine-learning/seg_04_gradient_direction.wav",
            "script": "The gradient vector points in the direction of steepest ascent on the loss surface. Therefore, to minimize error, we take steps in the negative gradient direction.",
            "latex_formula": "-\\nabla J(w) = -\\left[ \\frac{\\partial J}{\\partial w_1}, \\dots, \\frac{\\partial J}{\\partial w_d} \\right]^T",
            "rag_citation": "Nocedal & Wright, Numerical Optimization (Springer), Chapter 2.2: Line Search Methods",
            "timeline_events": [
                {"timestamp": 0.0, "event_type": "SHOW_TITLE", "content": "Gradient Vector Direction"},
                {"timestamp": 2.2, "event_type": "SHOW_DEFINITION", "content": "Vector of partial derivatives points uphill; taking negative vector descends."},
                {"timestamp": 4.8, "event_type": "SHOW_FORMULA", "latex": "p_t = -\\nabla J(w_t)"},
                {"timestamp": 6.8, "event_type": "HIGHLIGHT", "target": "tangent_vector"}
            ],
            "whiteboard_state": {"learning_rate": 0.1, "step_index": 3, "weight": 1.024, "loss": 1.05, "highlight": "gradient_direction"}
        },
        {
            "segment_id": "seg_05_update_rule",
            "title": "Parameter Update Rule: w_t+1 = w_t - alpha * grad",
            "teacher_state": "POINTING",
            "teacher_action": "point_to_formula",
            "duration": 8.34,
            "video_url": "/static/teacher-avatar/generated/machine-learning/seg_05_update_rule.mp4",
            "audio_url": "/static/teacher-avatar/generated/machine-learning/seg_05_update_rule.wav",
            "script": "Here is the master parameter update equation: theta at t plus one equals theta at t minus alpha times the gradient of the loss function.",
            "latex_formula": "w_{t+1} = w_t - \\alpha \\nabla J(w_t)",
            "rag_citation": "Robbins & Monro (1951), A Stochastic Approximation Method, Annals of Math. Statistics",
            "timeline_events": [
                {"timestamp": 0.0, "event_type": "SHOW_TITLE", "content": "Master Parameter Update Equation"},
                {"timestamp": 2.0, "event_type": "SHOW_FORMULA", "latex": "w_{t+1} = w_t - \\alpha \\nabla J(w_t)"},
                {"timestamp": 4.5, "event_type": "HIGHLIGHT", "target": "update_rule"},
                {"timestamp": 6.8, "event_type": "SHOW_DEFINITION", "content": "Subtracting alpha * grad moves parameters towards the minimum."}
            ],
            "whiteboard_state": {"learning_rate": 0.1, "step_index": 4, "weight": 0.819, "loss": 0.67, "highlight": "update_rule"}
        },
        {
            "segment_id": "seg_06_example",
            "title": "Model Training & Convergence Example",
            "teacher_state": "EXPLAINING",
            "teacher_action": "explain_example",
            "duration": 8.13,
            "video_url": "/static/teacher-avatar/generated/machine-learning/seg_06_example.mp4",
            "audio_url": "/static/teacher-avatar/generated/machine-learning/seg_06_example.wav",
            "script": "In training deep neural networks and linear models, repeated mini-batch gradient descent iteratively drives weights toward the global or local minimum.",
            "latex_formula": "w^{(k)} \\xrightarrow{k \\to \\infty} w^* \\quad \\text{where } \\nabla J(w^*) = 0",
            "rag_citation": "Stanford CS229: Machine Learning Course Notes (Andrew Ng)",
            "timeline_events": [
                {"timestamp": 0.0, "event_type": "SHOW_TITLE", "content": "Neural Network Convergence"},
                {"timestamp": 2.2, "event_type": "SHOW_EXAMPLE", "content": "Iterative epoch updates drive loss to asymptote at minimum."},
                {"timestamp": 4.8, "event_type": "SHOW_FORMULA", "latex": "J(w^*) = \\min_w J(w)"},
                {"timestamp": 6.8, "event_type": "HIGHLIGHT", "target": "converged_minimum"}
            ],
            "whiteboard_state": {"learning_rate": 0.1, "step_index": 4, "weight": 0.819, "loss": 0.67, "highlight": "convergence"}
        }
    ]
}


@teacher_bp.route("/lessons/<lesson_id>/visual-plan", methods=["GET"])
def get_lesson_visual_plan(lesson_id: str):
    """Returns the rich visual plan and whiteboard synchronization events for a lesson."""
    lid = lesson_id.lower().replace("-", "_")
    if "grad" in lid or "ml" in lid or "optim" in lid:
        plan = ML_VISUAL_PLAN
    else:
        plan = PHYSICS_VISUAL_PLAN
    return jsonify({
        "success": True,
        "lesson_id": lesson_id,
        "subject": plan["subject"],
        "visual_plan": plan
    })


@teacher_bp.route("/teacher/visual-plan", methods=["GET"])
def get_teacher_visual_plan():
    """Returns the visual plan for either Physics (Ohm's Law) or Machine Learning (Gradient Descent)."""
    subject = request.args.get("subject", "").lower()
    lesson_id = request.args.get("lesson_id", "").lower()

    if "grad" in subject or "ml" in subject or "machine" in subject or "grad" in lesson_id or "ml" in lesson_id:
        plan = ML_VISUAL_PLAN
    else:
        plan = PHYSICS_VISUAL_PLAN

    return jsonify({
        "success": True,
        "subject": plan["subject"],
        "visual_plan": plan
    })


@teacher_bp.route("/teacher/segments", methods=["GET"])
def list_demo_segments():
    """Returns the pre-generated concept segments for the selected subject."""
    subject = request.args.get("subject", "").lower()
    lesson_id = request.args.get("lesson_id", "").lower()

    if "grad" in subject or "ml" in subject or "machine" in subject or "grad" in lesson_id or "ml" in lesson_id:
        plan = ML_VISUAL_PLAN
    else:
        plan = PHYSICS_VISUAL_PLAN

    segments = []
    for s in plan["segments"]:
        segments.append({
            "segment_id": s["segment_id"],
            "title": s["title"],
            "teacher_state": s["teacher_state"],
            "teacher_action": s.get("teacher_action", "explaining"),
            "duration": s.get("duration", 8.0),
            "video_url": s["video_url"],
            "audio_url": s["audio_url"],
            "script": s["script"],
            "latex_formula": s.get("latex_formula"),
            "rag_citation": s.get("rag_citation"),
            "timeline_events": s.get("timeline_events", []),
            "whiteboard": s.get("whiteboard_state", {})
        })

    return jsonify({
        "success": True,
        "subject": plan["subject"],
        "count": len(segments),
        "segments": segments
    })


@teacher_bp.route("/media/teacher/<path:filename>", methods=["GET"])
@teacher_bp.route("/teacher/<path:filename>", methods=["GET"])
def serve_teacher_media(filename: str):
    """Streams generated teacher media files safely."""
    if os.path.exists(os.path.join(MEDIA_ROOT, filename)):
        return send_from_directory(MEDIA_ROOT, filename)
    static_teacher = os.path.abspath("app/static/teacher")
    if os.path.exists(os.path.join(static_teacher, filename)):
        return send_from_directory(static_teacher, filename)
    static_avatar = os.path.abspath("app/static/teacher-avatar")
    if os.path.exists(os.path.join(static_avatar, filename)):
        return send_from_directory(static_avatar, filename)
    public_avatar = os.path.abspath("public/teacher-avatar")
    if os.path.exists(os.path.join(public_avatar, filename)):
        return send_from_directory(public_avatar, filename)
    abort(404)


@teacher_bp.route("/teacher-avatar/<path:filename>", methods=["GET"])
@teacher_bp.route("/media/teacher-avatar/<path:filename>", methods=["GET"])
def serve_teacher_avatar_media(filename: str):
    """Streams canonical teacher avatar media files safely."""
    public_avatar = os.path.abspath("public/teacher-avatar")
    if os.path.exists(os.path.join(public_avatar, filename)):
        return send_from_directory(public_avatar, filename)
    static_avatar = os.path.abspath("app/static/teacher-avatar")
    if os.path.exists(os.path.join(static_avatar, filename)):
        return send_from_directory(static_avatar, filename)
    abort(404)


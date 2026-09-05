import time
import uuid
import logging
from flask import Flask, request, jsonify, g, make_response
from werkzeug.exceptions import HTTPException

from app.api.realtime import realtime_blueprint
from app.api.harness import harness_blueprint
from app.api.assessment import assessment_blueprint
from app.api.visuals import visuals_blueprint
from app.api.media import media_blueprint
from app.api.trace import trace_blueprint
from app.api.demo_ui import demo_ui_bp
from app.api.input import input_blueprint
from app.api.documents import documents_blueprint
from app.api.rag import rag_blueprint
from app.api.learner import learner_blueprint
from app.api.planner import planner_blueprint
from app.api.router import router_blueprint
from app.api.analytics import analytics_blueprint
from app.api.health import health_blueprint
from app.api.courses import courses_blueprint
from app.api.student_platform import student_platform_blueprint
from app.api.auth import auth_blueprint
from app.api.teacher import teacher_bp
from app.config import Settings
from app.integrations.agora import EnvironmentAgoraCredentialsProvider

logger = logging.getLogger("ApurvaApp")


def create_app(settings: Settings | str | None = None) -> Flask:
    if isinstance(settings, str) or settings is None:
        settings = Settings.from_env()
        
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SETTINGS"] = settings
    app.config["AGORA_CREDENTIALS_PROVIDER"] = EnvironmentAgoraCredentialsProvider(settings)
    max_mb = getattr(settings, "max_content_length_mb", 50)
    app.config["MAX_CONTENT_LENGTH"] = max_mb * 1024 * 1024

    # 1. Request tracking & context middleware
    @app.before_request
    def before_request_handler():
        g.request_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex[:12]}"
        g.start_time = time.time()
        
        # Handle CORS preflight options immediately
        if request.method == "OPTIONS":
            resp = make_response(("", 204))
            _apply_cors_headers(resp, settings)
            return resp

    # 2. Response hardening & security headers
    @app.after_request
    def after_request_handler(response):
        # Attach request ID to every outgoing response
        req_id = getattr(g, "request_id", "")
        if req_id:
            response.headers["X-Request-ID"] = req_id

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Apply CORS
        _apply_cors_headers(response, settings)

        # Telemetry logging for API calls
        if request.path.startswith("/api/"):
            duration_ms = round((time.time() - getattr(g, "start_time", time.time())) * 1000, 2)
            logger.debug(
                f"[{req_id}] {request.method} {request.path} -> {response.status_code} ({duration_ms}ms)"
            )

        return response

    # 3. Production structured error handlers
    @app.errorhandler(400)
    def handle_bad_request(err):
        msg = err.description if hasattr(err, "description") else "Bad request"
        return jsonify({"success": False, "error": str(msg), "status": 400}), 400

    @app.errorhandler(404)
    def handle_not_found(err):
        return jsonify({"success": False, "error": "Endpoint not found", "status": 404}), 404

    @app.errorhandler(413)
    def handle_large_entity(err):
        return jsonify({
            "success": False,
            "error": f"Request payload exceeds the maximum allowed size ({settings.max_content_length_mb}MB)",
            "status": 413
        }), 413

    @app.errorhandler(429)
    def handle_rate_limit(err):
        return jsonify({"success": False, "error": "Rate limit exceeded. Please retry shortly.", "status": 429}), 429

    @app.errorhandler(Exception)
    def handle_general_exception(err):
        req_id = getattr(g, "request_id", "unknown")
        if isinstance(err, HTTPException):
            return jsonify({"success": False, "error": err.description, "status": err.code}), err.code

        logger.error(f"[{req_id}] Unhandled Exception: {err}", exc_info=True)
        # Never leak raw stack traces or internal secrets to users
        return jsonify({
            "success": False,
            "error": "Internal server error. Request ID: " + req_id,
            "status": 500
        }), 500

    # Register demo UI blueprint
    app.register_blueprint(demo_ui_bp)

    # Register blueprints under versioned /api/v1 namespace
    app.register_blueprint(health_blueprint, url_prefix="/api/v1")
    app.register_blueprint(realtime_blueprint, url_prefix="/api/v1/realtime")
    app.register_blueprint(input_blueprint, url_prefix="/api/v1")
    app.register_blueprint(documents_blueprint, url_prefix="/api/v1")
    app.register_blueprint(courses_blueprint, url_prefix="/api/v1")
    app.register_blueprint(student_platform_blueprint, url_prefix="/api/v1")
    app.register_blueprint(auth_blueprint, url_prefix="/api/v1")
    app.register_blueprint(rag_blueprint, url_prefix="/api/v1")
    app.register_blueprint(learner_blueprint, url_prefix="/api/v1")
    app.register_blueprint(planner_blueprint, url_prefix="/api/v1")
    app.register_blueprint(router_blueprint, url_prefix="/api/v1")
    app.register_blueprint(analytics_blueprint, url_prefix="/api/v1")
    app.register_blueprint(harness_blueprint, url_prefix="/api/v1")
    app.register_blueprint(assessment_blueprint, url_prefix="/api/v1")
    app.register_blueprint(visuals_blueprint, url_prefix="/api/v1")
    app.register_blueprint(media_blueprint, url_prefix="/api/v1")
    app.register_blueprint(trace_blueprint, url_prefix="/api/v1")
    app.register_blueprint(teacher_bp, url_prefix="/api/v1")

    return app


def _apply_cors_headers(response, settings: Settings | None):
    """Safely applies CORS headers according to environment configuration."""
    origin = request.headers.get("Origin")
    allowed = settings.get_allowed_origins_list() if (settings and hasattr(settings, "get_allowed_origins_list")) else ["*"]

    if "*" in allowed:
        response.headers["Access-Control-Allow-Origin"] = "*"
    elif origin and (origin in allowed or any(origin.endswith(a.lstrip("*")) for a in allowed if a.startswith("*"))):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"

    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Request-ID, Accept, Origin"


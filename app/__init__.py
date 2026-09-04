from flask import Flask

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
from app.config import Settings
from app.integrations.agora import EnvironmentAgoraCredentialsProvider


def create_app(settings: Settings | None = None) -> Flask:
    settings = settings or Settings.from_env()
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SETTINGS"] = settings
    app.config["AGORA_CREDENTIALS_PROVIDER"] = EnvironmentAgoraCredentialsProvider(settings)

    # Register demo UI blueprint
    app.register_blueprint(demo_ui_bp)

    # Register blueprints under versioned /api/v1 namespace
    app.register_blueprint(realtime_blueprint, url_prefix="/api/v1/realtime")
    app.register_blueprint(input_blueprint, url_prefix="/api/v1")
    app.register_blueprint(documents_blueprint, url_prefix="/api/v1")
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

    return app

from flask import Flask

from app.api.realtime import realtime_blueprint
from app.config import Settings
from app.integrations.agora import EnvironmentAgoraCredentialsProvider


def create_app(settings: Settings | None = None) -> Flask:
    settings = settings or Settings.from_env()
    app = Flask(__name__)
    app.config["AGORA_CREDENTIALS_PROVIDER"] = EnvironmentAgoraCredentialsProvider(settings)
    app.register_blueprint(realtime_blueprint, url_prefix="/api/v1/realtime")
    return app


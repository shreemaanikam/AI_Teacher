from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request
from pydantic import BaseModel, Field, ValidationError, field_validator

from app.integrations.agora import AgoraCredentialsProvider, AgoraNotConfigured

realtime_blueprint = Blueprint("realtime", __name__)


class CredentialsRequest(BaseModel):
    channel: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    uid: int = Field(ge=1, le=4_294_967_295)
    role: str = "publisher"

    @field_validator("role")
    @classmethod
    def supported_role(cls, value: str) -> str:
        if value not in {"publisher", "subscriber"}:
            raise ValueError("role must be publisher or subscriber")
        return value


@realtime_blueprint.post("/agora/credentials")
def agora_credentials():
    try:
        payload = CredentialsRequest.model_validate(request.get_json(silent=True) or {})
    except ValidationError as error:
        return jsonify({"error": "invalid_request", "details": error.errors(include_url=False)}), 400

    provider: AgoraCredentialsProvider = current_app.config["AGORA_CREDENTIALS_PROVIDER"]
    try:
        credentials = provider.issue(payload.channel, payload.uid, payload.role)
    except AgoraNotConfigured:
        return jsonify({"error": "agora_not_configured"}), 503
    return jsonify(credentials.model_dump(mode="json"))


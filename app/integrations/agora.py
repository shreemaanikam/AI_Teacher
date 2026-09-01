from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Protocol

from pydantic import BaseModel

from app.config import Settings


class AgoraNotConfigured(RuntimeError):
    pass


class AgoraCredentials(BaseModel):
    app_id: str
    channel: str
    uid: int
    token: str | None
    expires_at: datetime


class AgoraCredentialsProvider(Protocol):
    def issue(self, channel: str, uid: int, role: str) -> AgoraCredentials: ...


class EnvironmentAgoraCredentialsProvider:
    """Development bootstrap using a Console-issued, already-scoped token."""

    def __init__(self, settings: Settings):
        self.settings = settings

    def issue(self, channel: str, uid: int, role: str) -> AgoraCredentials:
        del role
        if not self.settings.agora_app_id:
            raise AgoraNotConfigured
        return AgoraCredentials(
            app_id=self.settings.agora_app_id,
            channel=channel,
            uid=uid,
            token=self.settings.agora_temp_token,
            expires_at=datetime.now(UTC) + timedelta(seconds=self.settings.agora_token_ttl_seconds),
        )


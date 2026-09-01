from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    agora_app_id: str | None = None
    agora_temp_token: str | None = None
    agora_token_ttl_seconds: int = 3600

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            agora_app_id=os.getenv("AGORA_APP_ID") or None,
            agora_temp_token=os.getenv("AGORA_TEMP_TOKEN") or None,
            agora_token_ttl_seconds=int(os.getenv("AGORA_TOKEN_TTL_SECONDS", "3600")),
        )


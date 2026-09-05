"""
Configuration settings and environment variable management for AI Teacher.
Loads configuration from .env safely without printing or exposing secret values.
"""

from __future__ import annotations
from dataclasses import dataclass
import os


def load_env_file():
    """Safely loads .env key-value pairs into os.environ without third-party dependencies."""
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k not in os.environ:
                        os.environ[k] = v


# Load environment variables on module import
load_env_file()


@dataclass(frozen=True)
class Settings:
    # Google Gemini
    gemini_api_key: str | None = None
    
    # OpenAI
    openai_api_key: str | None = None
    
    # Neon PostgreSQL
    database_url: str | None = None
    
    # Upstash Redis
    upstash_redis_rest_url: str | None = None
    upstash_redis_rest_token: str | None = None
    
    # Pinecone
    pinecone_api_key: str | None = None
    pinecone_index_name: str = "ai-teacher"
    pinecone_host: str | None = None
    
    # Weaviate
    weaviate_url: str | None = None
    weaviate_api_key: str | None = None
    
    # Google Cloud Vision
    google_cloud_vision_api_key: str | None = None
    
    # ElevenLabs
    elevenlabs_api_key: str | None = None
    
    # D-ID
    did_api_key: str | None = None
    
    # Provider selection
    llm_provider: str = "gemini"
    embedding_provider: str = "gemini"
    vector_db_provider: str = "pinecone"
    ocr_provider: str = "google_vision"
    stt_provider: str = "openai"
    image_provider: str = "gemini"
    tts_provider: str = "elevenlabs"
    video_provider: str = "did"
    
    # Models
    llm_model: str = "gemini-3.5-flash-lite"
    embedding_model: str = "gemini-embedding-2"
    
    # Application & Environment
    app_env: str = "development"
    debug: bool = False
    allowed_origins: str = "*"
    max_content_length_mb: int = 50
    rate_limit_per_minute: int = 120
    request_timeout_seconds: int = 30
    
    # Agora
    agora_app_id: str | None = None
    agora_temp_token: str | None = None
    agora_token_ttl_seconds: int = 3600

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() in ("production", "prod")

    def get_allowed_origins_list(self) -> list[str]:
        if not self.allowed_origins or self.allowed_origins.strip() == "*":
            return ["*"]
        return [orig.strip() for orig in self.allowed_origins.split(",") if orig.strip()]

    @classmethod
    def from_env(cls) -> "Settings":
        load_env_file()
        weav_url = os.getenv("WEAVIATE_URL")
        if weav_url and not weav_url.startswith("http"):
            weav_url = f"https://{weav_url}"
            
        return cls(
            gemini_api_key=os.getenv("GEMINI_API_KEY") or None,
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
            database_url=os.getenv("DATABASE_URL") or None,
            upstash_redis_rest_url=os.getenv("UPSTASH_REDIS_REST_URL") or None,
            upstash_redis_rest_token=os.getenv("UPSTASH_REDIS_REST_TOKEN") or None,
            pinecone_api_key=os.getenv("PINECONE_API_KEY") or None,
            pinecone_index_name=os.getenv("PINECONE_INDEX_NAME") or "ai-teacher",
            pinecone_host=os.getenv("PINECONE_HOST") or None,
            weaviate_url=weav_url,
            weaviate_api_key=os.getenv("WEAVIATE_API_KEY") or None,
            google_cloud_vision_api_key=os.getenv("GOOGLE_CLOUD_VISION_API_KEY") or None,
            elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY") or None,
            did_api_key=os.getenv("DID_API_KEY") or None,
            llm_provider=(os.getenv("LLM_PROVIDER") or "gemini").lower(),
            embedding_provider=(os.getenv("EMBEDDING_PROVIDER") or "gemini").lower(),
            vector_db_provider=(os.getenv("VECTOR_DB_PROVIDER") or "pinecone").lower(),
            ocr_provider=(os.getenv("OCR_PROVIDER") or "google_vision").lower(),
            stt_provider=(os.getenv("STT_PROVIDER") or "openai").lower(),
            image_provider=(os.getenv("IMAGE_PROVIDER") or "gemini").lower(),
            tts_provider=(os.getenv("TTS_PROVIDER") or "elevenlabs").lower(),
            video_provider=(os.getenv("VIDEO_PROVIDER") or "did").lower(),
            llm_model=os.getenv("LLM_MODEL") or "gemini-3.5-flash-lite",
            embedding_model=os.getenv("EMBEDDING_MODEL") or "gemini-embedding-2",
            app_env=os.getenv("APP_ENV") or "development",
            debug=(os.getenv("DEBUG") or "false").lower() in ("true", "1", "yes"),
            allowed_origins=os.getenv("ALLOWED_ORIGINS") or "*",
            max_content_length_mb=int(os.getenv("MAX_CONTENT_LENGTH_MB", "50")),
            rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "120")),
            request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30")),
            agora_app_id=os.getenv("AGORA_APP_ID") or None,
            agora_temp_token=os.getenv("AGORA_TEMP_TOKEN") or None,
            agora_token_ttl_seconds=int(os.getenv("AGORA_TOKEN_TTL_SECONDS", "3600")),
        )


_SETTINGS: Settings | None = None


def get_settings() -> Settings:
    global _SETTINGS
    if _SETTINGS is None:
        _SETTINGS = Settings.from_env()
    return _SETTINGS

"""
Data models and schemas for Module 6: AI Model Intelligence & Model Router.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class TaskType(str, Enum):
    LESSON_PLANNING = "LESSON_PLANNING"
    EXPLANATION = "EXPLANATION"
    QUESTION_GENERATION = "QUESTION_GENERATION"
    ANSWER_EVALUATION = "ANSWER_EVALUATION"
    MISCONCEPTION_ANALYSIS = "MISCONCEPTION_ANALYSIS"
    TRANSLATION = "TRANSLATION"
    SUMMARIZATION = "SUMMARIZATION"
    VISUAL_PLANNING = "VISUAL_PLANNING"
    SCRIPT_GENERATION = "SCRIPT_GENERATION"
    RECOMMENDATION = "RECOMMENDATION"
    RAG_QUERY_REWRITE = "RAG_QUERY_REWRITE"


class RoutingMode(str, Enum):
    FAST = "FAST"
    BALANCED = "BALANCED"
    QUALITY = "QUALITY"


class ModelProviderType(str, Enum):
    OPENAI = "OPENAI"
    GEMINI = "GEMINI"
    LOCAL_FALLBACK = "LOCAL_FALLBACK"


class ModelRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: f"mreq_{uuid.uuid4().hex[:8]}")
    task_type: TaskType
    prompt: str
    subject: str = "physics"
    complexity: str = "medium"  # low, medium, high
    language: str = "en"
    routing_mode: RoutingMode = RoutingMode.BALANCED
    latency_budget_ms: int = 3000
    context_length: int = 500
    structured_schema: Optional[str] = None


class ModelDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"dec_{uuid.uuid4().hex[:8]}")
    task_type: TaskType
    chosen_provider: ModelProviderType
    chosen_model: str
    routing_mode: RoutingMode
    reason: str
    estimated_cost_usd: float = 0.0001
    estimated_latency_ms: int = 150
    fallback_chain: List[ModelProviderType] = Field(
        default_factory=lambda: [ModelProviderType.LOCAL_FALLBACK]
    )


class ModelUsageRecord(BaseModel):
    """Tracks token usage, cost, and latency for AI observability."""
    record_id: str = Field(default_factory=lambda: f"usg_{uuid.uuid4().hex[:8]}")
    request_id: str
    task_type: TaskType
    provider: ModelProviderType
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    estimated_cost_usd: float = 0.0
    success: bool = True
    fallback_used: bool = False
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

"""
Unit and integration tests for Gemini Primary LLM routing, fallback policies, and telemetry.
"""

import pytest
import os
from unittest.mock import patch, MagicMock

from app.router.router import ModelRouter, get_model_router
from app.router.models import ModelRequest, TaskType, RoutingMode, ModelProviderType
from app.router.providers import GeminiProvider, OpenAIProvider, LocalFallbackProvider
from app.config import get_settings


def test_1_gemini_primary_provider_selection():
    """Verify Gemini is selected as the primary provider when GEMINI_API_KEY is available."""
    router = ModelRouter()
    req = ModelRequest(
        task_type=TaskType.EXPLANATION,
        prompt="Explain Ohm's Law.",
        language="hi",
        routing_mode=RoutingMode.FAST,
    )
    decision = router.route_request(req)
    if os.getenv("GEMINI_API_KEY"):
        assert decision.chosen_provider == ModelProviderType.GEMINI
        assert "gemini" in decision.chosen_model.lower()


def test_2_model_router_fallback_hierarchy():
    """Verify fallback chain: Gemini -> OpenAI -> LocalFallback."""
    router = ModelRouter()
    req = ModelRequest(
        task_type=TaskType.LESSON_PLANNING,
        prompt="Plan lesson on Ohm's Law.",
        routing_mode=RoutingMode.QUALITY,
    )
    with patch.dict(os.environ, {"GEMINI_API_KEY": "dummy_key", "OPENAI_API_KEY": "dummy_key"}):
        decision = router.route_request(req)
        assert decision.chosen_provider == ModelProviderType.GEMINI
        assert ModelProviderType.OPENAI in decision.fallback_chain
        assert ModelProviderType.LOCAL_FALLBACK in decision.fallback_chain


def test_3_gemini_provider_offline_fallback():
    """Verify GeminiProvider falls back cleanly to LocalFallbackProvider when no API key is set."""
    provider = GeminiProvider(api_key=None)
    output = provider.generate("Explain Ohm's Law.")
    assert "Ohm's Law" in output or "voltage" in output.lower() or "current" in output.lower()


def test_4_gemini_provider_api_error_fallback():
    """Verify GeminiProvider falls back gracefully when API returns HTTP error."""
    provider = GeminiProvider(api_key="invalid_test_key")
    output = provider.generate("Explain Python variables.")
    assert "Python" in output or "variable" in output.lower()


def test_5_router_usage_telemetry_sanitization():
    """Verify telemetry records log model usage without leaking credentials or secret values."""
    router = ModelRouter()
    req = ModelRequest(
        task_type=TaskType.EXPLANATION,
        prompt="Explain Ohm's Law simply.",
        language="hi",
        routing_mode=RoutingMode.FAST,
    )
    router.execute(req)
    records = router.get_usage_records()
    assert len(records) > 0
    latest = records[-1]
    assert latest.task_type == TaskType.EXPLANATION
    assert latest.latency_ms >= 0
    record_str = str(latest)
    assert "AIza" not in record_str
    assert "sk-" not in record_str

"""
Intelligent Model Router for Module 6: AI Model Intelligence.
Separates AI model capability selection from pedagogical policy orchestration.
"""

from __future__ import annotations
import os
import time
import logging
from typing import Dict, List, Optional

from app.router.models import (
    TaskType,
    RoutingMode,
    ModelProviderType,
    ModelRequest,
    ModelDecision,
    ModelUsageRecord,
)
from app.router.providers import (
    ModelProvider,
    OpenAIProvider,
    GeminiProvider,
    LocalFallbackProvider,
)
from app.prompts import get_prompt_for_task

logger = logging.getLogger("ModelRouter")


class ModelRouter:
    """
    Evaluates task complexity, latency budget, cost, and routing mode to choose
    the optimal AI capability and execute with automated fallback chains.
    """

    def __init__(self):
        self.openai_provider = OpenAIProvider()
        self.gemini_provider = GeminiProvider()
        self.local_provider = LocalFallbackProvider()
        self._usage_records: List[ModelUsageRecord] = []

    def route_request(self, request: ModelRequest) -> ModelDecision:
        """Determines the optimal model provider and model ID based on task and routing mode."""
        has_openai = bool(os.getenv("OPENAI_API_KEY"))
        has_gemini = bool(os.getenv("GEMINI_API_KEY"))

        # Default fallback
        chosen_provider = ModelProviderType.LOCAL_FALLBACK
        chosen_model = "local_deterministic_v1"
        reason = "Local deterministic runtime selected."
        cost = 0.0
        lat = 50

        if request.routing_mode == RoutingMode.QUALITY and has_openai:
            chosen_provider = ModelProviderType.OPENAI
            chosen_model = "gpt-4o"
            reason = f"High-reasoning quality mode selected for {request.task_type.value}."
            cost = 0.005
            lat = 1200
        elif request.routing_mode == RoutingMode.QUALITY and has_gemini:
            chosen_provider = ModelProviderType.GEMINI
            chosen_model = "gemini-1.5-pro"
            reason = f"Deep reasoning quality mode selected for {request.task_type.value}."
            cost = 0.003
            lat = 1100
        elif request.routing_mode in [RoutingMode.FAST, RoutingMode.BALANCED]:
            if has_gemini:
                chosen_provider = ModelProviderType.GEMINI
                chosen_model = "gemini-2.0-flash"
                reason = "Fast, cost-effective multimodal model selected."
                cost = 0.0002
                lat = 400
            elif has_openai:
                chosen_provider = ModelProviderType.OPENAI
                chosen_model = "gpt-4o-mini"
                reason = "Fast balanced reasoning model selected."
                cost = 0.0003
                lat = 450
            else:
                chosen_provider = ModelProviderType.LOCAL_FALLBACK
                chosen_model = "local_deterministic_v1"
                reason = "Offline local fallback engine active (zero external API dependency)."
                cost = 0.0
                lat = 20

        # Construct fallback chain
        fallbacks = [ModelProviderType.LOCAL_FALLBACK]
        if chosen_provider == ModelProviderType.OPENAI and has_gemini:
            fallbacks.insert(0, ModelProviderType.GEMINI)
        elif chosen_provider == ModelProviderType.GEMINI and has_openai:
            fallbacks.insert(0, ModelProviderType.OPENAI)

        return ModelDecision(
            task_type=request.task_type,
            chosen_provider=chosen_provider,
            chosen_model=chosen_model,
            routing_mode=request.routing_mode,
            reason=reason,
            estimated_cost_usd=cost,
            estimated_latency_ms=lat,
            fallback_chain=fallbacks,
        )

    def execute(self, request: ModelRequest) -> str:
        """Executes the request through the routed provider with automated fallback chain and latency/token logging."""
        decision = self.route_request(request)
        system_prompt = get_prompt_for_task(request.task_type.value.lower())
        start_time = time.time()
        success = False
        fallback_used = False
        err_msg = None
        output = ""

        provider_map = {
            ModelProviderType.OPENAI: self.openai_provider,
            ModelProviderType.GEMINI: self.gemini_provider,
            ModelProviderType.LOCAL_FALLBACK: self.local_provider,
        }

        # Attempt primary chosen provider
        active_provider = provider_map[decision.chosen_provider]
        try:
            if request.task_type == TaskType.TRANSLATION:
                output = active_provider.translate(request.prompt, request.language)
            elif request.task_type == TaskType.ANSWER_EVALUATION:
                output = active_provider.evaluate(request.prompt, system_prompt)
            elif request.task_type in [TaskType.LESSON_PLANNING, TaskType.MISCONCEPTION_ANALYSIS]:
                output = active_provider.reason(request.prompt, system_prompt, decision.chosen_model)
            else:
                output = active_provider.generate(request.prompt, system_prompt, decision.chosen_model)
            success = True
        except Exception as e:
            logger.warning(f"Primary provider {decision.chosen_provider.value} failed: {e}. Trying fallback chain.")
            fallback_used = True
            err_msg = str(e)
            for fb in decision.fallback_chain:
                try:
                    fb_provider = provider_map[fb]
                    output = fb_provider.generate(request.prompt, system_prompt)
                    success = True
                    break
                except Exception as fb_err:
                    err_msg = f"{err_msg} | Fallback {fb.value} failed: {fb_err}"

        latency_ms = round((time.time() - start_time) * 1000, 2)
        in_tokens = len(request.prompt.split()) + len(system_prompt.split())
        out_tokens = len(output.split())

        # Record usage
        usage_record = ModelUsageRecord(
            request_id=request.request_id,
            task_type=request.task_type,
            provider=decision.chosen_provider if not fallback_used else ModelProviderType.LOCAL_FALLBACK,
            model=decision.chosen_model if not fallback_used else "local_deterministic_v1",
            input_tokens=in_tokens,
            output_tokens=out_tokens,
            latency_ms=latency_ms,
            estimated_cost_usd=decision.estimated_cost_usd if success and not fallback_used else 0.0,
            success=success,
            fallback_used=fallback_used,
            error_message=err_msg,
        )
        self._usage_records.append(usage_record)
        return output

    def get_usage_records(self) -> List[ModelUsageRecord]:
        return list(self._usage_records)


# Global singleton
_GLOBAL_MODEL_ROUTER = ModelRouter()


def get_model_router() -> ModelRouter:
    return _GLOBAL_MODEL_ROUTER

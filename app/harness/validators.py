"""
Structured Output Validator for Module 5 (Teaching Harness).
Ensures all AI and external outputs conform to strict Pydantic schemas with deterministic fallback recovery.
"""

from __future__ import annotations
import logging
from typing import Any, Callable, Dict, Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class StructuredOutputValidator:
    """
    Validates dictionary payloads against Pydantic models.
    Provides automatic fallback synthesis if LLM outputs fail schema validation.
    """

    def __init__(self, max_repairs: int = 1):
        self.max_repairs = max_repairs
        self.validation_errors_count = 0

    def validate_or_fallback(
        self,
        schema: Type[T],
        data: Any,
        fallback_factory: Callable[[], T],
        context_name: str = "general",
    ) -> T:
        """
        Validates raw data against the requested schema.
        If invalid, executes the fallback factory and logs the issue.
        """
        if isinstance(data, schema):
            return data

        if isinstance(data, dict):
            try:
                return schema.model_validate(data)
            except ValidationError as err:
                self.validation_errors_count += 1
                logger.warning(
                    f"Schema validation failed for {context_name} on {schema.__name__}: {err}. Applying fallback."
                )

        # Fallback invocation
        try:
            fallback_val = fallback_factory()
            logger.info(f"Fallback generated successfully for {context_name}")
            return fallback_val
        except Exception as e:
            self.validation_errors_count += 1
            logger.error(f"Fallback generation failed for {context_name}: {e}")
            raise e

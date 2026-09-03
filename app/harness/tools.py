"""
Tool Registry for Module 5 (Teaching Harness).
Provides internal dispatching and execution boundaries for specialist tools.
"""

from __future__ import annotations
import logging
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Central registry for teaching tools (Assessment, Visuals, Media, RAG, Learner Profile).
    Permits deterministic dispatching and mock injection during testing.
    """

    def __init__(self):
        self._tools: Dict[str, Callable[..., Any]] = {}

    def register(self, name: str, handler: Callable[..., Any]) -> None:
        self._tools[name] = handler
        logger.debug(f"Registered tool: {name}")

    def execute(self, name: str, *args, **kwargs) -> Any:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not registered in ToolRegistry.")
        try:
            return self._tools[name](*args, **kwargs)
        except Exception as e:
            logger.error(f"Error executing tool '{name}': {e}", exc_info=True)
            raise e

    def has_tool(self, name: str) -> bool:
        return name in self._tools

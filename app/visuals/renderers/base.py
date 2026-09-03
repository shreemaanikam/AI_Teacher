"""
Base Visual Renderer interface for Module 8.
"""

from abc import ABC, abstractmethod
from app.visuals.models import VisualSpec, VisualAsset


class BaseVisualRenderer(ABC):
    """Abstract base renderer for educational visual specs."""

    @abstractmethod
    def render(self, spec: VisualSpec) -> VisualAsset:
        """Renders the given VisualSpec into a concrete VisualAsset."""
        pass

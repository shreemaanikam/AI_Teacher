"""
Visual Intelligence Engine for Module 8.
Coordinates subject-aware visual strategy planning and deterministic asset rendering.
"""

from __future__ import annotations
import logging
from typing import Dict, Optional

from app.visuals.models import (
    VisualSpec,
    VisualAsset,
    VisualType,
    SubjectCategory,
    RenderFormat,
)
from app.visuals.strategies import VisualStrategyPlanner
from app.visuals.renderers import (
    BaseVisualRenderer,
    SvgCircuitRenderer,
    SvgAnalogyRenderer,
    MatplotlibPlotRenderer,
    MermaidRenderer,
    LatexEquationRenderer,
    CodeRenderer,
)
from app.harness.session import TeachingStrategy
from app.assessment.models import MisconceptionRecord

logger = logging.getLogger(__name__)


class VisualIntelligenceEngine:
    """
    Coordinates subject classification, strategy planning, and renderer dispatching.
    Produces high-fidelity deterministic graphics for lesson scenes and video composition.
    """

    def __init__(self, planner: Optional[VisualStrategyPlanner] = None):
        self.planner = planner or VisualStrategyPlanner()
        self._renderers: Dict[str, BaseVisualRenderer] = {
            "svg_circuit": SvgCircuitRenderer(),
            "svg_analogy": SvgAnalogyRenderer(),
            "matplotlib_plot": MatplotlibPlotRenderer(),
            "mermaid_renderer": MermaidRenderer(),
            "latex_equation": LatexEquationRenderer(),
            "code_renderer": CodeRenderer(),
        }
        self._assets_store: Dict[str, VisualAsset] = {}

    def register_renderer(self, name: str, renderer: BaseVisualRenderer) -> None:
        self._renderers[name] = renderer

    def plan_visual(
        self,
        subject: str,
        concept: str,
        teaching_strategy: TeachingStrategy = TeachingStrategy.DIRECT_EXPLANATION,
        misconception: Optional[MisconceptionRecord] = None,
        duration_seconds: int = 15,
    ) -> VisualSpec:
        """Plans the visual specification without yet generating the final asset."""
        return self.planner.plan_visual_spec(
            subject_hint=subject,
            concept=concept,
            teaching_strategy=teaching_strategy,
            misconception=misconception,
            duration_seconds=duration_seconds,
        )

    def render_visual(self, spec: VisualSpec) -> VisualAsset:
        """Executes the assigned deterministic renderer for the given spec."""
        renderer = self._renderers.get(spec.renderer)

        if not renderer:
            # Fallback based on visual type
            if spec.visual_type == VisualType.CIRCUIT_DIAGRAM:
                renderer = self._renderers["svg_circuit"]
            elif spec.visual_type == VisualType.ANALOGY_WATER_CIRCUIT:
                renderer = self._renderers["svg_analogy"]
            elif spec.visual_type == VisualType.GRAPH_PLOT:
                renderer = self._renderers["matplotlib_plot"]
            elif spec.visual_type == VisualType.LATEX_EQUATION:
                renderer = self._renderers["latex_equation"]
            elif spec.visual_type == VisualType.CODE_BLOCK:
                renderer = self._renderers["code_renderer"]
            else:
                renderer = self._renderers["mermaid_renderer"]

        asset = renderer.render(spec)
        self._assets_store[asset.asset_id] = asset
        return asset

    def generate_visual(
        self,
        subject: str,
        concept: str,
        teaching_strategy: TeachingStrategy = TeachingStrategy.DIRECT_EXPLANATION,
        misconception: Optional[MisconceptionRecord] = None,
        duration_seconds: int = 15,
    ) -> VisualAsset:
        """One-stop helper: plans spec and renders asset."""
        spec = self.plan_visual(subject, concept, teaching_strategy, misconception, duration_seconds)
        return self.render_visual(spec)

    def get_asset(self, asset_id: str) -> Optional[VisualAsset]:
        return self._assets_store.get(asset_id)

"""
Visual Intelligence Engine for Module 8.
Coordinates subject-aware visual strategy planning, deterministic asset rendering,
and multi-step progressive whiteboard teaching.
"""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional

from app.visuals.models import (
    VisualSpec,
    VisualAsset,
    VisualType,
    SubjectCategory,
    RenderFormat,
    TeachingVisualPlan,
    VisualBoardTheme,
)
from app.visuals.strategies import VisualStrategyPlanner
from app.visuals.board_engine import DynamicWhiteboardEngine
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
    Coordinates subject classification, strategy planning, renderer dispatching,
    and progressive step-by-step whiteboard execution.
    """

    def __init__(
        self,
        planner: Optional[VisualStrategyPlanner] = None,
        whiteboard_engine: Optional[DynamicWhiteboardEngine] = None,
    ):
        self.planner = planner or VisualStrategyPlanner()
        self.whiteboard_engine = whiteboard_engine or DynamicWhiteboardEngine()
        self._renderers: Dict[str, BaseVisualRenderer] = {
            "svg_circuit": SvgCircuitRenderer(),
            "svg_analogy": SvgAnalogyRenderer(),
            "matplotlib_plot": MatplotlibPlotRenderer(),
            "mermaid_renderer": MermaidRenderer(),
            "latex_equation": LatexEquationRenderer(),
            "code_renderer": CodeRenderer(),
        }
        self._assets_store: Dict[str, VisualAsset] = {}
        self._plans_store: Dict[str, TeachingVisualPlan] = {}

    def register_renderer(self, name: str, renderer: BaseVisualRenderer) -> None:
        self._renderers[name] = renderer

    def plan_visual(
        self,
        subject: str,
        concept: str,
        teaching_strategy: TeachingStrategy = TeachingStrategy.DIRECT_EXPLANATION,
        misconception: Optional[MisconceptionRecord] = None,
        duration_seconds: int = 15,
        document_id: Optional[str] = None,
        chunk_id: Optional[str] = None,
        source_reference: Optional[Dict[str, Any]] = None,
    ) -> VisualSpec:
        """Plans the visual specification without yet generating the final asset."""
        return self.planner.plan_visual_spec(
            subject_hint=subject,
            concept=concept,
            teaching_strategy=teaching_strategy,
            misconception=misconception,
            duration_seconds=duration_seconds,
            document_id=document_id,
            chunk_id=chunk_id,
            source_reference=source_reference,
        )

    def plan_visual_teaching(
        self,
        concept: str,
        subject_hint: str = "general",
        teaching_strategy: TeachingStrategy = TeachingStrategy.DIRECT_EXPLANATION,
        misconception: Optional[MisconceptionRecord] = None,
        duration_seconds: int = 15,
        document_id: Optional[str] = None,
        source_chunk_ids: Optional[List[str]] = None,
        source_reference: Optional[Dict[str, Any]] = None,
        evidence_snippets: Optional[List[str]] = None,
        language: str = "en",
        theme: VisualBoardTheme = VisualBoardTheme.CHALKBOARD,
    ) -> TeachingVisualPlan:
        """Generates a structured, source-grounded TeachingVisualPlan."""
        plan = self.planner.plan_teaching_visual(
            concept=concept,
            subject_hint=subject_hint,
            teaching_strategy=teaching_strategy,
            misconception=misconception,
            duration_seconds=duration_seconds,
            document_id=document_id,
            source_chunk_ids=source_chunk_ids,
            source_reference=source_reference,
            evidence_snippets=evidence_snippets,
            language=language,
            theme=theme,
        )
        self._plans_store[plan.visual_id] = plan
        return plan

    def render_visual(self, spec: VisualSpec) -> VisualAsset:
        """Executes the assigned renderer or dynamic whiteboard for the given spec."""
        # 1. Specialized legacy renderer dispatch if explicitly requested
        if spec.renderer in self._renderers and spec.renderer != "dynamic_whiteboard":
            renderer = self._renderers[spec.renderer]
            asset = renderer.render(spec)
            self._assets_store[asset.asset_id] = asset
            return asset

        # 2. Dynamic Whiteboard render if spec has an attached TeachingVisualPlan
        if spec.visual_plan:
            self._plans_store[spec.visual_plan.visual_id] = spec.visual_plan
            step_idx = spec.parameters.get("step_index", 0)
            asset = self.whiteboard_engine.render_plan_to_asset(spec.visual_plan, step_index=step_idx)
            self._assets_store[asset.asset_id] = asset
            return asset

        # 3. Dynamic Whiteboard render for multi-step interactive types
        if spec.renderer == "dynamic_whiteboard" or spec.visual_type in (
            VisualType.WHITEBOARD,
            VisualType.CHALKBOARD,
            VisualType.EQUATION_DERIVATION,
            VisualType.CODE_EXECUTION,
            VisualType.ARRAY_POINTER,
            VisualType.NETWORK_FLOW,
        ):
            plan = self.planner.plan_teaching_visual(
                concept=spec.concept,
                subject_hint=spec.subject.value,
                duration_seconds=spec.duration_seconds,
                document_id=spec.document_id,
                source_chunk_ids=[spec.chunk_id] if spec.chunk_id else [],
                source_reference=spec.source_reference,
            )
            self._plans_store[plan.visual_id] = plan
            step_idx = spec.parameters.get("step_index", 0)
            asset = self.whiteboard_engine.render_plan_to_asset(plan, step_index=step_idx)
            self._assets_store[asset.asset_id] = asset
            return asset

        # 4. Fallback renderer dispatch
        renderer = self._renderers.get(spec.renderer, self._renderers["mermaid_renderer"])
        asset = renderer.render(spec)
        self._assets_store[asset.asset_id] = asset
        return asset

    def render_teaching_visual(
        self,
        plan: TeachingVisualPlan,
        step_index: Optional[int] = None,
        aspect_ratio: str = "16:9",
    ) -> VisualAsset:
        """Renders a TeachingVisualPlan to an active VisualAsset."""
        self._plans_store[plan.visual_id] = plan
        asset = self.whiteboard_engine.render_plan_to_asset(plan, step_index=step_index, aspect_ratio=aspect_ratio)
        self._assets_store[asset.asset_id] = asset
        return asset

    def generate_visual(
        self,
        subject: str,
        concept: str,
        teaching_strategy: TeachingStrategy = TeachingStrategy.DIRECT_EXPLANATION,
        misconception: Optional[MisconceptionRecord] = None,
        duration_seconds: int = 15,
        document_id: Optional[str] = None,
        chunk_id: Optional[str] = None,
        source_reference: Optional[Dict[str, Any]] = None,
    ) -> VisualAsset:
        """One-stop helper: plans spec and renders asset."""
        spec = self.plan_visual(
            subject=subject,
            concept=concept,
            teaching_strategy=teaching_strategy,
            misconception=misconception,
            duration_seconds=duration_seconds,
            document_id=document_id,
            chunk_id=chunk_id,
            source_reference=source_reference,
        )
        return self.render_visual(spec)

    def step_visual(self, asset_id: str, target_step: int) -> Optional[VisualAsset]:
        """Scrubs or advances the visual asset to a specific step index."""
        asset = self.get_asset(asset_id)
        if not asset:
            return None

        # If asset has pre-compiled step_contents
        if asset.step_contents and target_step in asset.step_contents:
            asset.active_step = target_step
            asset.content = asset.step_contents[target_step]
            return asset

        # If plan is stored in _plans_store
        plan = self._plans_store.get(asset.spec_id)
        if plan:
            updated = self.whiteboard_engine.render_plan_to_asset(plan, step_index=target_step)
            updated.asset_id = asset.asset_id
            self._assets_store[asset.asset_id] = updated
            return updated

        return asset

    def replay_visual(self, asset_id: str) -> Optional[VisualAsset]:
        """Rewinds the visual presentation to step 0."""
        return self.step_visual(asset_id, target_step=0)

    def get_source_trace(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Returns the complete source grounding citation for an asset."""
        asset = self.get_asset(asset_id)
        if not asset:
            return None

        plan = self._plans_store.get(asset.spec_id)
        return {
            "asset_id": asset.asset_id,
            "visual_type": asset.visual_type.value,
            "concept_id": asset.metadata.get("concept", "unknown"),
            "subject": asset.metadata.get("subject", "general"),
            "is_grounded_in_source": asset.metadata.get("is_grounded", bool(asset.document_id)),
            "requires_external_knowledge": asset.metadata.get("requires_external", not bool(asset.document_id)),
            "document_id": asset.document_id,
            "chunk_id": asset.chunk_id,
            "source_reference": asset.source_reference or (plan.source_reference if plan else {}),
            "step_count": asset.steps_count,
            "active_step": asset.active_step,
            "cues_count": len(asset.narration_cues),
        }

    def get_asset(self, asset_id: str) -> Optional[VisualAsset]:
        return self._assets_store.get(asset_id)

    def get_plan(self, visual_id: str) -> Optional[TeachingVisualPlan]:
        return self._plans_store.get(visual_id)


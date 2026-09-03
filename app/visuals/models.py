"""
Data Models for Module 8 (Subject-Aware Visual Intelligence).
"""

from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class SubjectCategory(str, Enum):
    PHYSICS = "physics"
    MATHEMATICS = "mathematics"
    PROGRAMMING = "programming"
    BIOLOGY = "biology"
    CHEMISTRY = "chemistry"
    HISTORY = "history"
    GENERAL = "general"


class VisualType(str, Enum):
    CIRCUIT_DIAGRAM = "circuit_diagram"
    ANALOGY_WATER_CIRCUIT = "analogy_water_circuit"
    GRAPH_PLOT = "graph_plot"
    LATEX_EQUATION = "latex_equation"
    MERMAID_FLOWCHART = "mermaid_flowchart"
    CODE_BLOCK = "code_block"
    LABELED_DIAGRAM = "labeled_diagram"
    TIMELINE = "timeline"


class RenderFormat(str, Enum):
    SVG = "svg"
    PNG = "png"
    HTML = "html"
    MERMAID = "mermaid"
    LATEX = "latex"


class VisualSpec(BaseModel):
    """
    Structured, runtime-neutral specification for an educational visual asset.
    The AI/planner produces the specification, and deterministic renderers produce the asset.
    """
    spec_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    visual_type: VisualType = VisualType.CIRCUIT_DIAGRAM
    subject: SubjectCategory = SubjectCategory.PHYSICS
    concept: str
    purpose: str
    title: str = ""
    elements: List[Dict[str, Any]] = Field(default_factory=list)
    labels: List[str] = Field(default_factory=list)
    equations: List[str] = Field(default_factory=list)
    steps: List[str] = Field(default_factory=list)
    renderer: str = "svg"
    preferred_format: RenderFormat = RenderFormat.SVG
    parameters: Dict[str, Any] = Field(default_factory=dict)
    duration_seconds: int = 15
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class VisualAsset(BaseModel):
    """Rendered visual artifact ready for UI rendering and video timeline composition."""
    asset_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    spec_id: str
    visual_type: VisualType
    format: RenderFormat
    content: str  # SVG XML, HTML snippet, Mermaid definition, or Base64/data URI
    mime_type: str = "image/svg+xml"
    width: int = 800
    height: int = 450
    alt_text: str = ""
    is_fallback: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

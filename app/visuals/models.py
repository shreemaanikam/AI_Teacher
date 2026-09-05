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
    COMPUTER_SCIENCE = "computer_science"
    ENGINEERING = "engineering"
    BIOLOGY = "biology"
    CHEMISTRY = "chemistry"
    HISTORY = "history"
    GENERAL = "general"


class VisualType(str, Enum):
    # Core types
    WHITEBOARD = "whiteboard"
    CHALKBOARD = "chalkboard"
    STEP_BY_STEP_DIAGRAM = "step_by_step_diagram"
    CIRCUIT_DIAGRAM = "circuit_diagram"
    ANALOGY_WATER_CIRCUIT = "analogy_water_circuit"
    GRAPH_PLOT = "graph_plot"
    LATEX_EQUATION = "latex_equation"
    EQUATION_DERIVATION = "equation_derivation"
    CODE_BLOCK = "code_block"
    CODE_EXECUTION = "code_execution"
    ARRAY_POINTER = "array_pointer"
    TREE_GRAPH = "tree_graph"
    SIGNAL_WAVEFORM = "signal_waveform"
    NETWORK_FLOW = "network_flow"
    PROCESS_FLOWCHART = "process_flowchart"
    MERMAID_FLOWCHART = "mermaid_flowchart"
    LABELED_DIAGRAM = "labeled_diagram"
    TIMELINE = "timeline"


class VisualBoardTheme(str, Enum):
    CHALKBOARD = "chalkboard"       # Deep emerald / slate chalkboard with chalk aesthetics
    WHITEBOARD = "whiteboard"       # Modern crisp high-contrast digital whiteboard
    DARK_TECHNICAL = "dark_technical" # Sleek cyber / IDE dark canvas


class RenderFormat(str, Enum):
    SVG = "svg"
    PNG = "png"
    HTML = "html"
    MERMAID = "mermaid"
    LATEX = "latex"


class NarrationCue(BaseModel):
    """Synchronized spoken narration boundary mapped to teacher speech."""
    cue_id: str = Field(default_factory=lambda: f"nc_{uuid.uuid4().hex[:8]}")
    start_time: float
    end_time: float
    text: str
    concept_id: str = ""


class VisualCue(BaseModel):
    """Visual board transition or emphasis trigger synchronized with narration."""
    cue_id: str = Field(default_factory=lambda: f"vc_{uuid.uuid4().hex[:8]}")
    start_time: float
    end_time: float
    action: str  # HIGHLIGHT, DRAW_STEP, SHOW_ARROW, UPDATE_VAR, FADE_IN
    target: str   # identifier of component / equation term / code line
    parameters: Dict[str, Any] = Field(default_factory=dict)


class VisualTeachingStep(BaseModel):
    """A single progressive pedagogical reveal on the teaching board."""
    step_index: int
    title: str
    explanation: str
    action: str = "DRAW"
    content: str = ""
    highlight_target: Optional[str] = None
    duration_seconds: float = 3.0
    narration_cue_id: Optional[str] = None
    why_appears: str = ""


class TeachingVisualPlan(BaseModel):
    """
    General, subject-agnostic visual teaching plan grounded in student study material.
    Defines progressive whiteboard sequence, synchronized narration cues, and source attribution.
    """
    visual_id: str = Field(default_factory=lambda: f"vis_{uuid.uuid4().hex[:10]}")
    lesson_id: str = Field(default_factory=lambda: f"l_{uuid.uuid4().hex[:8]}")
    segment_id: Optional[str] = None
    document_id: Optional[str] = None
    concept_id: str = "core_concept"
    source_chunk_ids: List[str] = Field(default_factory=list)
    source_reference: Optional[Dict[str, Any]] = None  # doc_title, page, section, snippet
    subject: SubjectCategory = SubjectCategory.GENERAL
    visual_type: VisualType = VisualType.WHITEBOARD
    theme: VisualBoardTheme = VisualBoardTheme.CHALKBOARD
    teaching_purpose: str = "Visually explain target concept step-by-step"
    steps: List[VisualTeachingStep] = Field(default_factory=list)
    narration_cues: List[NarrationCue] = Field(default_factory=list)
    animation_cues: List[VisualCue] = Field(default_factory=list)
    labels: List[str] = Field(default_factory=list)
    equations: List[str] = Field(default_factory=list)
    code_blocks: List[str] = Field(default_factory=list)
    diagrams: List[Dict[str, Any]] = Field(default_factory=list)
    duration_seconds: float = 15.0
    language: str = "en"
    accessibility_description: str = ""
    is_grounded_in_source: bool = True
    requires_external_knowledge: bool = False
    aspect_ratio: str = "16:9"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class VisualSpec(BaseModel):
    """
    Structured, runtime-neutral specification for an educational visual asset.
    Preserves backwards compatibility with existing Module 8 callers while integrating
    with TeachingVisualPlan.
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
    theme: VisualBoardTheme = VisualBoardTheme.CHALKBOARD
    document_id: Optional[str] = None
    chunk_id: Optional[str] = None
    source_reference: Optional[Dict[str, Any]] = None
    visual_plan: Optional[TeachingVisualPlan] = None
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
    theme: VisualBoardTheme = VisualBoardTheme.CHALKBOARD
    steps_count: int = 1
    active_step: int = 0
    step_contents: Dict[int, str] = Field(default_factory=dict)
    document_id: Optional[str] = None
    chunk_id: Optional[str] = None
    source_reference: Optional[Dict[str, Any]] = None
    aspect_ratio: str = "16:9"
    narration_cues: List[NarrationCue] = Field(default_factory=list)
    visual_cues: List[VisualCue] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

"""
Deterministic Mermaid Diagram Renderer for Module 8 (Visual Intelligence).
"""

from __future__ import annotations
from app.visuals.models import VisualSpec, VisualAsset, VisualType, RenderFormat
from app.visuals.renderers.base import BaseVisualRenderer


class MermaidRenderer(BaseVisualRenderer):
    """Produces Mermaid flowchart and sequence definitions."""

    def render(self, spec: VisualSpec) -> VisualAsset:
        if "process" in spec.concept.lower() or "flow" in spec.concept.lower():
            mermaid_code = f"""graph TD
    A[{spec.title or spec.concept}] --> B[Input / Stimulus]
    B --> C{{Evaluation / Processing}}
    C -->|Condition True| D[State Adaptation]
    C -->|Condition False| E[Baseline Output]
    D --> F[Final Outcome]
    E --> F"""
        else:
            mermaid_code = f"""graph LR
    subgraph Core Concepts
    V[Voltage: Potential Push]
    R[Resistance: Flow Opposition]
    end
    subgraph Observable Effect
    I[Current: Flow of Charge]
    end
    V -->|Directly Proportional| I
    R -->|Inversely Proportional| I"""

        return VisualAsset(
            spec_id=spec.spec_id,
            visual_type=VisualType.MERMAID_FLOWCHART,
            format=RenderFormat.MERMAID,
            content=mermaid_code,
            mime_type="text/vnd.mermaid",
            width=800,
            height=450,
            alt_text=f"Mermaid conceptual flowchart for {spec.concept}",
        )

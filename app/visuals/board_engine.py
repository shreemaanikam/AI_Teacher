"""
Dynamic Visual Teaching Engine for Module 8 (Chalkboard & Whiteboard Generator).
Renders progressive, step-by-step educational visuals for Math, Computer Science,
Engineering, Physics, and Networks, strictly grounded in uploaded study materials.
"""

from __future__ import annotations
import html
import math
from typing import Any, Dict, List, Optional

from app.visuals.models import (
    VisualType,
    VisualBoardTheme,
    SubjectCategory,
    RenderFormat,
    TeachingVisualPlan,
    VisualTeachingStep,
    VisualAsset,
    NarrationCue,
    VisualCue,
)


class DynamicWhiteboardEngine:
    """
    Renders progressive, multi-step digital blackboard and whiteboard teaching visuals.
    Supports responsive SVG viewports (16:9, 4:3, 9:16) and active step highlighting.
    """

    THEME_STYLES = {
        VisualBoardTheme.CHALKBOARD: {
            "bg": "linear-gradient(135deg, #091e14 0%, #0d281a 100%)",
            "bg_color": "#0a1f15",
            "frame": "#1b4332",
            "grid": "rgba(45, 106, 79, 0.25)",
            "text_primary": "#f8fafc",
            "text_secondary": "#a7f3d0",
            "chalk_white": "#f1f5f9",
            "chalk_yellow": "#fef08a",
            "chalk_cyan": "#67e8f9",
            "chalk_green": "#86efac",
            "chalk_coral": "#fda4af",
            "highlight_glow": "rgba(103, 232, 249, 0.4)",
            "banner_bg": "rgba(6, 78, 59, 0.7)",
            "source_bg": "rgba(20, 83, 45, 0.9)",
            "font": "'Chalkboard', 'Comic Neue', 'Caveat', system-ui, sans-serif",
        },
        VisualBoardTheme.WHITEBOARD: {
            "bg": "linear-gradient(135deg, #0b1120 0%, #0f172a 100%)",
            "bg_color": "#0b1120",
            "frame": "#1e293b",
            "grid": "rgba(51, 65, 85, 0.3)",
            "text_primary": "#ffffff",
            "text_secondary": "#94a3b8",
            "chalk_white": "#ffffff",
            "chalk_yellow": "#fbbf24",
            "chalk_cyan": "#38bdf8",
            "chalk_green": "#34d399",
            "chalk_coral": "#f87171",
            "highlight_glow": "rgba(56, 189, 248, 0.4)",
            "banner_bg": "rgba(30, 41, 59, 0.8)",
            "source_bg": "rgba(15, 23, 42, 0.95)",
            "font": "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif",
        },
        VisualBoardTheme.DARK_TECHNICAL: {
            "bg": "linear-gradient(135deg, #050811 0%, #0b0f19 100%)",
            "bg_color": "#050811",
            "frame": "#1e293b",
            "grid": "rgba(30, 41, 59, 0.35)",
            "text_primary": "#f8fafc",
            "text_secondary": "#64748b",
            "chalk_white": "#f8fafc",
            "chalk_yellow": "#eab308",
            "chalk_cyan": "#06b6d4",
            "chalk_green": "#10b981",
            "chalk_coral": "#f43f5e",
            "highlight_glow": "rgba(6, 182, 212, 0.4)",
            "banner_bg": "rgba(15, 23, 42, 0.85)",
            "source_bg": "rgba(2, 6, 23, 0.95)",
            "font": "'Fira Code', 'JetBrains Mono', monospace, system-ui",
        },
    }

    def __init__(self):
        pass

    def render_plan_to_asset(
        self,
        plan: TeachingVisualPlan,
        step_index: Optional[int] = None,
        aspect_ratio: str = "16:9",
    ) -> VisualAsset:
        """
        Renders a TeachingVisualPlan into a standalone interactive VisualAsset,
        pre-compiling SVG state for every step index so students can scrub/replay smoothly.
        """
        steps = plan.steps or [
            VisualTeachingStep(
                step_index=0,
                title=f"Introduction to {plan.concept_id}",
                explanation="Overview of the foundational concept and principles.",
            )
        ]

        total_steps = len(steps)
        current_step = step_index if (step_index is not None and 0 <= step_index < total_steps) else 0

        # Generate SVG contents for all steps
        step_contents: Dict[int, str] = {}
        for s_idx in range(total_steps):
            step_contents[s_idx] = self._render_board_svg(plan, s_idx, total_steps, aspect_ratio)

        active_svg = step_contents[current_step]

        # Alt text description for accessibility
        cur_step_obj = steps[current_step]
        alt_text = f"Digital Teaching Board: {plan.teaching_purpose}. Step {current_step + 1} of {total_steps}: {cur_step_obj.title} - {cur_step_obj.explanation}"

        source_doc = plan.source_reference or {}
        chunk_id = plan.source_chunk_ids[0] if plan.source_chunk_ids else None

        return VisualAsset(
            spec_id=plan.visual_id,
            visual_type=plan.visual_type,
            format=RenderFormat.SVG,
            content=active_svg,
            mime_type="image/svg+xml",
            width=960,
            height=540,
            alt_text=alt_text,
            theme=plan.theme,
            steps_count=total_steps,
            active_step=current_step,
            step_contents=step_contents,
            document_id=plan.document_id,
            chunk_id=chunk_id,
            source_reference=source_doc,
            aspect_ratio=aspect_ratio,
            narration_cues=plan.narration_cues,
            visual_cues=plan.animation_cues,
            metadata={
                "concept": plan.concept_id,
                "subject": plan.subject.value,
                "is_grounded": plan.is_grounded_in_source,
                "requires_external": plan.requires_external_knowledge,
            },
        )

    def _render_board_svg(
        self,
        plan: TeachingVisualPlan,
        active_step_idx: int,
        total_steps: int,
        aspect_ratio: str = "16:9",
    ) -> str:
        """Assembles the complete responsive SVG board markup for a specific step."""
        theme = self.THEME_STYLES.get(plan.theme, self.THEME_STYLES[VisualBoardTheme.CHALKBOARD])
        
        # Dimensions based on aspect ratio
        w, h = 960, 540
        if aspect_ratio == "4:3":
            w, h = 800, 600
        elif aspect_ratio == "9:16":
            w, h = 540, 960

        current_step = plan.steps[active_step_idx] if active_step_idx < len(plan.steps) else plan.steps[-1]

        # 1. Background, Frame, and Grid
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%" style="border-radius: 14px; font-family: {theme["font"]}; user-select: none;">',
            f'  <defs>',
            f'    <linearGradient id="boardBg" x1="0%" y1="0%" x2="100%" y2="100%">',
            f'      <stop offset="0%" stop-color="{theme["bg_color"]}" />',
            f'      <stop offset="100%" stop-color="#020b06" />',
            f'    </linearGradient>',
            f'    <pattern id="chalkGrid" width="40" height="40" patternUnits="userSpaceOnUse">',
            f'      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="{theme["grid"]}" stroke-width="0.75" />',
            f'    </pattern>',
            f'    <filter id="chalkGlow" x="-20%" y="-20%" width="140%" height="140%">',
            f'      <feGaussianBlur stdDeviation="2.5" result="blur" />',
            f'      <feComposite in="SourceGraphic" in2="blur" operator="over" />',
            f'    </filter>',
            f'    <marker id="chalkArrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
            f'      <path d="M 0 1 L 10 5 L 0 9 z" fill="{theme["chalk_cyan"]}" />',
            f'    </marker>',
            f'    <marker id="accentArrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
            f'      <path d="M 0 1 L 10 5 L 0 9 z" fill="{theme["chalk_yellow"]}" />',
            f'    </marker>',
            f'  </defs>',
            f'  <!-- Blackboard Canvas -->',
            f'  <rect width="{w}" height="{h}" rx="12" fill="url(#boardBg)" stroke="{theme["frame"]}" stroke-width="4" />',
            f'  <rect width="{w}" height="{h}" rx="12" fill="url(#chalkGrid)" />',
        ]

        # 2. Header: Title, Subject Icon, Step Progress Pill, Grounding Citation
        source_ref = plan.source_reference or {}
        doc_title = source_ref.get("title") or "Uploaded Study Notes"
        page_no = source_ref.get("page")
        page_str = f", Page {page_no}" if page_no else ""
        grounding_badge = f"📖 {html.escape(doc_title)}{page_str}" if plan.is_grounded_in_source else "🌐 Supplementary Knowledge"

        svg_parts.extend([
            f'  <!-- Header Banner -->',
            f'  <g transform="translate(24, 20)">',
            f'    <rect width="{w - 48}" height="46" rx="8" fill="{theme["banner_bg"]}" stroke="{theme["frame"]}" stroke-width="1.5" />',
            f'    <!-- Subject & Title -->',
            f'    <text x="16" y="29" fill="{theme["chalk_white"]}" font-size="16" font-weight="700">',
            f'      ⚡ {html.escape(plan.concept_id.replace("_", " ").title())}',
            f'    </text>',
            f'    <!-- Grounding Citation Badge -->',
            f'    <g transform="translate({w - 380}, 10)">',
            f'      <rect width="210" height="26" rx="6" fill="{theme["source_bg"]}" stroke="{theme["chalk_green"]}" stroke-width="1" />',
            f'      <text x="105" y="17" fill="{theme["chalk_green"]}" font-size="11" font-weight="600" text-anchor="middle">',
            f'        {html.escape(grounding_badge[:28])}',
            f'      </text>',
            f'    </g>',
            f'    <!-- Step Counter Badge -->',
            f'    <g transform="translate({w - 150}, 10)">',
            f'      <rect width="115" height="26" rx="6" fill="{theme["source_bg"]}" stroke="{theme["chalk_cyan"]}" stroke-width="1" />',
            f'      <text x="57" y="17" fill="{theme["chalk_cyan"]}" font-size="11" font-weight="700" text-anchor="middle">',
            f'        Step {active_step_idx + 1} of {total_steps}',
            f'      </text>',
            f'    </g>',
            f'  </g>',
        ])

        # 3. Main Board Body: Render subject-specific discipline visual
        board_body = self._render_discipline_body(plan, active_step_idx, total_steps, theme, w, h)
        svg_parts.append(board_body)

        # 4. Step Indicator Tracker Bar at Bottom
        svg_parts.extend(self._render_step_timeline_bar(plan, active_step_idx, total_steps, theme, w, h))

        # 5. Teacher Active Insight Banner (Synchronized Step Explanation)
        exp_text = html.escape(current_step.explanation)
        title_text = html.escape(current_step.title)
        svg_parts.extend([
            f'  <!-- Teacher Active Insight Banner -->',
            f'  <g transform="translate(24, {h - 88})">',
            f'    <rect width="{w - 48}" height="42" rx="8" fill="{theme["banner_bg"]}" stroke="{theme["chalk_yellow"]}" stroke-width="1.5" />',
            f'    <text x="16" y="19" fill="{theme["chalk_yellow"]}" font-size="12" font-weight="700">',
            f'      POINT {active_step_idx + 1}: {title_text}',
            f'    </text>',
            f'    <text x="16" y="34" fill="{theme["text_primary"]}" font-size="11" font-weight="500">',
            f'      {exp_text[:110]}{"..." if len(exp_text) > 110 else ""}',
            f'    </text>',
            f'  </g>',
            f'</svg>',
        ])

        return "\n".join(svg_parts)

    def _render_step_timeline_bar(
        self,
        plan: TeachingVisualPlan,
        active_step_idx: int,
        total_steps: int,
        theme: Dict[str, Any],
        w: int,
        h: int,
    ) -> List[str]:
        """Renders the step progress bubbles along the lower edge of the board."""
        parts = [f'  <!-- Step Timeline Dots -->', f'  <g transform="translate(24, {h - 36})">']
        if total_steps <= 1:
            parts.append(f'  </g>')
            return parts

        available_w = w - 48
        spacing = available_w / max(1, total_steps - 1)

        # Connecting line
        parts.append(
            f'    <line x1="12" y1="12" x2="{available_w - 12}" y2="12" stroke="{theme["frame"]}" stroke-width="3" stroke-linecap="round" />'
        )
        if active_step_idx > 0:
            filled_w = min(available_w - 12, 12 + active_step_idx * spacing)
            parts.append(
                f'    <line x1="12" y1="12" x2="{filled_w}" y2="12" stroke="{theme["chalk_cyan"]}" stroke-width="3" stroke-linecap="round" />'
            )

        for i in range(total_steps):
            cx = 12 + i * spacing
            is_active = (i == active_step_idx)
            is_done = (i < active_step_idx)
            circle_color = theme["chalk_cyan"] if is_active else (theme["chalk_green"] if is_done else theme["frame"])
            fill_color = theme["source_bg"] if not is_active else theme["chalk_cyan"]
            text_color = "#000000" if is_active else theme["text_primary"]

            parts.append(
                f'    <circle cx="{cx}" cy="12" r="{10 if is_active else 8}" fill="{fill_color}" stroke="{circle_color}" stroke-width="2" />'
            )
            parts.append(
                f'    <text x="{cx}" y="15" fill="{text_color}" font-size="9" font-weight="700" text-anchor="middle">{i + 1}</text>'
            )

        parts.append(f'  </g>')
        return parts

    def _render_discipline_body(
        self,
        plan: TeachingVisualPlan,
        active_step_idx: int,
        total_steps: int,
        theme: Dict[str, Any],
        w: int,
        h: int,
    ) -> str:
        """Dispatches to discipline-specific chalk/whiteboard renderer based on subject or visual_type."""
        vtype = plan.visual_type
        subj = plan.subject

        if vtype == VisualType.ANALOGY_WATER_CIRCUIT:
            return self._render_remediation_analogy(plan, active_step_idx, theme, w, h)
        elif vtype == VisualType.EQUATION_DERIVATION or subj == SubjectCategory.MATHEMATICS:
            return self._render_math_derivation(plan, active_step_idx, theme, w, h)
        elif vtype in (VisualType.ARRAY_POINTER, VisualType.CODE_EXECUTION, VisualType.TREE_GRAPH) or subj in (
            SubjectCategory.PROGRAMMING,
            SubjectCategory.COMPUTER_SCIENCE,
        ):
            return self._render_cs_algorithm(plan, active_step_idx, theme, w, h)
        elif vtype == VisualType.NETWORK_FLOW:
            return self._render_network_flow(plan, active_step_idx, theme, w, h)
        elif vtype in (VisualType.CIRCUIT_DIAGRAM, VisualType.SIGNAL_WAVEFORM) or subj in (
            SubjectCategory.PHYSICS,
            SubjectCategory.ENGINEERING,
        ):
            return self._render_engineering_circuit(plan, active_step_idx, theme, w, h)
        else:
            return self._render_general_whiteboard(plan, active_step_idx, theme, w, h)

    # -------------------------------------------------------------
    # 1. Mathematics Derivation Renderer
    # -------------------------------------------------------------
    def _render_math_derivation(
        self,
        plan: TeachingVisualPlan,
        step_idx: int,
        theme: Dict[str, Any],
        w: int,
        h: int,
    ) -> str:
        """Renders step-by-step mathematical deductions with active term highlighting."""
        equations = plan.equations or [
            "f(x) = ax^2 + bx + c = 0",
            "x^2 + \\frac{b}{a}x + \\frac{c}{a} = 0",
            "\\left(x + \\frac{b}{2a}\\right)^2 = \\frac{b^2 - 4ac}{4a^2}",
            "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}",
        ]

        svg = ['  <!-- Mathematics Derivation Board -->', '  <g transform="translate(48, 80)">']
        
        # Left Panel: Progressive Equations Box
        svg.append(f'    <rect width="{w - 96}" height="{h - 185}" rx="10" fill="rgba(15, 23, 42, 0.45)" stroke="{theme["frame"]}" stroke-width="1.5" />')

        # Header for the derivation
        svg.append(
            f'    <text x="24" y="32" fill="{theme["chalk_yellow"]}" font-size="14" font-weight="700">MATHEMATICAL DERIVATION &amp; VARIABLE ANALYSIS</text>'
        )

        visible_eqs = equations[: step_idx + 1] if step_idx < len(equations) else equations
        y_cursor = 70

        for i, eq in enumerate(visible_eqs):
            is_active = (i == step_idx)
            stroke_color = theme["chalk_cyan"] if is_active else "transparent"
            bg_color = "rgba(56, 189, 248, 0.12)" if is_active else "transparent"
            text_color = theme["chalk_cyan"] if is_active else theme["chalk_white"]

            # Row container
            svg.append(f'    <g transform="translate(24, {y_cursor - 22})">')
            svg.append(f'      <rect width="{w - 144}" height="42" rx="6" fill="{bg_color}" stroke="{stroke_color}" stroke-width="{1.5 if is_active else 0}" />')
            
            # Step badge
            svg.append(f'      <circle cx="20" cy="21" r="11" fill="{theme["source_bg"]}" stroke="{text_color}" stroke-width="1.5" />')
            svg.append(f'      <text x="20" y="25" fill="{text_color}" font-size="11" font-weight="700" text-anchor="middle">{i + 1}</text>')

            # Equation content (escaped math text)
            clean_eq = html.escape(eq.replace("\\left", "").replace("\\right", "").replace("\\frac", "").replace("\\pm", "±"))
            svg.append(f'      <text x="44" y="27" fill="{text_color}" font-size="16" font-weight="700" font-family="monospace">')
            svg.append(f'        {clean_eq}')
            svg.append(f'      </text>')

            if is_active:
                # Active emphasis label
                svg.append(f'      <g transform="translate({w - 300}, 9)">')
                svg.append(f'        <rect width="130" height="24" rx="4" fill="{theme["banner_bg"]}" stroke="{theme["chalk_yellow"]}" stroke-width="1" />')
                svg.append(f'        <text x="65" y="16" fill="{theme["chalk_yellow"]}" font-size="10" font-weight="700" text-anchor="middle">ACTIVE STEP</text>')
                svg.append(f'      </g>')

            svg.append(f'    </g>')
            y_cursor += 50

        # Derivation summary / commentary at bottom of math card
        step_note = plan.steps[step_idx].why_appears if (step_idx < len(plan.steps) and plan.steps[step_idx].why_appears) else "Applying algebraic axioms grounded in course syllabus."
        svg.append(f'    <g transform="translate(24, {h - 235})">')
        svg.append(f'      <rect width="{w - 144}" height="32" rx="6" fill="rgba(6, 78, 59, 0.4)" stroke="{theme["chalk_green"]}" stroke-width="1" stroke-dasharray="4,4" />')
        svg.append(f'      <text x="14" y="20" fill="{theme["chalk_green"]}" font-size="11" font-weight="600">💡 Rule Applied: {html.escape(step_note[:90])}</text>')
        svg.append(f'    </g>')

        svg.append('  </g>')
        return "\n".join(svg)

    # -------------------------------------------------------------
    # 2. Computer Science & Algorithm Renderer
    # -------------------------------------------------------------
    def _render_cs_algorithm(
        self,
        plan: TeachingVisualPlan,
        step_idx: int,
        theme: Dict[str, Any],
        w: int,
        h: int,
    ) -> str:
        """Renders algorithm execution state, arrays with low/mid/high pointers, or code trace."""
        svg = ['  <!-- Computer Science & Algorithm Board -->', '  <g transform="translate(48, 80)">']
        
        # Determine whether to render Array / Pointer search, or Code execution
        if plan.visual_type == VisualType.CODE_EXECUTION:
            return self._render_code_execution_trace(plan, step_idx, theme, w, h)

        # Default CS: Array and Pointer Search (Binary Search / Pointer Trace)
        array_vals = [2, 5, 8, 12, 17, 25, 31]
        n = len(array_vals)
        box_w = 70
        box_h = 60
        start_x = (w - 96 - (n * box_w + (n - 1) * 12)) // 2
        y_array = 100

        # Step-dependent pointers for Binary Search (Target: 17)
        # Step 0: Initial array, Target: 17
        # Step 1: L=0, H=6, Mid=3 (val=12)
        # Step 2: 17 > 12 -> discard [0..3]
        # Step 3: L=4, H=6, Mid=5 (val=25)
        # Step 4: 17 < 25 -> discard [5..6], L=4, H=4, Mid=4 (val=17) MATCH!
        low_idx = 0
        high_idx = n - 1
        mid_idx = 3
        discarded_indices = set()
        matched_idx = None

        if step_idx == 0:
            low_idx, high_idx, mid_idx = 0, n - 1, None
        elif step_idx == 1:
            low_idx, high_idx, mid_idx = 0, n - 1, 3
        elif step_idx == 2:
            discarded_indices = {0, 1, 2, 3}
            low_idx, high_idx, mid_idx = 4, 6, 5
        elif step_idx >= 3:
            discarded_indices = {0, 1, 2, 3, 5, 6}
            low_idx, high_idx, mid_idx = 4, 4, 4
            matched_idx = 4

        # Board container
        svg.append(f'    <rect width="{w - 96}" height="{h - 185}" rx="10" fill="rgba(15, 23, 42, 0.45)" stroke="{theme["frame"]}" stroke-width="1.5" />')

        # Title of trace
        svg.append(
            f'    <text x="24" y="32" fill="{theme["chalk_cyan"]}" font-size="14" font-weight="700">ARRAY POINTER TRACE &amp; EXECUTION STATE</text>'
        )
        target_val = 17
        svg.append(
            f'    <text x="{w - 240}" y="32" fill="{theme["chalk_yellow"]}" font-size="13" font-weight="700">Target Value: {target_val}</text>'
        )

        # Draw array elements
        for i, val in enumerate(array_vals):
            bx = start_x + i * (box_w + 12)
            by = y_array

            is_discarded = i in discarded_indices
            is_mid = (i == mid_idx)
            is_match = (i == matched_idx)

            cell_bg = "rgba(30, 41, 59, 0.7)"
            border_color = theme["frame"]
            text_color = theme["chalk_white"]

            if is_match:
                cell_bg = "rgba(52, 211, 153, 0.3)"
                border_color = theme["chalk_green"]
                text_color = theme["chalk_green"]
            elif is_mid:
                cell_bg = "rgba(56, 189, 248, 0.25)"
                border_color = theme["chalk_cyan"]
                text_color = theme["chalk_cyan"]
            elif is_discarded:
                cell_bg = "rgba(15, 23, 42, 0.3)"
                border_color = "rgba(51, 65, 85, 0.4)"
                text_color = "rgba(148, 163, 184, 0.35)"

            # Index label above
            svg.append(f'    <text x="{bx + box_w // 2}" y="{by - 10}" fill="{theme["text_secondary"]}" font-size="11" font-weight="600" text-anchor="middle">[{i}]</text>')

            # Cell box
            svg.append(f'    <rect x="{bx}" y="{by}" width="{box_w}" height="{box_h}" rx="8" fill="{cell_bg}" stroke="{border_color}" stroke-width="{2.5 if (is_mid or is_match) else 1.5}" />')
            svg.append(f'    <text x="{bx + box_w // 2}" y="{by + box_h // 2 + 6}" fill="{text_color}" font-size="20" font-weight="700" text-anchor="middle">{val}</text>')

            if is_discarded:
                # Strike-through mark
                svg.append(f'    <line x1="{bx + 6}" y1="{by + 6}" x2="{bx + box_w - 6}" y2="{by + box_h - 6}" stroke="rgba(239, 68, 68, 0.6)" stroke-width="2" />')

        # Pointer badges below array
        if low_idx is not None and low_idx < n:
            lx = start_x + low_idx * (box_w + 12) + box_w // 2
            svg.append(f'    <line x1="{lx}" y1="{y_array + box_h + 30}" x2="{lx}" y2="{y_array + box_h + 8}" stroke="{theme["chalk_yellow"]}" stroke-width="2" marker-end="url(#accentArrow)" />')
            svg.append(f'    <text x="{lx}" y="{y_array + box_h + 46}" fill="{theme["chalk_yellow"]}" font-size="12" font-weight="700" text-anchor="middle">LOW ({low_idx})</text>')

        if high_idx is not None and high_idx < n and high_idx != low_idx:
            hx = start_x + high_idx * (box_w + 12) + box_w // 2
            svg.append(f'    <line x1="{hx}" y1="{y_array + box_h + 30}" x2="{hx}" y2="{y_array + box_h + 8}" stroke="{theme["chalk_coral"]}" stroke-width="2" marker-end="url(#accentArrow)" />')
            svg.append(f'    <text x="{hx}" y="{y_array + box_h + 46}" fill="{theme["chalk_coral"]}" font-size="12" font-weight="700" text-anchor="middle">HIGH ({high_idx})</text>')

        if mid_idx is not None and mid_idx < n:
            mx = start_x + mid_idx * (box_w + 12) + box_w // 2
            svg.append(f'    <g transform="translate({mx - 32}, {y_array + box_h + 60})">')
            svg.append(f'      <rect width="64" height="22" rx="4" fill="{theme["source_bg"]}" stroke="{theme["chalk_cyan"]}" stroke-width="1.5" />')
            svg.append(f'      <text x="32" y="15" fill="{theme["chalk_cyan"]}" font-size="10" font-weight="700" text-anchor="middle">MID: {mid_idx}</text>')
            svg.append(f'    </g>')

        # Trace condition explanation card at bottom
        status_msg = "Pointers initialized to bounds [0..6]."
        if step_idx == 1:
            status_msg = "Checking mid element: arr[3] = 12. Since 17 > 12, target must be in right subarray."
        elif step_idx == 2:
            status_msg = "Discarding left half [0..3]. Moving LOW pointer to mid + 1 = 4."
        elif step_idx >= 3:
            status_msg = "SUCCESS: arr[4] == 17. Search converged in O(log N) iterations!"

        svg.append(f'    <g transform="translate(24, {h - 235})">')
        svg.append(f'      <rect width="{w - 144}" height="32" rx="6" fill="rgba(15, 23, 42, 0.8)" stroke="{theme["chalk_cyan"]}" stroke-width="1" />')
        svg.append(f'      <text x="14" y="20" fill="{theme["chalk_cyan"]}" font-size="11" font-weight="600">⚡ State: {html.escape(status_msg)}</text>')
        svg.append(f'    </g>')

        svg.append('  </g>')
        return "\n".join(svg)

    def _render_code_execution_trace(
        self,
        plan: TeachingVisualPlan,
        step_idx: int,
        theme: Dict[str, Any],
        w: int,
        h: int,
    ) -> str:
        """Renders split code editor and variable watch memory panel."""
        code_lines = plan.code_blocks or [
            "def binary_search(arr, target):",
            "    low, high = 0, len(arr) - 1",
            "    while low <= high:",
            "        mid = (low + high) // 2",
            "        if arr[mid] == target: return mid",
            "        elif arr[mid] < target: low = mid + 1",
            "        else: high = mid - 1",
            "    return -1",
        ]

        active_line = min(step_idx + 1, len(code_lines) - 1)

        svg = [
            f'    <rect width="{w - 96}" height="{h - 185}" rx="10" fill="rgba(15, 23, 42, 0.45)" stroke="{theme["frame"]}" stroke-width="1.5" />',
            f'    <!-- Code Pane (Left) -->',
            f'    <g transform="translate(16, 20)">',
            f'      <rect width="{(w - 96) * 0.58}" height="{h - 225}" rx="8" fill="#020617" stroke="{theme["frame"]}" stroke-width="1" />',
        ]

        # Render code lines with active execution pointer
        for idx, line in enumerate(code_lines):
            is_exec = (idx == active_line)
            ly = 28 + idx * 24
            line_bg = "rgba(56, 189, 248, 0.15)" if is_exec else "transparent"
            txt_color = theme["chalk_yellow"] if is_exec else theme["chalk_white"]

            svg.append(f'      <rect x="0" y="{ly - 18}" width="{(w - 96) * 0.58}" height="22" fill="{line_bg}" />')
            if is_exec:
                svg.append(f'      <polygon points="6,{ly - 12} 14,{ly - 7} 6,{ly - 2}" fill="{theme["chalk_yellow"]}" />')
            svg.append(f'      <text x="24" y="{ly - 4}" fill="{theme["text_secondary"]}" font-size="11" font-family="monospace">{idx + 1}</text>')
            svg.append(f'      <text x="48" y="{ly - 4}" fill="{txt_color}" font-size="12" font-weight="{700 if is_exec else 500}" font-family="monospace">{html.escape(line)}</text>')

        svg.append(f'    </g>')

        # Variables & Memory Watch Panel (Right)
        svg.append(f'    <!-- Variables Panel (Right) -->')
        svg.append(f'    <g transform="translate({(w - 96) * 0.62 + 16}, 20)">')
        svg.append(f'      <rect width="{(w - 96) * 0.35}" height="{h - 225}" rx="8" fill="#020617" stroke="{theme["frame"]}" stroke-width="1" />')
        svg.append(f'      <text x="16" y="28" fill="{theme["chalk_cyan"]}" font-size="13" font-weight="700">VARIABLE INSPECTOR</text>')
        svg.append(f'      <line x1="16" y1="38" x2="{(w - 96) * 0.35 - 16}" y2="38" stroke="{theme["frame"]}" stroke-width="1" />')

        vars_state = [
            ("target", "17"),
            ("low", f"{min(4, step_idx * 2)}"),
            ("high", f"{6 if step_idx < 3 else 4}"),
            ("mid", f"{3 if step_idx == 1 else (5 if step_idx == 2 else 4)}"),
            ("status", "SEARCHING" if step_idx < 3 else "TARGET_FOUND"),
        ]

        for vi, (vname, vval) in enumerate(vars_state):
            vy = 65 + vi * 32
            svg.append(f'      <text x="20" y="{vy}" fill="{theme["text_secondary"]}" font-size="12" font-family="monospace">{vname}:</text>')
            svg.append(f'      <text x="110" y="{vy}" fill="{theme["chalk_green"]}" font-size="13" font-weight="700" font-family="monospace">{vval}</text>')

        svg.append(f'    </g>')
        svg.append('  </g>')
        return "\n".join(svg)

    # -------------------------------------------------------------
    # 3. Engineering & Circuit Diagram Renderer
    # -------------------------------------------------------------
    def _render_engineering_circuit(
        self,
        plan: TeachingVisualPlan,
        step_idx: int,
        theme: Dict[str, Any],
        w: int,
        h: int,
    ) -> str:
        """Renders circuit loop with step-by-step component activations, current arrows, and Ohm's law telemetry."""
        # Parameters
        voltage = 12.0
        # If student has misconception or higher steps, show variation
        resistance = 4.0 if step_idx < 2 else 8.0
        current = round(voltage / resistance, 2)

        svg = [
            '  <!-- Engineering & Physics Circuit Board -->',
            '  <g transform="translate(48, 80)">',
            f'    <rect width="{w - 96}" height="{h - 185}" rx="10" fill="rgba(15, 23, 42, 0.45)" stroke="{theme["frame"]}" stroke-width="1.5" />',
            f'    <text x="24" y="32" fill="{theme["chalk_green"]}" font-size="14" font-weight="700">DC Circuit Diagram &amp; Schematic</text>',
        ]

        # Circuit loop geometry
        cx1, cy1 = 150, 60
        cx2, cy2 = w - 240, 200

        # Wires
        wire_color = theme["chalk_cyan"] if step_idx >= 1 else theme["frame"]
        svg.append(f'    <!-- Wires -->')
        svg.append(f'    <rect x="{cx1}" y="{cy1}" width="{cx2 - cx1}" height="{cy2 - cy1}" rx="8" fill="none" stroke="{wire_color}" stroke-width="3.5" />')

        # Battery (Left side)
        bat_y = cy1 + (cy2 - cy1) // 2
        svg.append(f'    <!-- DC Voltage Source -->')
        svg.append(f'    <g transform="translate({cx1}, {bat_y})">')
        svg.append(f'      <rect x="-18" y="-28" width="36" height="56" fill="{theme["bg_color"]}" />')
        svg.append(f'      <line x1="-16" y1="-10" x2="16" y2="-10" stroke="#ef4444" stroke-width="4" />')
        svg.append(f'      <line x1="-8" y1="10" x2="8" y2="10" stroke="#94a3b8" stroke-width="6" />')
        svg.append(f'      <text x="-35" y="-6" fill="#ef4444" font-size="14" font-weight="700">+</text>')
        svg.append(f'      <text x="-35" y="16" fill="#94a3b8" font-size="14" font-weight="700">-</text>')
        svg.append(f'      <text x="28" y="5" fill="{theme["chalk_white"]}" font-size="12" font-weight="700">{voltage}V</text>')
        svg.append(f'    </g>')

        # Resistor (Top side)
        res_x = cx1 + (cx2 - cx1) // 2
        res_glow = f'filter="url(#chalkGlow)"' if step_idx >= 2 else ''
        res_stroke = theme["chalk_yellow"] if step_idx >= 2 else theme["chalk_white"]
        svg.append(f'    <!-- Resistor -->')
        svg.append(f'    <g transform="translate({res_x}, {cy1})">')
        svg.append(f'      <rect x="-45" y="-18" width="90" height="36" fill="{theme["bg_color"]}" />')
        svg.append(f'      <path d="M -40 0 L -30 -10 L -10 10 L 10 -10 L 30 10 L 40 0" fill="none" stroke="{res_stroke}" stroke-width="3.5" {res_glow} />')
        svg.append(f'      <text x="0" y="-18" fill="{res_stroke}" font-size="13" font-weight="700" text-anchor="middle">R = {resistance} Ω</text>')
        svg.append(f'    </g>')

        # Ammeter (Right side)
        am_y = bat_y
        svg.append(f'    <!-- Ammeter -->')
        svg.append(f'    <g transform="translate({cx2}, {am_y})">')
        svg.append(f'      <circle cx="0" cy="0" r="22" fill="{theme["source_bg"]}" stroke="{theme["chalk_cyan"]}" stroke-width="2.5" />')
        svg.append(f'      <text x="0" y="5" fill="{theme["chalk_cyan"]}" font-size="13" font-weight="800" text-anchor="middle">A</text>')
        svg.append(f'      <text x="32" y="5" fill="{theme["chalk_green"]}" font-size="13" font-weight="700">{current}A</text>')
        svg.append(f'    </g>')

        # Current Flow Arrows (Progressive activation in step 1+)
        if step_idx >= 1:
            svg.append(f'    <!-- Flow Arrows -->')
            arrow_count = 3
            for ai in range(arrow_count):
                ax = cx1 + 60 + ai * 140
                svg.append(f'    <line x1="{ax}" y1="{cy1 - 10}" x2="{ax + 30}" y2="{cy1 - 10}" stroke="{theme["chalk_cyan"]}" stroke-width="2" marker-end="url(#chalkArrow)" />')
            svg.append(f'    <text x="{cx1 + 100}" y="{cy1 - 18}" fill="{theme["chalk_cyan"]}" font-size="11" font-weight="700">Current Flow (I)</text>')

        # Interactive telemetry formula card at bottom
        svg.append(f'    <g transform="translate(24, {h - 235})">')
        svg.append(f'      <rect width="{w - 144}" height="32" rx="6" fill="rgba(15, 23, 42, 0.8)" stroke="{theme["chalk_yellow"]}" stroke-width="1" />')
        formula_math = f"I = V / R  ⟶  {voltage}V / {resistance}Ω = {current} Amperes"
        svg.append(f'      <text x="14" y="20" fill="{theme["chalk_yellow"]}" font-size="12" font-weight="700" font-family="monospace">⚡ Ohm\'s Law Calculation: {formula_math}</text>')
        svg.append(f'    </g>')

        svg.append('  </g>')
        return "\n".join(svg)

    # -------------------------------------------------------------
    # 4. Computer Networks Renderer
    # -------------------------------------------------------------
    def _render_network_flow(
        self,
        plan: TeachingVisualPlan,
        step_idx: int,
        theme: Dict[str, Any],
        w: int,
        h: int,
    ) -> str:
        """Renders protocol exchange (Client <-> DNS <-> Server) with packet flight."""
        nodes = [("Client Browser", 120), ("DNS Resolver", (w - 96) // 2), ("Origin Server", w - 220)]

        svg = [
            '  <!-- Computer Networks Board -->',
            '  <g transform="translate(48, 80)">',
            f'    <rect width="{w - 96}" height="{h - 185}" rx="10" fill="rgba(15, 23, 42, 0.45)" stroke="{theme["frame"]}" stroke-width="1.5" />',
            f'    <text x="24" y="32" fill="{theme["chalk_cyan"]}" font-size="14" font-weight="700">NETWORK PROTOCOL &amp; PACKET FLOW</text>',
        ]

        # Draw 3 Host Nodes
        for name, nx in nodes:
            svg.append(f'    <g transform="translate({nx}, 90)">')
            svg.append(f'      <rect x="-55" y="-30" width="110" height="60" rx="8" fill="{theme["source_bg"]}" stroke="{theme["chalk_cyan"]}" stroke-width="2" />')
            svg.append(f'      <text x="0" y="5" fill="{theme["chalk_white"]}" font-size="12" font-weight="700" text-anchor="middle">{name}</text>')
            svg.append(f'    </g>')

        # Packets in flight according to step_idx
        stages = [
            ("DNS Query (A Record lookup)", 120, (w - 96) // 2, 170, theme["chalk_yellow"]),
            ("TCP 3-Way Handshake [SYN]", 120, w - 220, 190, theme["chalk_cyan"]),
            ("TLS 1.3 Key Exchange", 120, w - 220, 210, theme["chalk_green"]),
            ("HTTP/2 GET Request & 200 OK Response", 120, w - 220, 230, theme["chalk_coral"]),
        ]

        for s_i, (stage_name, x1, x2, py, col) in enumerate(stages[: step_idx + 1]):
            svg.append(f'    <line x1="{x1}" y1="{py}" x2="{x2}" y2="{py}" stroke="{col}" stroke-width="2.5" marker-end="url(#chalkArrow)" />')
            svg.append(f'    <text x="{(x1 + x2) // 2}" y="{py - 6}" fill="{col}" font-size="11" font-weight="600" text-anchor="middle">{stage_name}</text>')

        svg.append('  </g>')
        return "\n".join(svg)

    # -------------------------------------------------------------
    # 5. General Grounded Whiteboard
    # -------------------------------------------------------------
    def _render_general_whiteboard(
        self,
        plan: TeachingVisualPlan,
        step_idx: int,
        theme: Dict[str, Any],
        w: int,
        h: int,
    ) -> str:
        """Universal blackboard for science, humanities, or general topics."""
        steps = plan.steps or []
        visible_steps = steps[: step_idx + 1]

        svg = [
            '  <!-- General Concept Whiteboard -->',
            '  <g transform="translate(48, 80)">',
            f'    <rect width="{w - 96}" height="{h - 185}" rx="10" fill="rgba(15, 23, 42, 0.45)" stroke="{theme["frame"]}" stroke-width="1.5" />',
            f'    <text x="24" y="32" fill="{theme["chalk_yellow"]}" font-size="14" font-weight="700">CONCEPT PRINCIPLES &amp; STEP REASONING</text>',
        ]

        y = 65
        for i, s in enumerate(visible_steps):
            is_active = (i == step_idx)
            box_bg = "rgba(56, 189, 248, 0.12)" if is_active else "rgba(15, 23, 42, 0.6)"
            border = theme["chalk_cyan"] if is_active else theme["frame"]

            svg.append(f'    <g transform="translate(24, {y})">')
            svg.append(f'      <rect width="{w - 144}" height="46" rx="6" fill="{box_bg}" stroke="{border}" stroke-width="{1.5 if is_active else 1}" />')
            svg.append(f'      <circle cx="20" cy="23" r="10" fill="{theme["source_bg"]}" stroke="{border}" stroke-width="1.5" />')
            svg.append(f'      <text x="20" y="27" fill="{theme["text_primary"]}" font-size="10" font-weight="700" text-anchor="middle">{i + 1}</text>')
            svg.append(f'      <text x="44" y="20" fill="{theme["chalk_white"]}" font-size="13" font-weight="700">{html.escape(s.title)}</text>')
            svg.append(f'      <text x="44" y="36" fill="{theme["text_secondary"]}" font-size="11">{html.escape(s.explanation[:95])}</text>')
            svg.append(f'    </g>')
            y += 56

        svg.append('  </g>')
        return "\n".join(svg)

    # -------------------------------------------------------------
    # 6. Remediation Water-Pipe Analogy Board
    # -------------------------------------------------------------
    def _render_remediation_analogy(
        self,
        plan: TeachingVisualPlan,
        step_idx: int,
        theme: Dict[str, Any],
        w: int,
        h: int,
    ) -> str:
        """Renders side-by-side Water Pipe System vs Electrical Circuit for misconception remediation."""
        half_w = (w - 120) // 2
        pipe_constriction = (step_idx >= 2)
        flow_rate = "1.5 L/s (Halved)" if pipe_constriction else "3.0 L/s"
        current_val = "1.5A (Halved)" if pipe_constriction else "3.0A"

        svg = [
            '  <!-- Remediation Analogy Board (Water Pipe vs Electrical Circuit) -->',
            '  <g transform="translate(48, 80)">',
            f'    <rect width="{w - 96}" height="{h - 185}" rx="10" fill="rgba(15, 23, 42, 0.45)" stroke="{theme["frame"]}" stroke-width="1.5" />',
            f'    <text x="24" y="30" fill="{theme["chalk_yellow"]}" font-size="14" font-weight="700">MISCONCEPTION REMEDIATION: WATER PIPE SYSTEM vs. ELECTRICAL CIRCUIT</text>',
            
            # Left Pane: Water Pipe System
            f'    <g transform="translate(20, 46)">',
            f'      <rect width="{half_w}" height="{h - 250}" rx="8" fill="rgba(2, 6, 23, 0.7)" stroke="{theme["chalk_cyan"]}" stroke-width="1.5" />',
            f'      <text x="16" y="24" fill="{theme["chalk_cyan"]}" font-size="13" font-weight="700">💧 Water Pipe System</text>',
            f'      <text x="16" y="42" fill="{theme["text_secondary"]}" font-size="11">Pump = Voltage | Constriction / Pinch = Resistance | Flow = Current</text>',
            
            # Water Pump
            f'      <rect x="24" y="60" width="70" height="40" rx="4" fill="{theme["source_bg"]}" stroke="{theme["chalk_cyan"]}" stroke-width="1.5" />',
            f'      <text x="59" y="85" fill="{theme["chalk_cyan"]}" font-size="11" font-weight="700" text-anchor="middle">Pump (12V)</text>',
            
            # Pipe Loop
            f'      <line x1="94" y1="80" x2="160" y2="80" stroke="{theme["chalk_cyan"]}" stroke-width="8" stroke-linecap="round" />',
        ]

        if pipe_constriction:
            # Constricted / Pinched Pipe
            svg.extend([
                f'      <!-- Pinched Pipe Section -->',
                f'      <path d="M 160 80 Q 185 86 210 80" fill="none" stroke="{theme["chalk_coral"]}" stroke-width="3" />',
                f'      <path d="M 185 58 L 185 74" stroke="{theme["chalk_coral"]}" stroke-width="3" marker-end="url(#accentArrow)" />',
                f'      <text x="185" y="52" fill="{theme["chalk_coral"]}" font-size="10" font-weight="700" text-anchor="middle">Pinch (High R!)</text>',
                f'      <line x1="210" y1="80" x2="{half_w - 30}" y2="80" stroke="{theme["chalk_cyan"]}" stroke-width="8" stroke-linecap="round" />',
            ])
        else:
            # Normal Wide Pipe
            svg.extend([
                f'      <!-- Normal Wide Pipe Section -->',
                f'      <line x1="160" y1="80" x2="{half_w - 30}" y2="80" stroke="{theme["chalk_cyan"]}" stroke-width="8" stroke-linecap="round" />',
                f'      <text x="210" y="66" fill="{theme["chalk_green"]}" font-size="10" font-weight="600">Wide Pipe (Low R)</text>',
            ])

        svg.extend([
            f'      <!-- Flow Telemetry -->',
            f'      <g transform="translate(24, 120)">',
            f'        <rect width="{half_w - 48}" height="28" rx="4" fill="{theme["source_bg"]}" stroke="{theme["frame"]}" stroke-width="1" />',
            f'        <text x="12" y="19" fill="{theme["chalk_white"]}" font-size="11">Water Flow Rate: <tspan fill="{theme["chalk_yellow"]}" font-weight="700">{flow_rate}</tspan></text>',
            f'      </g>',
            f'    </g>',

            # Right Pane: Electrical Circuit
            f'    <g transform="translate({half_w + 40}, 46)">',
            f'      <rect width="{half_w}" height="{h - 250}" rx="8" fill="rgba(2, 6, 23, 0.7)" stroke="{theme["chalk_green"]}" stroke-width="1.5" />',
            f'      <text x="16" y="24" fill="{theme["chalk_green"]}" font-size="13" font-weight="700">⚡ Electrical Circuit</text>',
            f'      <text x="16" y="42" fill="{theme["text_secondary"]}" font-size="11">Battery = 12V | Resistor R | Current I = V / R</text>',
            
            # Circuit schematic elements
            f'      <rect x="24" y="60" width="70" height="40" rx="4" fill="{theme["source_bg"]}" stroke="{theme["chalk_green"]}" stroke-width="1.5" />',
            f'      <text x="59" y="85" fill="{theme["chalk_green"]}" font-size="11" font-weight="700" text-anchor="middle">Battery 12V</text>',
            f'      <line x1="94" y1="80" x2="{half_w - 90}" y2="80" stroke="{theme["chalk_green"]}" stroke-width="3" />',
            f'      <circle cx="{half_w - 60}" cy="80" r="16" fill="{theme["source_bg"]}" stroke="{theme["chalk_yellow"]}" stroke-width="2" />',
            f'      <text x="{half_w - 60}" y="85" fill="{theme["chalk_yellow"]}" font-size="10" font-weight="800" text-anchor="middle">A</text>',
            
            f'      <!-- Circuit Telemetry -->',
            f'      <g transform="translate(24, 120)">',
            f'        <rect width="{half_w - 48}" height="28" rx="4" fill="{theme["source_bg"]}" stroke="{theme["frame"]}" stroke-width="1" />',
            f'        <text x="12" y="19" fill="{theme["chalk_white"]}" font-size="11">Electrical Current (I): <tspan fill="{theme["chalk_yellow"]}" font-weight="700">{current_val}</tspan></text>',
            f'      </g>',
            f'    </g>',

            # Bottom Inverse Relationship Rule
            f'    <g transform="translate(20, {h - 235})">',
            f'      <rect width="{w - 136}" height="32" rx="6" fill="rgba(6, 78, 59, 0.7)" stroke="{theme["chalk_green"]}" stroke-width="1.5" />',
            f'      <text x="16" y="20" fill="{theme["chalk_yellow"]}" font-size="12" font-weight="700">💡 KEY INVARIANT: More Obstruction / Pinch (Resistance ↑) = LESS FLOW (Current ↓). Never doubles!</text>',
            f'    </g>',
            f'  </g>',
        ])
        return "\n".join(svg)

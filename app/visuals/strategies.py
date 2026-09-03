"""
Visual Strategy Planner for Module 8 (Subject-Aware Visual Intelligence).
Translates educational concepts and diagnosed misconceptions into precise VisualSpecs.
"""

from __future__ import annotations
from typing import Optional
from app.visuals.models import (
    VisualSpec,
    VisualType,
    SubjectCategory,
    RenderFormat,
)
from app.harness.session import TeachingStrategy
from app.assessment.models import MisconceptionRecord


class VisualStrategyPlanner:
    """
    Plans the optimal visual representation based on subject classification,
    pedagogical goal, and learner misconception state.
    """

    def classify_subject(self, subject_hint: str, concept: str) -> SubjectCategory:
        """Determines subject category from text clues."""
        text = f"{subject_hint} {concept}".lower()
        if any(w in text for w in ["physics", "ohm", "voltage", "current", "circuit", "force", "velocity", "optics"]):
            return SubjectCategory.PHYSICS
        elif any(w in text for w in ["math", "algebra", "calculus", "equation", "fraction", "geometry", "trigonometry"]):
            return SubjectCategory.MATHEMATICS
        elif any(w in text for w in ["program", "code", "python", "javascript", "algorithm", "function", "variable", "loop"]):
            return SubjectCategory.PROGRAMMING
        elif any(w in text for w in ["bio", "cell", "respiration", "dna", "mitosis", "organ", "heart", "anatomy"]):
            return SubjectCategory.BIOLOGY
        elif any(w in text for w in ["chem", "molecule", "reaction", "atom", "acid", "base", "compound"]):
            return SubjectCategory.CHEMISTRY
        elif any(w in text for w in ["history", "war", "empire", "revolution", "century", "treaty"]):
            return SubjectCategory.HISTORY
        return SubjectCategory.GENERAL

    def plan_visual_spec(
        self,
        subject_hint: str,
        concept: str,
        teaching_strategy: TeachingStrategy = TeachingStrategy.DIRECT_EXPLANATION,
        misconception: Optional[MisconceptionRecord] = None,
        duration_seconds: int = 15,
    ) -> VisualSpec:
        """
        Creates a structured VisualSpec tailored to the learner's state and misconceptions.
        """
        subject = self.classify_subject(subject_hint, concept)
        concept_lower = concept.lower()

        # 1. Physics - Ohm's Law Adaptive Visuals
        if subject == SubjectCategory.PHYSICS and ("ohm" in concept_lower or "resistance" in concept_lower or "circuit" in concept_lower):
            if misconception and "inverse" in misconception.misconception_type.lower():
                return VisualSpec(
                    visual_type=VisualType.ANALOGY_WATER_CIRCUIT,
                    subject=SubjectCategory.PHYSICS,
                    concept=concept,
                    purpose="Demonstrate inverse relationship between resistance and current using water pipe constriction analogy.",
                    title="Ohm's Law Analogy: Electrical Circuit vs. Water Flow",
                    labels=["Battery (Pump)", "Current (Water Flow)", "Resistor (Constriction / Pinch)"],
                    equations=["I = V / R", "\\text{More Pinch (R } \\uparrow\\text{)} \\implies \\text{Less Flow (I } \\downarrow\\text{)}"],
                    renderer="svg_analogy",
                    preferred_format=RenderFormat.SVG,
                    parameters={"voltage": 12, "resistance": 6, "flow_rate": "reduced"},
                    duration_seconds=duration_seconds,
                )
            elif teaching_strategy == TeachingStrategy.VISUAL_EXPLANATION:
                return VisualSpec(
                    visual_type=VisualType.GRAPH_PLOT,
                    subject=SubjectCategory.PHYSICS,
                    concept=concept,
                    purpose="Show V-I characteristic curves and slope changes with varying resistance.",
                    title="Voltage vs. Current Graph (V = I * R)",
                    labels=["Current (I in Amperes)", "Voltage (V in Volts)", "Slope = Resistance (R)"],
                    equations=["V = I \\cdot R", "I = \\frac{V}{R}"],
                    renderer="matplotlib_plot",
                    preferred_format=RenderFormat.SVG,
                    parameters={"r_low": 2, "r_high": 10, "v_max": 20},
                    duration_seconds=duration_seconds,
                )
            else:
                return VisualSpec(
                    visual_type=VisualType.CIRCUIT_DIAGRAM,
                    subject=SubjectCategory.PHYSICS,
                    concept=concept,
                    purpose="Illustrate basic closed DC circuit with battery, resistor, ammeter and current flow.",
                    title="Basic DC Circuit - Ohm's Law",
                    labels=["Voltage Source (V)", "Resistor (R)", "Ammeter (I)", "Electron Flow"],
                    equations=["V = I \\cdot R"],
                    renderer="svg_circuit",
                    preferred_format=RenderFormat.SVG,
                    parameters={"voltage": 12, "resistance": 4, "current": 3},
                    duration_seconds=duration_seconds,
                )

        # 2. Mathematics
        if subject == SubjectCategory.MATHEMATICS:
            if "equation" in concept_lower or "algebra" in concept_lower:
                return VisualSpec(
                    visual_type=VisualType.LATEX_EQUATION,
                    subject=SubjectCategory.MATHEMATICS,
                    concept=concept,
                    purpose="Display step-by-step algebraic equation manipulation.",
                    title="Step-by-Step Algebraic Solution",
                    equations=["10 + 4 \\times 2", "= 10 + 8", "= 18"],
                    steps=["1. Evaluate multiplication: 4 * 2 = 8", "2. Evaluate addition: 10 + 8 = 18"],
                    renderer="latex_equation",
                    preferred_format=RenderFormat.HTML,
                    duration_seconds=duration_seconds,
                )
            return VisualSpec(
                visual_type=VisualType.GRAPH_PLOT,
                subject=SubjectCategory.MATHEMATICS,
                concept=concept,
                purpose="Plot mathematical function coordinate plane.",
                title="Function Plot f(x)",
                labels=["x-axis", "y-axis", "f(x)"],
                renderer="matplotlib_plot",
                preferred_format=RenderFormat.SVG,
                duration_seconds=duration_seconds,
            )

        # 3. Programming
        if subject == SubjectCategory.PROGRAMMING:
            return VisualSpec(
                visual_type=VisualType.CODE_BLOCK,
                subject=SubjectCategory.PROGRAMMING,
                concept=concept,
                purpose="Display formatted code example with execution annotations.",
                title=f"Python Implementation: {concept}",
                renderer="code_renderer",
                preferred_format=RenderFormat.HTML,
                parameters={"language": "python", "code": "# Example code\n"},
                duration_seconds=duration_seconds,
            )

        # 4. Default / General Mermaid Flowchart
        return VisualSpec(
            visual_type=VisualType.MERMAID_FLOWCHART,
            subject=subject,
            concept=concept,
            purpose=f"Visual concept map for {concept}",
            title=f"Concept Flow: {concept}",
            renderer="mermaid_renderer",
            preferred_format=RenderFormat.MERMAID,
            duration_seconds=duration_seconds,
        )

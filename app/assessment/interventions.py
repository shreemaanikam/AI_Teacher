"""
Intervention Engine for Module 7 (Assessment & Misconception Engine).
Selects targeted, differentiated pedagogical interventions when misconceptions or learning gaps are diagnosed.
"""

from __future__ import annotations
from typing import Optional
from app.assessment.models import InterventionPlan, MisconceptionRecord, QuestionType
from app.harness.session import TeachingStrategy


class InterventionEngine:
    """
    Constructs actionable pedagogical interventions that explicitly differ from
    previously attempted strategies to help students correct misconceptions.
    """

    def create_intervention_plan(
        self,
        misconception: MisconceptionRecord,
        current_strategy: TeachingStrategy,
        subject: str = "physics",
    ) -> InterventionPlan:
        """
        Builds a customized intervention plan tailored to the detected misconception.
        """
        # Determine strategy transition
        if current_strategy == TeachingStrategy.DIRECT_EXPLANATION:
            new_strategy = TeachingStrategy.SIMPLE_ANALOGY
            reason = "Direct theoretical explanation failed; switching to an intuitive physical analogy."
        elif current_strategy == TeachingStrategy.SIMPLE_ANALOGY:
            new_strategy = TeachingStrategy.VISUAL_EXPLANATION
            reason = "Analogy alone was insufficient; introducing a dynamic visual diagram with active flow cues."
        elif current_strategy == TeachingStrategy.VISUAL_EXPLANATION:
            new_strategy = TeachingStrategy.CONTRASTIVE_EXPLANATION
            reason = "Student still confused; presenting side-by-side comparison of direct vs inverse relationships."
        else:
            new_strategy = TeachingStrategy.PREREQUISITE_REVIEW
            reason = "Repeated misconception indicates a fundamental prerequisite gap; reviewing foundational definitions."

        steps = []
        analogy_prompt = None
        visual_type = "diagram"

        if "inverse" in misconception.misconception_type.lower():
            visual_type = "analogy_water_circuit"
            analogy_prompt = (
                "Think of electricity like water flowing through a water pipe. "
                "Voltage is the water pump pressure pushing the water. "
                "Resistance is a clamp pinching the water pipe. "
                "If you tighten the clamp (increase resistance), less water can get through (current decreases)."
            )
            steps = [
                "1. Highlight the inverse proportion in Ohm's Law: I = V / R.",
                "2. Deliver the water pipe pinch analogy.",
                "3. Present the side-by-side Circuit vs Water Pipe SVG diagram.",
                "4. Walk through a simple calculation (e.g. 10V / 2Ω = 5A vs 10V / 5Ω = 2A).",
                "5. Ask a re-check conceptual question to verify comprehension.",
            ]
        elif "voltage" in misconception.misconception_type.lower():
            visual_type = "circuit_diagram_with_meters"
            analogy_prompt = "Voltage is the potential energy height difference, while current is the waterfall flow rate."
            steps = [
                "1. Distinguish electrical potential difference (Volts) from charge flow rate (Amperes).",
                "2. Show voltmeter across battery and ammeter inline in the circuit.",
                "3. Re-test with a scenario question.",
            ]
        else:
            steps = [
                f"1. Directly address the misconception: '{misconception.belief}'.",
                f"2. Apply {new_strategy.value} technique.",
                "3. Present step-by-step verified example.",
                "4. Pose a targeted follow-up question.",
            ]

        return InterventionPlan(
            misconception_type=misconception.misconception_type,
            concept=misconception.concept,
            previous_strategy=current_strategy,
            new_strategy=new_strategy,
            reason_for_change=reason,
            analogy_prompt=analogy_prompt,
            visual_type=visual_type,
            recheck_question_type=QuestionType.CONCEPTUAL,
            steps=steps,
        )

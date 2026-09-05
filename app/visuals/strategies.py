"""
Visual Strategy Planner for Module 8 (Subject-Aware Visual Intelligence).
Translates educational concepts and diagnosed misconceptions into precise VisualSpecs
and dynamic, progressive TeachingVisualPlans grounded in student study materials.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import uuid

from app.visuals.models import (
    VisualSpec,
    VisualType,
    VisualBoardTheme,
    SubjectCategory,
    RenderFormat,
    TeachingVisualPlan,
    VisualTeachingStep,
    NarrationCue,
    VisualCue,
)
from app.harness.session import TeachingStrategy
from app.assessment.models import MisconceptionRecord


class VisualStrategyPlanner:
    """
    Plans optimal visual teaching representations based on subject classification,
    pedagogical goals, learner misconception states, and uploaded source materials.
    """

    def classify_subject(self, subject_hint: str, concept: str) -> SubjectCategory:
        """Determines subject category from text clues."""
        text = f"{subject_hint} {concept}".lower().replace('_', ' ')
        hint_clean = subject_hint.lower().replace('_', ' ')

        if hint_clean in ("computer science", "cs") and not any(w in concept.lower() for w in ["program", "python", "javascript", "code"]):
            return SubjectCategory.COMPUTER_SCIENCE
        elif any(w in text for w in ["network", "tcp", "packet", "dns", "http", "osi", "routing", "socket", "client", "server"]):
            return SubjectCategory.COMPUTER_SCIENCE
        elif any(w in text for w in ["program", "code", "python", "javascript", "algorithm", "function", "variable", "loop"]):
            return SubjectCategory.PROGRAMMING
        elif any(w in text for w in ["computer science", "data structure", "array", "stack", "queue", "tree", "pointer", "sorting", "bfs", "dfs", "search"]):
            return SubjectCategory.COMPUTER_SCIENCE
        elif any(w in text for w in ["math", "algebra", "calculus", "equation", "quadratic", "derivative", "integral", "matrix", "probability", "bayes", "vector", "geometry", "trigonometry", "fraction"]):
            return SubjectCategory.MATHEMATICS
        elif any(w in text for w in ["circuit", "signal", "logic gate", "microcontroller", "transistor", "amplifier", "opamp", "filter"]):
            return SubjectCategory.ENGINEERING
        elif any(w in text for w in ["physics", "ohm", "voltage", "current", "resistance", "force", "velocity", "faraday", "electromagnetism", "optics"]):
            return SubjectCategory.PHYSICS
        elif any(w in text for w in ["bio", "cell", "respiration", "dna", "mitosis", "organ", "heart", "anatomy", "protein"]):
            return SubjectCategory.BIOLOGY
        elif any(w in text for w in ["chem", "molecule", "reaction", "atom", "acid", "base", "compound"]):
            return SubjectCategory.CHEMISTRY
        elif any(w in text for w in ["history", "war", "empire", "revolution", "century", "treaty"]):
            return SubjectCategory.HISTORY
        return SubjectCategory.GENERAL

    def plan_teaching_visual(
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
        """
        Creates a subject-agnostic, source-grounded TeachingVisualPlan with step-by-step
        whiteboard reveals and synchronized narration/animation cues.
        """
        subject = self.classify_subject(subject_hint, concept)
        concept_lower = concept.lower()
        chunk_ids = source_chunk_ids or []
        is_grounded = bool(document_id or chunk_ids or source_reference or evidence_snippets)

        # 1. Subject & Concept Specific Visual Formulation
        if subject == SubjectCategory.MATHEMATICS or "equation" in concept_lower or "calculus" in concept_lower:
            visual_type = VisualType.EQUATION_DERIVATION
            purpose = f"Step-by-step mathematical deduction and variable analysis for {concept}."
            steps, equations, labels = self._build_math_steps(concept, evidence_snippets)

        elif subject in (SubjectCategory.COMPUTER_SCIENCE, SubjectCategory.PROGRAMMING) or any(w in concept_lower for w in ["search", "array", "pointer", "stack", "code", "loop", "python", "network", "tcp", "packet", "dns", "http", "tls", "handshake"]):
            if any(w in concept_lower for w in ["network", "tcp", "packet", "dns", "http", "tls", "handshake"]):
                visual_type = VisualType.NETWORK_FLOW
                purpose = f"Multi-party packet flow and protocol state progression for {concept}."
                steps, equations, labels = self._build_network_steps(concept, evidence_snippets)
            elif any(w in concept_lower for w in ["code", "loop", "python", "implementation", "fibonacci", "function"]):
                visual_type = VisualType.CODE_EXECUTION
                purpose = f"Live code execution trace and variable state watch for {concept}."
                steps, equations, labels = self._build_code_trace_steps(concept, evidence_snippets)
            else:
                visual_type = VisualType.ARRAY_POINTER
                purpose = f"Dynamic array pointer traversal and search invariant visualization for {concept}."
                steps, equations, labels = self._build_array_pointer_steps(concept, evidence_snippets)

        elif subject in (SubjectCategory.PHYSICS, SubjectCategory.ENGINEERING) and ("ohm" in concept_lower or "circuit" in concept_lower or "voltage" in concept_lower):
            if misconception and "inverse" in misconception.misconception_type.lower():
                visual_type = VisualType.ANALOGY_WATER_CIRCUIT
                purpose = "Remediate inverse-relationship misconception using dynamic water-pipe pinch analogy."
                steps, equations, labels = self._build_remediation_analogy_steps(concept, misconception)
            else:
                visual_type = VisualType.CIRCUIT_DIAGRAM
                purpose = f"Closed-loop electrical circuit schematic and real-time telemetry for {concept}."
                steps, equations, labels = self._build_circuit_steps(concept, evidence_snippets)

        else:
            visual_type = VisualType.WHITEBOARD
            purpose = f"Step-by-step whiteboard conceptual walkthrough of {concept}."
            steps, equations, labels = self._build_general_whiteboard_steps(concept, evidence_snippets)

        # 2. Construct Synchronized Narration and Visual Cues
        narration_cues: List[NarrationCue] = []
        visual_cues: List[VisualCue] = []
        step_duration = max(2.5, float(duration_seconds) / max(1, len(steps)))

        current_time = 0.0
        for idx, step in enumerate(steps):
            step.duration_seconds = step_duration
            nc_id = f"nc_{uuid.uuid4().hex[:8]}"
            vc_id = f"vc_{uuid.uuid4().hex[:8]}"
            step.narration_cue_id = nc_id

            narration_cues.append(
                NarrationCue(
                    cue_id=nc_id,
                    start_time=round(current_time, 2),
                    end_time=round(current_time + step_duration, 2),
                    text=f"{step.title}: {step.explanation}",
                    concept_id=concept,
                )
            )

            visual_cues.append(
                VisualCue(
                    cue_id=vc_id,
                    start_time=round(current_time, 2),
                    end_time=round(current_time + step_duration, 2),
                    action=step.action,
                    target=step.highlight_target or f"step_{idx}",
                    parameters={"step_index": idx, "action": step.action},
                )
            )
            current_time += step_duration

        return TeachingVisualPlan(
            visual_id=f"vis_{uuid.uuid4().hex[:10]}",
            concept_id=concept,
            subject=subject,
            visual_type=visual_type,
            theme=theme,
            teaching_purpose=purpose,
            steps=steps,
            narration_cues=narration_cues,
            animation_cues=visual_cues,
            labels=labels,
            equations=equations,
            duration_seconds=float(duration_seconds),
            language=language,
            accessibility_description=f"Interactive whiteboard explaining {concept} across {len(steps)} steps.",
            is_grounded_in_source=is_grounded,
            requires_external_knowledge=not is_grounded,
            document_id=document_id,
            source_chunk_ids=chunk_ids,
            source_reference=source_reference,
        )

    def plan_visual_spec(
        self,
        subject_hint: str,
        concept: str,
        teaching_strategy: TeachingStrategy = TeachingStrategy.DIRECT_EXPLANATION,
        misconception: Optional[MisconceptionRecord] = None,
        duration_seconds: int = 15,
        document_id: Optional[str] = None,
        chunk_id: Optional[str] = None,
        source_reference: Optional[Dict[str, Any]] = None,
    ) -> VisualSpec:
        """
        Backward-compatible VisualSpec generator that also attaches the new TeachingVisualPlan.
        """
        plan = self.plan_teaching_visual(
            concept=concept,
            subject_hint=subject_hint,
            teaching_strategy=teaching_strategy,
            misconception=misconception,
            duration_seconds=duration_seconds,
            document_id=document_id,
            source_chunk_ids=[chunk_id] if chunk_id else [],
            source_reference=source_reference,
        )

        subject = self.classify_subject(subject_hint, concept)
        concept_lower = concept.lower()

        # 1. Physics - Ohm's Law Adaptive Visuals
        if subject == SubjectCategory.PHYSICS and ("ohm" in concept_lower or "resistance" in concept_lower or "circuit" in concept_lower):
            if misconception and "inverse" in misconception.misconception_type.lower():
                return VisualSpec(
                    spec_id=plan.visual_id,
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
                    document_id=document_id,
                    chunk_id=chunk_id,
                    source_reference=source_reference,
                    visual_plan=plan,
                )
            elif teaching_strategy == TeachingStrategy.VISUAL_EXPLANATION:
                return VisualSpec(
                    spec_id=plan.visual_id,
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
                    document_id=document_id,
                    chunk_id=chunk_id,
                    source_reference=source_reference,
                    visual_plan=plan,
                )
            else:
                return VisualSpec(
                    spec_id=plan.visual_id,
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
                    document_id=document_id,
                    chunk_id=chunk_id,
                    source_reference=source_reference,
                    visual_plan=plan,
                )

        # 2. Mathematics
        if subject == SubjectCategory.MATHEMATICS:
            if "equation" in concept_lower or "algebra" in concept_lower:
                return VisualSpec(
                    spec_id=plan.visual_id,
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
                    document_id=document_id,
                    chunk_id=chunk_id,
                    source_reference=source_reference,
                    visual_plan=plan,
                )
            return VisualSpec(
                spec_id=plan.visual_id,
                visual_type=VisualType.GRAPH_PLOT,
                subject=SubjectCategory.MATHEMATICS,
                concept=concept,
                purpose="Plot mathematical function coordinate plane.",
                title="Function Plot f(x)",
                labels=["x-axis", "y-axis", "f(x)"],
                renderer="matplotlib_plot",
                preferred_format=RenderFormat.SVG,
                duration_seconds=duration_seconds,
                document_id=document_id,
                chunk_id=chunk_id,
                source_reference=source_reference,
                visual_plan=plan,
            )

        # 3. Programming
        if subject == SubjectCategory.PROGRAMMING:
            return VisualSpec(
                spec_id=plan.visual_id,
                visual_type=VisualType.CODE_BLOCK,
                subject=SubjectCategory.PROGRAMMING,
                concept=concept,
                purpose="Display formatted code example with execution annotations.",
                title=f"Python Implementation: {concept}",
                renderer="code_renderer",
                preferred_format=RenderFormat.HTML,
                parameters={"language": "python", "code": "# Example code\n"},
                duration_seconds=duration_seconds,
                document_id=document_id,
                chunk_id=chunk_id,
                source_reference=source_reference,
                visual_plan=plan,
            )

        # 4. Fallback / General Mermaid Flowchart
        return VisualSpec(
            spec_id=plan.visual_id,
            visual_type=VisualType.MERMAID_FLOWCHART,
            subject=subject,
            concept=concept,
            purpose=plan.teaching_purpose,
            title=f"{concept.replace('_', ' ').title()}",
            renderer="mermaid_renderer",
            preferred_format=RenderFormat.MERMAID,
            duration_seconds=duration_seconds,
            document_id=document_id,
            chunk_id=chunk_id,
            source_reference=source_reference,
            visual_plan=plan,
        )

    # -------------------------------------------------------------
    # Step Builders by Discipline
    # -------------------------------------------------------------
    def _build_math_steps(self, concept: str, snippets: Optional[List[str]] = None):
        equations = [
            "ax^2 + bx + c = 0",
            "x^2 + \\frac{b}{a}x = -\\frac{c}{a}",
            "\\left(x + \\frac{b}{2a}\\right)^2 = \\frac{b^2 - 4ac}{4a^2}",
            "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}",
        ]
        labels = ["Quadratic Term", "Linear Term", "Constant Term", "Discriminant (b² - 4ac)"]
        steps = [
            VisualTeachingStep(
                step_index=0,
                title="State General Algebraic Form",
                explanation="Write out the standard polynomial expression grounded in the textbook problem.",
                action="DRAW_EQUATION",
                content=equations[0],
                highlight_target="eq_standard",
                why_appears="Establishes base equality and defines coefficients a, b, and c.",
            ),
            VisualTeachingStep(
                step_index=1,
                title="Normalize by Leading Coefficient",
                explanation="Divide all terms by 'a' to isolate monic quadratic and linear terms.",
                action="HIGHLIGHT_TERMS",
                content=equations[1],
                highlight_target="term_divide_a",
                why_appears="Prepares the left-hand side for completing the square.",
            ),
            VisualTeachingStep(
                step_index=2,
                title="Complete the Square",
                explanation="Add (b / 2a)² to both sides of the equation to form a perfect binomial square.",
                action="SUBSTITUTE",
                content=equations[2],
                highlight_target="binomial_square",
                why_appears="Converts the polynomial into a single square term with constant remainder.",
            ),
            VisualTeachingStep(
                step_index=3,
                title="Extract Roots via Quadratic Formula",
                explanation="Take the square root of both sides to obtain the explicit closed-form solution.",
                action="BOX_FINAL_ANSWER",
                content=equations[3],
                highlight_target="final_roots",
                why_appears="Yields the definitive roots and highlights the role of the discriminant.",
            ),
        ]
        return steps, equations, labels

    def _build_array_pointer_steps(self, concept: str, snippets: Optional[List[str]] = None):
        labels = ["Index 0..6", "LOW Pointer", "HIGH Pointer", "MID Element", "Search Invariant"]
        steps = [
            VisualTeachingStep(
                step_index=0,
                title="Initialize Search Range (LOW & HIGH Bounds)",
                explanation="Define search space bounded by LOW at index 0 and HIGH at index 6.",
                action="INITIALIZE_POINTERS",
                highlight_target="low_high_bounds",
                why_appears="Precondition: Array is monotonically sorted in ascending order.",
            ),
            VisualTeachingStep(
                step_index=1,
                title="Compute Midpoint Index (MID Pointer)",
                explanation="Calculate mid = (low + high) // 2 = 3. Inspect value arr[3] = 12 against target 17.",
                action="CALCULATE_MID",
                highlight_target="mid_pointer",
                why_appears="Binary search divides the candidate search space in half at each iteration.",
            ),
            VisualTeachingStep(
                step_index=2,
                title="Discard Ineligible Subarray",
                explanation="Since target 17 > 12, discard the entire left partition indices 0 through 3.",
                action="DISCARD_PARTITION",
                highlight_target="discard_left",
                why_appears="Eliminates half the search elements in O(1) decision time.",
            ),
            VisualTeachingStep(
                step_index=3,
                title="Shift Boundary and Converge",
                explanation="Move LOW to mid + 1 = 4. Mid element arr[4] equals 17. Target found!",
                action="CONVERGE_TARGET",
                highlight_target="target_match",
                why_appears="Search successfully concludes in O(log N) total time complexity.",
            ),
        ]
        return steps, [], labels

    def _build_code_trace_steps(self, concept: str, snippets: Optional[List[str]] = None):
        labels = ["Code Editor", "Active Line", "Call Stack", "Variables Watch"]
        steps = [
            VisualTeachingStep(
                step_index=0,
                title="Function Invocation & Call Stack Frame",
                explanation="Enter binary_search function with parameters arr and target 17.",
                action="SET_FRAME",
                highlight_target="line_1",
                why_appears="Initializes stack frame on the call stack.",
            ),
            VisualTeachingStep(
                step_index=1,
                title="Loop Invariant Evaluation",
                explanation="Evaluate while condition: low <= high (0 <= 6 is True).",
                action="EVAL_CONDITION",
                highlight_target="line_3",
                why_appears="Guarantees termination when search bounds cross.",
            ),
            VisualTeachingStep(
                step_index=2,
                title="Branch Decision & Variable State Mutation",
                explanation="Condition arr[mid] < target evaluates True. Mutate low = mid + 1.",
                action="UPDATE_VARIABLE",
                highlight_target="line_6",
                why_appears="Advances pointers towards target element.",
            ),
            VisualTeachingStep(
                step_index=3,
                title="Return Value & Frame Tear-Down",
                explanation="Return index 4 to caller. Success status verified.",
                action="RETURN_VALUE",
                highlight_target="line_5",
                why_appears="Completes algorithmic contract.",
            ),
        ]
        return steps, [], labels

    def _build_network_steps(self, concept: str, snippets: Optional[List[str]] = None):
        labels = ["Client Browser", "DNS Server", "Web Server", "TCP/TLS Handshake", "HTTP Payload"]
        steps = [
            VisualTeachingStep(
                step_index=0,
                title="DNS Name Resolution",
                explanation="Client resolves domain name to target IP address via recursive DNS resolver.",
                action="SEND_DNS_QUERY",
                highlight_target="dns_arrow",
                why_appears="Translates human-readable hostname into network layer IP address.",
            ),
            VisualTeachingStep(
                step_index=1,
                title="TCP 3-Way Handshake",
                explanation="Client and server establish reliable transport channel using SYN, SYN-ACK, and ACK packets.",
                action="TCP_HANDSHAKE",
                highlight_target="tcp_flow",
                why_appears="Guarantees ordered, loss-free data transmission.",
            ),
            VisualTeachingStep(
                step_index=2,
                title="TLS 1.3 Cryptographic Handshake",
                explanation="Negotiate symmetric cipher keys via Diffie-Hellman exchange for encrypted communication.",
                action="TLS_EXCHANGE",
                highlight_target="tls_lock",
                why_appears="Enforces confidentiality and integrity of educational sessions.",
            ),
            VisualTeachingStep(
                step_index=3,
                title="HTTP Request & Application Data Transfer",
                explanation="Client issues GET request and server responds with HTTP 200 OK and study material content.",
                action="HTTP_TRANSACTION",
                highlight_target="http_stream",
                why_appears="Delivers application payload to student's browser.",
            ),
        ]
        return steps, [], labels

    def _build_circuit_steps(self, concept: str, snippets: Optional[List[str]] = None):
        equations = ["V = I \\cdot R", "I = \\frac{V}{R}"]
        labels = ["DC Battery (12V)", "Resistor R", "Ammeter A", "Current Loop I"]
        steps = [
            VisualTeachingStep(
                step_index=0,
                title="Schematic Architecture & Components",
                explanation="A closed electrical circuit with 12V DC power supply and initial 4-Ohm resistor.",
                action="LAYOUT_CIRCUIT",
                highlight_target="components",
                why_appears="Defines circuit topology and reference polarities.",
            ),
            VisualTeachingStep(
                step_index=1,
                title="Closed Loop Current Conduction",
                explanation="Electrons traverse circuit from negative to positive pole. Ammeter registers 3.0 Amperes.",
                action="ANIMATE_CURRENT",
                highlight_target="current_flow",
                why_appears="Demonstrates Ohm's Law baseline condition (I = 12V / 4Ω = 3A).",
            ),
            VisualTeachingStep(
                step_index=2,
                title="Resistance Doubled (Parametric Perturbation)",
                explanation="Resistance increased from 4 Ohms to 8 Ohms. Resistor experiences higher thermal obstruction.",
                action="INCREASE_RESISTANCE",
                highlight_target="resistor_glow",
                why_appears="Tests learner understanding of the inverse relationship.",
            ),
            VisualTeachingStep(
                step_index=3,
                title="Current Response & Equilibrium",
                explanation="Current drops proportionally by half from 3.0A to 1.5A as governed by I = V / R.",
                action="UPDATE_AMMETER",
                highlight_target="ammeter_telemetry",
                why_appears="Confirms that higher resistance reduces current flow.",
            ),
        ]
        return steps, equations, labels

    def _build_remediation_analogy_steps(self, concept: str, misc: MisconceptionRecord):
        equations = ["I = \\frac{V}{R}", "\\text{More Pinch } \\implies \\text{Less Water Flow}"]
        labels = ["Water Pump (Voltage)", "Pipe Constriction (Resistance)", "Water Flow Rate (Current)"]
        steps = [
            VisualTeachingStep(
                step_index=0,
                title="Address Student Misconception",
                explanation=f"Reviewing belief: '{misc.belief}'. Let's test this with a physical water pipe model.",
                action="INTRODUCE_ANALOGY",
                highlight_target="misconception_banner",
                why_appears="Directly reframes student's erroneous intuition.",
            ),
            VisualTeachingStep(
                step_index=1,
                title="Water Pump & Pipe Flow Analogy",
                explanation="Think of voltage as the water pump and electric current as the volume of water flowing through the pipe.",
                action="DRAW_PIPE",
                highlight_target="water_pump",
                why_appears="Connects abstract electrical concepts to concrete physical mechanics.",
            ),
            VisualTeachingStep(
                step_index=2,
                title="Pinching the Pipe (Increasing Resistance)",
                explanation="When you pinch or narrow the pipe, you create resistance. Does the water speed up and double? No, it restricts the flow.",
                action="CONSTRICT_PIPE",
                highlight_target="pinch_point",
                why_appears="Visually invalidates the misconception that resistance pushes more electrons.",
            ),
            VisualTeachingStep(
                step_index=3,
                title="Inverse Relationship Confirmed",
                explanation="More pinch (R ↑) always yields less flow (I ↓). The current must decrease.",
                action="CONFIRM_INVERSE",
                highlight_target="flow_decrease",
                why_appears="Locks in correct pedagogical insight before rechecking comprehension.",
            ),
        ]
        return steps, equations, labels

    def _build_general_whiteboard_steps(self, concept: str, snippets: Optional[List[str]] = None):
        labels = ["Core Definition", "Mechanism", "Application", "Summary"]
        steps = [
            VisualTeachingStep(
                step_index=0,
                title=f"Core Definition of {concept}",
                explanation=f"Foundational definition and scope of {concept} as presented in study material.",
                action="SHOW_DEFINITION",
                highlight_target="def_card",
                why_appears="Establishes formal terminology.",
            ),
            VisualTeachingStep(
                step_index=1,
                title="Operational Mechanism",
                explanation="How the primary components interact under operating conditions.",
                action="HIGHLIGHT_MECHANISM",
                highlight_target="mech_card",
                why_appears="Details internal state progression.",
            ),
            VisualTeachingStep(
                step_index=2,
                title="Practical Application & Example",
                explanation="Concrete illustrative example demonstrating the concept in a practical scenario.",
                action="SHOW_EXAMPLE",
                highlight_target="example_card",
                why_appears="Reinforces theoretical model with empirical context.",
            ),
            VisualTeachingStep(
                step_index=3,
                title="Key Takeaways & Exam Summary",
                explanation="Essential formulas, rules, and checkpoints for mastery.",
                action="HIGHLIGHT_SUMMARY",
                highlight_target="summary_card",
                why_appears="Prepares student for checkpoint assessment.",
            ),
        ]
        return steps, [], labels


"""
Extensible Misconception Taxonomy for Module 7 (Assessment & Misconception Engine).
Maintains structured patterns, indicators, and remedies across subjects.
"""

from __future__ import annotations
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from app.harness.session import TeachingStrategy


class MisconceptionDefinition(BaseModel):
    subject: str
    concept: str
    misconception_type: str
    belief_description: str
    indicator_keywords: List[str] = Field(default_factory=list)
    anti_patterns: List[str] = Field(default_factory=list)
    severity: str = "moderate"
    prerequisite_gap: Optional[str] = None
    default_strategy: TeachingStrategy = TeachingStrategy.SIMPLE_ANALOGY
    analogy_hint: str = ""
    remediation_template: str = ""


class MisconceptionTaxonomy:
    """Registry and taxonomy of common conceptual mistakes and mental models."""

    def __init__(self):
        self._taxonomy: Dict[str, Dict[str, List[MisconceptionDefinition]]] = {}
        self._initialize_core_taxonomy()

    def register(self, definition: MisconceptionDefinition) -> None:
        subj = definition.subject.lower()
        concept = definition.concept.lower()
        if subj not in self._taxonomy:
            self._taxonomy[subj] = {}
        if concept not in self._taxonomy[subj]:
            self._taxonomy[subj][concept] = []
        self._taxonomy[subj][concept].append(definition)

    def find_misconceptions(self, subject: str, concept: str) -> List[MisconceptionDefinition]:
        subj = subject.lower()
        concept = concept.lower()
        return self._taxonomy.get(subj, {}).get(concept, [])

    def _initialize_core_taxonomy(self) -> None:
        # 1. Physics - Ohm's Law & Electricity
        self.register(
            MisconceptionDefinition(
                subject="physics",
                concept="ohms_law",
                misconception_type="inverse_relationship_confusion",
                belief_description="Student believes increasing resistance increases electrical current.",
                indicator_keywords=["increases", "increase", "more current", "doubles", "higher current", "directly proportional"],
                anti_patterns=["current increases when resistance increases", "more resistance allows more current", "current doubles"],
                severity="severe",
                prerequisite_gap="electrical_resistance_definition",
                default_strategy=TeachingStrategy.SIMPLE_ANALOGY,
                analogy_hint="Water pipe with a narrow constriction: more resistance blocks the flow, reducing water current.",
                remediation_template="In Ohm's law (I = V / R), Current (I) is INVERSELY proportional to Resistance (R). When resistance increases, it resists the flow of electrons, so current MUST decrease.",
            )
        )
        self.register(
            MisconceptionDefinition(
                subject="physics",
                concept="ohms_law",
                misconception_type="voltage_current_confusion",
                belief_description="Student conflates voltage (push/potential) with current (flow rate).",
                indicator_keywords=["voltage flows", "voltage is consumed", "current pushes"],
                anti_patterns=["voltage flows through the wire", "voltage is the flow"],
                severity="moderate",
                prerequisite_gap="potential_difference_concept",
                default_strategy=TeachingStrategy.VISUAL_EXPLANATION,
                analogy_hint="Voltage is the water pressure pushing, current is the liters of water flowing per second.",
                remediation_template="Voltage is the electrical pressure (potential difference) that drives current; current is the actual flow rate of charge (Coulombs per second).",
            )
        )
        self.register(
            MisconceptionDefinition(
                subject="physics",
                concept="force_motion",
                misconception_type="force_velocity_confusion",
                belief_description="Student believes an object in motion must continuously have a net force acting on it (Aristotelian view).",
                indicator_keywords=["needs force to move", "force required to keep moving", "constant force for constant velocity"],
                anti_patterns=["force is required to maintain motion", "if moving then net force is non-zero"],
                severity="severe",
                prerequisite_gap="newtons_first_law",
                default_strategy=TeachingStrategy.CONTRASTIVE_EXPLANATION,
                analogy_hint="A puck sliding on frictionless ice continues moving forever without any pushing force.",
                remediation_template="Newton's 1st Law: Net force causes acceleration (change in velocity), not velocity itself. Constant velocity requires ZERO net force.",
            )
        )

        # 2. Mathematics
        self.register(
            MisconceptionDefinition(
                subject="mathematics",
                concept="algebra_equations",
                misconception_type="operator_precedence_error",
                belief_description="Student calculates operations strictly left-to-right ignoring multiplication/division precedence over addition.",
                indicator_keywords=["left to right", "added first", "multiplied last"],
                anti_patterns=["2 + 3 * 4 = 20"],
                severity="moderate",
                prerequisite_gap="pemdas_order_of_operations",
                default_strategy=TeachingStrategy.STEP_BY_STEP,
                analogy_hint="Multiplication binds terms into groups before addition sums the groups.",
                remediation_template="Remember PEMDAS/BODMAS: Perform multiplication and division BEFORE addition and subtraction.",
            )
        )
        self.register(
            MisconceptionDefinition(
                subject="mathematics",
                concept="algebra_equations",
                misconception_type="negative_sign_distribution",
                belief_description="Student fails to distribute a negative sign to all terms inside parentheses.",
                indicator_keywords=["forgot sign", "minus only first", "positive remaining"],
                anti_patterns=["-(x - 4) = -x - 4", "-(a + b) = -a + b"],
                severity="moderate",
                prerequisite_gap="distributive_property",
                default_strategy=TeachingStrategy.STEP_BY_STEP,
                analogy_hint="-(A - B) is multiplying both A and -B by -1, turning into -A + B.",
                remediation_template="When expanding -(A - B), distribute the negative sign to EVERY term inside: -1 * A = -A and -1 * (-B) = +B.",
            )
        )

        # 3. Programming
        self.register(
            MisconceptionDefinition(
                subject="programming",
                concept="python_basics",
                misconception_type="assignment_vs_equality",
                belief_description="Student confuses variable assignment '=' with boolean comparison '=='.",
                indicator_keywords=["single equals for check", "set equal", "condition uses ="],
                anti_patterns=["if x = 5", "comparing with single equal"],
                severity="moderate",
                prerequisite_gap="python_syntax_and_operators",
                default_strategy=TeachingStrategy.DIRECT_EXPLANATION,
                analogy_hint="'=' puts a value into a box; '==' asks if the box currently holds that value.",
                remediation_template="'=' is an assignment operator that assigns a value. '==' is a comparison operator that tests for equality.",
            )
        )
        self.register(
            MisconceptionDefinition(
                subject="programming",
                concept="python_basics",
                misconception_type="mutable_default_argument",
                belief_description="Student assumes default function parameters are evaluated on each call rather than at definition time.",
                indicator_keywords=["creates new list each time", "resets list", "fresh default"],
                anti_patterns=["new list is created every time function is called"],
                severity="severe",
                prerequisite_gap="python_object_mutability",
                default_strategy=TeachingStrategy.STEP_BY_STEP,
                analogy_hint="The default list is created once when the function is defined, so subsequent calls append to the same list.",
                remediation_template="In Python, default arguments are evaluated once when the function is defined. Use 'def fn(item, arr=None): if arr is None: arr = []'.",
            )
        )

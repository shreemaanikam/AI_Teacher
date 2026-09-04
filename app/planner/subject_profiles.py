"""
Subject-Aware Pedagogical Profiles for Module 4: AI Lesson Planner.
Defines domain-specific structural teaching flows without hardcoding individual lessons.
"""

from __future__ import annotations
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.harness.session import TeachingStrategy


class SubjectTeachingProfile(BaseModel):
    subject: str
    default_strategy: TeachingStrategy
    typical_sequence: List[str]  # e.g. ["intro", "formula", "visual", "example", "checkpoint"]
    primary_visual_type: str
    secondary_visual_type: str
    example_style: str
    question_format: str


SUBJECT_PROFILES: Dict[str, SubjectTeachingProfile] = {
    "physics": SubjectTeachingProfile(
        subject="physics",
        default_strategy=TeachingStrategy.DIRECT_EXPLANATION,
        typical_sequence=["intro", "core_concept", "formula", "circuit_or_physical_diagram", "worked_example", "checkpoint_question", "assessment"],
        primary_visual_type="circuit_diagram",
        secondary_visual_type="analogy_water_circuit",
        example_style="numerical_and_physical",
        question_format="conceptual_and_mcq",
    ),
    "mathematics": SubjectTeachingProfile(
        subject="mathematics",
        default_strategy=TeachingStrategy.STEP_BY_STEP,
        typical_sequence=["intro", "core_concept", "equation_derivation", "worked_example", "verification_problem", "checkpoint_question", "assessment"],
        primary_visual_type="plot_curve",
        secondary_visual_type="latex_card",
        example_style="step_by_step_algebraic",
        question_format="numerical",
    ),
    "programming": SubjectTeachingProfile(
        subject="programming",
        default_strategy=TeachingStrategy.EXAMPLE_FIRST,
        typical_sequence=["intro", "code_snippet", "execution_flow", "output_trace", "debugging_question", "checkpoint_question", "assessment"],
        primary_visual_type="code_block",
        secondary_visual_type="mermaid_diagram",
        example_style="syntax_and_runtime_trace",
        question_format="code_debugging_or_mcq",
    ),
    "biology": SubjectTeachingProfile(
        subject="biology",
        default_strategy=TeachingStrategy.VISUAL_EXPLANATION,
        typical_sequence=["intro", "core_concept", "process_diagram", "cellular_mechanisms", "checkpoint_question", "assessment"],
        primary_visual_type="mermaid_diagram",
        secondary_visual_type="svg_illustration",
        example_style="organism_and_cellular",
        question_format="process_recall_and_mcq",
    ),
    "history": SubjectTeachingProfile(
        subject="history",
        default_strategy=TeachingStrategy.CONTRASTIVE_EXPLANATION,
        typical_sequence=["intro", "timeline_context", "cause_and_effect", "primary_source_analysis", "checkpoint_question", "assessment"],
        primary_visual_type="mermaid_diagram",
        secondary_visual_type="timeline_chart",
        example_style="historical_case_study",
        question_format="cause_and_effect_inquiry",
    ),
    "chemistry": SubjectTeachingProfile(
        subject="chemistry",
        default_strategy=TeachingStrategy.DIRECT_EXPLANATION,
        typical_sequence=["intro", "core_concept", "reaction_equation", "molecular_structure", "worked_example", "checkpoint_question", "assessment"],
        primary_visual_type="latex_card",
        secondary_visual_type="mermaid_diagram",
        example_style="stoichiometric_and_atomic",
        question_format="reaction_balance_and_mcq",
    ),
}


def get_subject_profile(subject: str) -> SubjectTeachingProfile:
    """Returns specialized SubjectTeachingProfile or sensible STEM default."""
    subj_lower = subject.lower()
    return SUBJECT_PROFILES.get(
        subj_lower,
        SubjectTeachingProfile(
            subject=subj_lower,
            default_strategy=TeachingStrategy.DIRECT_EXPLANATION,
            typical_sequence=["intro", "core_concept", "worked_example", "checkpoint_question", "assessment"],
            primary_visual_type="latex_card",
            secondary_visual_type="mermaid_diagram",
            example_style="conceptual",
            question_format="conceptual",
        ),
    )

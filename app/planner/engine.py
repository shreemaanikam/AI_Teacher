"""
AI Lesson Planner Engine for Module 4.
Synthesizes TeachingRequest + RAG EvidencePackage + LearnerCognitiveState into a structured LessonPlan.
"""

from __future__ import annotations
import uuid
from typing import List, Dict, Optional

from app.planner.models import (
    LessonPlannerInput,
    LessonPlan,
    LessonSegment,
    VisualPlan,
    LearningObjectiveType,
    CompletionCriteria,
)
from app.planner.subject_profiles import get_subject_profile
from app.harness.session import TeachingStrategy
from app.input.models import LearnerLevel, TimeBudget
from app.rag.models import GroundingLevel


class LessonPlannerEngine:
    """
    Core planning engine that outputs deterministic, structured LessonPlans.
    """

    @classmethod
    def generate_plan(cls, plan_input: LessonPlannerInput) -> LessonPlan:
        """Constructs a fully structured, time-adapted, and RAG-grounded LessonPlan."""
        req = plan_input.teaching_request
        subject = req.subject
        profile = get_subject_profile(subject)
        topic = req.topic
        level = plan_input.educational_level
        objective = plan_input.learning_objective
        time_mins = plan_input.time_minutes
        evidence = plan_input.evidence_package

        # Determine difficulty base on learner level
        if level == LearnerLevel.ADVANCED:
            diff_level = 4
        elif level == LearnerLevel.INTERMEDIATE:
            diff_level = 3
        else:
            diff_level = 2

        # Extract evidence chunk IDs
        evidence_chunk_ids = [item.chunk_id for item in evidence.evidence_items] if evidence else []
        knowledge_conf = "HIGH"
        if evidence and evidence.grounding_level == GroundingLevel.UNSUPPORTED:
            knowledge_conf = "LOW"
        elif evidence and evidence.grounding_level == GroundingLevel.PARTIALLY_SUPPORTED:
            knowledge_conf = "MEDIUM"

        # Determine pedagogical strategy
        if req.teaching_style.value == "SIMPLE":
            base_strategy = TeachingStrategy.SIMPLE_ANALOGY if level == LearnerLevel.BEGINNER else TeachingStrategy.DIRECT_EXPLANATION
        elif req.teaching_style.value == "EXAM_FOCUSED":
            base_strategy = TeachingStrategy.STEP_BY_STEP
        elif req.teaching_style.value == "SOCRATIC":
            base_strategy = TeachingStrategy.SOCRATIC_QUESTIONING
        else:
            base_strategy = profile.default_strategy

        # Check if learner has a known effective strategy in cognitive profile
        if plan_input.learner_state:
            for s in plan_input.learner_state.strategy_history:
                if s.concept == topic and s.is_effective:
                    base_strategy = s.strategy
                    break

        segments: List[LessonSegment] = []
        visual_plans: List[VisualPlan] = []
        assessment_points: List[str] = []

        # ==========================================
        # TIME-AWARE TIMELINE GENERATION
        # ==========================================

        if time_mins <= 5:
            # 5-MINUTE SPRINT PLAN
            # 1. Intro & Core Concept
            seg1 = LessonSegment(
                concept=topic,
                purpose="intro_and_core",
                duration_minutes=2.5,
                teaching_strategy=base_strategy,
                explanation_goal=f"Fast concise overview of {topic}.",
                evidence_refs=evidence_chunk_ids[:1],
                visual_strategy=VisualPlan(
                    visual_type=profile.primary_visual_type,
                    purpose=f"Core visualization for {topic}",
                    concept=topic,
                ),
                difficulty=diff_level,
                knowledge_confidence=knowledge_conf,
            )
            segments.append(seg1)
            visual_plans.append(seg1.visual_strategy)

            # 2. Checkpoint Question & Quick Assessment
            seg2 = LessonSegment(
                concept=topic,
                purpose="checkpoint_question",
                duration_minutes=2.5,
                teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
                explanation_goal="Targeted checkpoint question to verify comprehension.",
                question_prompt=f"State the primary relationship or law governing {topic}.",
                question_type="conceptual",
                difficulty=diff_level,
                knowledge_confidence=knowledge_conf,
            )
            segments.append(seg2)
            assessment_points.append(seg2.segment_id)

        elif time_mins <= 25:
            # 20-MINUTE STANDARD LESSON PLAN
            # 1. Introduction & Motivation (3 mins)
            seg1 = LessonSegment(
                concept=topic,
                purpose="intro",
                duration_minutes=3.0,
                teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
                explanation_goal=f"Introduce real-world significance and motivation for {topic}.",
                evidence_refs=evidence_chunk_ids[:1],
                difficulty=diff_level - 1 if diff_level > 1 else 1,
                knowledge_confidence=knowledge_conf,
            )
            segments.append(seg1)

            # 2. Core Principles & Visual Demonstration (6 mins)
            v_plan = VisualPlan(
                visual_type=profile.primary_visual_type,
                purpose=f"Interactive schematic for {topic}",
                concept=topic,
                required_elements=["labels", "governing_variables", "flow_indicators"],
            )
            seg2 = LessonSegment(
                concept=topic,
                purpose="core_concept",
                duration_minutes=6.0,
                teaching_strategy=base_strategy,
                explanation_goal=f"Detailed pedagogical explanation of {topic} governing formulas and definitions.",
                evidence_refs=evidence_chunk_ids[:2],
                visual_strategy=v_plan,
                difficulty=diff_level,
                knowledge_confidence=knowledge_conf,
            )
            segments.append(seg2)
            visual_plans.append(v_plan)

            # 3. Formative Checkpoint Question (4 mins)
            seg3 = LessonSegment(
                concept=topic,
                purpose="checkpoint_question",
                duration_minutes=4.0,
                teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
                explanation_goal=f"Interactive checkpoint assessing foundational grasp of {topic}.",
                question_prompt=f"If the primary governing variable in {topic} changes, how is the output affected?",
                question_type="conceptual",
                difficulty=diff_level,
                knowledge_confidence=knowledge_conf,
            )
            segments.append(seg3)
            assessment_points.append(seg3.segment_id)

            # 4. Worked Example & Application (4 mins)
            seg4 = LessonSegment(
                concept=topic,
                purpose="worked_example",
                duration_minutes=4.0,
                teaching_strategy=TeachingStrategy.STEP_BY_STEP,
                explanation_goal=f"Step-by-step worked example problem applying {topic}.",
                evidence_refs=evidence_chunk_ids,
                difficulty=diff_level,
                knowledge_confidence=knowledge_conf,
            )
            segments.append(seg4)

            # 5. Final Assessment & Synthesis (3 mins)
            seg5 = LessonSegment(
                concept=topic,
                purpose="assessment",
                duration_minutes=3.0,
                teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
                explanation_goal=f"Final synthesis and mastery assessment for {topic}.",
                difficulty=diff_level,
                knowledge_confidence=knowledge_conf,
            )
            segments.append(seg5)
            assessment_points.append(seg5.segment_id)

        else:
            # 60-MINUTE DEEP DIVE PLAN
            # 1. Foundations & Prerequisites (8 mins)
            seg1 = LessonSegment(
                concept=f"{topic} Foundations",
                purpose="foundation",
                duration_minutes=8.0,
                teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
                explanation_goal=f"Review foundational prerequisites for {topic}.",
                difficulty=1,
                knowledge_confidence=knowledge_conf,
            )
            segments.append(seg1)

            # 2. Comprehensive Theory & Primary Visual (12 mins)
            v_plan1 = VisualPlan(
                visual_type=profile.primary_visual_type,
                purpose=f"Primary diagram for {topic}",
                concept=topic,
            )
            seg2 = LessonSegment(
                concept=topic,
                purpose="core_concept",
                duration_minutes=12.0,
                teaching_strategy=base_strategy,
                explanation_goal=f"In-depth mathematical and conceptual derivation of {topic}.",
                evidence_refs=evidence_chunk_ids,
                visual_strategy=v_plan1,
                difficulty=diff_level,
                knowledge_confidence=knowledge_conf,
            )
            segments.append(seg2)
            visual_plans.append(v_plan1)

            # 3. Checkpoint 1 (6 mins)
            seg3 = LessonSegment(
                concept=topic,
                purpose="checkpoint_question",
                duration_minutes=6.0,
                teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
                explanation_goal="First formative checkpoint question.",
                question_prompt=f"Analyze the relationship between key parameters in {topic}.",
                question_type="conceptual",
                difficulty=diff_level,
                knowledge_confidence=knowledge_conf,
            )
            segments.append(seg3)
            assessment_points.append(seg3.segment_id)

            # 4. Advanced Applications & Secondary Analogy (14 mins)
            v_plan2 = VisualPlan(
                visual_type=profile.secondary_visual_type,
                purpose=f"Secondary analogy visualization for {topic}",
                concept=topic,
            )
            seg4 = LessonSegment(
                concept=topic,
                purpose="advanced_applications",
                duration_minutes=14.0,
                teaching_strategy=TeachingStrategy.SIMPLE_ANALOGY,
                explanation_goal=f"Explore real-world industrial and laboratory applications of {topic}.",
                visual_strategy=v_plan2,
                difficulty=diff_level + 1,
                knowledge_confidence=knowledge_conf,
            )
            segments.append(seg4)
            visual_plans.append(v_plan2)

            # 5. Checkpoint 2: Problem Solving (10 mins)
            seg5 = LessonSegment(
                concept=topic,
                purpose="checkpoint_question",
                duration_minutes=10.0,
                teaching_strategy=TeachingStrategy.STEP_BY_STEP,
                explanation_goal="Quantitative and analytical problem solving checkpoint.",
                question_prompt=f"Solve a multi-step problem using {topic}.",
                question_type="numerical",
                difficulty=diff_level + 1,
                knowledge_confidence=knowledge_conf,
            )
            segments.append(seg5)
            assessment_points.append(seg5.segment_id)

            # 6. Summary & Revision (10 mins)
            seg6 = LessonSegment(
                concept=topic,
                purpose="summary",
                duration_minutes=10.0,
                teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
                explanation_goal="Comprehensive review of key takeaways and edge cases.",
                difficulty=diff_level,
                knowledge_confidence=knowledge_conf,
            )
            segments.append(seg6)
            assessment_points.append(seg6.segment_id)

        # Objective Customization (e.g. EXAM_PREPARATION or REVISION)
        if objective == LearningObjectiveType.EXAM_PREPARATION:
            for s in segments:
                if s.purpose == "worked_example":
                    s.explanation_goal += " Focus on high-yield exam patterns and common scoring pitfalls."
        elif objective == LearningObjectiveType.REVISION:
            for s in segments:
                s.duration_minutes = max(1.0, round(s.duration_minutes * 0.8, 1))

        return LessonPlan(
            title=f"Adaptive Lesson: {topic}",
            subject=subject,
            objective=objective,
            estimated_duration_minutes=time_mins,
            concepts=req.concepts_list or [topic],
            segments=segments,
            assessment_points=assessment_points,
            visual_plan=visual_plans,
            language=req.requested_language,
            educational_level=level,
            difficulty=diff_level,
            is_grounded=(knowledge_conf != "LOW"),
            completion_criteria=CompletionCriteria(
                minimum_mastery=0.80 if level == LearnerLevel.ADVANCED else 0.70,
                max_unresolved_misconceptions=0,
                required_questions_passed=len(assessment_points),
            ),
        )

"""
Input Normalization Engine for Module 1: Student & Input Intelligence.
Transforms raw client requests into a normalized, strongly-typed TeachingRequest.
"""

from __future__ import annotations
import os
import uuid
from typing import Dict, Any, Optional, List

from app.input.models import (
    TeachingRequest,
    LearnerProfile,
    LearnerLevel,
    TimeBudget,
    TeachingStyle,
    QuestionPreferenceType,
    UploadedDocumentMetadata,
)
from app.input.validator import InputSecurityValidator
from app.input.topic_detector import TopicDetector


class InputNormalizer:
    """Normalizes raw input forms, topics, or uploaded files into a unified TeachingRequest."""

    TIME_MINUTES_MAP = {
        TimeBudget.FIVE_MIN: 5,
        TimeBudget.TWENTY_MIN: 20,
        TimeBudget.SIXTY_MIN: 60,
        TimeBudget.CUSTOM: 20,
    }

    @classmethod
    def normalize_direct_topic(
        cls,
        topic: str,
        subject: Optional[str] = None,
        learner_profile: Optional[LearnerProfile] = None,
        language: str = "en",
        time_budget: TimeBudget = TimeBudget.TWENTY_MIN,
        custom_time_minutes: Optional[int] = None,
        educational_level: LearnerLevel = LearnerLevel.BEGINNER,
        teaching_style: TeachingStyle = TeachingStyle.SIMPLE,
        learning_objective: Optional[str] = None,
    ) -> TeachingRequest:
        """Normalizes a direct topic request."""
        clean_topic = InputSecurityValidator.sanitize_text_input(topic, max_length=150)
        if not clean_topic:
            clean_topic = "Foundational Scientific Principles"

        # If subject not specified, detect from topic text
        if not subject or subject == "general":
            detection = TopicDetector.detect_from_text(clean_topic, fallback_title=clean_topic)
            final_subject = detection.detected_subject
            candidate_concepts = detection.candidate_concepts
        else:
            final_subject = subject.lower()
            candidate_concepts = [clean_topic]

        # Calculate time in minutes
        if time_budget == TimeBudget.CUSTOM and custom_time_minutes:
            minutes = max(1, min(120, custom_time_minutes))
        else:
            minutes = cls.TIME_MINUTES_MAP.get(time_budget, 20)

        profile = learner_profile or LearnerProfile(
            educational_level=educational_level,
            preferred_language=language,
            teaching_style=teaching_style,
            available_time=time_budget,
            custom_time_minutes=minutes,
            subject=final_subject,
        )

        return TeachingRequest(
            learner_id=profile.learner_id,
            source_type="direct_topic",
            source_reference=None,
            topic=clean_topic,
            subject=final_subject,
            chapter=None,
            concepts_list=candidate_concepts,
            requested_language=language,
            material_language=language,
            learner_level=profile.educational_level,
            available_time=time_budget,
            time_minutes=minutes,
            learning_objective=learning_objective or f"Understand core concepts of {clean_topic}",
            teaching_style=profile.teaching_style,
            desired_depth=profile.desired_depth,
            requested_question_types=profile.preferred_question_types,
            learner_profile=profile,
        )

    @classmethod
    def normalize_document_upload(
        cls,
        document_metadata: UploadedDocumentMetadata,
        extracted_text_sample: str = "",
        learner_profile: Optional[LearnerProfile] = None,
        requested_language: str = "en",
        time_budget: TimeBudget = TimeBudget.TWENTY_MIN,
        custom_time_minutes: Optional[int] = None,
        teaching_style: TeachingStyle = TeachingStyle.SIMPLE,
    ) -> TeachingRequest:
        """Normalizes a document upload into a TeachingRequest."""
        detection = TopicDetector.detect_from_text(
            extracted_text_sample or document_metadata.original_filename,
            fallback_title=document_metadata.detected_title or document_metadata.original_filename,
        )

        minutes = custom_time_minutes if (time_budget == TimeBudget.CUSTOM and custom_time_minutes) else cls.TIME_MINUTES_MAP.get(time_budget, 20)

        profile = learner_profile or LearnerProfile(
            preferred_language=requested_language,
            material_language=document_metadata.detected_language,
            teaching_style=teaching_style,
            available_time=time_budget,
            custom_time_minutes=minutes,
            subject=detection.detected_subject,
        )

        return TeachingRequest(
            learner_id=profile.learner_id,
            source_type="uploaded_document",
            source_reference=document_metadata.document_id,
            topic=detection.detected_topic,
            subject=detection.detected_subject,
            chapter=detection.detected_chapter,
            concepts_list=detection.candidate_concepts,
            requested_language=requested_language,
            material_language=document_metadata.detected_language,
            learner_level=profile.educational_level,
            available_time=time_budget,
            time_minutes=minutes,
            learning_objective=f"Master key concepts from {detection.detected_topic}",
            teaching_style=profile.teaching_style,
            desired_depth=profile.desired_depth,
            requested_question_types=profile.preferred_question_types,
            learner_profile=profile,
        )

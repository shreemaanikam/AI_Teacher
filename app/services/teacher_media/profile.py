"""
Male Teacher Profile Configuration and State Enums.
Defines the canonical photorealistic adult male AI professor configuration.
"""

from enum import Enum
from typing import Dict, Any, List
from pydantic import BaseModel, Field


class TeacherState(str, Enum):
    INTRODUCING = "INTRODUCING"
    EXPLAINING = "EXPLAINING"
    POINTING = "POINTING"
    THINKING = "THINKING"
    ASKING = "ASKING"
    LISTENING = "LISTENING"
    EVALUATING = "EVALUATING"
    CORRECTING = "CORRECTING"
    ENCOURAGING = "ENCOURAGING"
    CELEBRATING = "CELEBRATING"


class MaleTeacherProfile(BaseModel):
    teacher_id: str = "male_professor_01"
    name: str = "Prof. Richard Davies"
    gender: str = "male"
    style: str = "photorealistic"
    role: str = "college professor"
    title: str = "Department of Applied Physics & Engineering"
    appearance: str = "Distinguished 45-year-old adult male professor with glasses, navy blazer, collared shirt, intelligent and warm demeanor"
    voice: str = "natural adult male educational voice"
    voice_id: str = "Daniel"  # High quality educational voice (macOS say / Kokoro am_michael)
    voice_sample_rate: int = 24000
    portrait_uri: str = "/teacher/male_professor_01.jpg"
    fallback_mode: str = "photorealistic_portrait_audio"
    supported_states: List[TeacherState] = list(TeacherState)
    
    state_cues: Dict[TeacherState, Dict[str, Any]] = {
        TeacherState.INTRODUCING: {
            "description": "Welcoming students to the lecture hall with confident, friendly eye contact",
            "head_tilt": 0.0,
            "expression": "warm_greeting",
            "gesture": "open_hands",
            "whiteboard_action": "title_focus"
        },
        TeacherState.EXPLAINING: {
            "description": "Active lecture mode with natural eye blinks and synchronized speech visemes",
            "head_tilt": 0.5,
            "expression": "focused_teaching",
            "gesture": "conversational_emphasis",
            "whiteboard_action": "highlight_concept"
        },
        TeacherState.POINTING: {
            "description": "Directing student focus to the whiteboard diagram or equation",
            "head_tilt": -1.5,
            "expression": "attentive_direction",
            "gesture": "point_to_board",
            "whiteboard_action": "laser_pointer"
        },
        TeacherState.THINKING: {
            "description": "Pondering an intuitive analogy or considering student perspective",
            "head_tilt": 2.0,
            "expression": "reflective",
            "gesture": "chin_touch",
            "whiteboard_action": "fade_secondary"
        },
        TeacherState.ASKING: {
            "description": "Posing a diagnostic conceptual checkpoint to the class",
            "head_tilt": 1.0,
            "expression": "inquisitive",
            "gesture": "open_query",
            "whiteboard_action": "question_box"
        },
        TeacherState.LISTENING: {
            "description": "Listening attentively during student doubt interruption",
            "head_tilt": 1.5,
            "expression": "patient_attentive",
            "gesture": "nodding",
            "whiteboard_action": "pause_highlight"
        },
        TeacherState.EVALUATING: {
            "description": "Analyzing student response for misconceptions and evidence",
            "head_tilt": 0.0,
            "expression": "analytical",
            "gesture": "deliberate",
            "whiteboard_action": "contrast_diagram"
        },
        TeacherState.CORRECTING: {
            "description": "Gently clarifying an invalid intuitive assumption with contrastive example",
            "head_tilt": -0.5,
            "expression": "empathetic_correction",
            "gesture": "remedial_guidance",
            "whiteboard_action": "show_correct_formula"
        },
        TeacherState.ENCOURAGING: {
            "description": "Motivating learner when working through challenging derivation",
            "head_tilt": 0.8,
            "expression": "encouraging_smile",
            "gesture": "open_nod",
            "whiteboard_action": "step_guide"
        },
        TeacherState.CELEBRATING: {
            "description": "Celebrating concept mastery with warm affirmation and nod",
            "head_tilt": 0.0,
            "expression": "pleased_affirmative",
            "gesture": "celebratory_thumbs_up",
            "whiteboard_action": "mastery_badge"
        }
    }


# Singleton default configuration
DEFAULT_MALE_TEACHER = MaleTeacherProfile()

"""
Lesson Segment Manager for Multi-Part College Teaching.
Tracks short, focused pedagogical segments with precise start/end timestamps,
source grounding, and synchronized visual board states.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from .profile import TeacherState, DEFAULT_MALE_TEACHER


class LessonSegment(BaseModel):
    segment_id: str
    lesson_id: str
    course_id: str = "physics_101"
    teacher_id: str = "male_professor_01"
    title: str
    script: str
    source_citations: List[str] = Field(default_factory=list)
    teacher_state: TeacherState = TeacherState.EXPLAINING
    audio_path: Optional[str] = None
    video_path: Optional[str] = None
    visual_id: str = ""
    duration: float = 0.0
    start_time: float = 0.0
    end_time: float = 0.0
    is_cached: bool = False
    whiteboard_data: Dict[str, Any] = Field(default_factory=dict)


class LessonSegmentManager:
    def __init__(self):
        self._segments: Dict[str, List[LessonSegment]] = {}

    def register_segments(self, lesson_id: str, segments: List[LessonSegment]):
        current_time = 0.0
        for seg in segments:
            seg.start_time = round(current_time, 2)
            seg.end_time = round(current_time + seg.duration, 2)
            current_time = seg.end_time
        self._segments[lesson_id] = segments

    def get_segments(self, lesson_id: str) -> List[LessonSegment]:
        return self._segments.get(lesson_id, [])

    def get_segment_by_timestamp(self, lesson_id: str, timestamp: float) -> Optional[LessonSegment]:
        for seg in self.get_segments(lesson_id):
            if seg.start_time <= timestamp <= seg.end_time:
                return seg
        return None

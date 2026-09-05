"""
Abstract Base Class for Teacher Avatar Providers.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any
import numpy as np
from ..profile import TeacherState


class BaseAvatarProvider(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def generate_video_frames(
        self,
        duration_seconds: float,
        fps: int = 24,
        teacher_state: TeacherState = TeacherState.EXPLAINING
    ) -> List[np.ndarray]:
        """Generates a list of BGR video frames for the teacher avatar."""
        pass

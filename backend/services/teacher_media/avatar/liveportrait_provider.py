"""
LivePortrait Avatar Provider.
Interfaces with hosted LivePortrait API (e.g. Fal.ai / Segmind / Replicate)
or local LivePortrait inference pipeline when configured.
"""

import os
from typing import List
import numpy as np
from .base import BaseAvatarProvider
from ..profile import TeacherState


class LivePortraitProvider(BaseAvatarProvider):
    def __init__(self, api_key: str = None, api_url: str = None):
        self.api_key = api_key or os.environ.get("LIVEPORTRAIT_API_KEY")
        self.api_url = api_url or os.environ.get("LIVEPORTRAIT_API_URL")

    def is_available(self) -> bool:
        # Check if liveportrait is enabled via explicit environment variable or API key
        if os.environ.get("LIVEPORTRAIT_ENABLED", "false").lower() == "true" and self.api_key:
            return True
        # Check if local liveportrait directory with weights exists
        if os.path.exists("models/liveportrait"):
            return True
        return False

    def generate_video_frames(
        self,
        duration_seconds: float,
        fps: int = 24,
        teacher_state: TeacherState = TeacherState.EXPLAINING
    ) -> List[np.ndarray]:
        if not self.is_available():
            raise RuntimeError("LivePortrait is not configured or unavailable. Use fallback.")
        
        # Hosted API execution if configured
        import requests
        # In case API is active, fetch resulting video frames...
        # If API times out or fails, raise error so factory falls back gracefully
        raise NotImplementedError("LivePortrait hosted session not initialized.")

"""
Base classes and interfaces for Avatar Providers.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional
from app.media.models import TeachingScript, AudioAsset, AvatarAsset


class AvatarProviderType(str, Enum):
    NEURAL_AVATAR = "NEURAL_AVATAR"
    PROCEDURAL_SVG = "PROCEDURAL_SVG"


class AvatarProvider(ABC):
    """Abstract interface for video/avatar presenters."""

    @abstractmethod
    def generate_avatar(
        self,
        script: TeachingScript,
        audio: AudioAsset,
        presenter_style: str = "academic_mentor",
        visual_context: Optional[str] = None,
    ) -> AvatarAsset:
        """Generates video or animated avatar presenter asset."""
        pass

    @abstractmethod
    def get_supported_styles(self) -> List[str]:
        pass

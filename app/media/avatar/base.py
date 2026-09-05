"""
Base classes and interfaces for Avatar Providers.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional
from app.media.models import TeachingScript, AudioAsset, AvatarAsset


class AvatarProviderType(str, Enum):
    DID_AVATAR = "DID_AVATAR"
    CANVAS_AVATAR = "CANVAS_AVATAR"
    FALLBACK_CARD = "FALLBACK_CARD"
    NEURAL_AVATAR = "NEURAL_AVATAR"
    PROCEDURAL_SVG = "PROCEDURAL_SVG"


class HumanAvatarProvider(ABC):
    """Abstract interface for human-like AI teacher avatar presenters."""

    @abstractmethod
    def generate_avatar(
        self,
        script: TeachingScript,
        audio: AudioAsset,
        presenter_style: str = "prof_apurva",
        visual_context: Optional[str] = None,
    ) -> AvatarAsset:
        """Generates video or animated avatar presenter asset."""
        pass

    @abstractmethod
    def get_supported_styles(self) -> List[str]:
        pass


AvatarProvider = HumanAvatarProvider


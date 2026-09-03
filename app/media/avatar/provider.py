"""
Avatar Provider interface for Module 9 (Voice + Avatar + Video Engine).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from app.media.models import AvatarAsset, TeachingScript, AudioAsset


class AvatarProvider(ABC):
    """Abstract interface for AI teacher avatar generation."""

    @abstractmethod
    def generate_avatar(
        self,
        script: TeachingScript,
        audio: Optional[AudioAsset] = None,
        presenter_style: str = "academic_mentor",
    ) -> AvatarAsset:
        """Generates the avatar presenter video or animation asset."""
        pass

    @abstractmethod
    def get_available_presenters(self) -> List[Dict[str, str]]:
        pass

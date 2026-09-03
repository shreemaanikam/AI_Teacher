"""
Factory for Avatar Presenter Providers.
"""

from __future__ import annotations
import os
from typing import Optional
from app.media.avatar.base import AvatarProvider, AvatarProviderType
from app.media.avatar.neural_avatar import NeuralAvatarProvider
from app.media.avatar.procedural_avatar import ProceduralAvatarProvider


def get_avatar_provider(prefer_neural: bool = True) -> AvatarProvider:
    """
    Returns the appropriate AvatarProvider.
    If prefer_neural is True and an API key is available in environment, returns NeuralAvatarProvider.
    Otherwise returns ProceduralAvatarProvider.
    """
    has_key = bool(os.getenv("AVATAR_API_KEY") or os.getenv("HEYGEN_API_KEY"))
    if prefer_neural and has_key:
        return NeuralAvatarProvider()
    return ProceduralAvatarProvider()

"""
Avatar Presenter Package for Module 9.
"""

from app.media.avatar.base import AvatarProvider, AvatarProviderType
from app.media.avatar.procedural_avatar import ProceduralAvatarProvider
from app.media.avatar.neural_avatar import NeuralAvatarProvider
from app.media.avatar.factory import get_avatar_provider

__all__ = [
    "AvatarProvider",
    "AvatarProviderType",
    "ProceduralAvatarProvider",
    "NeuralAvatarProvider",
    "get_avatar_provider",
]

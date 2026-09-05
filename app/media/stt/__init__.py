"""
Speech-to-Text package for Module 9.
"""
from app.media.stt.base import STTProvider
from app.media.stt.openai_stt import OpenAISTTProvider
from app.media.stt.local_stt import LocalSTTProvider
from app.media.stt.factory import get_stt_provider

__all__ = ["STTProvider", "OpenAISTTProvider", "LocalSTTProvider", "get_stt_provider"]

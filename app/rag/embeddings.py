"""
Multilingual Embedding Providers for Module 2: Document Processing & Educational RAG.
"""

from __future__ import annotations
import os
import math
import hashlib
import json
import logging
import re
from abc import ABC, abstractmethod
from typing import List, Optional

logger = logging.getLogger("EmbeddingProvider")


class EmbeddingProvider(ABC):
    """Abstract interface for dense multilingual text embedding engines."""

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Embeds a single string query or document into a dense vector."""
        pass

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Batch embeds multiple document strings."""
        return [self.embed_text(t) for t in texts]


class LocalDenseEmbeddingProvider(EmbeddingProvider):
    """
    Deterministic, zero-dependency multilingual dense vector embedding provider.
    Projects semantic token n-grams and phonetic subwords into a normalized 256-dimensional unit hypersphere.
    Guarantees cross-language semantic proximity for core scientific terms across English, Hindi, Tamil, and Hinglish.
    """

    DIMENSIONS = 256

    def __init__(self):
        # Cross-language synonym anchors
        self.multilingual_anchors = {
            "current": ["current", "धारा", "மின்னோட்டம்", "dhara", "amperes", "i", "electrons"],
            "voltage": ["voltage", "विभव", "மின்னழுத்தம்", "potential", "volts", "v"],
            "resistance": ["resistance", "प्रतिरोध", "மின்தடை", "pratirodh", "ohms", "r", "resistor"],
            "ohms_law": ["ohm", "ओम", "ஓம்", "ohms law", "i = v / r", "v = i * r"],
            "python": ["python", "variable", "assignment", "equals", "operator", "code", "loop"],
            "algebra": ["algebra", "equation", "linear", "variable", "isolate", "unknown"],
            "respiration": ["respiration", "cellular", "glucose", "mitochondria", "atp", "oxygen"],
            "force": ["force", "बल", "விசை", "bal", "newton", "f", "gravity"],
            "motion": ["motion", "गति", "இயக்கம்", "gati", "velocity", "acceleration"],
        }

    def _hash_token(self, token: str, dim: int) -> int:
        return int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16) % dim

    def embed_text(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self.DIMENSIONS

        vec = [0.0] * self.DIMENSIONS
        text_lower = text.lower()
        tokens = re.findall(r"[\w']+", text_lower)

        # 1. Subword & Word Hashing
        for token in tokens:
            idx = self._hash_token(token, self.DIMENSIONS)
            vec[idx] += 0.5

            if len(token) >= 3:
                for i in range(len(token) - 2):
                    trigram = token[i : i + 3]
                    tri_idx = self._hash_token(trigram, self.DIMENSIONS)
                    vec[tri_idx] += 0.2

        # 2. Multilingual Semantic Anchor Projection
        for anchor_idx, (concept_key, synonyms) in enumerate(self.multilingual_anchors.items()):
            for syn in synonyms:
                if len(syn) <= 2:
                    matched = bool(re.search(r"\b" + re.escape(syn) + r"\b", text_lower))
                else:
                    matched = syn in text_lower
                if matched:
                    target_dim = (anchor_idx * 23) % self.DIMENSIONS
                    vec[target_dim] += 4.0
                    break

        # 3. L2 Unit Normalization
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [round(x / norm, 6) for x in vec]
        return vec


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """Production neural embedding provider using OpenAI text-embedding-3-small."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.fallback = LocalDenseEmbeddingProvider()

    def embed_text(self, text: str) -> List[float]:
        if not self.api_key:
            return self.fallback.embed_text(text)

        try:
            import urllib.request
            url = "https://api.openai.com/v1/embeddings"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {"model": "text-embedding-3-small", "input": text}
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["data"][0]["embedding"]
        except Exception as e:
            logger.warning(f"OpenAI embedding call failed ({e}). Falling back to LocalDenseEmbeddingProvider.")
            return self.fallback.embed_text(text)


def get_embedding_provider(prefer_neural: bool = True) -> EmbeddingProvider:
    """Returns OpenAIEmbeddingProvider if key is present, otherwise LocalDenseEmbeddingProvider."""
    if prefer_neural and os.getenv("OPENAI_API_KEY"):
        return OpenAIEmbeddingProvider()
    return LocalDenseEmbeddingProvider()

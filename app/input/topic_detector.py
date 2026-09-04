"""
Heuristic and NLP Topic / Subject Detector for Module 1.
Extracts title, subject, chapter, and candidate concepts from text or document metadata without hallucination.
"""

from __future__ import annotations
import re
from typing import List, Optional
from app.input.models import TopicDetectionResult

SUBJECT_KEYWORDS = {
    "physics": ["current", "voltage", "resistance", "ohm", "circuit", "force", "velocity", "acceleration", "gravity", "energy", "wave", "thermodynamics", "optics", "charge", "magnet"],
    "mathematics": ["algebra", "equation", "calculus", "derivative", "integral", "matrix", "geometry", "triangle", "polynomial", "function", "theorem", "probability", "statistics"],
    "programming": ["python", "java", "javascript", "function", "variable", "array", "loop", "recursion", "class", "object", "algorithm", "data structure", "pointer", "syntax"],
    "biology": ["cell", "mitochondria", "respiration", "dna", "rna", "protein", "organism", "photosynthesis", "genetics", "evolution", "ecology", "enzyme", "membrane"],
    "chemistry": ["atom", "molecule", "reaction", "acid", "base", "periodic", "bond", "electron", "stoichiometry", "equilibrium", "thermodynamics", "organic", "polymer"],
}


class TopicDetector:
    """Infers subject category, main topic, and concepts from text excerpts or filenames."""

    @classmethod
    def detect_from_text(cls, text: str, fallback_title: Optional[str] = None) -> TopicDetectionResult:
        """Analyzes text to identify subject, topic, and concepts."""
        text_lower = text.lower().replace("_", " ").replace("-", " ")

        # 1. Subject Classification by keyword density
        subject_scores = {subj: 0 for subj in SUBJECT_KEYWORDS}
        for subj, keywords in SUBJECT_KEYWORDS.items():
            for kw in keywords:
                if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
                    subject_scores[subj] += 1
            if subj in text_lower:
                subject_scores[subj] += 2

        detected_subject = max(subject_scores, key=subject_scores.get)
        if subject_scores[detected_subject] == 0:
            detected_subject = "general_stem"

        # 2. Extract Document Title / Main Topic
        detected_topic = fallback_title or "Foundational Principles"
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for line in lines[:5]:
            if line.startswith("# "):
                detected_topic = line.replace("# ", "").strip()
                break
            elif "chapter" in line.lower() or "topic:" in line.lower() or "lesson:" in line.lower():
                detected_topic = line.split(":")[-1].strip()
                break
            elif len(line) < 60 and not line.endswith("."):
                detected_topic = line
                break

        # 3. Detect Chapters / Sections
        chapter_match = re.search(r"(?:Chapter|Unit|Module)\s*([0-9IVX]+[:\-]?\s*[A-Za-z0-9\s]+)", text, re.IGNORECASE)
        detected_chapter = chapter_match.group(0).strip() if chapter_match else None

        # 4. Extract Candidate Concepts
        candidate_concepts: List[str] = []
        concept_patterns = [
            r"(?:Concept|Principle|Law|Topic):\s*([A-Za-z0-9\s'-]+)",
            r"(?:Definition of|What is)\s+([A-Za-z0-9\s'-]+)\??",
            r"(?:Ohm's Law|Newton's Law|Gauss's Law|Faraday's Law)",
            r"(?:Variables|Loops|Functions|Recursion|Data Types)",
            r"(?:Cellular Respiration|Photosynthesis|Mitosis|Meiosis)",
        ]
        for pat in concept_patterns:
            matches = re.findall(pat, text, re.IGNORECASE)
            for m in matches:
                item = m.strip() if isinstance(m, str) else m[0].strip()
                if item and item.lower() not in [c.lower() for c in candidate_concepts]:
                    candidate_concepts.append(item)

        if not candidate_concepts:
            # Fallback based on subject keywords found
            found_kws = [kw.title() for kw in SUBJECT_KEYWORDS.get(detected_subject, []) if kw in text_lower]
            candidate_concepts = found_kws[:4] if found_kws else [detected_topic]

        return TopicDetectionResult(
            detected_topic=detected_topic,
            detected_subject=detected_subject,
            detected_chapter=detected_chapter,
            candidate_concepts=candidate_concepts,
            confidence=0.88 if subject_scores.get(detected_subject, 0) > 0 else 0.60,
            source="heuristic_analysis",
        )

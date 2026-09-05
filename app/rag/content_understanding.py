"""
Content Understanding Service for Next-Generation College AI Educator.
Transforms raw uploaded material (notes, PDFs, docs, presentations) or direct topic input
into an educational knowledge representation without assuming any single fixed subject or topic.
"""

from __future__ import annotations
import json
import os
import re
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.router.router import ModelRouter
from app.router.models import ModelRequest, TaskType, RoutingMode

# Academic Subject & Course Taxonomy
ACADEMIC_TAXONOMY = {
    "computer_science": {
        "canonical_name": "Computer Science",
        "keywords": [
            "data structure", "algorithm", "binary search", "tree", "graph", "recursion",
            "operating system", "process", "thread", "deadlock", "memory management",
            "dbms", "sql", "relational database", "normalization", "transaction",
            "computer network", "tcp", "udp", "ip address", "protocol", "packet",
            "python", "java", "c++", "pointer", "array", "linked list", "stack", "queue",
            "machine learning", "neural network", "deep learning", "supervised learning",
            "compiler", "automata", "turing machine", "complexity", "big-o", "time complexity"
        ],
        "default_course": "Data Structures & Algorithms"
    },
    "electronics_electrical": {
        "canonical_name": "Electronics & Electrical Engineering",
        "keywords": [
            "circuit", "voltage", "current", "resistance", "ohm's law", "kirchhoff",
            "inductor", "capacitor", "transistor", "diode", "op-amp", "semiconductor",
            "digital logic", "boolean algebra", "logic gate", "flip-flop", "multiplexer",
            "microprocessor", "microcontroller", "8085", "8086", "arm", "fpga",
            "signal", "fourier transform", "laplace", "modulation", "communication system"
        ],
        "default_course": "Circuit Theory & Electronic Devices"
    },
    "mathematics": {
        "canonical_name": "Mathematics",
        "keywords": [
            "calculus", "derivative", "integral", "limit", "differential equation",
            "linear algebra", "matrix", "vector", "eigenvalue", "determinant",
            "probability", "statistics", "random variable", "distribution", "bayes",
            "discrete mathematics", "set theory", "combinatorics", "graph theory",
            "polynomial", "geometry", "trigonometry", "proof", "theorem"
        ],
        "default_course": "College Calculus & Linear Algebra"
    },
    "physics": {
        "canonical_name": "Physics",
        "keywords": [
            "mechanics", "newton", "velocity", "acceleration", "force", "momentum", "friction",
            "work", "energy", "gravitation", "harmonic motion", "wave", "optics",
            "electromagnetism", "magnetic field", "electric field", "maxwell", "flux",
            "thermodynamics", "entropy", "heat transfer", "quantum", "photoelectric"
        ],
        "default_course": "University Physics"
    },
    "chemistry": {
        "canonical_name": "Chemistry",
        "keywords": [
            "organic chemistry", "inorganic", "physical chemistry", "molecule", "atom",
            "reaction", "stoichiometry", "chemical equilibrium", "acid", "base", "ph",
            "periodic table", "covalent bond", "ionic bond", "hybridization", "polymer",
            "electrochemistry", "redox", "kinetics", "catalyst"
        ],
        "default_course": "College Chemistry"
    },
    "biology": {
        "canonical_name": "Biology & Life Sciences",
        "keywords": [
            "cell biology", "mitochondria", "cell division", "mitosis", "meiosis",
            "genetics", "dna", "rna", "transcription", "translation", "mutation",
            "biochemistry", "enzyme", "protein synthesis", "respiration", "photosynthesis",
            "organism", "ecology", "evolution", "physiology", "immune system"
        ],
        "default_course": "Cellular Biology & Genetics"
    },
    "management_economics": {
        "canonical_name": "Business & Economics",
        "keywords": [
            "microeconomics", "macroeconomics", "supply and demand", "elasticity", "inflation",
            "gdp", "market structure", "monopoly", "competition", "finance", "accounting",
            "balance sheet", "income statement", "marketing", "management", "strategy"
        ],
        "default_course": "Principles of Economics"
    }
}


class CourseUnderstanding(BaseModel):
    """
    Normalized, structured representation of educational material or topic.
    Serves as the foundation for the entire college learning journey.
    """
    understanding_id: str = Field(default_factory=lambda: f"und_{uuid.uuid4().hex[:10]}")
    subject: str
    course: str
    topic: str
    chapter: Optional[str] = None
    unit: Optional[str] = None
    section: Optional[str] = None
    difficulty: str = "intermediate"  # beginner, intermediate, advanced
    chapters: List[Dict[str, Any]] = Field(default_factory=list)
    concepts: List[Dict[str, Any]] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    definitions: List[Dict[str, str]] = Field(default_factory=list)
    formulas: List[Dict[str, Any]] = Field(default_factory=list)
    examples: List[Dict[str, Any]] = Field(default_factory=list)
    problems: List[Dict[str, Any]] = Field(default_factory=list)
    important_topics: List[str] = Field(default_factory=list)
    practical_topics: List[str] = Field(default_factory=list)
    summary: str = ""
    source_type: str = "uploaded_material"  # uploaded_material | direct_topic
    source_title: str = ""
    source_reference: Optional[str] = None


class ContentUnderstandingService:
    """
    Intelligently analyzes any uploaded document, lecture notes, textbook excerpt,
    or direct topic statement to extract subject structure, concepts, and relationships.
    """

    def __init__(self, router: Optional[ModelRouter] = None):
        self.router = router or ModelRouter()

    def classify_subject_and_course(self, text: str, hint_title: Optional[str] = None) -> tuple[str, str]:
        """Classifies the academic subject and specific course from text analysis."""
        combined_text = f"{hint_title or ''} {text}".lower().replace("_", " ").replace("-", " ")
        scores = {}
        
        for key, data in ACADEMIC_TAXONOMY.items():
            score = 0
            for kw in data["keywords"]:
                if re.search(r"\b" + re.escape(kw) + r"\b", combined_text):
                    score += 2
            if key.replace("_", " ") in combined_text:
                score += 3
            scores[key] = score

        best_key = max(scores, key=scores.get) if scores and max(scores.values()) > 0 else "computer_science"
        subject_data = ACADEMIC_TAXONOMY[best_key]
        return subject_data["canonical_name"], subject_data["default_course"]

    def understand_content(
        self,
        text: str,
        filename: Optional[str] = None,
        subject_hint: Optional[str] = None,
        source_reference: Optional[str] = None,
    ) -> CourseUnderstanding:
        """
        Main entry point for understanding uploaded educational material.
        Uses AI-assisted extraction with structured JSON output, falling back to deep heuristics.
        """
        raw_text = text.strip()
        doc_title = (
            os.path.splitext(filename)[0].replace("_", " ").title()
            if filename
            else self._extract_first_heading(raw_text)
        )

        detected_subject, default_course = self.classify_subject_and_course(raw_text, hint_title=doc_title)
        if subject_hint:
            detected_subject = subject_hint

        # Attempt high-intelligence structured extraction via LLM if text is substantial
        if len(raw_text) > 80:
            ai_result = self._extract_with_llm(raw_text, doc_title, detected_subject)
            if ai_result:
                ai_result.source_type = "uploaded_material"
                ai_result.source_title = doc_title
                ai_result.source_reference = source_reference
                return ai_result

        # Robust deterministic heuristic extraction
        return self._extract_with_heuristics(
            text=raw_text,
            doc_title=doc_title,
            subject=detected_subject,
            course=default_course,
            source_reference=source_reference,
        )

    def understand_topic(self, topic: str, context: Optional[str] = None) -> CourseUnderstanding:
        """
        Generates comprehensive course structure for direct topic inputs (e.g. 'Operating Systems Unit 3').
        """
        clean_topic = topic.strip()
        combined_text = f"{clean_topic} {context or ''}"
        detected_subject, default_course = self.classify_subject_and_course(combined_text, hint_title=clean_topic)

        # Attempt structured AI generation for the topic
        ai_prompt = (
            f"Generate an academic curriculum understanding for the college topic: '{clean_topic}'.\n"
            f"Subject field: {detected_subject}.\n"
            "Return a clean JSON object adhering to this schema:\n"
            "{\n"
            '  "subject": "string",\n'
            '  "course": "string",\n'
            '  "topic": "string",\n'
            '  "chapter": "string",\n'
            '  "difficulty": "beginner | intermediate | advanced",\n'
            '  "concepts": [\n'
            '    {"name": "string", "description": "string", "prerequisites": ["string"], "definitions": ["string"], "formulas": ["string"], "examples": ["string"], "practical_application": "string"}\n'
            "  ],\n"
            '  "prerequisites": ["string"],\n'
            '  "important_topics": ["string"],\n'
            '  "practical_topics": ["string"],\n'
            '  "summary": "string"\n'
            "}"
        )

        try:
            req = ModelRequest(task_type=TaskType.LESSON_PLANNING, prompt=ai_prompt, routing_mode=RoutingMode.FAST)
            raw_response = self.router.execute(req)
            parsed = self._parse_json_block(raw_response)
            if parsed and "concepts" in parsed and len(parsed["concepts"]) > 0:
                return CourseUnderstanding(
                    subject=parsed.get("subject", detected_subject),
                    course=parsed.get("course", default_course),
                    topic=clean_topic,
                    chapter=parsed.get("chapter", f"Unit on {clean_topic}"),
                    difficulty=parsed.get("difficulty", "intermediate"),
                    concepts=parsed.get("concepts", []),
                    prerequisites=parsed.get("prerequisites", []),
                    important_topics=parsed.get("important_topics", []),
                    practical_topics=parsed.get("practical_topics", []),
                    summary=parsed.get("summary", f"College curriculum for {clean_topic}"),
                    source_type="direct_topic",
                    source_title=clean_topic,
                )
        except Exception:
            pass

        # Fallback deterministic topic expansion
        return self._build_deterministic_topic_understanding(clean_topic, detected_subject, default_course)

    def _extract_with_llm(self, text: str, doc_title: str, subject: str) -> Optional[CourseUnderstanding]:
        """Extracts structured curriculum representation using AI Model Router."""
        prompt = (
            f"Analyze the following college learning material titled '{doc_title}' ({subject}):\n\n"
            f"{text[:3000]}\n\n"
            "Extract a comprehensive educational structure. Output STRICT JSON with no markdown wrapping:\n"
            "{\n"
            '  "subject": "string",\n'
            '  "course": "string",\n'
            '  "topic": "string",\n'
            '  "chapter": "string or null",\n'
            '  "unit": "string or null",\n'
            '  "difficulty": "beginner | intermediate | advanced",\n'
            '  "chapters": [\n'
            '    {"title": "string", "sections": [{"title": "string", "concepts": ["string"]}]}\n'
            "  ],\n"
            '  "concepts": [\n'
            '    {"name": "string", "description": "string", "prerequisites": ["string"], "definitions": ["string"], "formulas": ["string"], "examples": ["string"], "practical_application": "string"}\n'
            "  ],\n"
            '  "prerequisites": ["string"],\n'
            '  "definitions": [{"term": "string", "definition": "string"}],\n'
            '  "formulas": [{"name": "string", "expression": "string", "variables": "string"}],\n'
            '  "examples": [{"title": "string", "content": "string"}],\n'
            '  "problems": [{"question": "string", "answer": "string"}],\n'
            '  "important_topics": ["string"],\n'
            '  "practical_topics": ["string"],\n'
            '  "summary": "string"\n'
            "}"
        )

        try:
            req = ModelRequest(task_type=TaskType.SUMMARIZATION, prompt=prompt, routing_mode=RoutingMode.FAST)
            raw_response = self.router.execute(req)
            parsed = self._parse_json_block(raw_response)
            if parsed and "concepts" in parsed and len(parsed["concepts"]) > 0:
                return CourseUnderstanding(
                    subject=parsed.get("subject", subject),
                    course=parsed.get("course", f"{subject} Studies"),
                    topic=parsed.get("topic", doc_title),
                    chapter=parsed.get("chapter"),
                    unit=parsed.get("unit"),
                    difficulty=parsed.get("difficulty", "intermediate"),
                    chapters=parsed.get("chapters", []),
                    concepts=parsed.get("concepts", []),
                    prerequisites=parsed.get("prerequisites", []),
                    definitions=parsed.get("definitions", []),
                    formulas=parsed.get("formulas", []),
                    examples=parsed.get("examples", []),
                    problems=parsed.get("problems", []),
                    important_topics=parsed.get("important_topics", []),
                    practical_topics=parsed.get("practical_topics", []),
                    summary=parsed.get("summary", f"Study material for {doc_title}"),
                )
        except Exception:
            return None
        return None

    def _extract_with_heuristics(
        self,
        text: str,
        doc_title: str,
        subject: str,
        course: str,
        source_reference: Optional[str] = None,
    ) -> CourseUnderstanding:
        """Deep deterministic extraction parsing chapters, sections, formulas, code, and definitions."""
        lines = text.splitlines()
        
        detected_chapters = []
        detected_concepts = []
        detected_definitions = []
        detected_formulas = []
        detected_examples = []
        detected_problems = []
        important_topics = []
        practical_topics = []

        current_ch_title = None
        current_sec_title = "Overview"
        current_sec_concepts = []

        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue

            # Detect Chapters or Units (# Chapter ... / Unit ...)
            if re.match(r"^#+\s*(?:Chapter|Unit|Module)\s*([0-9IVX]+[:\-\s]*)", trimmed, re.IGNORECASE) or (trimmed.startswith("# ") and len(trimmed) < 60):
                if current_ch_title:
                    detected_chapters.append({
                        "title": current_ch_title,
                        "sections": [{"title": current_sec_title, "concepts": current_sec_concepts}]
                    })
                    current_sec_concepts = []
                current_ch_title = re.sub(r"^#+\s*", "", trimmed).strip()
                continue

            # Detect Section headers (## ...)
            if trimmed.startswith("## ") or re.match(r"^Section\s+[0-9.]+", trimmed, re.IGNORECASE):
                sec_name = re.sub(r"^#+\s*", "", trimmed).strip()
                current_sec_title = sec_name
                important_topics.append(sec_name)
                continue

            # Detect Concepts (### ... or bold bullet points)
            if trimmed.startswith("### ") or re.match(r"^[-*]\s+\*\*([A-Za-z0-9\s_-]+)\*\*", trimmed):
                cname_match = re.search(r"\*\*([A-Za-z0-9\s_-]+)\*\*", trimmed)
                cname = cname_match.group(1).strip() if cname_match else re.sub(r"^#+\s*", "", trimmed).strip()
                if cname and len(cname) < 50:
                    current_sec_concepts.append(cname)
                    detected_concepts.append({
                        "name": cname,
                        "description": f"Core concept in {subject}: {cname}",
                        "prerequisites": [],
                        "definitions": [],
                        "formulas": [],
                        "examples": [],
                        "practical_application": f"Applied in {subject} real-world implementations."
                    })
                continue

            # Detect Definitions ("term is defined as...", "Definition: ...")
            def_match = re.search(r"(?:Definition|Define)\s*[:\-]\s*(.+)", trimmed, re.IGNORECASE) or re.search(r"(\b[A-Za-z\s]{3,25}\b)\s+is defined as\s+(.+)", trimmed, re.IGNORECASE)
            if def_match:
                term = def_match.group(1).strip()
                dtext = def_match.group(2).strip() if len(def_match.groups()) > 1 else def_match.group(1).strip()
                detected_definitions.append({"term": term, "definition": dtext})

            # Detect Formulas / Equations ("V = I * R", "f(x) = ...", "O(log n)")
            formula_match = re.search(r"([A-Za-z\(\)]+\s*=\s*[^;\n]{3,40})", trimmed)
            if formula_match and not re.search(r"[a-z]\s+=\s+[a-z]\s+and", trimmed):
                detected_formulas.append({
                    "name": f"Equation from {current_sec_title}",
                    "expression": formula_match.group(1).strip(),
                    "variables": "Identified in context"
                })

            # Detect Code snippets or practical algorithms
            if "def " in trimmed or "public class " in trimmed or "for (" in trimmed or "while (" in trimmed:
                practical_topics.append(f"Algorithm Implementation ({current_sec_title})")

            # Detect Examples & Problems
            if re.match(r"^(?:Example|Worked Example|Problem)\s*[0-9.:]*", trimmed, re.IGNORECASE):
                detected_examples.append({"title": trimmed[:50], "content": trimmed})

        # Append trailing chapter
        if current_ch_title:
            detected_chapters.append({
                "title": current_ch_title,
                "sections": [{"title": current_sec_title, "concepts": current_sec_concepts}]
            })
        elif not detected_chapters:
            detected_chapters.append({
                "title": f"Chapter 1: {doc_title}",
                "sections": [{"title": "Core Foundations", "concepts": [c["name"] for c in detected_concepts]}]
            })

        # Ensure concepts exist even from unstructured text
        if not detected_concepts:
            for kw in ACADEMIC_TAXONOMY.get(subject.lower().replace(" ", "_"), {}).get("keywords", []):
                if kw in text.lower():
                    detected_concepts.append({
                        "name": kw.title(),
                        "description": f"Essential concept of {kw.title()} in {subject}",
                        "prerequisites": [],
                        "definitions": [],
                        "formulas": [],
                        "examples": [],
                        "practical_application": f"Industrial implementation of {kw}."
                    })
                if len(detected_concepts) >= 4:
                    break

        if not detected_concepts:
            detected_concepts.append({
                "name": doc_title,
                "description": f"Foundational study of {doc_title}",
                "prerequisites": [],
                "definitions": [],
                "formulas": [],
                "examples": [],
                "practical_application": "Core conceptual foundation."
            })

        return CourseUnderstanding(
            subject=subject,
            course=course,
            topic=doc_title,
            chapter=detected_chapters[0]["title"] if detected_chapters else f"Unit on {doc_title}",
            difficulty="intermediate",
            chapters=detected_chapters,
            concepts=detected_concepts,
            prerequisites=[f"Basic foundation in {subject}"],
            definitions=detected_definitions,
            formulas=detected_formulas,
            examples=detected_examples,
            problems=detected_problems,
            important_topics=important_topics[:5] if important_topics else [c["name"] for c in detected_concepts[:4]],
            practical_topics=practical_topics[:4] if practical_topics else [f"Hands-on practice in {doc_title}"],
            summary=f"Curriculum extract covering {len(detected_concepts)} concepts for {doc_title}.",
            source_type="uploaded_material",
            source_title=doc_title,
            source_reference=source_reference,
        )

    def _build_deterministic_topic_understanding(self, topic: str, subject: str, course: str) -> CourseUnderstanding:
        """Deterministic topic generator for direct topic queries."""
        concepts = [
            {
                "name": f"{topic} Core Principles",
                "description": f"Primary theoretical foundations and definitions of {topic}.",
                "prerequisites": [f"Introduction to {subject}"],
                "definitions": [{"term": topic, "definition": f"Core subject matter of {topic} in {subject}."}],
                "formulas": [],
                "examples": [{"title": f"Introductory Example of {topic}", "content": f"Standard textbook case study in {topic}."}],
                "practical_application": f"Applied in real-world {subject} problem-solving."
            },
            {
                "name": f"{topic} Mechanisms & Operations",
                "description": f"Detailed step-by-step mechanisms, algorithms, or equations governing {topic}.",
                "prerequisites": [f"{topic} Core Principles"],
                "definitions": [],
                "formulas": [],
                "examples": [],
                "practical_application": f"Practical execution and troubleshooting of {topic}."
            }
        ]

        return CourseUnderstanding(
            subject=subject,
            course=course,
            topic=topic,
            chapter=f"Unit: {topic}",
            difficulty="intermediate",
            chapters=[{
                "title": f"Unit: {topic}",
                "sections": [{"title": "Fundamental Concepts", "concepts": [c["name"] for c in concepts]}]
            }],
            concepts=concepts,
            prerequisites=[f"Basic prerequisite knowledge in {subject}"],
            important_topics=[f"{topic} Fundamentals", f"{topic} Exam Scenarios"],
            practical_topics=[f"Problem Solving in {topic}"],
            summary=f"Structured college learning path for {topic}.",
            source_type="direct_topic",
            source_title=topic,
        )

    def _extract_first_heading(self, text: str) -> str:
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("# "):
                return line.replace("# ", "").strip()
            elif len(line) < 50 and not line.endswith("."):
                return line
        return "College Learning Material"

    def _parse_json_block(self, text: str) -> Optional[Dict[str, Any]]:
        """Safely parses JSON from an LLM response even with surrounding text or markdown ticks."""
        clean = text.strip()
        if "```json" in clean:
            match = re.search(r"```json\s*(.*?)\s*```", clean, re.DOTALL)
            if match:
                clean = match.group(1).strip()
        elif "```" in clean:
            match = re.search(r"```\s*(.*?)\s*```", clean, re.DOTALL)
            if match:
                clean = match.group(1).strip()

        try:
            return json.loads(clean)
        except Exception:
            # Fallback: search for first { and last }
            brace_match = re.search(r"(\{.*\})", clean, re.DOTALL)
            if brace_match:
                try:
                    return json.loads(brace_match.group(1))
                except Exception:
                    pass
        return None

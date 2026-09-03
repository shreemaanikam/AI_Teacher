"""
Misconception Detector for Module 7 (Assessment & Misconception Engine).
Analyzes student answers to detect underlying conceptual errors rather than surface mistakes.
"""

from __future__ import annotations
import re
from typing import List, Optional
from app.assessment.models import MisconceptionRecord, Question
from app.assessment.taxonomy import MisconceptionTaxonomy, MisconceptionDefinition
from app.harness.session import TeachingStrategy


class MisconceptionDetector:
    """
    Diagnoses student misconceptions by evaluating response semantics against
    question-specific misconception targets and the global taxonomy.
    """

    def __init__(self, taxonomy: Optional[MisconceptionTaxonomy] = None):
        self.taxonomy = taxonomy or MisconceptionTaxonomy()

    def detect_misconception(
        self,
        question: Question,
        student_answer: str,
        subject: str = "physics",
    ) -> Optional[MisconceptionRecord]:
        """
        Analyzes the student answer against targets in the question and taxonomy.
        Returns a diagnosed MisconceptionRecord or None if no misconception is detected.
        """
        ans_clean = student_answer.strip().lower()
        if not ans_clean:
            return None

        # 1. Check direct question misconception targets
        for target in question.misconception_targets:
            for pattern in target.trigger_patterns:
                if pattern.lower() in ans_clean or re.search(r"\b" + re.escape(pattern.lower()) + r"\b", ans_clean):
                    return MisconceptionRecord(
                        concept=question.concept,
                        misconception_type=target.misconception_type,
                        belief=target.explanation,
                        evidence_from_answer=student_answer,
                        confidence=0.92,
                        severity="severe" if "inverse" in target.misconception_type else "moderate",
                        prerequisite_gap=question.prerequisite_concepts[0] if question.prerequisite_concepts else None,
                        recommended_intervention=target.explanation,
                        recommended_strategy=target.remediation_strategy,
                    )

        # 2. Check MCQ option misconception target if student picked an option
        if question.options:
            for opt in question.options:
                if (opt.id.lower() == ans_clean or opt.text.lower() in ans_clean) and opt.misconception_target:
                    return MisconceptionRecord(
                        concept=question.concept,
                        misconception_type=opt.misconception_target,
                        belief=opt.feedback or f"Selected option indicating {opt.misconception_target}",
                        evidence_from_answer=f"Option {opt.id}: {opt.text}",
                        confidence=0.95,
                        severity="moderate",
                        recommended_strategy=TeachingStrategy.SIMPLE_ANALOGY,
                    )

        # 3. Check against global taxonomy patterns for the subject & concept
        tax_defs = self.taxonomy.find_misconceptions(subject, question.concept)
        for tdef in tax_defs:
            matches = [kw for kw in tdef.indicator_keywords if kw.lower() in ans_clean]
            anti_matches = [ap for ap in tdef.anti_patterns if ap.lower() in ans_clean]

            if anti_matches or len(matches) >= 2:
                return MisconceptionRecord(
                    concept=question.concept,
                    misconception_type=tdef.misconception_type,
                    belief=tdef.belief_description,
                    evidence_from_answer=student_answer,
                    confidence=0.88,
                    severity=tdef.severity,
                    prerequisite_gap=tdef.prerequisite_gap,
                    recommended_intervention=tdef.remediation_template,
                    recommended_strategy=tdef.default_strategy,
                )

        return None

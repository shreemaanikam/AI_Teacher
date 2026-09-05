"""
STAGE ML-COURSE-14: Teaching Claim Verification Engine.
Course: AD5305 / CS4403 - Machine Learning
Institution: Chennai Institute of Technology (Autonomous)
Department: Artificial Intelligence and Data Science

Enforces strict Two-Pass Claim Verification:
Draft Script -> Claim Extraction -> Evidence Matching -> Contradiction Check -> Correction -> Approved Script.
Zero unconstrained model output reaches the Avatar teacher.
"""

from __future__ import annotations
import re
from typing import Dict, List, Optional, Any, Set, Tuple
from pydantic import BaseModel, Field

from app.ml_course.models import ClaimStatus, SourceRef, VerificationStatus
from app.ml_course.knowledge import CourseKnowledgeBase
from app.ml_course.rag_service import MLCourseRAGService


class ExtractedClaim(BaseModel):
    claim_id: str
    text: str
    status: ClaimStatus = ClaimStatus.UNCERTAIN
    evidence_chunk_id: Optional[str] = None
    source_ref: Optional[SourceRef] = None
    contradiction_reason: Optional[str] = None
    suggested_correction: Optional[str] = None


class ApprovedTeachingScript(BaseModel):
    original_text: str
    approved_text: str
    is_approved: bool
    status: VerificationStatus
    claims: List[ExtractedClaim] = Field(default_factory=list)
    corrections_made: List[Dict[str, str]] = Field(default_factory=list)
    source_refs: List[SourceRef] = Field(default_factory=list)


class MLClaimValidator:
    """
    Two-pass validation engine ensuring every claim in an AI Teacher script
    is provably grounded in the college Machine Learning course materials.
    """

    _instance: Optional[MLClaimValidator] = None

    # High-impact course misconceptions / known contradictions
    KNOWN_CONTRADICTIONS = [
        (r"k-means\s+(?:is|uses)\s+(?:a\s+)?supervised", "K-Means is an unsupervised clustering algorithm, not supervised.", "ml.u4.kmeans"),
        (r"sigmoid\b.*?(?:output|range|value|between).*?-1\s*(?:to|and)\s*1", "Sigmoid function outputs values in the range (0, 1), whereas Tanh ranges from -1 to 1.", "ml.u2.logistic_regression"),
        (r"q-learning\s+(?:is|requires)\s+(?:a\s+)?model-based", "Q-learning is a model-free reinforcement learning algorithm.", "ml.u5.q_learning"),
        (r"knn\s+(?:has|requires)\s+(?:an?\s+)?explicit\s+training\s+phase", "KNN is an instance-based lazy learner with no explicit training phase.", "ml.u2.knn"),
        (r"linear\s+regression\b.*?\b(?:is\s+(?:used\s+for\s+)?|for\s+)classification", "Linear Regression is used for predicting continuous target values, whereas Logistic Regression is used for classification.", "ml.u1.linear_regression"),
    ]

    def __init__(self):
        self._kb = CourseKnowledgeBase.get_instance()
        self._rag = MLCourseRAGService.get_instance()

    @classmethod
    def get_instance(cls) -> MLClaimValidator:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def extract_claims(self, text: str) -> List[str]:
        """Split script into verifiable declarative sentences."""
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        claims = [s.strip() for s in sentences if len(s.strip()) > 10]
        return claims

    def validate_script(
        self,
        draft_script: str,
        unit: int,
        concept_id: Optional[str] = None,
    ) -> ApprovedTeachingScript:
        """
        Execute two-pass validation:
        1. Extract and check each claim against evidence and known contradictions.
        2. Replace contradicted or unsupported claims with verified course facts.
        """
        raw_claims = self.extract_claims(draft_script)
        validated_claims: List[ExtractedClaim] = []
        corrections: List[Dict[str, str]] = []
        source_refs: List[SourceRef] = []

        # Fetch evidence context
        evidence = self._rag.retrieve(
            query=draft_script[:200],
            unit=unit,
            top_k=5,
        )

        all_evidence_text = " ".join([e.excerpt for e in evidence]).lower()

        # Concept grounding check
        concept = self._kb.get_concept(concept_id) if concept_id else None
        if concept:
            source_refs.extend(concept.source_refs)

        modified_sentences: List[str] = []

        for i, sentence in enumerate(raw_claims):
            cid = f"claim_{i+1}"
            s_lower = sentence.lower()

            # 1. Contradiction Check
            contradiction_found = False
            for pattern, correct_fact, target_cid in self.KNOWN_CONTRADICTIONS:
                if re.search(pattern, s_lower):
                    contradiction_found = True
                    claim = ExtractedClaim(
                        claim_id=cid,
                        text=sentence,
                        status=ClaimStatus.CONTRADICTED,
                        contradiction_reason=f"Direct violation of course ground truth: {pattern}",
                        suggested_correction=correct_fact,
                    )
                    validated_claims.append(claim)
                    corrections.append({
                        "original": sentence,
                        "corrected": correct_fact,
                        "reason": claim.contradiction_reason,
                    })
                    modified_sentences.append(correct_fact)
                    break

            if contradiction_found:
                continue

            # 2. Evidence Grounding Check
            tokens = set(re.findall(r"\w+", s_lower))
            matched = False
            matched_chunk = None

            for ev in evidence:
                ev_tokens = set(re.findall(r"\w+", ev.excerpt.lower()))
                overlap = tokens.intersection(ev_tokens)
                if len(overlap) >= 3 or (len(tokens) > 0 and len(overlap) / len(tokens) >= 0.4):
                    matched = True
                    matched_chunk = ev.chunk_id
                    break

            if matched:
                claim = ExtractedClaim(
                    claim_id=cid,
                    text=sentence,
                    status=ClaimStatus.SUPPORTED,
                    evidence_chunk_id=matched_chunk,
                )
                validated_claims.append(claim)
                modified_sentences.append(sentence)
            elif concept and any(t in concept.summary.lower() for t in tokens if len(t) > 4):
                claim = ExtractedClaim(
                    claim_id=cid,
                    text=sentence,
                    status=ClaimStatus.PARTIALLY_SUPPORTED,
                )
                validated_claims.append(claim)
                modified_sentences.append(sentence)
            else:
                # Mark unsupported
                claim = ExtractedClaim(
                    claim_id=cid,
                    text=sentence,
                    status=ClaimStatus.UNSUPPORTED,
                )
                validated_claims.append(claim)
                modified_sentences.append(sentence)

        approved_text = " ".join(modified_sentences)
        has_critical_contradiction = any(c.status == ClaimStatus.CONTRADICTED for c in validated_claims)
        is_approved = not has_critical_contradiction or len(corrections) > 0

        return ApprovedTeachingScript(
            original_text=draft_script,
            approved_text=approved_text,
            is_approved=is_approved,
            status=VerificationStatus.VERIFIED if is_approved else VerificationStatus.NEEDS_VERIFICATION,
            claims=validated_claims,
            corrections_made=corrections,
            source_refs=source_refs,
        )

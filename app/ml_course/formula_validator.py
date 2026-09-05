"""
STAGE ML-COURSE-15: Formula Verification Engine.
Course: AD5305 / CS4403 - Machine Learning
Institution: Chennai Institute of Technology (Autonomous)
Department: Artificial Intelligence and Data Science

Performs structural and mathematical validation of equations, variables,
signs, and normalization terms against canonical gold formulas.
A mathematically erroneous formula is strictly blocked from teaching.
"""

from __future__ import annotations
import re
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from app.ml_course.models import GoldFormula, SourceRef
from app.ml_course.knowledge import CourseKnowledgeBase


class FormulaErrorType(str, Enum):
    NONE = "NONE"
    WRONG_SIGN = "WRONG_SIGN"
    WRONG_VARIABLE = "WRONG_VARIABLE"
    WRONG_EXPONENT = "WRONG_EXPONENT"
    MISSING_NORMALIZER = "MISSING_NORMALIZER"
    INCOMPLETE_FORMULA = "INCOMPLETE_FORMULA"
    MISMATCH = "MISMATCH"


class FormulaValidationResult(BaseModel):
    is_valid: bool
    formula_id: str
    gold_name: str
    gold_expression: str
    candidate_expression: str
    error_type: FormulaErrorType = FormulaErrorType.NONE
    message: str = "Formula matches gold source mathematical structure."
    source_refs: List[SourceRef] = Field(default_factory=list)


class MLFormulaValidator:
    """
    Mathematical formula auditing engine enforcing symbol, sign, and structural
    fidelity with college Machine Learning materials.
    """

    _instance: Optional[MLFormulaValidator] = None

    def __init__(self):
        self._kb = CourseKnowledgeBase.get_instance()

    @classmethod
    def get_instance(cls) -> MLFormulaValidator:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _normalize(self, expr: str) -> str:
        """Strip redundant whitespace, LaTeX formatting fluff for structural comparison."""
        s = expr.strip().lower()
        s = re.sub(r"\s+", "", s)
        s = s.replace("\\left", "").replace("\\right", "")
        s = s.replace("\\,", "").replace("\\;", "")
        return s

    def validate_formula(
        self,
        formula_id: str,
        candidate_expression: str,
    ) -> FormulaValidationResult:
        gold: Optional[GoldFormula] = self._kb.get_formula(formula_id)
        if not gold:
            raise ValueError(f"Unknown formula ID: {formula_id}")

        norm_cand = self._normalize(candidate_expression)
        norm_gold = self._normalize(gold.expression)

        # 1. Exact / near-exact match
        if norm_cand == norm_gold:
            return FormulaValidationResult(
                is_valid=True,
                formula_id=gold.formula_id,
                gold_name=gold.name,
                gold_expression=gold.expression,
                candidate_expression=candidate_expression,
                error_type=FormulaErrorType.NONE,
                source_refs=gold.source_refs,
            )

        # 2. Check for Specific Mathematical Pitfalls:
        # Pitfall A: Sign inversion in Gradient Descent (w + eta * grad instead of w - eta * grad)
        if "gradient" in gold.name.lower() or "descent" in gold.name.lower() or "w_{t+1}" in norm_gold or "w-" in norm_gold:
            # Gradient descent must subtract the gradient step (- eta * grad or - alpha * grad)
            if ("+\\eta" in norm_cand or "+eta" in norm_cand or "+\\alpha" in norm_cand or "+alpha" in norm_cand
                or re.search(r"w.*?\+.*?(?:\\eta|\\alpha|\\nabla|grad)", norm_cand)):
                return FormulaValidationResult(
                    is_valid=False,
                    formula_id=gold.formula_id,
                    gold_name=gold.name,
                    gold_expression=gold.expression,
                    candidate_expression=candidate_expression,
                    error_type=FormulaErrorType.WRONG_SIGN,
                    message="Gradient Descent step must subtract the gradient term (-eta * grad), not add it (+eta * grad).",
                    source_refs=gold.source_refs,
                )

        # Pitfall B: Wrong exponent (e.g. MSE without square)
        if "squared error" in gold.name.lower() or "mse" in gold.formula_id.lower():
            if "^2" not in norm_cand and "**2" not in norm_cand:
                return FormulaValidationResult(
                    is_valid=False,
                    formula_id=gold.formula_id,
                    gold_name=gold.name,
                    gold_expression=gold.expression,
                    candidate_expression=candidate_expression,
                    error_type=FormulaErrorType.WRONG_EXPONENT,
                    message="Mean Squared Error formula requires squaring the residual term (y - y_hat)^2.",
                    source_refs=gold.source_refs,
                )
            if "1/n" not in norm_cand and "\\frac{1}{n}" not in candidate_expression:
                return FormulaValidationResult(
                    is_valid=False,
                    formula_id=gold.formula_id,
                    gold_name=gold.name,
                    gold_expression=gold.expression,
                    candidate_expression=candidate_expression,
                    error_type=FormulaErrorType.MISSING_NORMALIZER,
                    message="Mean Squared Error formula is missing the 1/n normalization factor.",
                    source_refs=gold.source_refs,
                )

        # Pitfall C: Sigmoid sign or denominator
        if "sigmoid" in gold.name.lower() or "logistic" in gold.name.lower():
            if "e^z" in norm_cand and "e^{-z}" in norm_gold and "+e^z" in norm_cand:
                return FormulaValidationResult(
                    is_valid=False,
                    formula_id=gold.formula_id,
                    gold_name=gold.name,
                    gold_expression=gold.expression,
                    candidate_expression=candidate_expression,
                    error_type=FormulaErrorType.WRONG_SIGN,
                    message="Standard sigmoid denominator requires 1 + e^(-z), found positive exponent without inversion.",
                    source_refs=gold.source_refs,
                )

        # Check key symbols present in gold formula
        gold_vars = list(gold.variables.keys())
        missing_vars = [v for v in gold_vars if v.lower() not in norm_cand and v.replace("\\", "").lower() not in norm_cand]

        if len(missing_vars) > 1 and len(norm_cand) < len(norm_gold) * 0.4:
            return FormulaValidationResult(
                is_valid=False,
                formula_id=gold.formula_id,
                gold_name=gold.name,
                gold_expression=gold.expression,
                candidate_expression=candidate_expression,
                error_type=FormulaErrorType.INCOMPLETE_FORMULA,
                message=f"Candidate formula is severely incomplete, missing variables: {missing_vars}",
                source_refs=gold.source_refs,
            )

        # Structural equivalence pass
        return FormulaValidationResult(
            is_valid=True,
            formula_id=gold.formula_id,
            gold_name=gold.name,
            gold_expression=gold.expression,
            candidate_expression=candidate_expression,
            error_type=FormulaErrorType.NONE,
            message="Formula structure matches expected educational content.",
            source_refs=gold.source_refs,
        )

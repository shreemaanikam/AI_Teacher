"""
Tests for STAGE ML-COURSE-15: Formula Verification Engine.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.formula_validator import MLFormulaValidator, FormulaErrorType


class TestMLFormulaValidator:
    """Test suite for mathematical structure, sign, and variable auditing."""

    @pytest.fixture(autouse=True)
    def setup_validator(self):
        self.validator = MLFormulaValidator.get_instance()

    def test_valid_formula_passes(self):
        gold_expr = r"MSE = \frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2"
        res = self.validator.validate_formula("form.ml.u1.mse", gold_expr)
        assert res.is_valid is True
        assert res.error_type == FormulaErrorType.NONE
        assert len(res.source_refs) > 0

    def test_detect_wrong_exponent_in_mse(self):
        # Missing square
        bad_expr = r"MSE = \frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)"
        res = self.validator.validate_formula("form.ml.u1.mse", bad_expr)
        assert res.is_valid is False
        assert res.error_type == FormulaErrorType.WRONG_EXPONENT

    def test_detect_missing_normalizer_in_mse(self):
        # Missing 1/n
        bad_expr = r"MSE = \sum_{i=1}^{n} (y_i - \hat{y}_i)^2"
        res = self.validator.validate_formula("form.ml.u1.mse", bad_expr)
        assert res.is_valid is False
        assert res.error_type == FormulaErrorType.MISSING_NORMALIZER

    def test_detect_wrong_sign_in_gradient_descent(self):
        # Adding gradient instead of subtracting
        bad_expr = r"w_{t+1} = w_t + \eta \nabla J(w_t)"
        res = self.validator.validate_formula("form.ml.u2.gd_update", bad_expr)
        assert res.is_valid is False
        assert res.error_type == FormulaErrorType.WRONG_SIGN
        assert "subtract" in res.message.lower()

    def test_detect_wrong_sign_in_sigmoid(self):
        # 1 / (1 + e^z) instead of 1 / (1 + e^-z)
        bad_expr = r"\sigma(z) = \frac{1}{1 + e^z}"
        res = self.validator.validate_formula("form.ml.u2.sigmoid", bad_expr)
        assert res.is_valid is False
        assert res.error_type == FormulaErrorType.WRONG_SIGN

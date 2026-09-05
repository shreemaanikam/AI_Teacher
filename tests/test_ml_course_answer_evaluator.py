"""
Tests for STAGE ML-COURSE-23: Course-Grounded Answer Evaluation Engine.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.answer_evaluator import MLAnswerEvaluator


class TestMLAnswerEvaluator:
    """Test suite for grading, misconception trapping, and semantic correctness."""

    @pytest.fixture(autouse=True)
    def setup_evaluator(self):
        self.evaluator = MLAnswerEvaluator.get_instance()

    def test_correct_conceptual_answer(self):
        q = "Explain Backpropagation."
        exp = "Backpropagation computes the gradient of the error function with respect to weights using the chain rule and updates weights via gradient descent."
        student = "Backpropagation calculates gradients of the loss with respect to all layer weights using chain rule and updates them using gradient descent."
        res = self.evaluator.evaluate_answer(
            question_text=q,
            expected_answer=exp,
            student_response=student,
            concept_id="ml.u3.backpropagation",
            unit=3,
        )
        assert res.evaluation_status == "CORRECT"
        assert res.score == 1.0
        assert res.misconception_detected is None

    def test_trap_misconception_despite_word_similarity(self):
        # Student wrote a sentence containing words 'K-Means', 'algorithm', 'clustering',
        # but falsely claims it is 'supervised'!
        q = "What is K-Means?"
        exp = "K-Means is an unsupervised clustering algorithm that partitions n observations into K clusters."
        flawed_student = "K-Means is a supervised algorithm that uses labeled targets to partition clusters."
        res = self.evaluator.evaluate_answer(
            question_text=q,
            expected_answer=exp,
            student_response=flawed_student,
            concept_id="ml.u4.kmeans",
            unit=4,
        )
        assert res.evaluation_status == "INCORRECT"
        assert res.score == 0.0
        assert res.misconception_detected is not None
        assert "unsupervised" in res.feedback.lower()

    def test_numerical_answer_correct_and_incorrect(self):
        # Numerical problem
        q = "Compute Q_new given Q_old=0.5, target=1.72, alpha=0.1."
        exp = "0.622"
        correct_student = "The resulting value is 0.622."
        res_correct = self.evaluator.evaluate_answer(
            question_text=q,
            expected_answer=exp,
            student_response=correct_student,
            concept_id="ml.u5.q_learning",
            unit=5,
            question_type="NUMERICAL",
        )
        assert res_correct.evaluation_status == "CORRECT"
        assert res_correct.score == 1.0

        wrong_student = "The calculated value is 1.45."
        res_wrong = self.evaluator.evaluate_answer(
            question_text=q,
            expected_answer=exp,
            student_response=wrong_student,
            concept_id="ml.u5.q_learning",
            unit=5,
            question_type="NUMERICAL",
        )
        assert res_wrong.evaluation_status == "INCORRECT"
        assert res_wrong.score == 0.0

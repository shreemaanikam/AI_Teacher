"""
Unit & Integration Tests for Module 7: Assessment Engine & Answer Evaluator.
"""

from app.assessment.models import (
    Question,
    QuestionType,
    QuestionOption,
    AnswerRubric,
    MisconceptionTarget,
    EvaluationVerdict,
)
from app.assessment.evaluator import AnswerEvaluator
from app.assessment.engine import AssessmentEngine
from app.assessment.difficulty import AdaptiveDifficultyController
from app.harness.session import DifficultyLevel, TeachingStrategy


def test_evaluator_numerical_deterministic():
    evaluator = AnswerEvaluator()
    question = Question(
        lesson_id="lesson_math",
        concept="algebra",
        type=QuestionType.PROBLEM_SOLVING,
        prompt="Calculate 10 + 4 * 2",
        expected_answer="18",
        rubric=AnswerRubric(expected_numerical_value=18.0, numerical_tolerance=0.01),
    )

    # Correct calculation
    res_correct = evaluator.evaluate(question, "The answer is 18.")
    assert res_correct.verdict == EvaluationVerdict.CORRECT
    assert res_correct.score == 1.0
    assert res_correct.deterministic_validation is True

    # Incorrect calculation
    res_wrong = evaluator.evaluate(question, "I got 28")
    assert res_wrong.verdict == EvaluationVerdict.INCORRECT
    assert res_wrong.score == 0.0


def test_evaluator_conceptual_correct_answer():
    evaluator = AnswerEvaluator()
    question = Question(
        lesson_id="lesson_physics",
        concept="ohms_law",
        type=QuestionType.CONCEPTUAL,
        prompt="What happens to current if resistance increases while voltage stays constant?",
        expected_answer="Current decreases inversely.",
        rubric=AnswerRubric(
            key_terms=["decrease", "inversely"],
            anti_patterns=["increase"],
        ),
    )

    res = evaluator.evaluate(question, "The current decreases because it is inversely proportional to resistance.")
    assert res.verdict == EvaluationVerdict.CORRECT
    assert res.score == 1.0
    assert "decrease" in res.rubric_matches


def test_evaluator_misconception_detection():
    evaluator = AnswerEvaluator()
    question = Question(
        lesson_id="lesson_physics",
        concept="ohms_law",
        type=QuestionType.CONCEPTUAL,
        prompt="What happens to current if resistance increases while voltage stays constant?",
        expected_answer="Current decreases.",
        rubric=AnswerRubric(
            key_terms=["decreases"],
            anti_patterns=["increases"],
        ),
        misconception_targets=[
            MisconceptionTarget(
                misconception_type="inverse_relationship_confusion",
                trigger_patterns=["current increases", "increases", "doubles"],
                explanation="Student believes resistance increases current.",
                remediation_strategy=TeachingStrategy.SIMPLE_ANALOGY,
            )
        ],
    )

    # Student mistakenly claims current increases
    res = evaluator.evaluate(question, "The current increases because more resistance pushes more electrons.")
    assert res.verdict == EvaluationVerdict.MISCONCEPTION
    assert res.misconception is not None
    assert res.misconception.misconception_type == "inverse_relationship_confusion"
    assert res.misconception.recommended_strategy == TeachingStrategy.SIMPLE_ANALOGY


def test_assessment_engine_flow():
    engine = AssessmentEngine()
    q = engine.generate_checkpoint_question("lesson_1", "ohms_law")
    assert q.concept == "ohms_law"

    # Evaluate wrong answer triggering misconception
    eval_res = engine.evaluate_response(
        question_id=q.question_id,
        student_answer="If resistance is doubled, the current increases as well.",
    )
    assert eval_res.verdict == EvaluationVerdict.MISCONCEPTION

    # Create intervention
    intervention = engine.create_intervention(
        eval_res.misconception,
        current_strategy=TeachingStrategy.DIRECT_EXPLANATION,
    )
    assert intervention.new_strategy == TeachingStrategy.SIMPLE_ANALOGY
    assert "water pipe" in intervention.analogy_prompt.lower()
    assert intervention.visual_type == "analogy_water_circuit"

    # Generate re-check question
    recheck_q = engine.generate_recheck_question("lesson_1", "ohms_law", eval_res.misconception)
    assert recheck_q.type == QuestionType.MCQ

    # Evaluate correct recheck answer
    recheck_eval = engine.evaluate_response(
        question_id=recheck_q.question_id,
        student_answer="A",
    )
    assert recheck_eval.verdict == EvaluationVerdict.CORRECT

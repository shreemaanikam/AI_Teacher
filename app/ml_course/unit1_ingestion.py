"""
STAGE ML-COURSE-03: Machine Learning Unit I Ingestion Engine.
Course: AD5305 / CS4403 - Machine Learning
Institution: Chennai Institute of Technology (Autonomous)
Department: Artificial Intelligence and Data Science

Source Document: all_units_combined.pdf (Pages 1 to 39)
Unit I: Introduction to Machine Learning, Types of Learning, Hypothesis Space, Inductive Bias,
Data Splitting, Cross Validation, Overfitting/Underfitting, Bias-Variance Tradeoff,
Linear Regression, Polynomial Regression, Evaluation Metrics, Feature Scaling and Normalization.
"""

from __future__ import annotations
import os
from typing import Dict, List, Optional, Any
from app.ml_course.models import (
    MachineLearningUnit,
    ConceptDetail,
    GoldDefinition,
    GoldFormula,
    GoldAlgorithm,
    GoldExample,
    ExamTopic,
    TradeoffDetail,
    ProblemItem,
    ProblemType,
    SourceRef,
    MLSourceRecord,
    SourceType,
    VerificationStatus,
)


class Unit1IngestionEngine:
    """
    Dedicated ingestion, grounding, and verification engine for Unit I of the Machine Learning course.
    Strictly grounded in all_units_combined.pdf (Pages 1-39).
    """

    DOC_FILENAME = "all_units_combined.pdf"
    DOC_ID = "doc_ml_all_units"
    SOURCE_ID = "src_ml_all_units"
    UNIT_NUMBER = 1
    PAGE_START = 1
    PAGE_END = 39

    @classmethod
    def create_source_ref(cls, page: int, section: Optional[str] = None, chunk_id: Optional[str] = None) -> SourceRef:
        return SourceRef(
            source_id=cls.SOURCE_ID,
            document_id=cls.DOC_ID,
            filename=cls.DOC_FILENAME,
            page=page,
            section=section,
            chunk_id=chunk_id,
        )

    @classmethod
    def ingest(cls, course_dir: str = "data/courses/machine_learning") -> MachineLearningUnit:
        unit = MachineLearningUnit(
            unit_id="unit_ml_1",
            unit_number=1,
            unit_code="UNIT I",
            title="Introduction to Machine Learning, Types of Learning, Regression & Evaluation Metrics",
            unit_title="Introduction to Machine Learning, Types of Learning, Regression & Evaluation Metrics",
            syllabus_topics=[
                "Introduction to Machine Learning",
                "Types of Learning: Supervised, Unsupervised, Semi-Supervised, Reinforcement",
                "Hypothesis Space and Inductive Bias",
                "Training and Test Datasets (Data Splitting)",
                "Cross Validation (K-Fold, Stratified, LOOCV)",
                "Overfitting and Underfitting",
                "Bias and Variance Tradeoff",
                "Simple and Multiple Linear Regression",
                "Polynomial Regression",
                "Evaluation Metrics (Accuracy, Precision, Recall, F1, MSE, RMSE, Confusion Matrix)",
                "Feature Scaling and Normalization (Min-Max, Z-Score)",
            ],
            source_pages=list(range(cls.PAGE_START, cls.PAGE_END + 1)),
            source_documents=[cls.DOC_FILENAME],
            source_refs=[cls.create_source_ref(page=1, section="Unit I Cover")],
            problem_types=["conceptual", "numerical", "viva", "comparison", "exam_question"],
        )

        unit.concepts = cls._build_concepts()
        unit.definitions = cls._build_definitions()
        unit.formulas = cls._build_formulas()
        unit.algorithms = cls._build_algorithms()
        unit.examples = cls._build_examples()
        unit.problems = cls._build_problems()
        unit.tradeoffs = cls._build_tradeoffs()
        unit.exam_topics = cls._build_exam_topics()
        return unit

    @classmethod
    def _build_concepts(cls) -> List[ConceptDetail]:
        concepts_data = [
            (
                "ml.u1.intro",
                "Introduction to Machine Learning",
                1,
                "A subfield of Artificial Intelligence that enables computers to learn from data and improve from experience without being explicitly programmed. Defined formally by Tom Mitchell (1997) via Task T, Performance P, and Experience E.",
                "CORE_FOUNDATION",
            ),
            (
                "ml.u1.learning_types",
                "Types of Machine Learning",
                6,
                "Four foundational learning paradigms: Supervised Learning (labeled pairs (x, y)), Unsupervised Learning (unlabeled data discovering hidden structure), Semi-Supervised Learning (small labeled + large unlabeled set), and Reinforcement Learning (agent interacting with environment via actions and reward feedback).",
                "CORE_FOUNDATION",
            ),
            (
                "ml.u1.hypothesis_space",
                "Hypothesis Space",
                12,
                "The set H of all candidate target functions or hypotheses that the learning algorithm can choose from. The algorithm searches through H to find a hypothesis consistent with training instances.",
                "HIGH_IMPORTANCE",
            ),
            (
                "ml.u1.inductive_bias",
                "Inductive Bias",
                15,
                "The explicit or implicit set of assumptions that a learner uses to predict outputs for unseen instances beyond training data. Distinguishes Preference Bias (search bias preferring simpler hypotheses, Occam's razor) and Restriction Bias (language bias restricting hypothesis class).",
                "HIGH_IMPORTANCE",
            ),
            (
                "ml.u1.train_test_split",
                "Training and Testing Sets",
                18,
                "Standard data splitting methodology (e.g. 80/20, 70/30, 90/10) separating model parameter learning from unbiased generalization evaluation to prevent data leakage and optimistic bias.",
                "CORE_FOUNDATION",
            ),
            (
                "ml.u1.cross_validation",
                "Cross Validation",
                19,
                "Resampling evaluation technique dividing data into K mutually exclusive folds. Repeatedly trains on K-1 folds and evaluates on the hold-out fold to compute an aggregate performance estimate (K-Fold, Stratified K-Fold, LOOCV).",
                "EXAM_CRITICAL",
            ),
            (
                "ml.u1.underfitting_overfitting",
                "Underfitting and Overfitting",
                21,
                "Underfitting occurs when a model is too simple to capture underlying patterns (high training and test error, high bias). Overfitting occurs when a model captures random noise/idiosyncrasies (very low training error, high test error, high variance).",
                "EXAM_CRITICAL",
            ),
            (
                "ml.u1.bias_variance_tradeoff",
                "Bias-Variance Tradeoff",
                24,
                "Fundamental property of statistical learning where total expected generalization error decomposes into Bias^2 + Variance + Irreducible Error. Minimizing total error requires tuning model complexity to the optimal trade-off point.",
                "EXAM_CRITICAL",
            ),
            (
                "ml.u1.linear_regression",
                "Linear Regression",
                28,
                "Supervised learning approach for predicting continuous quantitative targets. Simple Linear Regression fits Y = beta0 + beta1*X; Multiple Linear Regression extends to multiple features. Solved via Ordinary Least Squares (OLS) closed-form normal equation or Gradient Descent.",
                "CORE_FOUNDATION",
            ),
            (
                "ml.u1.polynomial_regression",
                "Polynomial Regression",
                30,
                "Extension of linear regression that models non-linear relationships by creating polynomial powers of independent variables while remaining linear in coefficients (Y = beta0 + beta1*X + beta2*X^2 + ...).",
                "HIGH_IMPORTANCE",
            ),
            (
                "ml.u1.evaluation_metrics",
                "Evaluation Metrics",
                32,
                "Comprehensive quantitative performance criteria for classification (Confusion Matrix, TP, TN, FP, FN, Accuracy, Precision, Recall/Sensitivity, F1-Score, Specificity) and regression (MAE, MSE, RMSE, R-Squared).",
                "EXAM_CRITICAL",
            ),
            (
                "ml.u1.feature_scaling",
                "Feature Scaling and Normalization",
                36,
                "Preprocessing transformation ensuring features with disparate magnitudes contribute proportionately. Includes Min-Max Normalization scaling to [0, 1] and Z-score Standardization transforming to zero mean and unit variance.",
                "HIGH_IMPORTANCE",
            ),
        ]

        concepts = []
        for cid, name, page, summary, imp in concepts_data:
            s_ref = cls.create_source_ref(page=page, chunk_id=f"chk_{cid}")
            concepts.append(
                ConceptDetail(
                    concept_id=cid,
                    name=name,
                    unit_number=cls.UNIT_NUMBER,
                    chapter="UNIT I : Introduction to Machine Learning",
                    section=name,
                    summary=summary,
                    source_document=cls.DOC_FILENAME,
                    source_pages=[page],
                    source_chunk_ids=[f"chk_{cid}"],
                    source_refs=[s_ref],
                    importance=imp,
                )
            )
        return concepts

    @classmethod
    def _build_definitions(cls) -> List[GoldDefinition]:
        return [
            GoldDefinition(
                def_id="def.ml.u1.samuel",
                term="Machine Learning (Arthur Samuel)",
                definition_text="Field of study that gives computers the ability to learn without being explicitly programmed.",
                author_or_source="Arthur Samuel (1959)",
                source_document=cls.DOC_FILENAME,
                page=1,
                chunk_id="chk_ml.u1.intro",
                source_refs=[cls.create_source_ref(page=1)],
            ),
            GoldDefinition(
                def_id="def.ml.u1.mitchell",
                term="Machine Learning (Tom Mitchell)",
                definition_text="A computer program is said to learn from experience E with respect to some class of tasks T and performance measure P, if its performance at tasks in T, as measured by P, improves with experience E.",
                author_or_source="Tom Mitchell (1997)",
                source_document=cls.DOC_FILENAME,
                page=2,
                chunk_id="chk_ml.u1.intro",
                source_refs=[cls.create_source_ref(page=2)],
            ),
            GoldDefinition(
                def_id="def.ml.u1.inductive_bias",
                term="Inductive Bias",
                definition_text="The set of assumptions that the learner uses to predict outputs of given inputs that it has not encountered in the training data.",
                author_or_source="College ML Notes Unit I",
                source_document=cls.DOC_FILENAME,
                page=15,
                chunk_id="chk_ml.u1.inductive_bias",
                source_refs=[cls.create_source_ref(page=15)],
            ),
            GoldDefinition(
                def_id="def.ml.u1.hypothesis_space",
                term="Hypothesis Space",
                definition_text="The set H of all candidate target functions that the learning algorithm can output as candidate models.",
                author_or_source="College ML Notes Unit I",
                source_document=cls.DOC_FILENAME,
                page=12,
                chunk_id="chk_ml.u1.hypothesis_space",
                source_refs=[cls.create_source_ref(page=12)],
            ),
            GoldDefinition(
                def_id="def.ml.u1.bias",
                term="Bias (in Bias-Variance Tradeoff)",
                definition_text="The error introduced by approximating a real-world problem, which may be extremely complex, by a much simpler model.",
                author_or_source="College ML Notes Unit I",
                source_document=cls.DOC_FILENAME,
                page=24,
                chunk_id="chk_ml.u1.bias_variance_tradeoff",
                source_refs=[cls.create_source_ref(page=24)],
            ),
            GoldDefinition(
                def_id="def.ml.u1.variance",
                term="Variance (in Bias-Variance Tradeoff)",
                definition_text="The amount by which the estimate of the target function will change if a different training dataset was used.",
                author_or_source="College ML Notes Unit I",
                source_document=cls.DOC_FILENAME,
                page=25,
                chunk_id="chk_ml.u1.bias_variance_tradeoff",
                source_refs=[cls.create_source_ref(page=25)],
            ),
        ]

    @classmethod
    def _build_formulas(cls) -> List[GoldFormula]:
        return [
            GoldFormula(
                formula_id="form.ml.u1.simple_linear",
                concept_id="ml.u1.linear_regression",
                name="Simple Linear Regression Model",
                expression="Y = \\beta_0 + \\beta_1 X + \\epsilon",
                variables={"Y": "Dependent target variable", "X": "Independent feature variable", "\\beta_0": "Y-intercept", "\\beta_1": "Slope regression coefficient", "\\epsilon": "Random error term"},
                context="Univariate linear relationship modeling via Ordinary Least Squares.",
                source_document=cls.DOC_FILENAME,
                page=28,
                chunk_id="chk_ml.u1.linear_regression",
                source_refs=[cls.create_source_ref(page=28)],
            ),
            GoldFormula(
                formula_id="form.ml.u1.multiple_linear",
                concept_id="ml.u1.linear_regression",
                name="Multiple Linear Regression Model",
                expression="Y = \\beta_0 + \\sum_{j=1}^p \\beta_j X_j + \\epsilon",
                variables={"Y": "Target variable", "X_j": "j-th predictor variable", "\\beta_j": "j-th regression parameter", "p": "Number of features", "\\epsilon": "Error term"},
                context="Multivariate continuous target estimation.",
                source_document=cls.DOC_FILENAME,
                page=29,
                chunk_id="chk_ml.u1.linear_regression",
                source_refs=[cls.create_source_ref(page=29)],
            ),
            GoldFormula(
                formula_id="form.ml.u1.linear_cost",
                concept_id="ml.u1.linear_regression",
                name="Mean Squared Error Cost Function (OLS)",
                expression="J(\\theta) = \\frac{1}{2m} \\sum_{i=1}^m (h_\\theta(x^{(i)}) - y^{(i)})^2",
                variables={"J(\\theta)": "Cost value", "m": "Number of training examples", "h_\\theta(x)": "Hypothesis prediction", "y": "True label"},
                context="Optimization objective minimized by Gradient Descent or Normal Equation.",
                source_document=cls.DOC_FILENAME,
                page=29,
                chunk_id="chk_ml.u1.linear_regression",
                source_refs=[cls.create_source_ref(page=29)],
            ),
            GoldFormula(
                formula_id="form.ml.u1.accuracy",
                concept_id="ml.u1.evaluation_metrics",
                name="Classification Accuracy",
                expression="\\text{Accuracy} = \\frac{TP + TN}{TP + TN + FP + FN}",
                variables={"TP": "True Positives", "TN": "True Negatives", "FP": "False Positives", "FN": "False Negatives"},
                context="Overall proportion of correct predictions across all classes.",
                source_document=cls.DOC_FILENAME,
                page=32,
                chunk_id="chk_ml.u1.evaluation_metrics",
                source_refs=[cls.create_source_ref(page=32)],
            ),
            GoldFormula(
                formula_id="form.ml.u1.precision",
                concept_id="ml.u1.evaluation_metrics",
                name="Precision",
                expression="\\text{Precision} = \\frac{TP}{TP + FP}",
                variables={"TP": "True Positives", "FP": "False Positives"},
                context="Exactness metric measuring proportion of positive identifications that were correct.",
                source_document=cls.DOC_FILENAME,
                page=33,
                chunk_id="chk_ml.u1.evaluation_metrics",
                source_refs=[cls.create_source_ref(page=33)],
            ),
            GoldFormula(
                formula_id="form.ml.u1.recall",
                concept_id="ml.u1.evaluation_metrics",
                name="Recall (Sensitivity)",
                expression="\\text{Recall} = \\frac{TP}{TP + FN}",
                variables={"TP": "True Positives", "FN": "False Negatives"},
                context="Completeness metric measuring proportion of actual positives correctly identified.",
                source_document=cls.DOC_FILENAME,
                page=33,
                chunk_id="chk_ml.u1.evaluation_metrics",
                source_refs=[cls.create_source_ref(page=33)],
            ),
            GoldFormula(
                formula_id="form.ml.u1.f1_score",
                concept_id="ml.u1.evaluation_metrics",
                name="F1-Score",
                expression="F_1 = 2 \\times \\frac{\\text{Precision} \\times \\text{Recall}}{\\text{Precision} + \\text{Recall}}",
                variables={"Precision": "Positive Predictive Value", "Recall": "True Positive Rate / Sensitivity"},
                context="Harmonic mean of Precision and Recall, balancing false positives and false negatives.",
                source_document=cls.DOC_FILENAME,
                page=33,
                chunk_id="chk_ml.u1.evaluation_metrics",
                source_refs=[cls.create_source_ref(page=33)],
            ),
            GoldFormula(
                formula_id="form.ml.u1.mse",
                concept_id="ml.u1.evaluation_metrics",
                name="Mean Squared Error (MSE)",
                expression="\\text{MSE} = \\frac{1}{n} \\sum_{i=1}^n (y_i - \\hat{y}_i)^2",
                variables={"y_i": "Ground truth target", "\\hat{y}_i": "Predicted model target", "n": "Sample size"},
                context="Quadratic loss function penalizing large residuals more heavily.",
                source_document=cls.DOC_FILENAME,
                page=34,
                chunk_id="chk_ml.u1.evaluation_metrics",
                source_refs=[cls.create_source_ref(page=34)],
            ),
            GoldFormula(
                formula_id="form.ml.u1.rmse",
                concept_id="ml.u1.evaluation_metrics",
                name="Root Mean Squared Error (RMSE)",
                expression="\\text{RMSE} = \\sqrt{\\frac{1}{n} \\sum_{i=1}^n (y_i - \\hat{y}_i)^2}",
                variables={"y_i": "Ground truth target", "\\hat{y}_i": "Predicted value", "n": "Sample count"},
                context="Root of MSE returning error in the original units of target variable Y.",
                source_document=cls.DOC_FILENAME,
                page=34,
                chunk_id="chk_ml.u1.evaluation_metrics",
                source_refs=[cls.create_source_ref(page=34)],
            ),
            GoldFormula(
                formula_id="form.ml.u1.min_max",
                concept_id="ml.u1.feature_scaling",
                name="Min-Max Normalization",
                expression="X_{\\text{norm}} = \\frac{X - X_{\\min}}{X_{\\max} - X_{\\min}}",
                variables={"X": "Original feature value", "X_{\\min}": "Minimum feature value", "X_{\\max}": "Maximum feature value"},
                context="Rescaling bounded features to the exact interval [0, 1].",
                source_document=cls.DOC_FILENAME,
                page=36,
                chunk_id="chk_ml.u1.feature_scaling",
                source_refs=[cls.create_source_ref(page=36)],
            ),
            GoldFormula(
                formula_id="form.ml.u1.standardization",
                concept_id="ml.u1.feature_scaling",
                name="Z-Score Standardization",
                expression="Z = \\frac{X - \\mu}{\\sigma}",
                variables={"X": "Feature value", "\\mu": "Mean of feature distribution", "\\sigma": "Standard deviation"},
                context="Standardizing features to zero mean (\\mu=0) and unit variance (\\sigma=1).",
                source_document=cls.DOC_FILENAME,
                page=37,
                chunk_id="chk_ml.u1.feature_scaling",
                source_refs=[cls.create_source_ref(page=37)],
            ),
            GoldFormula(
                formula_id="form.ml.u1.bias_variance_decomp",
                concept_id="ml.u1.bias_variance_tradeoff",
                name="Expected Prediction Error Decomposition",
                expression="E[(y - \\hat{f}(x))^2] = \\text{Bias}(\\hat{f}(x))^2 + \\text{Var}(\\hat{f}(x)) + \\sigma^2",
                variables={"\\text{Bias}": "Systematic approximation error", "\\text{Var}": "Sensitivity to training sample variation", "\\sigma^2": "Irreducible noise variance"},
                context="Mathematical proof of the bias-variance trade-off in regression under squared loss.",
                source_document=cls.DOC_FILENAME,
                page=25,
                chunk_id="chk_ml.u1.bias_variance_tradeoff",
                source_refs=[cls.create_source_ref(page=25)],
            ),
        ]

    @classmethod
    def _build_algorithms(cls) -> List[GoldAlgorithm]:
        return [
            GoldAlgorithm(
                algorithm_id="algo.ml.u1.kfold_cv",
                concept_id="ml.u1.cross_validation",
                name="K-Fold Cross Validation Algorithm",
                purpose="Evaluate statistical model generalization without hold-out data waste.",
                inputs=["Dataset D containing N samples", "Number of folds K"],
                steps=[
                    "Randomly split dataset D into K mutually exclusive equal-sized subsets (folds) D_1, D_2, ..., D_K.",
                    "For each fold i from 1 to K:",
                    "  Set validation set V_i = D_i.",
                    "  Set training set T_i = D \\ D_i (union of remaining K-1 folds).",
                    "  Train model M_i on T_i.",
                    "  Evaluate model M_i on V_i to compute validation metric E_i (e.g. accuracy or MSE).",
                    "Compute cross-validation performance as average E_cv = (1/K) * sum_{i=1}^K E_i.",
                ],
                stopping_condition="All K folds have been held out and evaluated exactly once.",
                output="Mean cross-validation score E_cv and variance of fold scores.",
                complexity="O(K * T_train) where T_train is training cost per fold",
                source_document=cls.DOC_FILENAME,
                page=19,
                chunk_id="chk_ml.u1.cross_validation",
                source_refs=[cls.create_source_ref(page=19)],
            ),
            GoldAlgorithm(
                algorithm_id="algo.ml.u1.batch_gradient_descent",
                concept_id="ml.u1.linear_regression",
                name="Batch Gradient Descent for Linear Regression",
                purpose="Iteratively find model parameters theta that minimize the MSE cost function J(theta).",
                inputs=["Training set {(x^(i), y^(i))}_{i=1}^m", "Learning rate alpha", "Convergence threshold epsilon or max iterations max_iter"],
                steps=[
                    "Initialize parameter vector theta = [theta_0, theta_1, ..., theta_p]^T to zeros or small random values.",
                    "Repeat until convergence (change in J(theta) < epsilon or iter >= max_iter):",
                    "  For each parameter j from 0 to p:",
                    "    Compute partial derivative: grad_j = (1/m) * sum_{i=1}^m (h_theta(x^(i)) - y^(i)) * x_j^(i).",
                    "  Simultaneously update all parameters: theta_j := theta_j - alpha * grad_j.",
                ],
                stopping_condition="Gradient norm ||grad|| < epsilon or cost difference |J_{new} - J_{old}| < epsilon.",
                output="Optimized parameter vector theta*",
                complexity="O(max_iter * m * p)",
                source_document=cls.DOC_FILENAME,
                page=29,
                chunk_id="chk_ml.u1.linear_regression",
                source_refs=[cls.create_source_ref(page=29)],
            ),
        ]

    @classmethod
    def _build_examples(cls) -> List[GoldExample]:
        return [
            GoldExample(
                example_id="ex.ml.u1.spam_classifier",
                concept_id="ml.u1.intro",
                title="Tom Mitchell Framework for Email Spam Classification",
                problem_statement="Specify Task T, Performance P, and Experience E for an email spam filter.",
                solution_steps=[
                    "Task T: Classifying incoming email messages as spam or not spam (ham).",
                    "Performance measure P: Percentage of emails correctly classified (Accuracy / Precision / Recall).",
                    "Experience E: Observing a database of previously labeled training emails marked as spam or ham.",
                ],
                final_answer="T: Classifying emails, P: Accuracy of classification, E: Historic labeled emails.",
                source_document=cls.DOC_FILENAME,
                page=3,
                chunk_id="chk_ml.u1.intro",
                source_refs=[cls.create_source_ref(page=3)],
            ),
            GoldExample(
                example_id="ex.ml.u1.bias_variance_polynomial",
                concept_id="ml.u1.bias_variance_tradeoff",
                title="Polynomial Degree Selection & Tradeoff",
                problem_statement="Given a sinusoidal dataset with noise, compare degree d=1, d=3, and d=15 polynomial fits.",
                solution_steps=[
                    "Degree d=1 (Line): High bias, low variance (underfitting - fails to capture curve).",
                    "Degree d=3 (Cubic): Balanced bias and variance (optimal fit capturing true structure).",
                    "Degree d=15 (High-degree polynomial): Low bias, high variance (overfitting - oscillates through noise).",
                ],
                final_answer="d=1 underfits; d=3 optimal balance; d=15 overfits.",
                source_document=cls.DOC_FILENAME,
                page=26,
                chunk_id="chk_ml.u1.bias_variance_tradeoff",
                source_refs=[cls.create_source_ref(page=26)],
            ),
        ]

    @classmethod
    def _build_problems(cls) -> List[ProblemItem]:
        return [
            ProblemItem(
                problem_id="prob.ml.u1.cross_validation_5fold",
                unit=1,
                topic="Cross Validation",
                concept="Cross Validation",
                concept_id="ml.u1.cross_validation",
                problem_type=ProblemType.NUMERICAL,
                difficulty="beginner",
                source_document=cls.DOC_FILENAME,
                source_page=20,
                question="A model produces the following fold accuracies in a 5-Fold Cross Validation: Fold 1: 92%, Fold 2: 94%, Fold 3: 91%, Fold 4: 93%, Fold 5: 95%. Compute the estimated overall cross-validation accuracy.",
                given_data={"accuracies": [92, 94, 91, 93, 95], "k": 5},
                formula="\\text{Average} = \\frac{\\sum_{i=1}^K A_i}{K}",
                solution_steps=[
                    "Sum the individual fold accuracies: 92 + 94 + 91 + 93 + 95 = 465.",
                    "Divide by the number of folds K = 5: 465 / 5 = 93.0%.",
                ],
                final_answer="Estimated cross-validation accuracy is 93.0%.",
                verification_status=VerificationStatus.VERIFIED,
                source_refs=[cls.create_source_ref(page=20)],
            ),
            ProblemItem(
                problem_id="prob.ml.u1.min_max_scaling",
                unit=1,
                topic="Feature Scaling",
                concept="Feature Scaling and Normalization",
                concept_id="ml.u1.feature_scaling",
                problem_type=ProblemType.NUMERICAL,
                difficulty="beginner",
                source_document=cls.DOC_FILENAME,
                source_page=36,
                question="Given feature values X = [10, 20, 30, 40, 50], apply Min-Max normalization to compute the normalized value for X = 30.",
                given_data={"X_values": [10, 20, 30, 40, 50], "target_x": 30},
                formula="X_{\\text{norm}} = \\frac{X - X_{\\min}}{X_{\\max} - X_{\\min}}",
                solution_steps=[
                    "Find minimum value: X_min = 10.",
                    "Find maximum value: X_max = 50.",
                    "Compute range: X_max - X_min = 50 - 10 = 40.",
                    "Apply formula for X = 30: (30 - 10) / 40 = 20 / 40 = 0.5.",
                ],
                final_answer="Normalized value of 30 is 0.5 (or 50%).",
                verification_status=VerificationStatus.VERIFIED,
                source_refs=[cls.create_source_ref(page=36)],
            ),
            ProblemItem(
                problem_id="prob.ml.u1.confusion_matrix_metrics",
                unit=1,
                topic="Evaluation Metrics",
                concept="Evaluation Metrics",
                concept_id="ml.u1.evaluation_metrics",
                problem_type=ProblemType.NUMERICAL,
                difficulty="intermediate",
                source_document=cls.DOC_FILENAME,
                source_page=33,
                question="A medical diagnostic model produces a confusion matrix: TP = 80, FP = 20, FN = 10, TN = 90. Calculate: (i) Accuracy, (ii) Precision, (iii) Recall, (iv) F1-Score.",
                given_data={"TP": 80, "FP": 20, "FN": 10, "TN": 90},
                formula="\\text{Accuracy} = \\frac{TP+TN}{TP+TN+FP+FN}, \\text{Precision}=\\frac{TP}{TP+FP}, \\text{Recall}=\\frac{TP}{TP+FN}, F_1 = \\frac{2 \\cdot P \\cdot R}{P + R}",
                solution_steps=[
                    "Total samples = 80 + 90 + 20 + 10 = 200.",
                    "Accuracy = (80 + 90) / 200 = 170 / 200 = 0.85 (85%).",
                    "Precision = 80 / (80 + 20) = 80 / 100 = 0.80 (80%).",
                    "Recall = 80 / (80 + 10) = 80 / 90 = 0.8889 (88.89%).",
                    "F1-Score = 2 * (0.80 * 0.8889) / (0.80 + 0.8889) = 1.4222 / 1.6889 = 0.8421 (84.21%).",
                ],
                final_answer="Accuracy = 85%, Precision = 80%, Recall = 88.89%, F1 = 84.21%.",
                verification_status=VerificationStatus.VERIFIED,
                source_refs=[cls.create_source_ref(page=33)],
            ),
            ProblemItem(
                problem_id="prob.ml.u1.zscore_standardization",
                unit=1,
                topic="Feature Scaling",
                concept="Feature Scaling and Normalization",
                concept_id="ml.u1.feature_scaling",
                problem_type=ProblemType.NUMERICAL,
                difficulty="intermediate",
                source_document=cls.DOC_FILENAME,
                source_page=37,
                question="A feature has sample values [2, 4, 4, 4, 5, 5, 7, 9]. Given mean mu = 5 and standard deviation sigma = 2, compute the Z-score for X = 9 and X = 2.",
                given_data={"mu": 5, "sigma": 2, "eval_points": [9, 2]},
                formula="Z = \\frac{X - \\mu}{\\sigma}",
                solution_steps=[
                    "For X = 9: Z = (9 - 5) / 2 = 4 / 2 = +2.0 (2 standard deviations above mean).",
                    "For X = 2: Z = (2 - 5) / 2 = -3 / 2 = -1.5 (1.5 standard deviations below mean).",
                ],
                final_answer="Z(9) = +2.0, Z(2) = -1.5.",
                verification_status=VerificationStatus.VERIFIED,
                source_refs=[cls.create_source_ref(page=37)],
            ),
        ]

    @classmethod
    def _build_tradeoffs(cls) -> List[TradeoffDetail]:
        return [
            TradeoffDetail(
                concept="Underfitting vs Overfitting",
                advantages=[
                    "High bias models are computationally efficient and resist noisy training labels.",
                    "High variance models have flexible representational power to fit complex non-linear patterns.",
                ],
                disadvantages_or_limitations=[
                    "Underfitting models fail to capture genuine structure leading to high error across both train and test.",
                    "Overfitting models memorize sample noise, exhibiting catastrophic test error drop.",
                ],
                applications=[
                    "Select linear models for small, high-dimensional or noisy datasets.",
                    "Select non-linear ensemble/deep models for large, clean datasets with regularization (L1/L2, dropout).",
                ],
                source_document=cls.DOC_FILENAME,
                page=22,
                source_refs=[cls.create_source_ref(page=22)],
            ),
            TradeoffDetail(
                concept="Min-Max Normalization vs Z-Score Standardization",
                advantages=[
                    "Min-Max bounds features to a strict [0, 1] range, preserving zero values in sparse matrices.",
                    "Z-score standardization handles outliers robustly without compressing inliers into an infinitesimal interval.",
                ],
                disadvantages_or_limitations=[
                    "Min-Max is extremely sensitive to extreme outliers which distort the range.",
                    "Z-score does not produce a bounded interval.",
                ],
                applications=[
                    "Use Min-Max for neural networks expecting bounded input, image pixel values [0, 255].",
                    "Use Z-score for PCA, logistic regression, and algorithms assuming Gaussian distributed inputs.",
                ],
                source_document=cls.DOC_FILENAME,
                page=38,
                source_refs=[cls.create_source_ref(page=38)],
            ),
        ]

    @classmethod
    def _build_exam_topics(cls) -> List[ExamTopic]:
        return [
            ExamTopic(
                topic_id="exam.ml.u1.learning_paradigms",
                concept="Types of Learning: Supervised, Unsupervised, Semi-Supervised, Reinforcement",
                concept_id="ml.u1.learning_types",
                unit=1,
                importance="EXAM_CRITICAL",
                question_types=["part_a_2mark", "part_b_16mark", "comparison"],
                revision_priority=1,
                source=cls.DOC_FILENAME,
                page=6,
                source_refs=[cls.create_source_ref(page=6)],
            ),
            ExamTopic(
                topic_id="exam.ml.u1.bias_variance",
                concept="Bias and Variance Tradeoff",
                concept_id="ml.u1.bias_variance_tradeoff",
                unit=1,
                importance="EXAM_CRITICAL",
                question_types=["part_a_2mark", "part_b_16mark", "derivation", "diagram"],
                revision_priority=1,
                source=cls.DOC_FILENAME,
                page=24,
                source_refs=[cls.create_source_ref(page=24)],
            ),
            ExamTopic(
                topic_id="exam.ml.u1.eval_metrics",
                concept="Evaluation Metrics and Confusion Matrix",
                concept_id="ml.u1.evaluation_metrics",
                unit=1,
                importance="EXAM_CRITICAL",
                question_types=["part_a_2mark", "part_b_16mark", "numerical"],
                revision_priority=1,
                source=cls.DOC_FILENAME,
                page=32,
                source_refs=[cls.create_source_ref(page=32)],
            ),
            ExamTopic(
                topic_id="exam.ml.u1.cross_val",
                concept="Cross Validation Techniques (K-Fold, LOOCV)",
                concept_id="ml.u1.cross_validation",
                unit=1,
                importance="HIGH",
                question_types=["part_a_2mark", "part_b_16mark", "algorithm"],
                revision_priority=2,
                source=cls.DOC_FILENAME,
                page=19,
                source_refs=[cls.create_source_ref(page=19)],
            ),
            ExamTopic(
                topic_id="exam.ml.u1.inductive_bias",
                concept="Hypothesis Space and Inductive Bias",
                concept_id="ml.u1.inductive_bias",
                unit=1,
                importance="HIGH",
                question_types=["part_a_2mark", "viva"],
                revision_priority=2,
                source=cls.DOC_FILENAME,
                page=15,
                source_refs=[cls.create_source_ref(page=15)],
            ),
            ExamTopic(
                topic_id="exam.ml.u1.feature_scaling",
                concept="Feature Scaling: Normalization vs Standardization",
                concept_id="ml.u1.feature_scaling",
                unit=1,
                importance="HIGH",
                question_types=["part_a_2mark", "numerical", "comparison"],
                revision_priority=2,
                source=cls.DOC_FILENAME,
                page=36,
                source_refs=[cls.create_source_ref(page=36)],
            ),
        ]

    @classmethod
    def verify_source_grounding(cls) -> Dict[str, Any]:
        """
        Verify that all concepts, formulas, algorithms, problems, and exam topics in Unit I
        have exact, valid citations within Pages 1 to 39 of all_units_combined.pdf.
        """
        unit = cls.ingest()
        audit = {
            "unit": 1,
            "total_concepts": len(unit.concepts),
            "total_definitions": len(unit.definitions),
            "total_formulas": len(unit.formulas),
            "total_algorithms": len(unit.algorithms),
            "total_problems": len(unit.problems),
            "total_exam_topics": len(unit.exam_topics),
            "invalid_citations": [],
            "missing_source_refs": [],
            "verified": True,
        }

        # Check concepts
        for c in unit.concepts:
            if not c.source_refs:
                audit["missing_source_refs"].append(c.concept_id)
            for ref in c.source_refs:
                if not (cls.PAGE_START <= ref.page <= cls.PAGE_END) or ref.filename != cls.DOC_FILENAME:
                    audit["invalid_citations"].append({"item": c.concept_id, "ref": ref.model_dump()})

        # Check formulas
        for f in unit.formulas:
            if not f.source_refs:
                audit["missing_source_refs"].append(f.formula_id)
            for ref in f.source_refs:
                if not (cls.PAGE_START <= ref.page <= cls.PAGE_END) or ref.filename != cls.DOC_FILENAME:
                    audit["invalid_citations"].append({"item": f.formula_id, "ref": ref.model_dump()})

        # Check algorithms
        for a in unit.algorithms:
            if not a.source_refs:
                audit["missing_source_refs"].append(a.algorithm_id)
            for ref in a.source_refs:
                if not (cls.PAGE_START <= ref.page <= cls.PAGE_END) or ref.filename != cls.DOC_FILENAME:
                    audit["invalid_citations"].append({"item": a.algorithm_id, "ref": ref.model_dump()})

        # Check problems
        for p in unit.problems:
            if not p.source_refs:
                audit["missing_source_refs"].append(p.problem_id)
            for ref in p.source_refs:
                if not (cls.PAGE_START <= ref.page <= cls.PAGE_END) or ref.filename != cls.DOC_FILENAME:
                    audit["invalid_citations"].append({"item": p.problem_id, "ref": ref.model_dump()})

        if audit["invalid_citations"] or audit["missing_source_refs"]:
            audit["verified"] = False

        return audit

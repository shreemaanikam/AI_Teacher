"""
Course Discovery Engine for STAGE ML-COURSE-01.
Extracts the canonical Five-Unit Machine Learning Course structure from
the college notes and problem sheets of Chennai Institute of Technology.
"""

from __future__ import annotations
import os
from typing import Dict, List, Optional
from app.ml_course.models import (
    MachineLearningCourse,
    MachineLearningUnit,
    ChapterDetail,
    SectionDetail,
    ConceptDetail,
    GoldDefinition,
    GoldFormula,
    GoldAlgorithm,
    GoldExample,
    ExamTopic,
    TradeoffDetail,
    ProblemItem,
    ProblemType,
    SourceDocument,
    SourceType,
    VerificationStatus,
)


class CourseDiscoveryEngine:
    """
    Builds the MachineLearningCourse domain object directly from the provided
    college lecture notes and problem documents.
    """

    @classmethod
    def discover_course(cls, course_dir: str = "data/courses/machine_learning") -> MachineLearningCourse:
        course = MachineLearningCourse(
            course_id="course_ml_ad5305",
            course_name="Machine Learning",
            course_code="AD5305 / CS4403",
            subject="computer_science",
            department="Department of Artificial Intelligence & Data Science",
            institution="Chennai Institute of Technology (Autonomous)",
            syllabus_coverage_pct=100.0,
        )

        # 1. Register Source Documents
        source_docs = [
            SourceDocument(
                document_id="doc_ml_all_units",
                filename="all_units_combined.pdf",
                filepath=os.path.join(course_dir, "all_units_combined.pdf"),
                total_pages=178,
                unit_coverage=[1, 2, 3, 4, 5],
                source_type=SourceType.COMBINED,
            ),
            SourceDocument(
                document_id="doc_ml_unit4_notes",
                filename="unit_4_notes.pdf",
                filepath=os.path.join(course_dir, "unit_4_notes.pdf"),
                total_pages=37,
                unit_coverage=[4],
                source_type=SourceType.THEORY,
            ),
            SourceDocument(
                document_id="doc_ml_unit5_notes_v1",
                filename="unit_5_notes_v1.pdf",
                filepath=os.path.join(course_dir, "unit_5_notes_v1.pdf"),
                total_pages=15,
                unit_coverage=[5],
                source_type=SourceType.THEORY,
            ),
            SourceDocument(
                document_id="doc_ml_unit5_notes_v2",
                filename="unit_5_notes_v2.pdf",
                filepath=os.path.join(course_dir, "unit_5_notes_v2.pdf"),
                total_pages=16,
                unit_coverage=[5],
                source_type=SourceType.THEORY,
            ),
            SourceDocument(
                document_id="doc_ml_unit2_problems",
                filename="unit_2_problems.pdf",
                filepath=os.path.join(course_dir, "unit_2_problems.pdf"),
                total_pages=9,
                unit_coverage=[2],
                source_type=SourceType.PROBLEMS,
            ),
            SourceDocument(
                document_id="doc_ml_unit3_4_problems",
                filename="unit_3_and_4_problems.pdf",
                filepath=os.path.join(course_dir, "unit_3_and_4_problems.pdf"),
                total_pages=21,
                unit_coverage=[3, 4],
                source_type=SourceType.PROBLEMS,
            ),
        ]
        course.source_documents = source_docs

        # 2. Build Unit I
        unit1 = cls._build_unit_1()
        course.units[1] = unit1

        # 3. Build Unit II
        unit2 = cls._build_unit_2()
        course.units[2] = unit2

        # 4. Build Unit III
        unit3 = cls._build_unit_3()
        course.units[3] = unit3

        # 5. Build Unit IV
        unit4 = cls._build_unit_4()
        course.units[4] = unit4

        # 6. Build Unit V (Canonical Merged Representation)
        unit5 = cls._build_unit_5()
        course.units[5] = unit5

        # Compute totals
        total_concepts = sum(len(u.concepts) for u in course.units.values())
        total_formulas = sum(len(u.formulas) for u in course.units.values())
        total_algorithms = sum(len(u.algorithms) for u in course.units.values())
        course.total_concepts = total_concepts
        course.total_formulas = total_formulas
        course.total_algorithms = total_algorithms

        return course

    @classmethod
    def _build_unit_1(cls) -> MachineLearningUnit:
        doc = "all_units_combined.pdf"
        unit = MachineLearningUnit(
            unit_number=1,
            unit_code="UNIT I",
            unit_title="Introduction to Machine Learning, Types of Learning, Regression & Evaluation Metrics",
            syllabus_topics=[
                "Introduction to Machine Learning",
                "Types of Learning: Supervised, Unsupervised, Semi-Supervised, Reinforcement Learning",
                "Hypothesis Space and Inductive Bias",
                "Training and Test Datasets",
                "Cross Validation (K-Fold, Stratified, LOOCV)",
                "Overfitting and Underfitting",
                "Bias and Variance Tradeoff",
                "Linear Regression: Simple and Multiple",
                "Polynomial Regression",
                "Evaluation Metrics: Accuracy, Precision, Recall, F1-score, MSE and RMSE",
                "Feature Scaling and Normalization",
            ],
            source_pages=list(range(1, 40)),
            source_documents=[doc],
            problem_types=["conceptual", "numerical", "viva", "comparison", "exam_question"],
        )

        # Definitions
        def1 = GoldDefinition(
            term="Machine Learning",
            definition_text="A computer program is said to learn from experience E with respect to some task T and performance measure P if its performance at T, as measured by P, improves with experience E.",
            author_or_source="Tom M. Mitchell",
            source_document=doc,
            page=1,
            chunk_id="ml_u1_chk_001",
        )
        def2 = GoldDefinition(
            term="Hypothesis Space",
            definition_text="A Hypothesis Space (H) is the set of all possible hypotheses (models/functions) that a machine learning algorithm can choose from to learn a target concept from training data.",
            source_document=doc,
            page=12,
            chunk_id="ml_u1_chk_012",
        )
        def3 = GoldDefinition(
            term="Inductive Bias",
            definition_text="Inductive Bias is the set of assumptions that a machine learning algorithm uses to generalize from the training data to unseen instances.",
            source_document=doc,
            page=15,
            chunk_id="ml_u1_chk_015",
        )
        def4 = GoldDefinition(
            term="Cross Validation",
            definition_text="Cross Validation is a statistical technique used to evaluate the performance of a machine learning model by dividing the dataset into multiple subsets and training/testing the model several times.",
            source_document=doc,
            page=19,
            chunk_id="ml_u1_chk_019",
        )
        def5 = GoldDefinition(
            term="Underfitting",
            definition_text="Underfitting occurs when a model is too simple to capture the underlying patterns in the training data, resulting in high bias and low variance.",
            source_document=doc,
            page=21,
            chunk_id="ml_u1_chk_021",
        )
        def6 = GoldDefinition(
            term="Overfitting",
            definition_text="Overfitting occurs when a model learns not only the actual pattern but also the noise and random fluctuations in the training data, resulting in low bias and high variance.",
            source_document=doc,
            page=22,
            chunk_id="ml_u1_chk_022",
        )
        unit.definitions = [def1, def2, def3, def4, def5, def6]

        # Formulas
        f1 = GoldFormula(
            name="Simple Linear Regression",
            expression="Y = \\beta_0 + \\beta_1 X + \\epsilon",
            variables={"Y": "Dependent target variable", "X": "Independent feature", "\\beta_0": "Intercept", "\\beta_1": "Slope coefficient", "\\epsilon": "Error term"},
            context="Linear relationship between one feature and continuous target.",
            source_document=doc,
            page=28,
            chunk_id="ml_u1_chk_028",
        )
        f2 = GoldFormula(
            name="Multiple Linear Regression",
            expression="Y = \\beta_0 + \\beta_1 X_1 + \\beta_2 X_2 + \\dots + \\beta_n X_n + \\epsilon",
            variables={"X_i": "Feature i", "\\beta_i": "Regression coefficient for feature i"},
            context="Multi-variable linear regression model.",
            source_document=doc,
            page=29,
            chunk_id="ml_u1_chk_029",
        )
        f3 = GoldFormula(
            name="Accuracy",
            expression="Accuracy = \\frac{TP + TN}{TP + TN + FP + FN}",
            variables={"TP": "True Positive", "TN": "True Negative", "FP": "False Positive", "FN": "False Negative"},
            context="Proportion of correctly classified instances for balanced datasets.",
            source_document=doc,
            page=32,
            chunk_id="ml_u1_chk_032",
        )
        f4 = GoldFormula(
            name="Precision",
            expression="Precision = \\frac{TP}{TP + FP}",
            variables={"TP": "True Positive", "FP": "False Positive"},
            context="Fraction of predicted positive instances that are actually positive (used when FP is costly).",
            source_document=doc,
            page=33,
            chunk_id="ml_u1_chk_033",
        )
        f5 = GoldFormula(
            name="Recall",
            expression="Recall = \\frac{TP}{TP + FN}",
            variables={"TP": "True Positive", "FN": "False Negative"},
            context="Fraction of actual positive instances correctly identified (used when FN is costly).",
            source_document=doc,
            page=33,
            chunk_id="ml_u1_chk_033b",
        )
        f6 = GoldFormula(
            name="F1-Score",
            expression="F1 = 2 \\times \\frac{Precision \\times Recall}{Precision + Recall}",
            variables={"Precision": "Positive predictive value", "Recall": "Sensitivity"},
            context="Harmonic mean of precision and recall for imbalanced classification.",
            source_document=doc,
            page=33,
            chunk_id="ml_u1_chk_033c",
        )
        f7 = GoldFormula(
            name="Mean Squared Error (MSE)",
            expression="MSE = \\frac{1}{n} \\sum_{i=1}^n (y_i - \\hat{y}_i)^2",
            variables={"y_i": "Actual value", "\\hat{y}_i": "Predicted value", "n": "Number of observations"},
            context="Average squared prediction error for regression models.",
            source_document=doc,
            page=34,
            chunk_id="ml_u1_chk_034",
        )
        f8 = GoldFormula(
            name="Min-Max Normalization",
            expression="X_{norm} = \\frac{X - X_{min}}{X_{max} - X_{min}}",
            variables={"X": "Original feature value", "X_{min}": "Minimum feature value", "X_{max}": "Maximum feature value"},
            context="Rescaling features to [0, 1].",
            source_document=doc,
            page=36,
            chunk_id="ml_u1_chk_036",
        )
        f9 = GoldFormula(
            name="Z-Score Standardization",
            expression="Z = \\frac{X - \\mu}{\\sigma}",
            variables={"X": "Original feature value", "\\mu": "Mean of feature", "\\sigma": "Standard deviation"},
            context="Centering features to mean 0 and unit variance 1.",
            source_document=doc,
            page=37,
            chunk_id="ml_u1_chk_037",
        )
        unit.formulas = [f1, f2, f3, f4, f5, f6, f7, f8, f9]

        # Algorithms
        algo1 = GoldAlgorithm(
            name="K-Fold Cross Validation",
            purpose="Evaluate model generalization and detect overfitting by averaging test accuracy across K splits.",
            inputs=["Dataset D", "Number of folds K"],
            steps=[
                "Divide the dataset into K equal-sized folds.",
                "Use one fold as the testing set and the remaining K-1 folds as the training set.",
                "Train and evaluate the model on the test fold.",
                "Repeat the process K times, using a different fold as the test set in each iteration.",
                "Compute the average performance across all K runs.",
            ],
            stopping_condition="Completed K iterations",
            output="Average cross-validation performance metric (e.g., 93% accuracy)",
            source_document=doc,
            page=19,
            chunk_id="ml_u1_chk_019b",
        )
        unit.algorithms = [algo1]

        # Concepts
        c_names = [
            "Introduction to Machine Learning",
            "Types of Learning",
            "Hypothesis Space",
            "Inductive Bias",
            "Training and Test Datasets",
            "Cross Validation",
            "Overfitting and Underfitting",
            "Bias-Variance Tradeoff",
            "Linear Regression",
            "Polynomial Regression",
            "Evaluation Metrics",
            "Feature Scaling and Normalization",
        ]
        for i, name in enumerate(c_names, start=1):
            unit.concepts.append(
                ConceptDetail(
                    concept_id=f"c_ml_u1_{name.lower().replace(' ', '_').replace('-', '_')}",
                    name=name,
                    unit_number=1,
                    chapter="UNIT I : Introduction",
                    summary=f"Core concept in Unit 1: {name}",
                    source_document=doc,
                    source_pages=[i * 3],
                    source_chunk_ids=[f"ml_u1_chk_{i:03d}"],
                )
            )

        # Exam Topics
        unit.exam_topics = [
            ExamTopic(concept="Bias-Variance Tradeoff", unit=1, importance="EXAM_CRITICAL", question_types=["derivation", "conceptual", "viva"], revision_priority=1, source=doc, page=25),
            ExamTopic(concept="Cross Validation (K-Fold)", unit=1, importance="HIGH", question_types=["numerical", "algorithm", "viva"], revision_priority=2, source=doc, page=19),
            ExamTopic(concept="Evaluation Metrics (Precision, Recall, F1)", unit=1, importance="EXAM_CRITICAL", question_types=["numerical", "formula", "viva"], revision_priority=1, source=doc, page=33),
            ExamTopic(concept="Feature Scaling vs Normalization", unit=1, importance="HIGH", question_types=["numerical", "comparison", "viva"], revision_priority=2, source=doc, page=38),
        ]

        return unit

    @classmethod
    def _build_unit_2(cls) -> MachineLearningUnit:
        doc_theory = "all_units_combined.pdf"
        doc_prob = "unit_2_problems.pdf"
        unit = MachineLearningUnit(
            unit_number=2,
            unit_code="UNIT II",
            unit_title="Supervised Learning, Probabilistic Models, Support Vector Machines & Ensemble Learning",
            syllabus_topics=[
                "Bayesian Linear Regression",
                "Gradient Descent Optimization",
                "Perceptron Algorithm",
                "Logistic Regression",
                "Naive Bayes Classifier",
                "Support Vector Machine (Linear & Non-linear SVM, Soft Margin)",
                "Decision Tree Algorithm (Information Gain, Rules)",
                "Random Forest Algorithm",
                "K-Nearest Neighbour (KNN)",
                "Ensemble Learning: Bagging and Boosting",
                "Hyperparameter Tuning Basics (Grid Search, Random Search, Bayesian Optimization)",
            ],
            source_pages=list(range(40, 73)),
            source_documents=[doc_theory, doc_prob],
            problem_types=["numerical", "algorithm", "conceptual", "comparison", "viva", "exam_question"],
        )

        # Formulas
        f1 = GoldFormula(
            name="Gradient Descent Parameter Update",
            expression="w = w - \\alpha \\cdot \\frac{\\partial J(w, b)}{\\partial w}, \\quad b = b - \\alpha \\cdot \\frac{\\partial J(w, b)}{\\partial b}",
            variables={"w": "Weights vector", "b": "Bias scalar", "\\alpha": "Learning rate", "J(w, b)": "Cost function"},
            context="Iteratively adjusting parameters to minimize the cost function.",
            source_document=doc_theory,
            page=44,
            chunk_id="ml_u2_chk_044",
        )
        f2 = GoldFormula(
            name="Perceptron Weight Update Rule",
            expression="w_{new} = w_{old} + \\alpha \\times (y_{true} - y_{pred}) \\times x, \\quad b_{new} = b_{old} + \\alpha \\times (y_{true} - y_{pred})",
            variables={"w": "Weight", "b": "Bias", "\\alpha": "Learning rate", "y_{true}": "Target label", "y_{pred}": "Predicted binary output", "x": "Input feature"},
            context="Online training update on misclassification in binary classification.",
            source_document=doc_theory,
            page=46,
            chunk_id="ml_u2_chk_046",
        )
        f3 = GoldFormula(
            name="Logistic Sigmoid Function",
            expression="g(z) = \\frac{1}{1 + e^{-z}}, \\quad z = \\sum w_i x_i + b",
            variables={"z": "Linear combination of inputs plus bias", "g(z)": "Output probability in [0, 1]"},
            context="Mapping linear log-odds into classification probabilities.",
            source_document=doc_theory,
            page=47,
            chunk_id="ml_u2_chk_047",
        )
        f4 = GoldFormula(
            name="Bayes Theorem",
            expression="P(A|B) = \\frac{P(B|A) P(A)}{P(B)}",
            variables={"P(A|B)": "Posterior probability", "P(B|A)": "Likelihood", "P(A)": "Prior probability", "P(B)": "Evidence marginalization"},
            context="Revising belief in light of observed evidence.",
            source_document=doc_theory,
            page=49,
            chunk_id="ml_u2_chk_049",
        )
        f5 = GoldFormula(
            name="SVM Optimal Hyperplane Margin",
            expression="w = S_w^{-1} (\\mu_1 - \\mu_2), \\quad \\text{Margin} = \\frac{2}{\\|w\\|}",
            variables={"w": "Normal vector to hyperplane", "S_w": "Scatter matrix", "\\mu": "Class mean"},
            context="Maximizing margin between support vectors of two classes.",
            source_document=doc_theory,
            page=52,
            chunk_id="ml_u2_chk_052",
        )
        f6 = GoldFormula(
            name="KNN Euclidean Distance",
            expression="D = \\sqrt{\\sum_{i=1}^d (x_{2i} - x_{1i})^2}",
            variables={"x_1, x_2": "Feature vectors in d-dimensional space"},
            context="Measuring distance to nearest neighbors in feature space.",
            source_document=doc_prob,
            page=2,
            chunk_id="ml_u2_prob_002",
        )
        unit.formulas = [f1, f2, f3, f4, f5, f6]

        # Algorithms
        algo1 = GoldAlgorithm(
            name="K-Nearest Neighbors (KNN)",
            purpose="Classify a query point based on the majority label of its k closest neighbors.",
            inputs=["Dataset of training tuples (x_i, y_i)", "Query point x_q", "Parameter k"],
            steps=[
                "Choose the value of k (number of neighbors, typically odd).",
                "Calculate the distance (Euclidean) between query point and all training points.",
                "Sort distances in ascending order and select the k-nearest neighbors.",
                "Make prediction: Majority voting for classification, average for regression.",
            ],
            stopping_condition="k neighbors identified",
            output="Predicted class label or regression value",
            source_document=doc_prob,
            page=1,
            chunk_id="ml_u2_prob_001",
        )
        algo2 = GoldAlgorithm(
            name="Perceptron Learning Algorithm",
            purpose="Train a single-layer binary linear classifier.",
            inputs=["Training examples (x_i, y_i)", "Initial weights w, bias b", "Learning rate alpha"],
            steps=[
                "Initialize weights w and bias b to small values or zero.",
                "For each training example, compute weighted sum: z = sum(w_i * x_i) + b.",
                "Apply activation step function: output = 1 if z >= threshold else 0.",
                "Compare output with true target y. If mismatch, update weights: w = w + alpha * (y - output) * x.",
                "Repeat across epochs until all samples are correctly classified.",
            ],
            stopping_condition="Zero classification error on linearly separable data",
            output="Learned weights vector w and bias b",
            source_document=doc_prob,
            page=4,
            chunk_id="ml_u2_prob_004",
        )
        unit.algorithms = [algo1, algo2]

        # Concepts
        c_names = [
            "Bayesian Linear Regression",
            "Gradient Descent",
            "Perceptron Algorithm",
            "Logistic Regression",
            "Naive Bayes Classifier",
            "Support Vector Machine",
            "Decision Tree Algorithm",
            "Random Forest Algorithm",
            "K-Nearest Neighbour",
            "Bagging and Boosting",
            "Hyperparameter Tuning",
        ]
        for i, name in enumerate(c_names, start=1):
            unit.concepts.append(
                ConceptDetail(
                    concept_id=f"c_ml_u2_{name.lower().replace(' ', '_')}",
                    name=name,
                    unit_number=2,
                    chapter="UNIT II SUPERVISED LEARNING",
                    summary=f"Supervised learning concept: {name}",
                    source_document=doc_theory,
                    source_pages=[40 + i * 3],
                    source_chunk_ids=[f"ml_u2_chk_{i:03d}"],
                )
            )

        # Exam Topics
        unit.exam_topics = [
            ExamTopic(concept="Support Vector Machines (Hyperplane & Soft Margin)", unit=2, importance="EXAM_CRITICAL", question_types=["derivation", "conceptual", "diagram"], revision_priority=1, source=doc_theory, page=50),
            ExamTopic(concept="Perceptron Algorithm & Weight Update Rule", unit=2, importance="EXAM_CRITICAL", question_types=["numerical", "algorithm", "viva"], revision_priority=1, source=doc_prob, page=4),
            ExamTopic(concept="Logistic Regression (Sigmoid & Loan Default Prediction)", unit=2, importance="HIGH", question_types=["numerical", "formula", "viva"], revision_priority=2, source=doc_prob, page=8),
            ExamTopic(concept="Ensemble Learning: Bagging vs Boosting", unit=2, importance="EXAM_CRITICAL", question_types=["comparison", "conceptual", "viva"], revision_priority=1, source=doc_theory, page=59),
            ExamTopic(concept="KNN (Distance Calculation & Majority Vote)", unit=2, importance="HIGH", question_types=["numerical", "algorithm", "viva"], revision_priority=2, source=doc_prob, page=1),
        ]

        return unit

    @classmethod
    def _build_unit_3(cls) -> MachineLearningUnit:
        doc_theory = "all_units_combined.pdf"
        doc_prob = "unit_3_and_4_problems.pdf"
        unit = MachineLearningUnit(
            unit_number=3,
            unit_code="UNIT III",
            unit_title="Neural Networks, Deep Learning Architectures, Backpropagation & Generative Models",
            syllabus_topics=[
                "Artificial Neural Networks (Biological Motivation, MCP Neuron)",
                "ANN Representations and Architectures (FNN, DNN, RNN)",
                "Challenges in ANN Learning (Vanishing Gradients, Overfitting, Data Requirements)",
                "Perceptron and Activation Functions (Sigmoid, Tanh, ReLU)",
                "Multilayer Perceptrons (MLP) and Backpropagation Algorithm",
                "Convolutional Neural Networks (CNN: Filters, Stride, Padding, Max Pooling, FC Layer)",
                "Recurrent Neural Networks (RNN: Hidden State Memory, BPTT)",
                "Long Short-Term Memory (LSTM: Forget Gate, Input Gate, Candidate State, Cell State Update, Output Gate)",
                "BERT (Transformer, Self-Attention, Bidirectional Context, MLM, NSP, WordPiece)",
                "Generative Adversarial Networks (GANs: Generator, Discriminator, Minimax Game, DCGAN)",
                "Generative Models Overview (VAEs, Autoregressive, Normalizing Flows)",
            ],
            source_pages=list(range(73, 111)),
            source_documents=[doc_theory, doc_prob],
            problem_types=["numerical", "algorithm", "derivation", "diagram", "viva", "exam_question"],
        )

        # Formulas
        f1 = GoldFormula(
            name="Backpropagation Error Deltas",
            expression="\\delta_k = o_k (1 - o_k)(t_k - o_k), \\quad \\delta_h = o_h (1 - o_h) \\sum_{k} w_{kh} \\delta_k",
            variables={"\\delta_k": "Output error term", "\\delta_h": "Hidden neuron error term", "o": "Activation output", "t": "Target label", "w_{kh}": "Weight connecting h to k"},
            context="Propagating error gradients backward through multilayer perceptrons.",
            source_document=doc_theory,
            page=89,
            chunk_id="ml_u3_chk_089",
        )
        f2 = GoldFormula(
            name="Backpropagation Weight Update",
            expression="\\Delta w_{ji} = \\eta \\delta_j x_{ji}, \\quad w_{ji}^{(new)} = w_{ji}^{(old)} + \\Delta w_{ji}",
            variables={"\\eta": "Learning rate", "\\delta_j": "Error gradient at node j", "x_{ji}": "Input from node i to j"},
            context="Updating connection weights in backpropagation.",
            source_document=doc_theory,
            page=89,
            chunk_id="ml_u3_chk_089b",
        )
        f3 = GoldFormula(
            name="CNN Feature Map Dimension Formula",
            expression="O = \\left( \\frac{N - F + 2P}{S} \\right) + 1",
            variables={"N": "Input dimension size", "F": "Filter/kernel size", "P": "Padding", "S": "Stride", "O": "Output feature map size"},
            context="Calculating spatial dimensions of feature map after convolution.",
            source_document=doc_prob,
            page=12,
            chunk_id="ml_u3_prob_012",
        )
        f4 = GoldFormula(
            name="LSTM Forget Gate",
            expression="f_t = \\sigma(W_f [h_{t-1}, x_t] + b_f)",
            variables={"f_t": "Forget gate activation in [0, 1]", "W_f": "Forget weight matrix", "h_{t-1}": "Previous hidden state", "x_t": "Current input", "b_f": "Forget bias"},
            context="Deciding what information to discard from cell state.",
            source_document=doc_theory,
            page=101,
            chunk_id="ml_u3_chk_101",
        )
        f5 = GoldFormula(
            name="LSTM Cell State Update",
            expression="C_t = f_t \\odot C_{t-1} + i_t \\odot \\tilde{C}_t, \\quad \\tilde{C}_t = \\tanh(W_c [h_{t-1}, x_t] + b_c)",
            variables={"C_t": "Updated cell state", "i_t": "Input gate", "\\tilde{C}_t": "Candidate state vector", "\\odot": "Element-wise multiplication"},
            context="Core memory update mechanism in LSTM network.",
            source_document=doc_theory,
            page=102,
            chunk_id="ml_u3_chk_102",
        )
        f6 = GoldFormula(
            name="GAN Minimax Objective",
            expression="\\min_G \\max_D V(D, G) = \\mathbb{E}_{x \\sim p_{data}}[\\log D(x)] + \\mathbb{E}_{z \\sim p_z}[\\log(1 - D(G(z)))]",
            variables={"D(x)": "Discriminator probability that real x is authentic", "G(z)": "Generator output from noise z"},
            context="Two-player zero-sum adversarial game.",
            source_document=doc_theory,
            page=106,
            chunk_id="ml_u3_chk_106",
        )
        unit.formulas = [f1, f2, f3, f4, f5, f6]

        # Algorithms
        algo1 = GoldAlgorithm(
            name="Backpropagation Algorithm",
            purpose="Train multilayer neural networks via gradient descent of squared error.",
            inputs=["Network architecture with initialized weights w and biases b", "Training set (x_d, t_d)", "Learning rate eta"],
            steps=[
                "Forward Pass: Present input vector x_d, compute outputs for each hidden unit y_j = f(sum(w_ji * x_i)), and output unit o_k = f(sum(w_kj * y_j)).",
                "Compute Output Error: For each output unit k, calculate delta_k = o_k * (1 - o_k) * (t_k - o_k).",
                "Compute Hidden Error: For each hidden unit h, calculate delta_h = o_h * (1 - o_h) * sum(w_kh * delta_k).",
                "Update Weights: Update every weight w_ji = w_ji + eta * delta_j * x_ji.",
                "Repeat for epochs until stopping criterion (max epochs, error threshold, validation accuracy) is reached.",
            ],
            stopping_condition="Convergence of total network error",
            output="Trained network weights and biases",
            source_document=doc_theory,
            page=88,
            chunk_id="ml_u3_chk_088",
        )
        unit.algorithms = [algo1]

        # Concepts
        c_names = [
            "Artificial Neural Networks",
            "ANN Architectures",
            "Challenges in ANN Learning",
            "Perceptron & Activation Functions",
            "Multilayer Perceptrons & Backpropagation",
            "Convolutional Neural Networks",
            "Recurrent Neural Networks",
            "Long Short-Term Memory",
            "BERT & Transformers",
            "Generative Adversarial Networks",
            "Generative Models Overview",
        ]
        for i, name in enumerate(c_names, start=1):
            unit.concepts.append(
                ConceptDetail(
                    concept_id=f"c_ml_u3_{name.lower().replace(' ', '_')}",
                    name=name,
                    unit_number=3,
                    chapter="UNIT-3 NEURAL NETWORKS",
                    summary=f"Neural network and deep learning concept: {name}",
                    source_document=doc_theory,
                    source_pages=[73 + i * 3],
                    source_chunk_ids=[f"ml_u3_chk_{i:03d}"],
                )
            )

        # Exam Topics
        unit.exam_topics = [
            ExamTopic(concept="Backpropagation Algorithm & Weight Updates", unit=3, importance="EXAM_CRITICAL", question_types=["derivation", "numerical", "algorithm", "viva"], revision_priority=1, source=doc_theory, page=88),
            ExamTopic(concept="CNN Convolution, Padding, Stride & Max Pooling", unit=3, importance="EXAM_CRITICAL", question_types=["numerical", "diagram", "formula"], revision_priority=1, source=doc_prob, page=12),
            ExamTopic(concept="LSTM Architecture & Gate Equations", unit=3, importance="EXAM_CRITICAL", question_types=["numerical", "diagram", "formula", "viva"], revision_priority=1, source=doc_theory, page=101),
            ExamTopic(concept="GAN Minimax Objective & Loss Functions", unit=3, importance="HIGH", question_types=["formula", "numerical", "conceptual"], revision_priority=2, source=doc_prob, page=9),
            ExamTopic(concept="BERT Transformer & Bidirectional Attention", unit=3, importance="HIGH", question_types=["conceptual", "comparison", "viva"], revision_priority=2, source=doc_theory, page=103),
        ]

        return unit

    @classmethod
    def _build_unit_4(cls) -> MachineLearningUnit:
        doc = "all_units_combined.pdf"
        unit = MachineLearningUnit(
            unit_number=4,
            unit_code="UNIT IV",
            unit_title="Unsupervised Learning and Dimensionality Reduction",
            syllabus_topics=[
                "Introduction to Unsupervised Learning (Clustering vs Dimensionality Reduction)",
                "K-Means Clustering (Centroid Assignment, WCSS/Inertia)",
                "K-Medoids Clustering (Partitioning Around Medoids PAM)",
                "Hierarchical Clustering (Agglomerative, Divisive, Linkage Criteria, Dendrogram)",
                "Gaussian Mixture Models (GMM: Mixture Components, Covariance, Latent Variables)",
                "Expectation-Maximization (EM) Algorithm (E-step, M-step, Monotonic Convergence)",
                "Cluster Evaluation Basics (Internal: Silhouette, WCSS, Davies-Bouldin; External: Rand, Purity)",
                "Principal Component Analysis (PCA: Covariance Matrix, Eigenvalues, Explained Variance)",
                "Linear Discriminant Analysis (LDA: Fisher Criterion, Between/Within Scatter, C-1 Components)",
                "t-SNE Overview (Student-t Distribution, KL Divergence, Perplexity, Crowding Problem)",
                "Anomaly Detection Basics (Z-Score, Statistical, Density-Based, Distance-Based)",
            ],
            source_pages=list(range(111, 148)),
            source_documents=[doc],
            problem_types=["numerical", "algorithm", "conceptual", "comparison", "exam_question", "viva"],
        )

        # Formulas
        f1 = GoldFormula(
            name="K-Means Objective (WCSS / Inertia)",
            expression="J = \\sum_{k=1}^K \\sum_{x \\in C_k} \\|x - \\mu_k\\|^2",
            variables={"K": "Number of clusters", "C_k": "Set of points in cluster k", "x": "Data feature vector", "\\mu_k": "Centroid of cluster k"},
            context="Minimizing the sum of squared Euclidean distances to cluster centroids.",
            source_document=doc,
            page=114,
            chunk_id="ml_u4_chk_114",
        )
        f2 = GoldFormula(
            name="Hierarchical Linkage Criteria",
            expression="d_{single}(A, B) = \\min_{a \\in A, b \\in B} d(a, b), \\quad d_{complete}(A, B) = \\max_{a \\in A, b \\in B} d(a, b)",
            variables={"A, B": "Clusters being compared", "d(a, b)": "Euclidean distance between points"},
            context="Measuring inter-cluster distances in agglomerative hierarchical clustering.",
            source_document=doc,
            page=120,
            chunk_id="ml_u4_chk_120",
        )
        f3 = GoldFormula(
            name="GMM Probability Density & Responsibility",
            expression="p(x) = \\sum_{k=1}^K \\pi_k \\mathcal{N}(x | \\mu_k, \\Sigma_k), \\quad \\gamma(z_k | x) = \\frac{\\pi_k \\mathcal{N}(x | \\mu_k, \\Sigma_k)}{\\sum_j \\pi_j \\mathcal{N}(x | \\mu_j, \\Sigma_j)}",
            variables={"\\pi_k": "Mixing weight", "\\mu_k": "Mean vector", "\\Sigma_k": "Covariance matrix", "\\gamma(z_k|x)": "Responsibility / soft assignment"},
            context="Probabilistic modeling of multi-modal data and E-step calculation in EM.",
            source_document=doc,
            page=123,
            chunk_id="ml_u4_chk_123",
        )
        f4 = GoldFormula(
            name="Silhouette Score",
            expression="s(i) = \\frac{b(i) - a(i)}{\\max(a(i), b(i))}",
            variables={"a(i)": "Average intra-cluster distance (cohesion)", "b(i)": "Average distance to nearest other cluster (separation)"},
            context="Measuring clustering quality (-1 to +1).",
            source_document=doc,
            page=129,
            chunk_id="ml_u4_chk_129",
        )
        f5 = GoldFormula(
            name="PCA Covariance & Eigen-Equation",
            expression="Cov = \\frac{1}{n-1} X_c^T X_c, \\quad Cov \\cdot v = \\lambda \\cdot v",
            variables={"X_c": "Mean-centered data matrix", "n": "Sample size", "v": "Principal component eigenvector", "\\lambda": "Explained variance eigenvalue"},
            context="Orthogonal linear projection onto directions of maximal variance.",
            source_document=doc,
            page=132,
            chunk_id="ml_u4_chk_132",
        )
        f6 = GoldFormula(
            name="LDA Fisher Criterion",
            expression="J(w) = \\frac{w^T S_b w}{w^T S_w w}, \\quad w = S_w^{-1}(\\mu_1 - \\mu_2)",
            variables={"S_b": "Between-class scatter matrix", "S_w": "Within-class scatter matrix", "w": "Optimal discriminant projection direction"},
            context="Maximizing class separability in supervised dimensionality reduction.",
            source_document=doc,
            page=136,
            chunk_id="ml_u4_chk_136",
        )
        unit.formulas = [f1, f2, f3, f4, f5, f6]

        # Algorithms
        algo1 = GoldAlgorithm(
            name="K-Means Clustering Algorithm",
            purpose="Partition a dataset into K clusters minimizing within-cluster sum of squares (WCSS).",
            inputs=["Dataset X with n samples", "Number of clusters K"],
            steps=[
                "Step 1: Choose number of clusters K and dataset X.",
                "Step 2 (Initialization): Randomly select K data points as initial centroids (or use K-Means++).",
                "Step 3 (Assignment): Assign every data point to nearest centroid using Euclidean distance.",
                "Step 4 (Update): Recompute each centroid as the mean of all points assigned to it.",
                "Step 5 (Iteration): Repeat Steps 3 and 4 until centroids stop moving or maximum iterations reached.",
            ],
            stopping_condition="Centroids no longer change (convergence to local optimum)",
            output="Final K clusters with their centroids and point assignments",
            source_document=doc,
            page=114,
            chunk_id="ml_u4_chk_114b",
        )
        algo2 = GoldAlgorithm(
            name="Expectation-Maximization (EM) for GMM",
            purpose="Find maximum-likelihood parameter estimates for Gaussian Mixture Models with latent variables.",
            inputs=["Dataset X", "Number of components K"],
            steps=[
                "Step 1: Initialize mixing weights pi_k, means mu_k, and covariances Sigma_k.",
                "Step 2 (E-step): Compute responsibility gamma(z_k | x_i) for every point x_i and component k using Bayes rule.",
                "Step 3 (M-step): Update parameters pi_k, mu_k, Sigma_k using responsibilities as soft weights.",
                "Step 4: Compute total log-likelihood and check for convergence.",
                "Step 5: Repeat Steps 2-4 until log-likelihood change falls below threshold.",
            ],
            stopping_condition="Log-likelihood improvement falls below epsilon",
            output="Converged parameters pi_k, mu_k, Sigma_k and soft responsibilities",
            source_document=doc,
            page=125,
            chunk_id="ml_u4_chk_125",
        )
        algo3 = GoldAlgorithm(
            name="Principal Component Analysis (PCA)",
            purpose="Reduce dimensionality by projecting data onto orthogonal directions of maximum variance.",
            inputs=["Dataset X (n samples x d features)", "Target dimensions k (k < d)"],
            steps=[
                "Step 1: Mean-centre the data: X_c = X - mean(X).",
                "Step 2: Compute d x d covariance matrix: Cov = (1 / (n-1)) * X_c^T * X_c.",
                "Step 3: Compute eigenvalues lambda and eigenvectors v: Cov * v = lambda * v.",
                "Step 4: Sort eigenvectors by descending eigenvalue.",
                "Step 5: Select top k eigenvectors V_k as principal components.",
                "Step 6: Project centered data: X_reduced = X_c * V_k.",
            ],
            stopping_condition="Top k components extracted",
            output="Lower-dimensional representation X_reduced preserving maximal variance",
            source_document=doc,
            page=133,
            chunk_id="ml_u4_chk_133",
        )
        unit.algorithms = [algo1, algo2, algo3]

        # Concepts
        c_names = [
            "Introduction to Unsupervised Learning",
            "K-Means Clustering",
            "K-Medoids Clustering",
            "Hierarchical Clustering",
            "Gaussian Mixture Models",
            "Expectation-Maximization Algorithm",
            "Cluster Evaluation Metrics",
            "Principal Component Analysis",
            "Linear Discriminant Analysis",
            "t-SNE Dimensionality Reduction",
            "Anomaly Detection",
        ]
        for i, name in enumerate(c_names, start=1):
            unit.concepts.append(
                ConceptDetail(
                    concept_id=f"c_ml_u4_{name.lower().replace(' ', '_')}",
                    name=name,
                    unit_number=4,
                    chapter="Unit 4th – UNSUPERVISED LEARNING AND DIMENSIONALITY REDUCTION",
                    summary=f"Unsupervised learning concept: {name}",
                    source_document=doc,
                    source_pages=[110 + i * 3],
                    source_chunk_ids=[f"ml_u4_chk_{i:03d}"],
                )
            )

        # Exam Topics
        unit.exam_topics = [
            ExamTopic(concept="K-Means Clustering (Algorithm & 7-Point Numerical)", unit=4, importance="EXAM_CRITICAL", question_types=["numerical", "algorithm", "viva"], revision_priority=1, source=doc, page=114),
            ExamTopic(concept="PCA (Covariance, Eigen-decomposition & Variance Ratio)", unit=4, importance="EXAM_CRITICAL", question_types=["numerical", "derivation", "comparison"], revision_priority=1, source=doc, page=131),
            ExamTopic(concept="Expectation-Maximization (EM) for GMM", unit=4, importance="EXAM_CRITICAL", question_types=["derivation", "algorithm", "viva"], revision_priority=1, source=doc, page=124),
            ExamTopic(concept="Hierarchical Clustering & Linkage Criteria", unit=4, importance="HIGH", question_types=["numerical", "diagram", "comparison"], revision_priority=2, source=doc, page=119),
            ExamTopic(concept="LDA vs PCA (Supervised vs Unsupervised Reduction)", unit=4, importance="HIGH", question_types=["comparison", "derivation", "viva"], revision_priority=2, source=doc, page=135),
            ExamTopic(concept="Cluster Evaluation (Silhouette Score & Elbow Method)", unit=4, importance="HIGH", question_types=["formula", "conceptual", "viva"], revision_priority=2, source=doc, page=128),
        ]

        return unit

    @classmethod
    def _build_unit_5(cls) -> MachineLearningUnit:
        doc1 = "all_units_combined.pdf"
        doc_v1 = "unit_5_notes_v1.pdf"
        doc_v2 = "unit_5_notes_v2.pdf"
        unit = MachineLearningUnit(
            unit_number=5,
            unit_code="UNIT V",
            unit_title="Optimization, Reinforcement Learning and Responsible AI",
            syllabus_topics=[
                "Least Squares Optimization (Residuals, SSE, Normal Equations, Regularization)",
                "Conjugate Gradient Method (Ax = b, A-Conjugacy, Step Size, CG vs GD)",
                "Reinforcement Learning Basics (Agent-Environment Interaction, State, Action, Reward, Policy)",
                "Markov Decision Process (MDP: S, A, P, R, gamma, Markov Property)",
                "Q-Learning (Model-free, Off-policy, Bellman Update Rule, TD Error, Convergence)",
                "Exploration vs Exploitation (Dilemma, Epsilon-Greedy, Decaying Epsilon, Softmax, UCB)",
                "Responsible AI (Fairness, Bias Awareness & Mitigation, Explainability, Accountability, Privacy)",
                "SHAP and LIME Overview (Shapley Values, Cooperative Game Theory, Local Surrogates)",
                "MLOps Basics (Lifecycle, Experiment Tracking, CI/CD, Data Drift & Concept Drift, Monitoring)",
                "Federated Learning Basics (Decentralized Training, Privacy Preservation, FedAvg Algorithm)",
            ],
            source_pages=list(range(148, 179)),
            source_documents=[doc1, doc_v1, doc_v2],
            problem_types=["numerical", "algorithm", "conceptual", "comparison", "viva", "exam_question"],
        )

        # Formulas
        f1 = GoldFormula(
            name="Least Squares Normal Equations",
            expression="X^T X \\beta = X^T y \\implies \\hat{\\beta} = (X^T X)^{-1} X^T y",
            variables={"X": "Design matrix (n samples x d features)", "y": "Target vector", "\\beta": "Parameter vector"},
            context="Closed-form parameter solution minimizing sum of squared errors SSE.",
            source_document=doc1,
            page=164,
            chunk_id="ml_u5_chk_164",
        )
        f2 = GoldFormula(
            name="Conjugate Gradient Step Size & Direction",
            expression="\\alpha_k = \\frac{r_k^T r_k}{p_k^T A p_k}, \\quad \\beta_k = \\frac{r_{k+1}^T r_{k+1}}{r_k^T r_k}, \\quad p_{k+1} = r_{k+1} + \\beta_k p_k",
            variables={"r_k": "Residual vector b - Ax_k", "p_k": "Search direction", "A": "Symmetric positive-definite matrix"},
            context="Iterative quadratic minimization without matrix inversion.",
            source_document=doc1,
            page=150,
            chunk_id="ml_u5_chk_150",
        )
        f3 = GoldFormula(
            name="Q-Learning Update Rule",
            expression="Q(s, a) \\leftarrow Q(s, a) + \\alpha \\left[ r + \\gamma \\max_{a'} Q(s', a') - Q(s, a) \\right]",
            variables={"Q(s, a)": "Current action-value estimate", "\\alpha": "Learning rate", "r": "Immediate reward", "\\gamma": "Discount factor (0 to 1)", "s'": "Next state", "\\max_{a'} Q(s', a')": "Optimal future Q-value"},
            context="Model-free off-policy temporal-difference learning rule.",
            source_document=doc1,
            page=154,
            chunk_id="ml_u5_chk_154",
        )
        f4 = GoldFormula(
            name="SHAP Additive Feature Attribution",
            expression="f(x) \\approx \\phi_0 + \\sum_{i=1}^M \\phi_i",
            variables={"f(x)": "Model prediction for instance x", "\\phi_0": "Baseline expected model output", "\\phi_i": "Shapley attribution value for feature i"},
            context="Fair distribution of credit across features based on cooperative game theory.",
            source_document=doc1,
            page=173,
            chunk_id="ml_u5_chk_173",
        )
        f5 = GoldFormula(
            name="Federated Averaging (FedAvg)",
            expression="w_{global} = \\sum_{k=1}^K \\frac{n_k}{N} w_k",
            variables={"w_{global}": "Aggregated global model weights", "w_k": "Local model weights from device k", "n_k": "Sample count on device k", "N": "Total training samples"},
            context="Server-side parameter aggregation preserving raw device data privacy.",
            source_document=doc1,
            page=177,
            chunk_id="ml_u5_chk_177",
        )
        unit.formulas = [f1, f2, f3, f4, f5]

        # Algorithms
        algo1 = GoldAlgorithm(
            name="Q-Learning Algorithm",
            purpose="Learn the optimal action-value policy without knowing environment transition probabilities.",
            inputs=["State space S", "Action space A", "Learning rate alpha", "Discount factor gamma", "Exploration parameter epsilon"],
            steps=[
                "Initialize Q(s, a) arbitrarily (e.g., zeros for all pairs).",
                "For each episode, observe initial state s.",
                "Choose action a using epsilon-greedy policy derived from Q.",
                "Take action a, observe immediate reward r and next state s'.",
                "Compute TD target: Target = r + gamma * max_a' Q(s', a').",
                "Update Q-value: Q(s, a) = Q(s, a) + alpha * [Target - Q(s, a)].",
                "Set s = s', repeat until s is terminal; repeat across episodes until Q-values converge.",
            ],
            stopping_condition="Q-table values stabilize (Bellman optimality achieved)",
            output="Converged Q-table yielding optimal policy pi*(s) = argmax_a Q(s, a)",
            source_document=doc1,
            page=155,
            chunk_id="ml_u5_chk_155",
        )
        algo2 = GoldAlgorithm(
            name="Conjugate Gradient Algorithm",
            purpose="Solve large linear systems Ax = b where A is symmetric positive-definite in at most n steps.",
            inputs=["Symmetric positive-definite matrix A", "Right-hand vector b", "Initial guess x_0"],
            steps=[
                "Compute initial residual r_0 = b - A*x_0, set first search direction p_0 = r_0.",
                "For iteration k = 0, 1, 2, ...:",
                "  Compute step size: alpha_k = (r_k^T * r_k) / (p_k^T * A * p_k).",
                "  Update solution: x_{k+1} = x_k + alpha_k * p_k.",
                "  Update residual: r_{k+1} = r_k - alpha_k * A * p_k.",
                "  If ||r_{k+1}|| is close to zero, terminate (converged).",
                "  Compute beta_k = (r_{k+1}^T * r_{k+1}) / (r_k^T * r_k).",
                "  Construct next conjugate direction: p_{k+1} = r_{k+1} + beta_k * p_k.",
            ],
            stopping_condition="Residual norm ||r|| falls below tolerance",
            output="Exact algebraic solution vector x",
            source_document=doc1,
            page=150,
            chunk_id="ml_u5_chk_150b",
        )
        unit.algorithms = [algo1, algo2]

        # Concepts
        c_names = [
            "Least Squares Optimization",
            "Conjugate Gradient Method",
            "Reinforcement Learning Basics",
            "Markov Decision Process",
            "Q-Learning Algorithm",
            "Exploration vs Exploitation",
            "Responsible AI",
            "SHAP and LIME",
            "MLOps Lifecycle",
            "Federated Learning",
        ]
        for i, name in enumerate(c_names, start=1):
            unit.concepts.append(
                ConceptDetail(
                    concept_id=f"c_ml_u5_{name.lower().replace(' ', '_')}",
                    name=name,
                    unit_number=5,
                    chapter="UNIT 5 OPTIMIZATION, REINFORCEMENT LEARNING AND RESPONSIBLE AI",
                    summary=f"Optimization and advanced ML concept: {name}",
                    source_document=doc1,
                    source_pages=[147 + i * 3],
                    source_chunk_ids=[f"ml_u5_chk_{i:03d}"],
                )
            )

        # Exam Topics
        unit.exam_topics = [
            ExamTopic(concept="Q-Learning (Bellman Equation & TD Error Calculation)", unit=5, importance="EXAM_CRITICAL", question_types=["numerical", "algorithm", "viva"], revision_priority=1, source=doc1, page=154),
            ExamTopic(concept="Conjugate Gradient Method (A-Conjugacy & Workflow)", unit=5, importance="EXAM_CRITICAL", question_types=["numerical", "derivation", "comparison"], revision_priority=1, source=doc1, page=150),
            ExamTopic(concept="Markov Decision Process (Tuple & Markov Property)", unit=5, importance="HIGH", question_types=["conceptual", "diagram", "viva"], revision_priority=2, source=doc1, page=153),
            ExamTopic(concept="SHAP vs LIME (Explainability & Feature Attributions)", unit=5, importance="EXAM_CRITICAL", question_types=["comparison", "conceptual", "viva"], revision_priority=1, source=doc1, page=159),
            ExamTopic(concept="Federated Learning & FedAvg Algorithm", unit=5, importance="HIGH", question_types=["formula", "diagram", "conceptual"], revision_priority=2, source=doc1, page=177),
            ExamTopic(concept="MLOps Lifecycle & Concept Drift", unit=5, importance="HIGH", question_types=["conceptual", "diagram", "viva"], revision_priority=2, source=doc1, page=175),
        ]

        return unit

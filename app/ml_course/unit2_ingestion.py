"""
STAGE ML-COURSE-04: Machine Learning Unit II Ingestion Engine.
Course: AD5305 / CS4403 - Machine Learning
Institution: Chennai Institute of Technology (Autonomous)
Department: Artificial Intelligence and Data Science

Source Documents:
1. all_units_combined.pdf (Pages 40 to 72) - Theory
2. unit_2_problems.pdf (Pages 1 to 9) - Problem Sheets & Solved Numericals

Unit II: Supervised Learning, Bayesian Linear Regression, Gradient Descent, Perceptron,
Logistic Regression, Naive Bayes, Support Vector Machines (SVM), Decision Trees,
Random Forest, K-Nearest Neighbors (KNN), Bagging vs Boosting, Hyperparameter Tuning.
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


class Unit2IngestionEngine:
    """
    Dedicated ingestion, grounding, and verification engine for Unit II of the Machine Learning course.
    Dual-sourced from all_units_combined.pdf (Pages 40-72) and unit_2_problems.pdf (Pages 1-9).
    """

    THEORY_FILENAME = "all_units_combined.pdf"
    THEORY_DOC_ID = "doc_ml_all_units"
    THEORY_SRC_ID = "src_ml_all_units"
    THEORY_PAGE_START = 40
    THEORY_PAGE_END = 72

    PROB_FILENAME = "unit_2_problems.pdf"
    PROB_DOC_ID = "doc_ml_unit2_probs"
    PROB_SRC_ID = "src_ml_unit2_probs"
    PROB_PAGE_START = 1
    PROB_PAGE_END = 9

    UNIT_NUMBER = 2

    @classmethod
    def create_theory_ref(cls, page: int, section: Optional[str] = None, chunk_id: Optional[str] = None) -> SourceRef:
        return SourceRef(
            source_id=cls.THEORY_SRC_ID,
            document_id=cls.THEORY_DOC_ID,
            filename=cls.THEORY_FILENAME,
            page=page,
            section=section,
            chunk_id=chunk_id,
        )

    @classmethod
    def create_problem_ref(cls, page: int, section: Optional[str] = None, chunk_id: Optional[str] = None) -> SourceRef:
        return SourceRef(
            source_id=cls.PROB_SRC_ID,
            document_id=cls.PROB_DOC_ID,
            filename=cls.PROB_FILENAME,
            page=page,
            section=section,
            chunk_id=chunk_id,
        )

    @classmethod
    def ingest(cls, course_dir: str = "data/courses/machine_learning") -> MachineLearningUnit:
        unit = MachineLearningUnit(
            unit_id="unit_ml_2",
            unit_number=2,
            unit_code="UNIT II",
            title="Supervised Learning, Probabilistic Models, Support Vector Machines & Ensemble Learning",
            unit_title="Supervised Learning, Probabilistic Models, Support Vector Machines & Ensemble Learning",
            syllabus_topics=[
                "Bayesian Linear Regression",
                "Gradient Descent Optimization",
                "Perceptron Learning Algorithm",
                "Logistic Regression",
                "Naive Bayes Classifier",
                "Support Vector Machine (Linear, Non-Linear, Soft Margin)",
                "Decision Tree Algorithm (Information Gain, DTL, Rules)",
                "Random Forest Algorithm",
                "K-Nearest Neighbour (KNN)",
                "Ensemble Learning: Bagging and Boosting (AdaBoost, Gradient Boosting, XGBoost)",
                "Hyperparameter Tuning (Grid Search, Random Search, Bayesian Optimization)",
            ],
            source_pages=list(range(cls.THEORY_PAGE_START, cls.THEORY_PAGE_END + 1)),
            source_documents=[cls.THEORY_FILENAME, cls.PROB_FILENAME],
            source_refs=[
                cls.create_theory_ref(page=40, section="Unit II Cover"),
                cls.create_problem_ref(page=1, section="Unit II Problem Sheet Cover"),
            ],
            problem_types=["numerical", "algorithm", "conceptual", "comparison", "viva", "exam_question"],
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
                "ml.u2.bayesian_regression",
                "Bayesian Linear Regression",
                40,
                "Probabilistic regression formulating parameters as random variables with prior distributions. Computes parameter posterior distribution combining prior beliefs and sample likelihood using Bayes rule and Bayesian Ridge regularization.",
                "HIGH_IMPORTANCE",
                [],
            ),
            (
                "ml.u2.gradient_descent",
                "Gradient Descent",
                43,
                "First-order iterative numerical optimization adjusting weights along negative gradient direction to find loss minima. Variants include Batch Gradient Descent, Stochastic Gradient Descent (SGD), and Mini-Batch GD.",
                "CORE_FOUNDATION",
                [],
            ),
            (
                "ml.u2.perceptron",
                "Perceptron Algorithm",
                45,
                "Linear threshold classifier proposed by Frank Rosenblatt (1958). Computes weighted inner product and applies step activation. Proven by Perceptron Convergence Theorem to converge for linearly separable data, but fails on non-linearly separable problems like XOR.",
                "CORE_FOUNDATION",
                [cls.create_problem_ref(page=4, chunk_id="chk_ml.u2.perceptron_prob")],
            ),
            (
                "ml.u2.logistic_regression",
                "Logistic Regression",
                47,
                "Supervised classification algorithm modeling class posterior probability using the standard logistic sigmoid function sigma(z) = 1 / (1 + exp(-z)). Optimizes binary cross-entropy loss via maximum likelihood estimation.",
                "CORE_FOUNDATION",
                [cls.create_problem_ref(page=8, chunk_id="chk_ml.u2.logistic_prob")],
            ),
            (
                "ml.u2.naive_bayes",
                "Naive Bayes Classifier",
                48,
                "Probabilistic generative classifier based on Bayes' theorem under the conditional independence assumption among attributes given the class label. Solves zero-frequency counts with Laplace smoothing.",
                "CORE_FOUNDATION",
                [],
            ),
            (
                "ml.u2.svm",
                "Support Vector Machine",
                50,
                "Maximum margin hyperplane classifier maximizing geometric distance 2 / ||w|| between nearest data points (support vectors). Employs slack variables for soft margin non-separable data and the Kernel Trick for non-linear mappings (RBF, polynomial).",
                "EXAM_CRITICAL",
                [],
            ),
            (
                "ml.u2.decision_tree",
                "Decision Tree Algorithm",
                53,
                "Non-parametric hierarchical divide-and-conquer classifier partitioning feature space recursively into axis-aligned hyperplanes. Split decisions evaluate Information Gain (ID3), Gain Ratio (C4.5), or Gini Index (CART).",
                "EXAM_CRITICAL",
                [],
            ),
            (
                "ml.u2.random_forest",
                "Random Forest Algorithm",
                56,
                "Ensemble learning method creating a committee of de-correlated decision trees via bootstrap aggregation (bagging) and random feature subspace selection. Aggregates outputs via majority voting.",
                "HIGH_IMPORTANCE",
                [],
            ),
            (
                "ml.u2.knn",
                "K-Nearest Neighbour",
                55,
                "Instance-based lazy learning classifier storing all training instances. Classifies a query point by computing pairwise distance metrics (Euclidean, Manhattan) and taking a majority vote among its K closest neighbors.",
                "CORE_FOUNDATION",
                [cls.create_problem_ref(page=1, chunk_id="chk_ml.u2.knn_prob")],
            ),
            (
                "ml.u2.bagging_boosting",
                "Bagging vs Boosting",
                59,
                "Foundational ensemble paradigms: Bagging (Bootstrap Aggregating) trains base estimators independently in parallel to reduce variance; Boosting trains estimators sequentially, weighting misclassified samples to reduce bias (AdaBoost, Gradient Boosting, XGBoost).",
                "EXAM_CRITICAL",
                [],
            ),
            (
                "ml.u2.hyperparameter_tuning",
                "Hyperparameter Tuning",
                63,
                "Systematic optimization of algorithmic hyperparameters prior to model training. Evaluates candidates using Grid Search (exhaustive combinatorial), Random Search (probabilistic sampling), and Bayesian Optimization.",
                "HIGH_IMPORTANCE",
                [],
            ),
        ]

        concepts = []
        for cid, name, page, summary, imp, extra_refs in concepts_data:
            s_refs = [cls.create_theory_ref(page=page, chunk_id=f"chk_{cid}")]
            s_refs.extend(extra_refs)
            concepts.append(
                ConceptDetail(
                    concept_id=cid,
                    name=name,
                    unit_number=cls.UNIT_NUMBER,
                    chapter="UNIT II SUPERVISED LEARNING",
                    section=name,
                    summary=summary,
                    source_document=cls.THEORY_FILENAME,
                    source_pages=[page],
                    source_chunk_ids=[f"chk_{cid}"],
                    source_refs=s_refs,
                    importance=imp,
                )
            )
        return concepts

    @classmethod
    def _build_definitions(cls) -> List[GoldDefinition]:
        return [
            GoldDefinition(
                def_id="def.ml.u2.perceptron",
                term="Perceptron",
                definition_text="An algorithm for supervised learning of single-layer binary classifiers that maps its input x to an output value f(x) using a weighted linear combination and threshold activation function.",
                author_or_source="Frank Rosenblatt (1958)",
                source_document=cls.THEORY_FILENAME,
                page=45,
                chunk_id="chk_ml.u2.perceptron",
                source_refs=[cls.create_theory_ref(page=45)],
            ),
            GoldDefinition(
                def_id="def.ml.u2.svm_hyperplane",
                term="Maximum Margin Hyperplane (SVM)",
                definition_text="The unique decision boundary w^T x + b = 0 that separates two classes while maximizing the geometric margin to the closest training data points (support vectors).",
                author_or_source="Vapnik & Chervonenkis",
                source_document=cls.THEORY_FILENAME,
                page=50,
                chunk_id="chk_ml.u2.svm",
                source_refs=[cls.create_theory_ref(page=50)],
            ),
            GoldDefinition(
                def_id="def.ml.u2.naive_bayes_assumption",
                term="Conditional Independence Assumption (Naive Bayes)",
                definition_text="The naive assumption that the presence or value of a particular feature of a class is completely independent of the value of any other feature, given the class variable.",
                author_or_source="College ML Notes Unit II",
                source_document=cls.THEORY_FILENAME,
                page=48,
                chunk_id="chk_ml.u2.naive_bayes",
                source_refs=[cls.create_theory_ref(page=48)],
            ),
            GoldDefinition(
                def_id="def.ml.u2.entropy",
                term="Entropy (Information Theory)",
                definition_text="A measure of the impurity, disorder, or unpredictability in a set of training examples S, maximized when all classes are equally probable.",
                author_or_source="Claude Shannon (1948)",
                source_document=cls.THEORY_FILENAME,
                page=53,
                chunk_id="chk_ml.u2.decision_tree",
                source_refs=[cls.create_theory_ref(page=53)],
            ),
        ]

    @classmethod
    def _build_formulas(cls) -> List[GoldFormula]:
        return [
            GoldFormula(
                formula_id="form.ml.u2.gd_update",
                concept_id="ml.u2.gradient_descent",
                name="Gradient Descent Weight Update",
                expression="w = w - \\alpha \\frac{\\partial J(w, b)}{\\partial w}, \\quad b = b - \\alpha \\frac{\\partial J(w, b)}{\\partial b}",
                variables={"w": "Weights vector", "b": "Scalar bias", "\\alpha": "Learning rate parameter", "J": "Cost function"},
                context="General iterative optimization rule moving in negative gradient direction.",
                source_document=cls.THEORY_FILENAME,
                page=44,
                chunk_id="chk_ml.u2.gradient_descent",
                source_refs=[cls.create_theory_ref(page=44)],
            ),
            GoldFormula(
                formula_id="form.ml.u2.perceptron_rule",
                concept_id="ml.u2.perceptron",
                name="Perceptron Learning Rule",
                expression="w_{new} = w_{old} + \\alpha (y_{true} - y_{pred}) x",
                variables={"w": "Weight vector", "\\alpha": "Learning rate", "y_{true}": "Target label", "y_{pred}": "Perceptron predicted output", "x": "Feature input vector"},
                context="Weight update performed only when a classification mismatch occurs.",
                source_document=cls.THEORY_FILENAME,
                page=46,
                chunk_id="chk_ml.u2.perceptron",
                source_refs=[
                    cls.create_theory_ref(page=46),
                    cls.create_problem_ref(page=5),
                ],
            ),
            GoldFormula(
                formula_id="form.ml.u2.sigmoid",
                concept_id="ml.u2.logistic_regression",
                name="Logistic Sigmoid Function",
                expression="g(z) = \\frac{1}{1 + e^{-z}}, \\quad z = \\sum_{i=1}^n w_i x_i + b",
                variables={"z": "Linear combination score / logit", "g(z)": "Posterior probability P(y=1|x)", "w_i": "Feature weight", "b": "Bias"},
                context="Maps arbitrary real-valued score (-inf, +inf) into a valid probability range [0, 1].",
                source_document=cls.THEORY_FILENAME,
                page=47,
                chunk_id="chk_ml.u2.logistic_regression",
                source_refs=[
                    cls.create_theory_ref(page=47),
                    cls.create_problem_ref(page=8),
                ],
            ),
            GoldFormula(
                formula_id="form.ml.u2.log_loss",
                concept_id="ml.u2.logistic_regression",
                name="Binary Cross-Entropy Loss (Log Loss)",
                expression="J(w) = -\\frac{1}{m} \\sum_{i=1}^m [y^{(i)} \\ln(h_w(x^{(i)})) + (1 - y^{(i)}) \\ln(1 - h_w(x^{(i)}))]",
                variables={"m": "Sample count", "y^{(i)}": "True binary class", "h_w(x)": "Sigmoid probability"},
                context="Convex loss function for logistic regression solved via gradient descent.",
                source_document=cls.THEORY_FILENAME,
                page=47,
                chunk_id="chk_ml.u2.logistic_regression",
                source_refs=[cls.create_theory_ref(page=47)],
            ),
            GoldFormula(
                formula_id="form.ml.u2.bayes",
                concept_id="ml.u2.naive_bayes",
                name="Bayes Theorem",
                expression="P(A|B) = \\frac{P(B|A) P(A)}{P(B)}",
                variables={"P(A|B)": "Posterior probability", "P(B|A)": "Likelihood", "P(A)": "Prior probability", "P(B)": "Marginal evidence"},
                context="Foundational conditional probability formulation in machine learning.",
                source_document=cls.THEORY_FILENAME,
                page=49,
                chunk_id="chk_ml.u2.naive_bayes",
                source_refs=[cls.create_theory_ref(page=49)],
            ),
            GoldFormula(
                formula_id="form.ml.u2.entropy",
                concept_id="ml.u2.decision_tree",
                name="Shannon Entropy",
                expression="H(S) = -\\sum_{i=1}^c p_i \\log_2(p_i)",
                variables={"S": "Sample dataset", "c": "Number of classes", "p_i": "Proportion of class i in S"},
                context="Measures impurity of dataset for Decision Tree split selection.",
                source_document=cls.THEORY_FILENAME,
                page=53,
                chunk_id="chk_ml.u2.decision_tree",
                source_refs=[cls.create_theory_ref(page=53)],
            ),
            GoldFormula(
                formula_id="form.ml.u2.info_gain",
                concept_id="ml.u2.decision_tree",
                name="Information Gain (ID3)",
                expression="Gain(S, A) = H(S) - \\sum_{v \\in Values(A)} \\frac{|S_v|}{|S|} H(S_v)",
                variables={"S": "Parent dataset", "A": "Attribute candidate", "S_v": "Subset where attribute A takes value v", "H": "Entropy"},
                context="Expected reduction in entropy achieved by partitioning dataset on attribute A.",
                source_document=cls.THEORY_FILENAME,
                page=54,
                chunk_id="chk_ml.u2.decision_tree",
                source_refs=[cls.create_theory_ref(page=54)],
            ),
            GoldFormula(
                formula_id="form.ml.u2.svm_margin",
                concept_id="ml.u2.svm",
                name="SVM Geometric Margin Optimization",
                expression="\\min_{w, b} \\frac{1}{2} \\|w\\|^2 + C \\sum_{i=1}^m \\xi_i \\quad \\text{s.t.} \\quad y^{(i)}(w^T x^{(i)} + b) \\ge 1 - \\xi_i",
                variables={"w": "Hyperplane normal", "b": "Intercept", "C": "Regularization penalty", "\\xi_i": "Slack variables"},
                context="Soft margin Support Vector Machine primal optimization problem.",
                source_document=cls.THEORY_FILENAME,
                page=51,
                chunk_id="chk_ml.u2.svm",
                source_refs=[cls.create_theory_ref(page=51)],
            ),
            GoldFormula(
                formula_id="form.ml.u2.euclidean_dist",
                concept_id="ml.u2.knn",
                name="Euclidean Distance",
                expression="D = \\sqrt{\\sum_{i=1}^n (x_{2i} - x_{1i})^2}",
                variables={"x_1, x_2": "Two observation coordinate vectors in n-dimensional feature space"},
                context="Distance metric used for K-Nearest Neighbors sample similarity.",
                source_document=cls.PROB_FILENAME,
                page=2,
                chunk_id="chk_ml.u2.knn",
                source_refs=[cls.create_problem_ref(page=2)],
            ),
        ]

    @classmethod
    def _build_algorithms(cls) -> List[GoldAlgorithm]:
        return [
            GoldAlgorithm(
                algorithm_id="algo.ml.u2.knn",
                concept_id="ml.u2.knn",
                name="K-Nearest Neighbors (KNN) Classification",
                purpose="Classify query instance based on majority vote of k closest training examples.",
                inputs=["Training set D = {(x_i, y_i)}", "Query sample x", "Neighbor count k (odd number)", "Distance metric d(., .)"],
                steps=[
                    "Calculate distance d(x, x_i) between query x and every training instance x_i in D.",
                    "Sort all training instances in ascending order of distance.",
                    "Select top k instances with smallest distances to form neighborhood N_k(x).",
                    "Count frequency of each class label among samples in N_k(x).",
                    "Return class with highest frequency as predicted label y.",
                ],
                stopping_condition="Top k neighbors identified and majority class resolved.",
                output="Predicted discrete class label y",
                complexity="O(N * D) per query where N is samples and D is features",
                source_document=cls.PROB_FILENAME,
                page=1,
                chunk_id="chk_ml.u2.knn_algo",
                source_refs=[cls.create_problem_ref(page=1)],
            ),
            GoldAlgorithm(
                algorithm_id="algo.ml.u2.perceptron",
                concept_id="ml.u2.perceptron",
                name="Perceptron Learning Algorithm (PLA)",
                purpose="Train binary linear classifier weights on linearly separable data.",
                inputs=["Training dataset {(x^(i), y^(i))}_{i=1}^m where y in {0, 1}", "Learning rate alpha", "Threshold theta", "Max epochs"],
                steps=[
                    "Initialize weight vector w and bias b to zero or small initial values.",
                    "For epoch = 1 to Max_epochs:",
                    "  errors = 0",
                    "  For each sample i = 1 to m:",
                    "    Compute net input: z = w^T x^(i) + b.",
                    "    Compute predicted output: y_hat = 1 if z >= theta else 0.",
                    "    If y_hat != y^(i):",
                    "      w = w + alpha * (y^(i) - y_hat) * x^(i)",
                    "      errors += 1",
                    "  If errors == 0, terminate early.",
                ],
                stopping_condition="Zero classification errors on training set or max epochs reached.",
                output="Final converged weight vector w* and bias b*",
                complexity="O(epochs * m * features)",
                source_document=cls.PROB_FILENAME,
                page=4,
                chunk_id="chk_ml.u2.perceptron_algo",
                source_refs=[cls.create_problem_ref(page=4)],
            ),
            GoldAlgorithm(
                algorithm_id="algo.ml.u2.id3",
                concept_id="ml.u2.decision_tree",
                name="ID3 Decision Tree Induction Algorithm",
                purpose="Construct a decision tree top-down by greedily maximizing Information Gain.",
                inputs=["Dataset S", "Target attribute", "List of candidate features F"],
                steps=[
                    "If all examples in S belong to the same class C, return a single-node tree with label C.",
                    "If feature list F is empty, return a single-node tree with the most common class in S.",
                    "Calculate Entropy H(S).",
                    "For each attribute A in F, calculate Information Gain: Gain(S, A).",
                    "Select best attribute A_best that maximizes Information Gain.",
                    "Create a decision node with test A_best.",
                    "For each possible value v of A_best:",
                    "  Create subset S_v = {x in S | A_best(x) = v}.",
                    "  If S_v is empty, add leaf node with majority class of S.",
                    "  Else recursively call ID3(S_v, Target, F \\ {A_best}) and attach as child branch.",
                ],
                stopping_condition="All samples in partition are pure or all attributes are exhausted.",
                output="Root node of the constructed Decision Tree.",
                complexity="O(|F| * |S| * depth)",
                source_document=cls.THEORY_FILENAME,
                page=54,
                chunk_id="chk_ml.u2.decision_tree_algo",
                source_refs=[cls.create_theory_ref(page=54)],
            ),
        ]

    @classmethod
    def _build_examples(cls) -> List[GoldExample]:
        return [
            GoldExample(
                example_id="ex.ml.u2.xor_limitation",
                concept_id="ml.u2.perceptron",
                title="Perceptron Linear Separability Limitation (XOR Gate)",
                problem_statement="Explain why a single-layer perceptron cannot solve the XOR problem.",
                solution_steps=[
                    "XOR truth table: (0,0)->0, (0,1)->1, (1,0)->1, (1,1)->0.",
                    "Plotting points in 2D shows class 1 at (0,1) and (1,0), class 0 at (0,0) and (1,1).",
                    "No single linear line w1*x1 + w2*x2 + b = 0 can separate the diagonally opposed classes.",
                    "Minsky and Papert (1969) proved single-layer perceptrons are strictly limited to linearly separable functions.",
                    "Solution requires multi-layer perceptrons (MLP) with non-linear hidden layer activations.",
                ],
                final_answer="Single linear hyperplane cannot separate diagonal parity; requires multi-layer network.",
                source_document=cls.THEORY_FILENAME,
                page=46,
                chunk_id="chk_ml.u2.perceptron",
                source_refs=[cls.create_theory_ref(page=46)],
            ),
        ]

    @classmethod
    def _build_problems(cls) -> List[ProblemItem]:
        return [
            ProblemItem(
                problem_id="prob.ml.u2.knn_angelina",
                unit=2,
                topic="K-Nearest Neighbour",
                concept="K-Nearest Neighbour",
                concept_id="ml.u2.knn",
                problem_type=ProblemType.NUMERICAL,
                difficulty="intermediate",
                source_document=cls.PROB_FILENAME,
                source_page=2,
                question="Using KNN algorithm (k=3), determine which sport Angelina (Age: 5, Gender: F) belongs to given 10 student records.",
                given_data={
                    "query": {"Age": 5, "Gender": 1},
                    "k": 3,
                    "records": [
                        {"id": 1, "Age": 32, "Gender": 0, "Sport": "Football"},
                        {"id": 2, "Age": 40, "Gender": 0, "Sport": "Cricket"},
                        {"id": 3, "Age": 16, "Gender": 1, "Sport": "Cricket"},
                        {"id": 4, "Age": 34, "Gender": 1, "Sport": "Cricket"},
                        {"id": 5, "Age": 55, "Gender": 0, "Sport": "Football"},
                        {"id": 6, "Age": 40, "Gender": 0, "Sport": "Cricket"},
                        {"id": 7, "Age": 20, "Gender": 0, "Sport": "Cricket"},
                        {"id": 8, "Age": 15, "Gender": 1, "Sport": "Cricket"},
                        {"id": 9, "Age": 55, "Gender": 1, "Sport": "Football"},
                        {"id": 10, "Age": 15, "Gender": 0, "Sport": "Football"},
                    ],
                },
                formula="D = \\sqrt{(Age_2 - Age_1)^2 + (Gender_2 - Gender_1)^2}",
                solution_steps=[
                    "Encode Gender: Male = 0, Female = 1.",
                    "Calculate Euclidean distance from Angelina (5, 1) to all 10 students:",
                    "d1 = sqrt((32-5)^2 + (0-1)^2) = sqrt(729 + 1) = 27.02",
                    "d2 = sqrt((40-5)^2 + (0-1)^2) = sqrt(1225 + 1) = 35.01",
                    "d3 = sqrt((16-5)^2 + (1-1)^2) = sqrt(121 + 0) = 11.00 (Cricket)",
                    "d4 = sqrt((34-5)^2 + (1-1)^2) = sqrt(841 + 0) = 29.00",
                    "d5 = sqrt((55-5)^2 + (0-1)^2) = sqrt(2500 + 1) = 50.01",
                    "d6 = sqrt((40-5)^2 + (0-1)^2) = sqrt(1225 + 1) = 35.01",
                    "d7 = sqrt((20-5)^2 + (0-1)^2) = sqrt(225 + 1) = 15.03",
                    "d8 = sqrt((15-5)^2 + (1-1)^2) = sqrt(100 + 0) = 10.00 (Cricket)",
                    "d9 = sqrt((55-5)^2 + (1-1)^2) = sqrt(2500 + 0) = 50.00",
                    "d10 = sqrt((15-5)^2 + (0-1)^2) = sqrt(100 + 1) = 10.05 (Football)",
                    "Rank 3 smallest distances: d8 (10.00, Cricket), d10 (10.05, Football), d3 (11.00, Cricket).",
                    "Majority vote among k=3 neighbors: {Cricket, Football, Cricket} -> Cricket wins with 2 votes.",
                ],
                final_answer="Angelina will choose Cricket.",
                verification_status=VerificationStatus.VERIFIED,
                source_refs=[cls.create_problem_ref(page=2)],
            ),
            ProblemItem(
                problem_id="prob.ml.u2.perceptron_and_gate",
                unit=2,
                topic="Perceptron Algorithm",
                concept="Perceptron Algorithm",
                concept_id="ml.u2.perceptron",
                problem_type=ProblemType.NUMERICAL,
                difficulty="intermediate",
                source_document=cls.PROB_FILENAME,
                source_page=4,
                question="Classify AND gate using Perceptron with initial weights w1=1.2, w2=0.6, threshold=1, learning rate alpha=0.5. Verify outputs and update weights on mismatch.",
                given_data={"w1": 1.2, "w2": 0.6, "threshold": 1.0, "alpha": 0.5, "gate": "AND"},
                formula="w_i = w_i + \\alpha (y_{true} - y_{pred}) x_i",
                solution_steps=[
                    "AND Gate Truth Table: (0,0)->0, (0,1)->0, (1,0)->0, (1,1)->1.",
                    "Test (0, 0): z = (0)(1.2) + (0)(0.6) = 0 < 1 => Output 0 (Match).",
                    "Test (0, 1): z = (0)(1.2) + (1)(0.6) = 0.6 < 1 => Output 0 (Match).",
                    "Test (1, 0): z = (1)(1.2) + (0)(0.6) = 1.2 >= 1 => Output 1 (Mismatch! Target is 0).",
                    "Weight Update on (1, 0):",
                    "  w1 = 1.2 + 0.5 * (0 - 1) * 1 = 1.2 - 0.5 = 0.7",
                    "  w2 = 0.6 + 0.5 * (0 - 1) * 0 = 0.6",
                    "Re-evaluate all inputs with new weights w1=0.7, w2=0.6:",
                    "  (0, 0): z = 0 < 1 => Output 0 (Match)",
                    "  (0, 1): z = 0.6 < 1 => Output 0 (Match)",
                    "  (1, 0): z = 0.7 < 1 => Output 0 (Match)",
                    "  (1, 1): z = 0.7 + 0.6 = 1.3 >= 1 => Output 1 (Match)",
                    "All four vectors match their targets. Perceptron converges.",
                ],
                final_answer="Converged weights: w1 = 0.7, w2 = 0.6.",
                verification_status=VerificationStatus.VERIFIED,
                source_refs=[cls.create_problem_ref(page=4)],
            ),
            ProblemItem(
                problem_id="prob.ml.u2.logistic_loan_default",
                unit=2,
                topic="Logistic Regression",
                concept="Logistic Regression",
                concept_id="ml.u2.logistic_regression",
                problem_type=ProblemType.NUMERICAL,
                difficulty="intermediate",
                source_document=cls.PROB_FILENAME,
                source_page=8,
                question="A bank predicts loan default (Yes=1, No=0). Given Credit Score x1=650, Monthly Income x2=50K, w1=-0.005, w2=-0.04, bias=4, threshold=0.5. Predict default probability and class.",
                given_data={"x1": 650, "x2": 50, "w1": -0.005, "w2": -0.04, "bias": 4, "threshold": 0.5},
                formula="z = w_1 x_1 + w_2 x_2 + b, \\quad P = \\frac{1}{1 + e^{-z}}",
                solution_steps=[
                    "Calculate linear score z: z = (-0.005 * 650) + (-0.04 * 50) + 4 = -3.25 - 2.00 + 4 = -1.25",
                    "Compute Sigmoid: P(default) = 1 / (1 + exp(-(-1.25))) = 1 / (1 + exp(1.25))",
                    "exp(1.25) approx 3.4903",
                    "P = 1 / (1 + 3.4903) = 1 / 4.4903 = 0.2227 (22.27%)",
                    "Compare with decision threshold 0.5: 0.2227 < 0.5",
                    "Decision: Predict Class 0 (No default / Loan Approved).",
                ],
                final_answer="Probability of default is 22.27% (<0.5). Customer is approved (Class 0).",
                verification_status=VerificationStatus.VERIFIED,
                source_refs=[cls.create_problem_ref(page=8)],
            ),
        ]

    @classmethod
    def _build_tradeoffs(cls) -> List[TradeoffDetail]:
        return [
            TradeoffDetail(
                concept="Bagging vs Boosting",
                advantages=[
                    "Bagging (Random Forest) trains base learners in parallel, robust against noise, significantly reduces variance.",
                    "Boosting (AdaBoost, XGBoost) sequentially corrects residual errors, significantly reduces bias, often achieves higher accuracy.",
                ],
                disadvantages_or_limitations=[
                    "Bagging does not reduce bias of base models.",
                    "Boosting is prone to overfitting noisy labels and is computationally sequential.",
                ],
                applications=[
                    "Bagging: high-variance deep decision trees, unstable classifiers.",
                    "Boosting: tabular competitive ML, structured fraud detection.",
                ],
                source_document=cls.THEORY_FILENAME,
                page=60,
                source_refs=[cls.create_theory_ref(page=60)],
            ),
            TradeoffDetail(
                concept="Linear vs Non-Linear SVM Kernels",
                advantages=[
                    "Linear SVM is extremely fast, O(N), interpretable, ideal for large sparse text/gene classification.",
                    "RBF / Polynomial kernels can learn complex non-linear decision boundaries.",
                ],
                disadvantages_or_limitations=[
                    "Linear kernel fails if data is fundamentally non-separable.",
                    "RBF kernel is computationally expensive O(N^2) to O(N^3) and prone to overfitting if gamma/C not tuned.",
                ],
                applications=[
                    "Linear: Text categorization, high-dimensional genomics.",
                    "RBF: Image recognition, bioinformatics non-linear biosignals.",
                ],
                source_document=cls.THEORY_FILENAME,
                page=52,
                source_refs=[cls.create_theory_ref(page=52)],
            ),
        ]

    @classmethod
    def _build_exam_topics(cls) -> List[ExamTopic]:
        return [
            ExamTopic(
                topic_id="exam.ml.u2.svm_hyperplane",
                concept="Support Vector Machine Hyperplane, Margin & Kernels",
                concept_id="ml.u2.svm",
                unit=2,
                importance="EXAM_CRITICAL",
                question_types=["part_a_2mark", "part_b_16mark", "derivation", "diagram"],
                revision_priority=1,
                source=cls.THEORY_FILENAME,
                page=50,
                source_refs=[cls.create_theory_ref(page=50)],
            ),
            ExamTopic(
                topic_id="exam.ml.u2.perceptron_training",
                concept="Perceptron Algorithm Training and Weight Updates",
                concept_id="ml.u2.perceptron",
                unit=2,
                importance="EXAM_CRITICAL",
                question_types=["part_a_2mark", "numerical", "algorithm", "viva"],
                revision_priority=1,
                source=cls.PROB_FILENAME,
                page=4,
                source_refs=[cls.create_problem_ref(page=4)],
            ),
            ExamTopic(
                topic_id="exam.ml.u2.decision_tree_id3",
                concept="Decision Tree ID3 Information Gain & Entropy",
                concept_id="ml.u2.decision_tree",
                unit=2,
                importance="EXAM_CRITICAL",
                question_types=["part_a_2mark", "part_b_16mark", "algorithm"],
                revision_priority=1,
                source=cls.THEORY_FILENAME,
                page=53,
                source_refs=[cls.create_theory_ref(page=53)],
            ),
            ExamTopic(
                topic_id="exam.ml.u2.knn_numerical",
                concept="K-Nearest Neighbor Multi-Attribute Classification",
                concept_id="ml.u2.knn",
                unit=2,
                importance="HIGH",
                question_types=["numerical", "part_b_16mark", "viva"],
                revision_priority=2,
                source=cls.PROB_FILENAME,
                page=1,
                source_refs=[cls.create_problem_ref(page=1)],
            ),
            ExamTopic(
                topic_id="exam.ml.u2.ensemble_bag_boost",
                concept="Ensemble Learning: Bagging vs Boosting",
                concept_id="ml.u2.bagging_boosting",
                unit=2,
                importance="EXAM_CRITICAL",
                question_types=["part_a_2mark", "part_b_16mark", "comparison"],
                revision_priority=1,
                source=cls.THEORY_FILENAME,
                page=59,
                source_refs=[cls.create_theory_ref(page=59)],
            ),
            ExamTopic(
                topic_id="exam.ml.u2.logistic_regression",
                concept="Logistic Regression Sigmoid & Loan Default Prediction",
                concept_id="ml.u2.logistic_regression",
                unit=2,
                importance="HIGH",
                question_types=["numerical", "formula", "part_a_2mark"],
                revision_priority=2,
                source=cls.PROB_FILENAME,
                page=8,
                source_refs=[cls.create_problem_ref(page=8)],
            ),
        ]

    @classmethod
    def verify_source_grounding(cls) -> Dict[str, Any]:
        """
        Verify that all Unit II items map strictly to either:
        - all_units_combined.pdf (Pages 40 to 72)
        - unit_2_problems.pdf (Pages 1 to 9)
        """
        unit = cls.ingest()
        audit = {
            "unit": 2,
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

        def check_ref(item_id: str, ref: SourceRef):
            if ref.filename == cls.THEORY_FILENAME:
                if not (cls.THEORY_PAGE_START <= ref.page <= cls.THEORY_PAGE_END):
                    audit["invalid_citations"].append({"item": item_id, "ref": ref.model_dump(), "reason": "Theory page out of range"})
            elif ref.filename == cls.PROB_FILENAME:
                if not (cls.PROB_PAGE_START <= ref.page <= cls.PROB_PAGE_END):
                    audit["invalid_citations"].append({"item": item_id, "ref": ref.model_dump(), "reason": "Problem page out of range"})
            else:
                audit["invalid_citations"].append({"item": item_id, "ref": ref.model_dump(), "reason": "Unknown filename"})

        for c in unit.concepts:
            if not c.source_refs:
                audit["missing_source_refs"].append(c.concept_id)
            for r in c.source_refs:
                check_ref(c.concept_id, r)

        for f in unit.formulas:
            if not f.source_refs:
                audit["missing_source_refs"].append(f.formula_id)
            for r in f.source_refs:
                check_ref(f.formula_id, r)

        for a in unit.algorithms:
            if not a.source_refs:
                audit["missing_source_refs"].append(a.algorithm_id)
            for r in a.source_refs:
                check_ref(a.algorithm_id, r)

        for p in unit.problems:
            if not p.source_refs:
                audit["missing_source_refs"].append(p.problem_id)
            for r in p.source_refs:
                check_ref(p.problem_id, r)

        if audit["invalid_citations"] or audit["missing_source_refs"]:
            audit["verified"] = False

        return audit

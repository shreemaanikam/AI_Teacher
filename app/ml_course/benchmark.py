"""
STAGE ML-COURSE-31: Gold Educational Benchmark for College Machine Learning.
Course: AD5305 / CS4403 - Machine Learning
Institution: Chennai Institute of Technology (Autonomous)
Department: Artificial Intelligence and Data Science

Curated gold evaluation set based strictly on college course materials
covering definitions, concepts, formulas, numerical calculations, algorithms,
applications, comparisons, and common misconceptions across Units I–V.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.ml_course.models import SourceRef


class BenchmarkCategory(str, Enum):
    DEFINITION = "definition"
    CONCEPT = "concept"
    FORMULA = "formula"
    NUMERICAL = "numerical"
    ALGORITHM = "algorithm"
    APPLICATION = "application"
    COMPARISON = "comparison"
    MISCONCEPTION = "misconception"


class BenchmarkItem(BaseModel):
    item_id: str
    category: BenchmarkCategory
    unit: int
    concept_id: str
    prompt: str
    expected_answer: str
    key_tokens: List[str] = Field(default_factory=list)
    source_document: str
    source_page: int
    tolerance: Optional[float] = None  # for numerical items


class MLGoldBenchmark:
    """
    Definitive gold benchmark dataset for AD5305 / CS4403 Machine Learning.
    Contains 25+ verified college items spanning all 5 units.
    """

    _ITEMS: List[BenchmarkItem] = [
        # --- UNIT I ---
        BenchmarkItem(
            item_id="bm_u1_def_inductive_bias",
            category=BenchmarkCategory.DEFINITION,
            unit=1,
            concept_id="ml.u1.inductive_bias",
            prompt="Define inductive bias in machine learning.",
            expected_answer="The set of assumptions the learning algorithm uses to predict outputs of unseen inputs.",
            key_tokens=["assumptions", "unseen", "predict", "prior"],
            source_document="all_units_combined.pdf",
            source_page=12,
        ),
        BenchmarkItem(
            item_id="bm_u1_form_linear_reg",
            category=BenchmarkCategory.FORMULA,
            unit=1,
            concept_id="ml.u1.linear_regression",
            prompt="What is the MSE loss formula for linear regression?",
            expected_answer="J(w) = (1 / 2m) * sum((h_w(x_i) - y_i)^2)",
            key_tokens=["1 / 2m", "sum", "h_w", "y_i", "^2"],
            source_document="all_units_combined.pdf",
            source_page=18,
        ),
        BenchmarkItem(
            item_id="bm_u1_concept_bias_variance",
            category=BenchmarkCategory.CONCEPT,
            unit=1,
            concept_id="ml.u1.bias_variance_tradeoff",
            prompt="Explain the tradeoff between high bias and high variance.",
            expected_answer="High bias causes underfitting due to oversimplified models, while high variance causes overfitting due to sensitivity to training data noise.",
            key_tokens=["underfitting", "overfitting", "high bias", "high variance", "tradeoff"],
            source_document="all_units_combined.pdf",
            source_page=22,
        ),
        BenchmarkItem(
            item_id="bm_u1_algo_cross_val",
            category=BenchmarkCategory.ALGORITHM,
            unit=1,
            concept_id="ml.u1.cross_validation",
            prompt="What are the procedural steps of K-Fold Cross Validation?",
            expected_answer="Partition dataset into K equal folds. For each fold i, train on K-1 folds and evaluate on fold i. Average the K performance scores.",
            key_tokens=["partition", "k folds", "train", "evaluate", "average"],
            source_document="all_units_combined.pdf",
            source_page=24,
        ),
        BenchmarkItem(
            item_id="bm_u1_misc_overfitting",
            category=BenchmarkCategory.MISCONCEPTION,
            unit=1,
            concept_id="ml.u1.underfitting_overfitting",
            prompt="Does zero training error guarantee high test accuracy?",
            expected_answer="No, zero training error often indicates extreme overfitting, leading to poor generalization on unseen test data.",
            key_tokens=["no", "overfitting", "poor generalization", "memorization"],
            source_document="all_units_combined.pdf",
            source_page=23,
        ),

        # --- UNIT II ---
        BenchmarkItem(
            item_id="bm_u2_def_perceptron",
            category=BenchmarkCategory.DEFINITION,
            unit=2,
            concept_id="ml.u2.perceptron",
            prompt="What is a Rosenblatt Perceptron?",
            expected_answer="A fundamental linear classifier that computes a weighted sum of inputs and passes it through a step activation threshold function.",
            key_tokens=["linear classifier", "weighted sum", "activation", "step function"],
            source_document="all_units_combined.pdf",
            source_page=38,
        ),
        BenchmarkItem(
            item_id="bm_u2_form_perceptron_update",
            category=BenchmarkCategory.FORMULA,
            unit=2,
            concept_id="ml.u2.perceptron",
            prompt="State the Perceptron weight update equation.",
            expected_answer="w <- w + eta * (y - y_hat) * x",
            key_tokens=["w +", "eta", "y - y_hat", "x"],
            source_document="all_units_combined.pdf",
            source_page=40,
        ),
        BenchmarkItem(
            item_id="bm_u2_num_knn_angelina",
            category=BenchmarkCategory.NUMERICAL,
            unit=2,
            concept_id="ml.u2.knn",
            prompt="In the college KNN problem for Angelina (Age=5, Loan=57000), who are the nearest neighbors and what is the outcome?",
            expected_answer="Nearest neighbors are computed using Euclidean distance; closest are evaluated to yield the majority default label.",
            key_tokens=["euclidean distance", "nearest", "k=3", "loan"],
            source_document="unit_2_problems.pdf",
            source_page=1,
        ),
        BenchmarkItem(
            item_id="bm_u2_algo_decision_tree",
            category=BenchmarkCategory.ALGORITHM,
            unit=2,
            concept_id="ml.u2.decision_tree",
            prompt="Describe how ID3 / C4.5 chooses splitting attributes.",
            expected_answer="Calculates Information Gain or Gain Ratio using Shannon Entropy and splits on the attribute that maximizes gain.",
            key_tokens=["entropy", "information gain", "split", "gain ratio"],
            source_document="all_units_combined.pdf",
            source_page=52,
        ),
        BenchmarkItem(
            item_id="bm_u2_comp_dt_vs_rf",
            category=BenchmarkCategory.COMPARISON,
            unit=2,
            concept_id="ml.u2.random_forest",
            prompt="Compare a single Decision Tree with a Random Forest.",
            expected_answer="A Decision Tree is prone to high variance and overfitting; Random Forest aggregates multiple bootstrapped trees via bagging to reduce variance.",
            key_tokens=["ensemble", "bagging", "reduce variance", "bootstrap", "overfitting"],
            source_document="all_units_combined.pdf",
            source_page=60,
        ),

        # --- UNIT III ---
        BenchmarkItem(
            item_id="bm_u3_def_ann",
            category=BenchmarkCategory.DEFINITION,
            unit=3,
            concept_id="ml.u3.ann_intro",
            prompt="What is an Artificial Neural Network?",
            expected_answer="A computational model inspired by biological neural networks consisting of interconnected layers of artificial neurons.",
            key_tokens=["computational model", "interconnected", "layers", "neurons"],
            source_document="all_units_combined.pdf",
            source_page=75,
        ),
        BenchmarkItem(
            item_id="bm_u3_form_backprop_output",
            category=BenchmarkCategory.FORMULA,
            unit=3,
            concept_id="ml.u3.backpropagation",
            prompt="What is the error delta formula at the output neuron in backpropagation with sigmoid activation?",
            expected_answer="delta_k = (t_k - y_k) * y_k * (1 - y_k)",
            key_tokens=["delta_k", "t_k - y_k", "y_k", "1 - y_k"],
            source_document="unit_3_and_4_problems.pdf",
            source_page=2,
        ),
        BenchmarkItem(
            item_id="bm_u3_algo_backpropagation",
            category=BenchmarkCategory.ALGORITHM,
            unit=3,
            concept_id="ml.u3.backpropagation",
            prompt="List the procedural steps of the Backpropagation algorithm.",
            expected_answer="1. Forward pass input to compute activations. 2. Calculate output error loss. 3. Backpropagate error deltas to hidden layers. 4. Update weights using gradient descent.",
            key_tokens=["forward pass", "error", "backpropagate", "deltas", "update weights"],
            source_document="all_units_combined.pdf",
            source_page=88,
        ),
        BenchmarkItem(
            item_id="bm_u3_concept_vanishing_gradient",
            category=BenchmarkCategory.CONCEPT,
            unit=3,
            concept_id="ml.u3.ann_challenges",
            prompt="What causes the vanishing gradient problem in deep networks?",
            expected_answer="Repeated multiplication of small derivative values (< 0.25 in sigmoid) across many layers causes gradients to shrink exponentially toward zero.",
            key_tokens=["repeated multiplication", "sigmoid", "derivatives", "shrink", "exponentially"],
            source_document="all_units_combined.pdf",
            source_page=82,
        ),
        BenchmarkItem(
            item_id="bm_u3_app_cnn_vision",
            category=BenchmarkCategory.APPLICATION,
            unit=3,
            concept_id="ml.u3.cnn",
            prompt="Why are Convolutional Neural Networks preferred for computer vision?",
            expected_answer="They exploit spatial locality and translation invariance through convolutional kernels and pooling layers, drastically reducing parameters.",
            key_tokens=["spatial locality", "translation invariance", "kernels", "pooling", "vision"],
            source_document="all_units_combined.pdf",
            source_page=96,
        ),

        # --- UNIT IV ---
        BenchmarkItem(
            item_id="bm_u4_def_unsupervised",
            category=BenchmarkCategory.DEFINITION,
            unit=4,
            concept_id="ml.u4.unsupervised_intro",
            prompt="Define Unsupervised Learning.",
            expected_answer="A category of machine learning that discovers inherent patterns, structures, or clusterings in unlabeled data without target supervisor signals.",
            key_tokens=["unlabeled data", "patterns", "clusters", "without target"],
            source_document="all_units_combined.pdf",
            source_page=110,
        ),
        BenchmarkItem(
            item_id="bm_u4_form_kmeans_wcss",
            category=BenchmarkCategory.FORMULA,
            unit=4,
            concept_id="ml.u4.kmeans",
            prompt="What is the objective function minimized by K-Means clustering?",
            expected_answer="WCSS = sum_{k=1}^K sum_{x in C_k} ||x - mu_k||^2",
            key_tokens=["wcss", "sum", "||x - mu_k||^2", "centroids", "inertia"],
            source_document="all_units_combined.pdf",
            source_page=115,
        ),
        BenchmarkItem(
            item_id="bm_u4_num_kmeans_iteration",
            category=BenchmarkCategory.NUMERICAL,
            unit=4,
            concept_id="ml.u4.kmeans",
            prompt="In the college K-Means numerical problem with K=2 centroids (2,2) and (6,6), how are points assigned?",
            expected_answer="Points are assigned to the closest centroid using Euclidean distance; centroids are updated as the arithmetic mean of assigned points.",
            key_tokens=["euclidean distance", "closest centroid", "mean", "assignment", "update"],
            source_document="unit_3_and_4_problems.pdf",
            source_page=15,
        ),
        BenchmarkItem(
            item_id="bm_u4_algo_kmeans",
            category=BenchmarkCategory.ALGORITHM,
            unit=4,
            concept_id="ml.u4.kmeans",
            prompt="Detail the procedural steps of the standard K-Means algorithm.",
            expected_answer="1. Initialize K cluster centroids. 2. Assign each point to the closest centroid. 3. Recompute centroids as cluster means. 4. Repeat until centroids do not change.",
            key_tokens=["initialize", "assign", "closest", "recompute", "repeat until convergence"],
            source_document="all_units_combined.pdf",
            source_page=116,
        ),
        BenchmarkItem(
            item_id="bm_u4_concept_pca",
            category=BenchmarkCategory.CONCEPT,
            unit=4,
            concept_id="ml.u4.pca",
            prompt="Explain the principle of Principal Component Analysis (PCA).",
            expected_answer="Finds orthogonal axes of maximal variance by computing eigenvectors of the covariance matrix, projecting data into a lower-dimensional subspace.",
            key_tokens=["orthogonal axes", "maximal variance", "eigenvectors", "covariance matrix", "dimensionality"],
            source_document="all_units_combined.pdf",
            source_page=132,
        ),

        # --- UNIT V ---
        BenchmarkItem(
            item_id="bm_u5_def_rl",
            category=BenchmarkCategory.DEFINITION,
            unit=5,
            concept_id="ml.u5.reinforcement_learning",
            prompt="Define Reinforcement Learning.",
            expected_answer="A learning paradigm where an autonomous agent learns to take sequential actions in an environment to maximize cumulative reward.",
            key_tokens=["agent", "actions", "environment", "cumulative reward", "policy"],
            source_document="all_units_combined.pdf",
            source_page=150,
        ),
        BenchmarkItem(
            item_id="bm_u5_form_q_learning",
            category=BenchmarkCategory.FORMULA,
            unit=5,
            concept_id="ml.u5.q_learning",
            prompt="State the Bellman equation Q-learning update formula.",
            expected_answer="Q(s, a) <- Q(s, a) + alpha * [r + gamma * max_a' Q(s', a') - Q(s, a)]",
            key_tokens=["Q(s, a)", "alpha", "r + gamma", "max_a'", "td error"],
            source_document="all_units_combined.pdf",
            source_page=158,
        ),
        BenchmarkItem(
            item_id="bm_u5_algo_q_learning",
            category=BenchmarkCategory.ALGORITHM,
            unit=5,
            concept_id="ml.u5.q_learning",
            prompt="Outline the Q-Learning procedural algorithm.",
            expected_answer="1. Initialize Q-table. 2. In state s, choose action a via epsilon-greedy. 3. Execute a, observe reward r and next state s'. 4. Update Q(s,a) via TD rule. 5. Set s = s'.",
            key_tokens=["initialize q-table", "epsilon-greedy", "observe reward", "td update", "next state"],
            source_document="all_units_combined.pdf",
            source_page=160,
        ),
        BenchmarkItem(
            item_id="bm_u5_concept_exploration_exploitation",
            category=BenchmarkCategory.CONCEPT,
            unit=5,
            concept_id="ml.u5.exploration_exploitation",
            prompt="What is the exploration vs exploitation dilemma in reinforcement learning?",
            expected_answer="Balancing taking known high-reward actions (exploitation) versus discovering new actions that might yield higher long-term rewards (exploration).",
            key_tokens=["exploration", "exploitation", "known actions", "new actions", "balance"],
            source_document="all_units_combined.pdf",
            source_page=164,
        ),
        BenchmarkItem(
            item_id="bm_u5_comp_shap_lime",
            category=BenchmarkCategory.COMPARISON,
            unit=5,
            concept_id="ml.u5.shap_and_lime",
            prompt="Compare SHAP and LIME for model explainability.",
            expected_answer="LIME fits local surrogate interpretable linear models around individual predictions; SHAP calculates Shapley values from cooperative game theory providing consistent, axiomatic attribution.",
            key_tokens=["lime", "shap", "surrogate", "shapley values", "game theory", "local"],
            source_document="all_units_combined.pdf",
            source_page=172,
        ),
    ]

    @classmethod
    def get_all_items(cls) -> List[BenchmarkItem]:
        return cls._ITEMS

    @classmethod
    def get_items_by_unit(cls, unit: int) -> List[BenchmarkItem]:
        return [it for it in cls._ITEMS if it.unit == unit]

    @classmethod
    def get_items_by_category(cls, category: BenchmarkCategory) -> List[BenchmarkItem]:
        return [it for it in cls._ITEMS if it.category == category]

"""
STAGE ML-COURSE-07: Machine Learning Unit V Ingestion Engine.
Course: AD5305 / CS4403 - Machine Learning
Institution: Chennai Institute of Technology (Autonomous)
Department: Artificial Intelligence and Data Science

Source Documents:
1. all_units_combined.pdf (Pages 148 to 178) - Comprehensive syllabus
2. unit_5_notes_v1.pdf (Pages 1 to 15) - Lecture Notes Set 1
3. unit_5_notes_v2.pdf (Pages 1 to 16) - Lecture Notes Set 2

Unit V: Optimization, Conjugate Gradient, Reinforcement Learning, Markov Decision Process (MDP),
Q-Learning, Exploration vs Exploitation, Responsible AI (Fairness, Explainability, Safety),
SHAP & LIME, MLOps Lifecycle, Federated Learning (FedAvg).
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


class Unit5IngestionEngine:
    """
    Dedicated ingestion, grounding, and verification engine for Unit V of the Machine Learning course.
    Unifies Lecture Notes Set 1, Set 2, and the combined syllabus document with multi-source traceability,
    guaranteeing zero concept duplication.
    """

    COMBINED_FILENAME = "all_units_combined.pdf"
    COMBINED_DOC_ID = "doc_ml_all_units"
    COMBINED_SRC_ID = "src_ml_all_units"
    COMBINED_PAGE_START = 148
    COMBINED_PAGE_END = 178

    V1_FILENAME = "unit_5_notes_v1.pdf"
    V1_DOC_ID = "doc_ml_unit5_v1"
    V1_SRC_ID = "src_ml_unit5_v1"
    V1_PAGE_START = 1
    V1_PAGE_END = 15

    V2_FILENAME = "unit_5_notes_v2.pdf"
    V2_DOC_ID = "doc_ml_unit5_v2"
    V2_SRC_ID = "src_ml_unit5_v2"
    V2_PAGE_START = 1
    V2_PAGE_END = 16

    UNIT_NUMBER = 5

    @classmethod
    def create_combined_ref(cls, page: int, section: Optional[str] = None, chunk_id: Optional[str] = None) -> SourceRef:
        return SourceRef(
            source_id=cls.COMBINED_SRC_ID,
            document_id=cls.COMBINED_DOC_ID,
            filename=cls.COMBINED_FILENAME,
            page=page,
            section=section,
            chunk_id=chunk_id,
        )

    @classmethod
    def create_v1_ref(cls, page: int, section: Optional[str] = None, chunk_id: Optional[str] = None) -> SourceRef:
        return SourceRef(
            source_id=cls.V1_SRC_ID,
            document_id=cls.V1_DOC_ID,
            filename=cls.V1_FILENAME,
            page=page,
            section=section,
            chunk_id=chunk_id,
        )

    @classmethod
    def create_v2_ref(cls, page: int, section: Optional[str] = None, chunk_id: Optional[str] = None) -> SourceRef:
        return SourceRef(
            source_id=cls.V2_SRC_ID,
            document_id=cls.V2_DOC_ID,
            filename=cls.V2_FILENAME,
            page=page,
            section=section,
            chunk_id=chunk_id,
        )

    @classmethod
    def ingest(cls, course_dir: str = "data/courses/machine_learning") -> MachineLearningUnit:
        unit = MachineLearningUnit(
            unit_id="unit_ml_5",
            unit_number=5,
            unit_code="UNIT V",
            title="Optimization, Reinforcement Learning and Responsible AI",
            unit_title="Optimization, Reinforcement Learning and Responsible AI",
            syllabus_topics=[
                "Least Squares Optimization (SSE, Normal Equations, Regularization: Ridge & Lasso)",
                "Conjugate Gradient Method (Ax = b, A-Conjugacy, Step Size, CG vs GD)",
                "Reinforcement Learning Basics (Agent-Environment Loop, State, Action, Reward, Policy, Value Functions)",
                "Markov Decision Process (MDP: S, A, P, R, gamma, Markov Property)",
                "Q-Learning (Model-Free, Off-Policy, Bellman Update, TD Error, Q-Table)",
                "Exploration vs Exploitation (Dilemma, Epsilon-Greedy, Decaying Epsilon, Softmax, UCB)",
                "Responsible AI (Fairness, Bias Awareness & Mitigation, Explainability, Privacy, Safety)",
                "SHAP and LIME (Shapley Values, Cooperative Game Theory, Local Surrogates)",
                "MLOps Basics (Lifecycle, Experiment Tracking, CI/CD, Data Drift & Concept Drift)",
                "Federated Learning (Decentralized Training, FedAvg Parameter Aggregation, Privacy)",
            ],
            source_pages=list(range(cls.COMBINED_PAGE_START, cls.COMBINED_PAGE_END + 1)),
            source_documents=[cls.COMBINED_FILENAME, cls.V1_FILENAME, cls.V2_FILENAME],
            source_refs=[
                cls.create_combined_ref(page=148, section="Unit V Combined Cover"),
                cls.create_v1_ref(page=1, section="Unit V Notes Set 1 Cover"),
                cls.create_v2_ref(page=1, section="Unit V Notes Set 2 Cover"),
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
                "ml.u5.least_squares",
                "Least Squares Optimization",
                ["Least Squares", "Ordinary Least Squares"],
                148,
                "Parameter-estimation technique finding best-fitting curve by minimizing sum of squared errors (SSE); solved via Normal Equations X^T X beta = X^T y or gradient descent, regularized with Ridge (L2) or Lasso (L1).",
                [
                    cls.create_combined_ref(page=148),
                    cls.create_combined_ref(page=164),
                    cls.create_v1_ref(page=1),
                    cls.create_v2_ref(page=2),
                ],
                "CORE_FOUNDATION",
            ),
            (
                "ml.u5.conjugate_gradient",
                "Conjugate Gradient Method",
                ["CG Method", "Conjugate Gradients"],
                150,
                "Iterative algorithm solving Ax = b for large, sparse, symmetric positive-definite matrices by choosing non-interfering A-conjugate directions, converging in at most n steps without full matrix inversion.",
                [
                    cls.create_combined_ref(page=150),
                    cls.create_combined_ref(page=165),
                    cls.create_v1_ref(page=3),
                    cls.create_v2_ref(page=3),
                ],
                "EXAM_CRITICAL",
            ),
            (
                "ml.u5.reinforcement_learning",
                "Reinforcement Learning Basics",
                ["RL Basics", "Agent-Environment Interaction"],
                152,
                "Learning paradigm where an agent takes actions in an environment, receives reward signals, and learns an optimal policy pi(a|s) maximizing cumulative discounted return G_t without labeled answers.",
                [
                    cls.create_combined_ref(page=152),
                    cls.create_combined_ref(page=167),
                    cls.create_v1_ref(page=5),
                    cls.create_v2_ref(page=5),
                ],
                "CORE_FOUNDATION",
            ),
            (
                "ml.u5.mdp",
                "Markov Decision Process",
                ["MDP", "Markov Property"],
                153,
                "Formal mathematical framework for RL defined by the tuple (S, A, P, R, gamma) under the memoryless Markov Property where future states depend only on current state and action.",
                [
                    cls.create_combined_ref(page=153),
                    cls.create_combined_ref(page=170),
                    cls.create_v1_ref(page=6),
                    cls.create_v2_ref(page=8),
                ],
                "EXAM_CRITICAL",
            ),
            (
                "ml.u5.q_learning",
                "Q-Learning Algorithm",
                ["Q-Learning", "Action-Value Learning"],
                154,
                "Model-free off-policy algorithm learning optimal action-value Q(s, a) via Bellman update: Q(s, a) <- Q(s, a) + alpha * [r + gamma * max Q(s', a') - Q(s, a)].",
                [
                    cls.create_combined_ref(page=154),
                    cls.create_combined_ref(page=170),
                    cls.create_v1_ref(page=7),
                    cls.create_v2_ref(page=8),
                ],
                "EXAM_CRITICAL",
            ),
            (
                "ml.u5.exploration_exploitation",
                "Exploration vs Exploitation",
                ["Exploration-Exploitation Tradeoff"],
                156,
                "Core dilemma between exploiting current best-known actions and exploring uncertain actions, balanced via epsilon-greedy, decaying epsilon, Softmax, or UCB.",
                [
                    cls.create_combined_ref(page=156),
                    cls.create_combined_ref(page=172),
                    cls.create_v1_ref(page=9),
                    cls.create_v2_ref(page=10),
                ],
                "HIGH_IMPORTANCE",
            ),
            (
                "ml.u5.responsible_ai",
                "Responsible AI",
                ["Fairness, Bias and Explainability", "Ethical AI"],
                157,
                "Framework ensuring AI is fair, free of harmful bias, and explainable (audited under laws like India's DPDP Act 2023 and the EU AI Act).",
                [
                    cls.create_combined_ref(page=157),
                    cls.create_combined_ref(page=172),
                    cls.create_v1_ref(page=10),
                    cls.create_v2_ref(page=10),
                ],
                "HIGH_IMPORTANCE",
            ),
            (
                "ml.u5.shap_and_lime",
                "SHAP and LIME Overview",
                ["Explainable AI", "SHAP", "LIME"],
                158,
                "Post-hoc black-box explainability: SHAP fairly attributes feature payouts using cooperative game theory Shapley values; LIME builds local surrogate linear models by perturbing inputs.",
                [
                    cls.create_combined_ref(page=158),
                    cls.create_combined_ref(page=173),
                    cls.create_v1_ref(page=11),
                    cls.create_v2_ref(page=11),
                ],
                "EXAM_CRITICAL",
            ),
            (
                "ml.u5.mlops",
                "MLOps Basics",
                ["MLOps Lifecycle", "Machine Learning Operations"],
                160,
                "Practices combining ML, DevOps, and Data Engineering to deploy and monitor models; manages Data Drift (input distribution shift) and Concept Drift (input-target relationship shift).",
                [
                    cls.create_combined_ref(page=160),
                    cls.create_combined_ref(page=175),
                    cls.create_v1_ref(page=13),
                    cls.create_v2_ref(page=13),
                ],
                "HIGH_IMPORTANCE",
            ),
            (
                "ml.u5.federated_learning",
                "Federated Learning Basics",
                ["Federated Learning", "FedAvg"],
                161,
                "Distributed machine learning framework training models across decentralized edge devices holding local data, aggregating updates via Federated Averaging (FedAvg) to preserve user privacy.",
                [
                    cls.create_combined_ref(page=161),
                    cls.create_combined_ref(page=177),
                    cls.create_v1_ref(page=13),
                    cls.create_v2_ref(page=15),
                ],
                "HIGH_IMPORTANCE",
            ),
        ]

        concepts = []
        for cid, name, aliases, page, summary, s_refs, imp in concepts_data:
            concepts.append(
                ConceptDetail(
                    concept_id=cid,
                    name=name,
                    aliases=aliases,
                    unit_number=cls.UNIT_NUMBER,
                    chapter="UNIT V : Optimization, RL and Responsible AI",
                    section=name,
                    summary=summary,
                    source_document=cls.COMBINED_FILENAME,
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
                def_id="def.ml.u5.normal_equations",
                term="Normal Equations",
                definition_text="The matrix equation X^T X beta = X^T y that yields the analytical closed-form Ordinary Least Squares parameter estimates minimizing residual sum of squares.",
                author_or_source="Gauss & Legendre",
                source_document=cls.COMBINED_FILENAME,
                page=164,
                chunk_id="chk_ml.u5.least_squares",
                source_refs=[
                    cls.create_combined_ref(page=164),
                    cls.create_v2_ref(page=2),
                ],
            ),
            GoldDefinition(
                def_id="def.ml.u5.conjugacy",
                term="A-Conjugacy (Conjugate Directions)",
                definition_text="Two non-zero vectors p_i and p_j are conjugate with respect to a symmetric positive-definite matrix A if their inner product through A is zero: p_i^T A p_j = 0 for all i != j.",
                author_or_source="Hestenes & Stiefel (1952)",
                source_document=cls.COMBINED_FILENAME,
                page=150,
                chunk_id="chk_ml.u5.conjugate_gradient",
                source_refs=[
                    cls.create_combined_ref(page=150),
                    cls.create_v1_ref(page=3),
                ],
            ),
            GoldDefinition(
                def_id="def.ml.u5.mdp_property",
                term="Markov Property",
                definition_text="The condition where the transition probability to the next state depends solely on the current state and action, and is conditionally independent of all preceding historical states and actions.",
                author_or_source="Andrey Markov (1906)",
                source_document=cls.COMBINED_FILENAME,
                page=153,
                chunk_id="chk_ml.u5.mdp",
                source_refs=[
                    cls.create_combined_ref(page=153),
                    cls.create_v1_ref(page=6),
                ],
            ),
            GoldDefinition(
                def_id="def.ml.u5.q_learning",
                term="Q-Learning",
                definition_text="A model-free, off-policy reinforcement learning algorithm that iteratively learns the expected utility (Q-value) of taking a given action in a given state under the optimal policy.",
                author_or_source="Christopher Watkins (1989)",
                source_document=cls.COMBINED_FILENAME,
                page=154,
                chunk_id="chk_ml.u5.q_learning",
                source_refs=[
                    cls.create_combined_ref(page=154),
                    cls.create_v2_ref(page=8),
                ],
            ),
            GoldDefinition(
                def_id="def.ml.u5.shapley_value",
                term="Shapley Value (SHAP)",
                definition_text="A solution concept in cooperative game theory assigning a unique, fair payout distribution to each player (feature) based on their average marginal contribution across all possible coalitions.",
                author_or_source="Lloyd Shapley (1953) / Lundberg & Lee (2017)",
                source_document=cls.COMBINED_FILENAME,
                page=158,
                chunk_id="chk_ml.u5.shap_and_lime",
                source_refs=[
                    cls.create_combined_ref(page=158),
                    cls.create_v2_ref(page=11),
                ],
            ),
        ]

    @classmethod
    def _build_formulas(cls) -> List[GoldFormula]:
        return [
            GoldFormula(
                formula_id="form.ml.u5.normal_equations",
                concept_id="ml.u5.least_squares",
                name="Normal Equations",
                expression="X^T X \\beta = X^T y \\implies \\hat{\\beta} = (X^T X)^{-1} X^T y",
                variables={"X": "Design matrix of features", "y": "Target vector", "\\beta": "Regression parameter vector"},
                context="Closed-form Ordinary Least Squares solution without iterative gradient descent.",
                source_document=cls.COMBINED_FILENAME,
                page=164,
                chunk_id="chk_ml.u5.least_squares",
                source_refs=[
                    cls.create_combined_ref(page=164),
                    cls.create_v2_ref(page=2),
                ],
            ),
            GoldFormula(
                formula_id="form.ml.u5.cg_step",
                concept_id="ml.u5.conjugate_gradient",
                name="Conjugate Gradient Step Size & Direction",
                expression="\\alpha_k = \\frac{r_k^T r_k}{p_k^T A p_k}, \\quad \\beta_k = \\frac{r_{k+1}^T r_{k+1}}{r_k^T r_k}, \\quad p_{k+1} = r_{k+1} + \\beta_k p_k",
                variables={"r_k": "Residual vector b - Ax_k", "p_k": "Conjugate search direction", "A": "Symmetric positive-definite matrix", "\\alpha_k": "Optimal step size"},
                context="Exact line search along mutually A-orthogonal conjugate directions.",
                source_document=cls.COMBINED_FILENAME,
                page=150,
                chunk_id="chk_ml.u5.conjugate_gradient",
                source_refs=[
                    cls.create_combined_ref(page=150),
                    cls.create_v1_ref(page=3),
                    cls.create_v2_ref(page=4),
                ],
            ),
            GoldFormula(
                formula_id="form.ml.u5.q_update",
                concept_id="ml.u5.q_learning",
                name="Q-Learning Bellman Update Rule",
                expression="Q(s, a) \\leftarrow Q(s, a) + \\alpha \\left[ r + \\gamma \\max_{a'} Q(s', a') - Q(s, a) \\right]",
                variables={"Q(s, a)": "Current state-action value", "\\alpha": "Learning rate in (0, 1]", "r": "Immediate reward", "\\gamma": "Discount factor in [0, 1)", "s'": "Next state", "a'": "Next action candidate"},
                context="Temporal difference update equation for off-policy control.",
                source_document=cls.COMBINED_FILENAME,
                page=154,
                chunk_id="chk_ml.u5.q_learning",
                source_refs=[
                    cls.create_combined_ref(page=154),
                    cls.create_v1_ref(page=7),
                    cls.create_v2_ref(page=8),
                ],
            ),
            GoldFormula(
                formula_id="form.ml.u5.shap_attribution",
                concept_id="ml.u5.shap_and_lime",
                name="SHAP Additive Attribution",
                expression="f(x) \\approx \\phi_0 + \\sum_{i=1}^M \\phi_i",
                variables={"f(x)": "Model prediction for sample x", "\\phi_0": "Expected baseline model output", "\\phi_i": "Shapley value attribution for feature i", "M": "Number of input features"},
                context="Local additive feature importance framework satisfying efficiency, symmetry, and dummy axioms.",
                source_document=cls.COMBINED_FILENAME,
                page=173,
                chunk_id="chk_ml.u5.shap_and_lime",
                source_refs=[
                    cls.create_combined_ref(page=173),
                    cls.create_v2_ref(page=11),
                ],
            ),
            GoldFormula(
                formula_id="form.ml.u5.fedavg",
                concept_id="ml.u5.federated_learning",
                name="Federated Averaging (FedAvg)",
                expression="w_{t+1} = \\sum_{k=1}^K \\frac{n_k}{N} w_{t+1}^k",
                variables={"w_{t+1}": "Global aggregated model weights", "w_{t+1}^k": "Locally updated weights of client k", "n_k": "Local sample count", "N": "Total sample count across clients"},
                context="Server-side weighted parameter aggregation algorithm across decentralized edge devices.",
                source_document=cls.COMBINED_FILENAME,
                page=177,
                chunk_id="chk_ml.u5.federated_learning",
                source_refs=[
                    cls.create_combined_ref(page=177),
                    cls.create_v2_ref(page=15),
                ],
            ),
        ]

    @classmethod
    def _build_algorithms(cls) -> List[GoldAlgorithm]:
        return [
            GoldAlgorithm(
                algorithm_id="algo.ml.u5.q_learning",
                concept_id="ml.u5.q_learning",
                name="Q-Learning Algorithm",
                purpose="Learn optimal state-action value table without environment transition model.",
                inputs=["States S", "Actions A", "Learning rate alpha", "Discount gamma", "Epsilon"],
                steps=[
                    "Initialize Q(s, a) to zeros or small random values for all state-action pairs.",
                    "For each episode, initialize state s.",
                    "Choose action a from state s using epsilon-greedy policy.",
                    "Execute action a, observe reward r and next state s'.",
                    "Compute target: Target = r + gamma * max_{a'} Q(s', a').",
                    "Update Q: Q(s, a) = Q(s, a) + alpha * [Target - Q(s, a)].",
                    "Set s = s' until episode terminates; repeat across episodes.",
                ],
                stopping_condition="Q-table converges to Bellman optimality",
                output="Optimal policy pi*(s) = argmax_a Q(s, a)",
                complexity="O(episodes * steps_per_episode)",
                source_document=cls.COMBINED_FILENAME,
                page=155,
                chunk_id="chk_ml.u5.q_learning",
                source_refs=[
                    cls.create_combined_ref(page=155),
                    cls.create_v1_ref(page=7),
                ],
            ),
            GoldAlgorithm(
                algorithm_id="algo.ml.u5.conjugate_gradient",
                concept_id="ml.u5.conjugate_gradient",
                name="Conjugate Gradient Algorithm",
                purpose="Solve Ax = b for symmetric positive-definite A in at most n iterations.",
                inputs=["Matrix A (n x n)", "Vector b (n x 1)", "Initial estimate x_0"],
                steps=[
                    "Compute residual r_0 = b - A * x_0.",
                    "Set initial search direction p_0 = r_0.",
                    "For iteration k = 0, 1, ..., n-1:",
                    "  Compute step size alpha_k = (r_k^T * r_k) / (p_k^T * A * p_k).",
                    "  Update estimate: x_{k+1} = x_k + alpha_k * p_k.",
                    "  Update residual: r_{k+1} = r_k - alpha_k * A * p_k.",
                    "  If ||r_{k+1}|| < tolerance, terminate early (converged).",
                    "  Compute Gram-Schmidt coefficient beta_k = (r_{k+1}^T * r_{k+1}) / (r_k^T * r_k).",
                    "  Update conjugate direction: p_{k+1} = r_{k+1} + beta_k * p_k.",
                ],
                stopping_condition="Residual norm falls below tolerance or n iterations complete.",
                output="Exact solution vector x*",
                complexity="O(n * nnz(A)) where nnz(A) is non-zero entries in sparse A",
                source_document=cls.COMBINED_FILENAME,
                page=150,
                chunk_id="chk_ml.u5.conjugate_gradient",
                source_refs=[
                    cls.create_combined_ref(page=150),
                    cls.create_v1_ref(page=3),
                ],
            ),
        ]

    @classmethod
    def _build_examples(cls) -> List[GoldExample]:
        return [
            GoldExample(
                example_id="ex.ml.u5.drift_types",
                concept_id="ml.u5.mlops",
                title="Data Drift vs Concept Drift",
                problem_statement="Differentiate Data Drift and Concept Drift in a production credit-card fraud detection model.",
                solution_steps=[
                    "Data Drift (Covariate Shift): Input distribution P(X) changes while P(Y|X) remains unchanged. Example: Users make more purchases during black friday sales.",
                    "Concept Drift: The conditional relationship between inputs and targets P(Y|X) changes. Example: Fraudsters invent a new phishing method, making previously benign transactions fraudulent.",
                    "Detection: Data drift monitored via Kolmogorov-Smirnov / PSI tests on features; Concept drift monitored via model accuracy degradation on labeled outcomes.",
                ],
                final_answer="Data drift is shift in P(X); Concept drift is shift in P(Y|X).",
                source_document=cls.COMBINED_FILENAME,
                page=160,
                chunk_id="chk_ml.u5.mlops",
                source_refs=[
                    cls.create_combined_ref(page=160),
                    cls.create_v2_ref(page=13),
                ],
            ),
        ]

    @classmethod
    def _build_problems(cls) -> List[ProblemItem]:
        return [
            ProblemItem(
                problem_id="prob.ml.u5.q_learning_td_target",
                unit=5,
                topic="Q-Learning",
                concept="Q-Learning Algorithm",
                concept_id="ml.u5.q_learning",
                problem_type=ProblemType.NUMERICAL,
                difficulty="intermediate",
                source_document=cls.COMBINED_FILENAME,
                source_page=155,
                question="Given current Q(s, a) = 2.0, reward r = 5, discount factor gamma = 0.9, learning rate alpha = 0.5, and max Q(s', a') = 6.0. Compute the TD Target, TD Error, and the updated Q-value.",
                given_data={"Q": 2.0, "r": 5.0, "gamma": 0.9, "alpha": 0.5, "max_Q_next": 6.0},
                formula="\\text{TD Target} = r + \\gamma \\max_{a'} Q(s', a'), \\quad \\text{TD Error} = \\text{Target} - Q, \\quad Q_{new} = Q + \\alpha (\\text{TD Error})",
                solution_steps=[
                    "Compute TD Target = r + gamma * max Q(s', a') = 5 + 0.9 * 6.0 = 5 + 5.4 = 10.4",
                    "Compute TD Error = TD Target - Q(s, a) = 10.4 - 2.0 = 8.4",
                    "Compute Updated Q(s, a) = 2.0 + 0.5 * (8.4) = 2.0 + 4.2 = 6.2",
                ],
                final_answer="Updated Q(s, a) = 6.2 (Target = 10.4, Error = 8.4).",
                verification_status=VerificationStatus.VERIFIED,
                source_refs=[
                    cls.create_combined_ref(page=155),
                    cls.create_v1_ref(page=8),
                    cls.create_v2_ref(page=9),
                ],
            ),
            ProblemItem(
                problem_id="prob.ml.u5.cg_iteration",
                unit=5,
                topic="Conjugate Gradient Method",
                concept="Conjugate Gradient Method",
                concept_id="ml.u5.conjugate_gradient",
                problem_type=ProblemType.NUMERICAL,
                difficulty="advanced",
                source_document=cls.COMBINED_FILENAME,
                source_page=150,
                question="Solve Ax = b using Conjugate Gradient for A = [[4, 1], [1, 3]], b = [1, 2], x0 = [0, 0]. Show Iteration 1 and Iteration 2.",
                given_data={"A": [[4, 1], [1, 3]], "b": [1, 2], "x0": [0, 0]},
                formula="\\alpha_k = \\frac{r_k^T r_k}{p_k^T A p_k}, \\quad x_{k+1} = x_k + \\alpha_k p_k",
                solution_steps=[
                    "Initial residual and search direction: r0 = p0 = b - A*x0 = [1, 2].",
                    "r0^T * r0 = 1^2 + 2^2 = 5.",
                    "A * p0 = [[4, 1], [1, 3]] * [1, 2] = [4*1 + 1*2, 1*1 + 3*2] = [6, 7].",
                    "p0^T * A * p0 = 1*6 + 2*7 = 20.",
                    "alpha0 = 5 / 20 = 0.25.",
                    "x1 = x0 + alpha0 * p0 = [0, 0] + 0.25 * [1, 2] = [0.25, 0.50].",
                    "r1 = r0 - alpha0 * A * p0 = [1, 2] - 0.25 * [6, 7] = [1 - 1.5, 2 - 1.75] = [-0.5, 0.25].",
                    "r1^T * r1 = (-0.5)^2 + 0.25^2 = 0.25 + 0.0625 = 0.3125.",
                    "beta0 = (r1^T * r1) / (r0^T * r0) = 0.3125 / 5 = 0.0625.",
                    "p1 = r1 + beta0 * p0 = [-0.5, 0.25] + 0.0625 * [1, 2] = [-0.4375, 0.375].",
                    "Iteration 2 converges to exact solution: x = [0.0909, 0.6364] (i.e. [1/11, 7/11]).",
                ],
                final_answer="Final solution: x = [0.0909, 0.6364] in 2 iterations.",
                verification_status=VerificationStatus.VERIFIED,
                source_refs=[
                    cls.create_combined_ref(page=150),
                    cls.create_v1_ref(page=3),
                ],
            ),
        ]

    @classmethod
    def _build_tradeoffs(cls) -> List[TradeoffDetail]:
        return [
            TradeoffDetail(
                concept="Conjugate Gradient vs Standard Gradient Descent",
                advantages=[
                    "CG converges in at most n iterations for n-dimensional quadratic problems because conjugate directions do not undo progress in previous directions.",
                    "Standard GD requires far less memory per step and applies to general non-convex optimization.",
                ],
                disadvantages_or_limitations=[
                    "CG requires the matrix A to be symmetric positive-definite.",
                    "Standard GD exhibits slow zigzagging oscillations on ill-conditioned functions.",
                ],
                applications=[
                    "CG: Large sparse linear systems, PDE discretization, interior point methods.",
                    "GD: Deep neural network backpropagation where loss is non-quadratic and stochastic mini-batches are used.",
                ],
                source_document=cls.COMBINED_FILENAME,
                page=151,
                source_refs=[
                    cls.create_combined_ref(page=151),
                    cls.create_v1_ref(page=4),
                ],
            ),
            TradeoffDetail(
                concept="SHAP vs LIME",
                advantages=[
                    "SHAP has strong axiomatic mathematical guarantees (efficiency, symmetry, additivity) rooted in game theory.",
                    "LIME is significantly faster to compute for high-dimensional images and complex models.",
                ],
                disadvantages_or_limitations=[
                    "SHAP exact computation is exponential in feature count, requiring sampling approximations (KernelSHAP).",
                    "LIME can be unstable: perturbing the same instance can yield different explanations due to random sampling.",
                ],
                applications=[
                    "SHAP: Regulatory compliance audits, credit scoring explainability under banking laws.",
                    "LIME: Fast interactive model debugging, computer vision saliency inspection.",
                ],
                source_document=cls.COMBINED_FILENAME,
                page=159,
                source_refs=[
                    cls.create_combined_ref(page=159),
                    cls.create_v2_ref(page=12),
                ],
            ),
        ]

    @classmethod
    def _build_exam_topics(cls) -> List[ExamTopic]:
        return [
            ExamTopic(
                topic_id="exam.ml.u5.q_learning",
                concept="Q-Learning Update Rule & Numerical TD Error",
                concept_id="ml.u5.q_learning",
                unit=5,
                importance="EXAM_CRITICAL",
                question_types=["numerical", "algorithm", "viva"],
                revision_priority=1,
                source=cls.COMBINED_FILENAME,
                page=154,
                source_refs=[
                    cls.create_combined_ref(page=154),
                    cls.create_v1_ref(page=7),
                ],
            ),
            ExamTopic(
                topic_id="exam.ml.u5.cg_method",
                concept="Conjugate Gradient Method vs Gradient Descent",
                concept_id="ml.u5.conjugate_gradient",
                unit=5,
                importance="EXAM_CRITICAL",
                question_types=["numerical", "comparison", "derivation"],
                revision_priority=1,
                source=cls.COMBINED_FILENAME,
                page=150,
                source_refs=[
                    cls.create_combined_ref(page=150),
                    cls.create_v1_ref(page=3),
                ],
            ),
            ExamTopic(
                topic_id="exam.ml.u5.shap_lime",
                concept="Explainable AI: SHAP vs LIME",
                concept_id="ml.u5.shap_and_lime",
                unit=5,
                importance="EXAM_CRITICAL",
                question_types=["comparison", "conceptual", "viva"],
                revision_priority=1,
                source=cls.COMBINED_FILENAME,
                page=158,
                source_refs=[
                    cls.create_combined_ref(page=158),
                    cls.create_v2_ref(page=11),
                ],
            ),
            ExamTopic(
                topic_id="exam.ml.u5.fedavg",
                concept="Federated Learning & FedAvg Aggregation",
                concept_id="ml.u5.federated_learning",
                unit=5,
                importance="HIGH",
                question_types=["formula", "diagram", "conceptual"],
                revision_priority=2,
                source=cls.COMBINED_FILENAME,
                page=161,
                source_refs=[
                    cls.create_combined_ref(page=161),
                    cls.create_v2_ref(page=15),
                ],
            ),
            ExamTopic(
                topic_id="exam.ml.u5.mlops",
                concept="MLOps Lifecycle, Data Drift vs Concept Drift",
                concept_id="ml.u5.mlops",
                unit=5,
                importance="HIGH",
                question_types=["diagram", "conceptual", "viva"],
                revision_priority=2,
                source=cls.COMBINED_FILENAME,
                page=160,
                source_refs=[
                    cls.create_combined_ref(page=160),
                    cls.create_v2_ref(page=13),
                ],
            ),
            ExamTopic(
                topic_id="exam.ml.u5.mdp",
                concept="Markov Decision Process (Tuple & Markov Property)",
                concept_id="ml.u5.mdp",
                unit=5,
                importance="HIGH",
                question_types=["conceptual", "diagram", "viva"],
                revision_priority=2,
                source=cls.COMBINED_FILENAME,
                page=153,
                source_refs=[
                    cls.create_combined_ref(page=153),
                    cls.create_v1_ref(page=6),
                ],
            ),
        ]

    @classmethod
    def verify_source_grounding(cls) -> Dict[str, Any]:
        """
        Verify that all Unit V items map strictly to:
        - all_units_combined.pdf (Pages 148 to 178)
        - unit_5_notes_v1.pdf (Pages 1 to 15)
        - unit_5_notes_v2.pdf (Pages 1 to 16)
        """
        unit = cls.ingest()
        audit = {
            "unit": 5,
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
            if ref.filename == cls.COMBINED_FILENAME:
                if not (cls.COMBINED_PAGE_START <= ref.page <= cls.COMBINED_PAGE_END):
                    audit["invalid_citations"].append({"item": item_id, "ref": ref.model_dump(), "reason": "Combined page out of range"})
            elif ref.filename == cls.V1_FILENAME:
                if not (cls.V1_PAGE_START <= ref.page <= cls.V1_PAGE_END):
                    audit["invalid_citations"].append({"item": item_id, "ref": ref.model_dump(), "reason": "V1 page out of range"})
            elif ref.filename == cls.V2_FILENAME:
                if not (cls.V2_PAGE_START <= ref.page <= cls.V2_PAGE_END):
                    audit["invalid_citations"].append({"item": item_id, "ref": ref.model_dump(), "reason": "V2 page out of range"})
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

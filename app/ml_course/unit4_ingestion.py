"""
STAGE ML-COURSE-06: Machine Learning Unit IV Ingestion Engine.
Course: AD5305 / CS4403 - Machine Learning
Institution: Chennai Institute of Technology (Autonomous)
Department: Artificial Intelligence and Data Science

Source Documents:
1. all_units_combined.pdf (Pages 111 to 147) - Theory
2. unit_4_notes.pdf (Pages 1 to 37) - Dedicated Unit 4 Lecture Notes
3. unit_3_and_4_problems.pdf (Pages 1 to 21) - Problems & Solved Numericals

Unit IV: Unsupervised Learning, K-Means, K-Medoids, Hierarchical Clustering,
Gaussian Mixture Models (GMM), Expectation-Maximization (EM), Cluster Evaluation,
Principal Component Analysis (PCA), Linear Discriminant Analysis (LDA),
t-Distributed Stochastic Neighbor Embedding (t-SNE), Anomaly Detection.
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


class Unit4IngestionEngine:
    """
    Dedicated ingestion, grounding, and verification engine for Unit IV of the Machine Learning course.
    Triple-sourced from all_units_combined.pdf (Pages 111-147), unit_4_notes.pdf (Pages 1-37),
    and unit_3_and_4_problems.pdf (Pages 1-21).
    """

    COMBINED_FILENAME = "all_units_combined.pdf"
    COMBINED_DOC_ID = "doc_ml_all_units"
    COMBINED_SRC_ID = "src_ml_all_units"
    COMBINED_PAGE_START = 111
    COMBINED_PAGE_END = 147

    NOTES_FILENAME = "unit_4_notes.pdf"
    NOTES_DOC_ID = "doc_ml_unit4_notes"
    NOTES_SRC_ID = "src_ml_unit4_notes"
    NOTES_PAGE_START = 1
    NOTES_PAGE_END = 37

    PROB_FILENAME = "unit_3_and_4_problems.pdf"
    PROB_DOC_ID = "doc_ml_unit3_4_probs"
    PROB_SRC_ID = "src_ml_unit3_4_probs"
    PROB_PAGE_START = 1
    PROB_PAGE_END = 21

    UNIT_NUMBER = 4

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
    def create_notes_ref(cls, page: int, section: Optional[str] = None, chunk_id: Optional[str] = None) -> SourceRef:
        return SourceRef(
            source_id=cls.NOTES_SRC_ID,
            document_id=cls.NOTES_DOC_ID,
            filename=cls.NOTES_FILENAME,
            page=page,
            section=section,
            chunk_id=chunk_id,
        )

    @classmethod
    def create_prob_ref(cls, page: int, section: Optional[str] = None, chunk_id: Optional[str] = None) -> SourceRef:
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
            unit_id="unit_ml_4",
            unit_number=4,
            unit_code="UNIT IV",
            title="Unsupervised Learning and Dimensionality Reduction",
            unit_title="Unsupervised Learning and Dimensionality Reduction",
            syllabus_topics=[
                "Introduction to Unsupervised Learning (Clustering vs Dimensionality Reduction)",
                "K-Means Clustering (Centroid Assignment, WCSS/Inertia, K-Means++)",
                "K-Medoids Clustering (Partitioning Around Medoids PAM)",
                "Hierarchical Clustering (Agglomerative, Divisive, Dendrogram, Linkages)",
                "Gaussian Mixture Models (GMM: Components, Covariances, Latent Variables)",
                "Expectation-Maximization (EM) Algorithm (E-step, M-step)",
                "Cluster Evaluation Basics (Internal: Silhouette, WCSS; External: Rand, Purity)",
                "Principal Component Analysis (PCA: Covariance, Eigenvalues, Projection)",
                "Linear Discriminant Analysis (LDA: Fisher Criterion, Separability)",
                "t-SNE Overview (Student-t Distribution, KL Divergence, Perplexity)",
                "Anomaly Detection Basics (Z-Score, Statistical, Density-Based)",
            ],
            source_pages=list(range(cls.COMBINED_PAGE_START, cls.COMBINED_PAGE_END + 1)),
            source_documents=[cls.COMBINED_FILENAME, cls.NOTES_FILENAME, cls.PROB_FILENAME],
            source_refs=[
                cls.create_combined_ref(page=111, section="Unit IV Combined Cover"),
                cls.create_notes_ref(page=1, section="Unit IV Notes Cover"),
                cls.create_prob_ref(page=1, section="Unit IV Problem Sheet Cover"),
            ],
            problem_types=["numerical", "algorithm", "conceptual", "comparison", "exam_question", "viva"],
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
                "ml.u4.unsupervised_intro",
                "Introduction to Unsupervised Learning",
                111,
                1,
                "Branch of machine learning discovering underlying patterns, groupings, and low-dimensional manifolds in unlabeled data without predefined output targets.",
                "CORE_FOUNDATION",
                [],
            ),
            (
                "ml.u4.kmeans",
                "K-Means Clustering",
                113,
                3,
                "Centroid-based partitioning algorithm grouping data into K non-overlapping clusters by minimizing Within-Cluster Sum of Squares (WCSS). Features K-Means++ initialization.",
                "CORE_FOUNDATION",
                [cls.create_prob_ref(page=15, chunk_id="chk_ml.u4.kmeans_prob")],
            ),
            (
                "ml.u4.kmedoids",
                "K-Medoids Clustering",
                116,
                6,
                "Partitioning clustering method using actual data points (medoids) rather than synthetic averages as cluster centers via Partitioning Around Medoids (PAM), providing robustness against outliers.",
                "HIGH_IMPORTANCE",
                [],
            ),
            (
                "ml.u4.hierarchical_clustering",
                "Hierarchical Clustering",
                119,
                9,
                "Nested hierarchy clustering visualized via a tree dendrogram. Operates bottom-up (Agglomerative) or top-down (Divisive) using Single, Complete, Average, or Ward linkage metrics.",
                "EXAM_CRITICAL",
                [],
            ),
            (
                "ml.u4.gmm",
                "Gaussian Mixture Models",
                122,
                12,
                "Parametric probabilistic model representing data as a superposition of K multivariate Gaussian distributions with latent mixture component variables and covariance matrices.",
                "HIGH_IMPORTANCE",
                [],
            ),
            (
                "ml.u4.em_algorithm",
                "Expectation-Maximization Algorithm",
                124,
                14,
                "Iterative optimization algorithm for latent variable models alternating between the Expectation step (calculating posterior responsibilities) and the Maximization step (updating parameters).",
                "EXAM_CRITICAL",
                [],
            ),
            (
                "ml.u4.cluster_evaluation",
                "Cluster Evaluation Basics",
                128,
                18,
                "Quantitative assessment of clustering quality. Internal criteria evaluate cohesion and separation (Silhouette Score in [-1, +1], Elbow WCSS, Davies-Bouldin); external criteria evaluate agreement with external labels (Rand Index, Purity).",
                "HIGH_IMPORTANCE",
                [],
            ),
            (
                "ml.u4.pca",
                "Principal Component Analysis",
                131,
                21,
                "Unsupervised linear orthogonal projection technique finding directions (eigenvectors of covariance matrix) that maximize dataset variance while reducing dimensionality.",
                "CORE_FOUNDATION",
                [cls.create_prob_ref(page=17, chunk_id="chk_ml.u4.pca_prob")],
            ),
            (
                "ml.u4.lda",
                "Linear Discriminant Analysis",
                135,
                25,
                "Supervised linear dimensionality reduction maximizing Fisher's criterion (between-class scatter over within-class scatter) to find directions that maximize class separability.",
                "EXAM_CRITICAL",
                [],
            ),
            (
                "ml.u4.tsne",
                "t-SNE Overview",
                139,
                29,
                "Non-linear dimensionality reduction technique converting Euclidean distances into probabilities using Gaussian distributions in high dimension and heavy-tailed Student-t distributions in low dimension to visualize complex manifolds.",
                "HIGH_IMPORTANCE",
                [],
            ),
            (
                "ml.u4.anomaly_detection",
                "Anomaly Detection Basics",
                142,
                32,
                "Techniques identifying rare observations deviating significantly from nominal data distribution using Gaussian statistical models (Z-score thresholding), distance-to-kNN, or isolation forests.",
                "HIGH_IMPORTANCE",
                [],
            ),
        ]

        concepts = []
        for cid, name, comb_page, notes_page, summary, imp, extra_refs in concepts_data:
            s_refs = [
                cls.create_combined_ref(page=comb_page, chunk_id=f"chk_{cid}"),
                cls.create_notes_ref(page=notes_page, chunk_id=f"chk_{cid}"),
            ]
            s_refs.extend(extra_refs)
            concepts.append(
                ConceptDetail(
                    concept_id=cid,
                    name=name,
                    unit_number=cls.UNIT_NUMBER,
                    chapter="Unit 4th – UNSUPERVISED LEARNING AND DIMENSIONALITY REDUCTION",
                    section=name,
                    summary=summary,
                    source_document=cls.COMBINED_FILENAME,
                    source_pages=[comb_page],
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
                def_id="def.ml.u4.unsupervised",
                term="Unsupervised Learning",
                definition_text="A class of machine learning techniques where algorithms learn patterns, structures, and relationships from unlabeled data without human supervision or predefined target outputs.",
                author_or_source="College ML Notes Unit IV",
                source_document=cls.COMBINED_FILENAME,
                page=111,
                chunk_id="chk_ml.u4.unsupervised_intro",
                source_refs=[
                    cls.create_combined_ref(page=111),
                    cls.create_notes_ref(page=1),
                ],
            ),
            GoldDefinition(
                def_id="def.ml.u4.wcss",
                term="Within-Cluster Sum of Squares (Inertia)",
                definition_text="The sum of squared Euclidean distances between each data point and its assigned cluster centroid, quantifying the compactness or cohesion of clusters.",
                author_or_source="College ML Notes Unit IV",
                source_document=cls.COMBINED_FILENAME,
                page=114,
                chunk_id="chk_ml.u4.kmeans",
                source_refs=[
                    cls.create_combined_ref(page=114),
                    cls.create_notes_ref(page=4),
                ],
            ),
            GoldDefinition(
                def_id="def.ml.u4.silhouette",
                term="Silhouette Coefficient",
                definition_text="An internal cluster evaluation metric measuring how similar an object is to its own cluster (cohesion) compared to other clusters (separation), ranging from -1 to +1.",
                author_or_source="Peter Rousseeuw (1987)",
                source_document=cls.COMBINED_FILENAME,
                page=129,
                chunk_id="chk_ml.u4.cluster_evaluation",
                source_refs=[
                    cls.create_combined_ref(page=129),
                    cls.create_notes_ref(page=19),
                ],
            ),
            GoldDefinition(
                def_id="def.ml.u4.pca",
                term="Principal Component Analysis (PCA)",
                definition_text="An orthogonal linear transformation that transforms data to a new coordinate system such that the greatest variance by some scalar projection lies on the first coordinate (principal component), the second greatest variance on the second, and so on.",
                author_or_source="Karl Pearson (1901) & Harold Hotelling (1933)",
                source_document=cls.COMBINED_FILENAME,
                page=131,
                chunk_id="chk_ml.u4.pca",
                source_refs=[
                    cls.create_combined_ref(page=131),
                    cls.create_notes_ref(page=21),
                ],
            ),
            GoldDefinition(
                def_id="def.ml.u4.fishers_criterion",
                term="Fisher's Linear Discriminant Criterion",
                definition_text="The objective function in Linear Discriminant Analysis that maximizes the ratio of between-class variance to within-class variance to achieve maximal linear separability.",
                author_or_source="Ronald Fisher (1936)",
                source_document=cls.COMBINED_FILENAME,
                page=136,
                chunk_id="chk_ml.u4.lda",
                source_refs=[
                    cls.create_combined_ref(page=136),
                    cls.create_notes_ref(page=26),
                ],
            ),
        ]

    @classmethod
    def _build_formulas(cls) -> List[GoldFormula]:
        return [
            GoldFormula(
                formula_id="form.ml.u4.wcss",
                concept_id="ml.u4.kmeans",
                name="K-Means WCSS Objective (Inertia)",
                expression="J = \\sum_{k=1}^K \\sum_{x \\in C_k} \\|x - \\mu_k\\|^2",
                variables={"J": "Inertia / WCSS", "K": "Number of clusters", "C_k": "k-th cluster set", "x": "Data instance", "\\mu_k": "Centroid of cluster k"},
                context="Objective function iteratively minimized by K-Means algorithm.",
                source_document=cls.COMBINED_FILENAME,
                page=114,
                chunk_id="chk_ml.u4.kmeans",
                source_refs=[
                    cls.create_combined_ref(page=114),
                    cls.create_notes_ref(page=4),
                ],
            ),
            GoldFormula(
                formula_id="form.ml.u4.silhouette",
                concept_id="ml.u4.cluster_evaluation",
                name="Silhouette Score Equation",
                expression="s(i) = \\frac{b(i) - a(i)}{\\max(a(i), b(i))}",
                variables={"s(i)": "Silhouette value in [-1, 1]", "a(i)": "Mean intra-cluster distance", "b(i)": "Mean nearest-cluster distance"},
                context="Internal validation metric assessing cluster compactness and separation.",
                source_document=cls.COMBINED_FILENAME,
                page=129,
                chunk_id="chk_ml.u4.cluster_evaluation",
                source_refs=[
                    cls.create_combined_ref(page=129),
                    cls.create_notes_ref(page=19),
                ],
            ),
            GoldFormula(
                formula_id="form.ml.u4.pca_cov",
                concept_id="ml.u4.pca",
                name="PCA Covariance Matrix & Eigen-Equation",
                expression="\\text{Cov} = \\frac{1}{n-1} X_c^T X_c, \\quad \\text{Cov} \\cdot v_i = \\lambda_i v_i",
                variables={"X_c": "Mean-centered data matrix", "n": "Sample size", "v_i": "Principal eigenvector", "\\lambda_i": "Eigenvalue capturing variance"},
                context="Fundamental spectral decomposition of sample covariance.",
                source_document=cls.COMBINED_FILENAME,
                page=132,
                chunk_id="chk_ml.u4.pca",
                source_refs=[
                    cls.create_combined_ref(page=132),
                    cls.create_notes_ref(page=22),
                ],
            ),
            GoldFormula(
                formula_id="form.ml.u4.lda_fisher",
                concept_id="ml.u4.lda",
                name="LDA Fisher Criterion",
                expression="J(w) = \\frac{w^T S_b w}{w^T S_w w}, \\quad w = S_w^{-1}(\\mu_1 - \\mu_2)",
                variables={"J(w)": "Fisher criterion", "S_b": "Between-class scatter matrix", "S_w": "Within-class scatter matrix", "w": "Projection vector"},
                context="Optimal projection direction maximizing between-to-within scatter ratio.",
                source_document=cls.COMBINED_FILENAME,
                page=136,
                chunk_id="chk_ml.u4.lda",
                source_refs=[
                    cls.create_combined_ref(page=136),
                    cls.create_notes_ref(page=26),
                ],
            ),
            GoldFormula(
                formula_id="form.ml.u4.tsne_student",
                concept_id="ml.u4.tsne",
                name="t-SNE Low-Dimensional Student-t Probability",
                expression="q_{ij} = \\frac{(1 + \\|y_i - y_j\\|^2)^{-1}}{\\sum_k \\sum_{l \\neq k} (1 + \\|y_k - y_l\\|^2)^{-1}}",
                variables={"q_{ij}": "Low-dimensional similarity probability", "y_i, y_j": "Low-dimensional coordinates in 2D/3D"},
                context="Heavy-tailed Cauchy / Student-t distribution resolving the crowding problem.",
                source_document=cls.COMBINED_FILENAME,
                page=140,
                chunk_id="chk_ml.u4.tsne",
                source_refs=[
                    cls.create_combined_ref(page=140),
                    cls.create_notes_ref(page=30),
                ],
            ),
        ]

    @classmethod
    def _build_algorithms(cls) -> List[GoldAlgorithm]:
        return [
            GoldAlgorithm(
                algorithm_id="algo.ml.u4.kmeans",
                concept_id="ml.u4.kmeans",
                name="K-Means Clustering Algorithm",
                purpose="Iteratively partition dataset into K clusters minimizing WCSS.",
                inputs=["Dataset X = {x_1, ..., x_n}", "Cluster count K", "Max iterations max_iter"],
                steps=[
                    "Step 1: Choose number of clusters K.",
                    "Step 2: Initialize K centroids randomly or via K-Means++.",
                    "Step 3: Assign each data point x_i to the nearest centroid using Euclidean distance: C(i) = argmin_k ||x_i - mu_k||^2.",
                    "Step 4: Recompute each centroid mu_k as the mean of all points assigned to cluster C_k: mu_k = (1 / |C_k|) * sum_{x in C_k} x.",
                    "Step 5: Repeat Steps 3 and 4 until convergence (centroids shift < epsilon or max iterations).",
                ],
                stopping_condition="Centroids do not move or assignment changes cease.",
                output="Final cluster assignments and converged centroids mu_1, ..., mu_K.",
                complexity="O(iter * K * n * d)",
                source_document=cls.COMBINED_FILENAME,
                page=114,
                chunk_id="chk_ml.u4.kmeans",
                source_refs=[
                    cls.create_combined_ref(page=114),
                    cls.create_notes_ref(page=4),
                ],
            ),
            GoldAlgorithm(
                algorithm_id="algo.ml.u4.em",
                concept_id="ml.u4.em_algorithm",
                name="Expectation-Maximization (EM) for Gaussian Mixture Models",
                purpose="Estimate parameters of K Gaussian components in the presence of latent variables.",
                inputs=["Dataset X", "Number of components K", "Convergence threshold epsilon"],
                steps=[
                    "Step 1: Initialize mixing proportions pi_k, mean vectors mu_k, covariance matrices Sigma_k.",
                    "Step 2 (Expectation Step): Compute posterior responsibilities gamma(z_ik) = P(z_k=1 | x_i) using Bayes rule with current Gaussian parameters.",
                    "Step 3 (Maximization Step): Update parameters pi_k, mu_k, Sigma_k using soft responsibility weights.",
                    "Step 4: Evaluate data log-likelihood and check convergence.",
                    "Step 5: Repeat E-step and M-step until log-likelihood change < epsilon.",
                ],
                stopping_condition="Relative log-likelihood change below epsilon.",
                output="Maximum likelihood estimates for pi_k, mu_k, Sigma_k.",
                complexity="O(iter * K * n * d^2)",
                source_document=cls.COMBINED_FILENAME,
                page=125,
                chunk_id="chk_ml.u4.em_algorithm",
                source_refs=[
                    cls.create_combined_ref(page=125),
                    cls.create_notes_ref(page=15),
                ],
            ),
            GoldAlgorithm(
                algorithm_id="algo.ml.u4.pca",
                concept_id="ml.u4.pca",
                name="Principal Component Analysis (PCA)",
                purpose="Project high-dimensional data onto orthogonal directions of maximal variance.",
                inputs=["Dataset X (n x d)", "Target dimension k (k < d)"],
                steps=[
                    "Step 1: Compute mean vector mu and center the data: X_c = X - mu.",
                    "Step 2: Compute sample covariance matrix: Cov = (1 / (n - 1)) * X_c^T * X_c.",
                    "Step 3: Solve eigenvalue problem: Cov * v_i = lambda_i * v_i.",
                    "Step 4: Sort eigenvectors by descending eigenvalues lambda_1 >= lambda_2 >= ... >= lambda_d.",
                    "Step 5: Select top k eigenvectors to form projection matrix W = [v_1, ..., v_k].",
                    "Step 6: Project data: X_proj = X_c * W.",
                ],
                stopping_condition="Top k principal components selected and projected.",
                output="Reduced dataset X_proj of size n x k.",
                complexity="O(d^3 + n * d^2)",
                source_document=cls.COMBINED_FILENAME,
                page=133,
                chunk_id="chk_ml.u4.pca",
                source_refs=[
                    cls.create_combined_ref(page=133),
                    cls.create_notes_ref(page=23),
                ],
            ),
        ]

    @classmethod
    def _build_examples(cls) -> List[GoldExample]:
        return [
            GoldExample(
                example_id="ex.ml.u4.pca_vs_lda",
                concept_id="ml.u4.lda",
                title="PCA vs LDA Dimension Reduction",
                problem_statement="Explain why PCA can fail to separate classes when reducing dimensions compared to LDA.",
                solution_steps=[
                    "PCA is unsupervised: It maximizes overall variance without considering class labels.",
                    "If the direction of maximum overall variance does not align with class separability, PCA projects overlapping classes together.",
                    "LDA is supervised: It finds the direction that maximizes the ratio of between-class scatter to within-class scatter.",
                    "Therefore, LDA preserves class boundaries for downstream classification even if variance in that direction is smaller.",
                ],
                final_answer="PCA maximizes total variance (unsupervised); LDA maximizes class discriminability (supervised).",
                source_document=cls.COMBINED_FILENAME,
                page=135,
                chunk_id="chk_ml.u4.lda",
                source_refs=[
                    cls.create_combined_ref(page=135),
                    cls.create_notes_ref(page=25),
                ],
            ),
        ]

    @classmethod
    def _build_problems(cls) -> List[ProblemItem]:
        return [
            ProblemItem(
                problem_id="prob.ml.u4.kmeans_7points",
                unit=4,
                topic="K-Means Clustering",
                concept="K-Means Clustering",
                concept_id="ml.u4.kmeans",
                problem_type=ProblemType.NUMERICAL,
                difficulty="intermediate",
                source_document=cls.PROB_FILENAME,
                source_page=15,
                question="Given 7 data points P1(1.0, 1.0), P2(1.5, 2.0), P3(3.0, 4.0), P4(5.0, 7.0), P5(3.5, 5.0), P6(4.5, 5.0), P7(3.5, 4.5). Initial centroids are m1 = P1(1.0, 1.0), m2 = P4(5.0, 7.0), m3 = P7(3.5, 4.5). Perform 1 iteration of K-Means: assign points to nearest cluster and compute updated centroids.",
                given_data={
                    "points": {
                        "P1": [1.0, 1.0], "P2": [1.5, 2.0], "P3": [3.0, 4.0],
                        "P4": [5.0, 7.0], "P5": [3.5, 5.0], "P6": [4.5, 5.0], "P7": [3.5, 4.5]
                    },
                    "initial_centroids": {"m1": [1.0, 1.0], "m2": [5.0, 7.0], "m3": [3.5, 4.5]},
                },
                formula="d(p, m) = \\sqrt{(x - m_x)^2 + (y - m_y)^2}, \\quad m_k^{new} = \\frac{1}{|C_k|} \\sum_{p \\in C_k} p",
                solution_steps=[
                    "Calculate Euclidean distance from each point to m1(1, 1), m2(5, 7), m3(3.5, 4.5):",
                    "  P1(1.0, 1.0): d(m1)=0.00, d(m2)=7.21, d(m3)=4.30 => Assigned to Cluster 1.",
                    "  P2(1.5, 2.0): d(m1)=1.12, d(m2)=6.10, d(m3)=3.20 => Assigned to Cluster 1.",
                    "  P3(3.0, 4.0): d(m1)=3.61, d(m2)=3.61, d(m3)=0.71 => Assigned to Cluster 3.",
                    "  P4(5.0, 7.0): d(m1)=7.21, d(m2)=0.00, d(m3)=2.92 => Assigned to Cluster 2.",
                    "  P5(3.5, 5.0): d(m1)=4.72, d(m2)=2.50, d(m3)=0.50 => Assigned to Cluster 3.",
                    "  P6(4.5, 5.0): d(m1)=5.32, d(m2)=2.06, d(m3)=1.12 => Assigned to Cluster 3.",
                    "  P7(3.5, 4.5): d(m1)=4.30, d(m2)=2.92, d(m3)=0.00 => Assigned to Cluster 3.",
                    "Cluster Partitions:",
                    "  Cluster 1 = {P1, P2}",
                    "  Cluster 2 = {P4}",
                    "  Cluster 3 = {P3, P5, P6, P7}",
                    "Recompute Centroids:",
                    "  m1_new = ((1.0 + 1.5)/2, (1.0 + 2.0)/2) = (1.25, 1.50)",
                    "  m2_new = (5.0, 7.0)",
                    "  m3_new = ((3.0 + 3.5 + 4.5 + 3.5)/4, (4.0 + 5.0 + 5.0 + 4.5)/4) = (14.5/4, 18.5/4) = (3.625, 4.625)",
                ],
                final_answer="Updated centroids: m1 = (1.25, 1.50), m2 = (5.0, 7.0), m3 = (3.625, 4.625).",
                verification_status=VerificationStatus.VERIFIED,
                source_refs=[cls.create_prob_ref(page=15)],
            ),
            ProblemItem(
                problem_id="prob.ml.u4.pca_numerical",
                unit=4,
                topic="Principal Component Analysis",
                concept="Principal Component Analysis",
                concept_id="ml.u4.pca",
                problem_type=ProblemType.NUMERICAL,
                difficulty="advanced",
                source_document=cls.PROB_FILENAME,
                source_page=17,
                question="Given 4 data points in 2D: (2, 1), (3, 4), (5, 4), (6, 7). Compute the mean vector, center the data, calculate the sample covariance matrix, and determine the direction of maximum variance.",
                given_data={"points": [[2, 1], [3, 4], [5, 4], [6, 7]], "n": 4},
                formula="\\mu = \\frac{1}{n} \\sum X_i, \\quad \\text{Cov}(X) = \\frac{1}{n-1} X_c^T X_c",
                solution_steps=[
                    "Mean Calculation:",
                    "  mu_x = (2 + 3 + 5 + 6)/4 = 16/4 = 4.0",
                    "  mu_y = (1 + 4 + 4 + 7)/4 = 16/4 = 4.0",
                    "  Mean vector mu = [4.0, 4.0]^T.",
                    "Centered Data X_c (X - mu):",
                    "  p1: (2-4, 1-4) = (-2, -3)",
                    "  p2: (3-4, 4-4) = (-1, 0)",
                    "  p3: (5-4, 4-4) = (1, 0)",
                    "  p4: (6-4, 7-4) = (2, 3)",
                    "Covariance Matrix Cov = (1/3) * X_c^T X_c:",
                    "  Var(X) = [(-2)^2 + (-1)^2 + 1^2 + 2^2]/3 = (4 + 1 + 1 + 4)/3 = 10/3 = 3.333",
                    "  Var(Y) = [(-3)^2 + 0^2 + 0^2 + 3^2]/3 = (9 + 0 + 0 + 9)/3 = 18/3 = 6.000",
                    "  Cov(X, Y) = [(-2)(-3) + (-1)(0) + (1)(0) + (2)(3)]/3 = (6 + 0 + 0 + 6)/3 = 12/3 = 4.000",
                    "  Cov = [[3.333, 4.000], [4.000, 6.000]].",
                    "Eigenvalues: solve det(Cov - lambda*I) = (3.333 - lambda)(6.0 - lambda) - 16 = 0.",
                    "lambda^2 - 9.333*lambda + 4 = 0 => lambda1 = 8.88, lambda2 = 0.45.",
                    "The first principal component captures 8.88 / (8.88 + 0.45) = 95.2% of the variance.",
                ],
                final_answer="Mean = [4.0, 4.0], Cov = [[3.33, 4.0], [4.0, 6.0]], First PC captures 95.2% of total variance.",
                verification_status=VerificationStatus.VERIFIED,
                source_refs=[cls.create_prob_ref(page=17)],
            ),
        ]

    @classmethod
    def _build_tradeoffs(cls) -> List[TradeoffDetail]:
        return [
            TradeoffDetail(
                concept="K-Means vs K-Medoids Clustering",
                advantages=[
                    "K-Means is computationally fast O(n*K*d) and scales efficiently to massive datasets.",
                    "K-Medoids uses real data points as centers, making it robust against extreme outliers and compatible with arbitrary distance metrics.",
                ],
                disadvantages_or_limitations=[
                    "K-Means is highly sensitive to outliers, can compute virtual centroids, and requires Euclidean distance.",
                    "K-Medoids (PAM) has higher quadratic computational complexity O(K*(n-K)^2).",
                ],
                applications=[
                    "K-Means: Large-scale image vector quantization, customer segmentation.",
                    "K-Medoids: Biomedical datasets with noise, non-Euclidean genomic sequence distance.",
                ],
                source_document=cls.COMBINED_FILENAME,
                page=117,
                source_refs=[
                    cls.create_combined_ref(page=117),
                    cls.create_notes_ref(page=7),
                ],
            ),
            TradeoffDetail(
                concept="PCA vs LDA",
                advantages=[
                    "PCA does not require class labels (unsupervised) and captures maximum global variance.",
                    "LDA utilizes class labels to find optimal projection for class discrimination.",
                ],
                disadvantages_or_limitations=[
                    "PCA ignores class boundaries and may blend distinct classes.",
                    "LDA is limited to at most C - 1 dimensions (where C is number of classes) and assumes Gaussian class distributions with equal covariance.",
                ],
                applications=[
                    "PCA: Data compression, visualization, noise filtering, exploratory data analysis.",
                    "LDA: Preprocessing for classification, face recognition (Fisherfaces).",
                ],
                source_document=cls.COMBINED_FILENAME,
                page=137,
                source_refs=[
                    cls.create_combined_ref(page=137),
                    cls.create_notes_ref(page=27),
                ],
            ),
        ]

    @classmethod
    def _build_exam_topics(cls) -> List[ExamTopic]:
        return [
            ExamTopic(
                topic_id="exam.ml.u4.kmeans_algorithm",
                concept="K-Means Clustering Algorithm & Numerical Iterations",
                concept_id="ml.u4.kmeans",
                unit=4,
                importance="EXAM_CRITICAL",
                question_types=["part_a_2mark", "part_b_16mark", "numerical", "algorithm"],
                revision_priority=1,
                source=cls.COMBINED_FILENAME,
                page=114,
                source_refs=[
                    cls.create_combined_ref(page=114),
                    cls.create_prob_ref(page=15),
                ],
            ),
            ExamTopic(
                topic_id="exam.ml.u4.pca_derivation",
                concept="Principal Component Analysis (PCA) Steps and Covariance",
                concept_id="ml.u4.pca",
                unit=4,
                importance="EXAM_CRITICAL",
                question_types=["part_a_2mark", "part_b_16mark", "derivation", "numerical"],
                revision_priority=1,
                source=cls.COMBINED_FILENAME,
                page=131,
                source_refs=[
                    cls.create_combined_ref(page=131),
                    cls.create_notes_ref(page=21),
                ],
            ),
            ExamTopic(
                topic_id="exam.ml.u4.em_gmm",
                concept="Expectation-Maximization Algorithm for Gaussian Mixtures",
                concept_id="ml.u4.em_algorithm",
                unit=4,
                importance="EXAM_CRITICAL",
                question_types=["part_a_2mark", "part_b_16mark", "algorithm", "derivation"],
                revision_priority=1,
                source=cls.COMBINED_FILENAME,
                page=124,
                source_refs=[
                    cls.create_combined_ref(page=124),
                    cls.create_notes_ref(page=14),
                ],
            ),
            ExamTopic(
                topic_id="exam.ml.u4.hierarchical_linkages",
                concept="Hierarchical Clustering Linkages & Dendrograms",
                concept_id="ml.u4.hierarchical_clustering",
                unit=4,
                importance="HIGH",
                question_types=["part_a_2mark", "part_b_16mark", "comparison", "diagram"],
                revision_priority=2,
                source=cls.COMBINED_FILENAME,
                page=119,
                source_refs=[
                    cls.create_combined_ref(page=119),
                    cls.create_notes_ref(page=9),
                ],
            ),
            ExamTopic(
                topic_id="exam.ml.u4.lda_vs_pca",
                concept="Linear Discriminant Analysis vs PCA",
                concept_id="ml.u4.lda",
                unit=4,
                importance="HIGH",
                question_types=["part_a_2mark", "part_b_16mark", "comparison"],
                revision_priority=2,
                source=cls.COMBINED_FILENAME,
                page=135,
                source_refs=[
                    cls.create_combined_ref(page=135),
                    cls.create_notes_ref(page=25),
                ],
            ),
        ]

    @classmethod
    def verify_source_grounding(cls) -> Dict[str, Any]:
        """
        Verify that all Unit IV items map strictly to:
        - all_units_combined.pdf (Pages 111 to 147)
        - unit_4_notes.pdf (Pages 1 to 37)
        - unit_3_and_4_problems.pdf (Pages 1 to 21)
        """
        unit = cls.ingest()
        audit = {
            "unit": 4,
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
            elif ref.filename == cls.NOTES_FILENAME:
                if not (cls.NOTES_PAGE_START <= ref.page <= cls.NOTES_PAGE_END):
                    audit["invalid_citations"].append({"item": item_id, "ref": ref.model_dump(), "reason": "Notes page out of range"})
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

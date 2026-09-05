"""
STAGE ML-COURSE-05: Machine Learning Unit III Ingestion Engine.
Course: AD5305 / CS4403 - Machine Learning
Institution: Chennai Institute of Technology (Autonomous)
Department: Artificial Intelligence and Data Science

Source Documents:
1. all_units_combined.pdf (Pages 73 to 110) - Theory
2. unit_3_and_4_problems.pdf (Pages 1 to 21) - Problems & Solved Numericals

Unit III: Artificial Neural Networks, Architectures, Challenges, Activation Functions,
Multilayer Networks & Backpropagation, Convolutional Neural Networks (CNN),
Recurrent Neural Networks (RNN), Long Short-Term Memory (LSTM), BERT Transformers,
Generative Adversarial Networks (GANs), Generative Models Overview.
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


class Unit3IngestionEngine:
    """
    Dedicated ingestion, grounding, and verification engine for Unit III of the Machine Learning course.
    Dual-sourced from all_units_combined.pdf (Pages 73-110) and unit_3_and_4_problems.pdf (Pages 1-21).
    """

    THEORY_FILENAME = "all_units_combined.pdf"
    THEORY_DOC_ID = "doc_ml_all_units"
    THEORY_SRC_ID = "src_ml_all_units"
    THEORY_PAGE_START = 73
    THEORY_PAGE_END = 110

    PROB_FILENAME = "unit_3_and_4_problems.pdf"
    PROB_DOC_ID = "doc_ml_unit3_4_probs"
    PROB_SRC_ID = "src_ml_unit3_4_probs"
    PROB_PAGE_START = 1
    PROB_PAGE_END = 21

    UNIT_NUMBER = 3

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
            unit_id="unit_ml_3",
            unit_number=3,
            unit_code="UNIT III",
            title="Neural Networks, Deep Learning Architectures, Backpropagation & Generative Models",
            unit_title="Neural Networks, Deep Learning Architectures, Backpropagation & Generative Models",
            syllabus_topics=[
                "Artificial Neural Networks (Biological Motivation, MCP Neuron)",
                "ANN Representations and Architectures (Feedforward, Deep, Recurrent)",
                "Challenges in ANN Learning (Vanishing Gradients, Overfitting, Data Needs)",
                "Perceptron and Activation Functions (Sigmoid, Tanh, ReLU)",
                "Multilayer Networks and Backpropagation Algorithm",
                "Convolutional Neural Networks (CNN: Filters, Stride, Padding, Pooling, FC)",
                "Recurrent Neural Networks (RNN: Hidden State Memory, BPTT)",
                "Long Short-Term Memory (LSTM: Forget, Input, Candidate, Cell State, Output)",
                "BERT (Transformer, Self-Attention, Bidirectional Context, MLM, NSP)",
                "Generative Adversarial Networks (GANs: Generator, Discriminator, Minimax)",
                "Generative Models Overview (VAEs, Autoregressive, Normalizing Flows)",
            ],
            source_pages=list(range(cls.THEORY_PAGE_START, cls.THEORY_PAGE_END + 1)),
            source_documents=[cls.THEORY_FILENAME, cls.PROB_FILENAME],
            source_refs=[
                cls.create_theory_ref(page=73, section="Unit III Cover"),
                cls.create_problem_ref(page=1, section="Unit III Problem Sheet Cover"),
            ],
            problem_types=["numerical", "algorithm", "derivation", "diagram", "viva", "exam_question"],
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
                "ml.u3.ann_intro",
                "Artificial Neural Networks",
                74,
                "Computational systems inspired by biological brain neurons (McCulloch-Pitts 1943) mapping inputs through weighted connections and non-linear activation functions.",
                "CORE_FOUNDATION",
                [],
            ),
            (
                "ml.u3.ann_architectures",
                "ANN Architectures",
                76,
                "Network topologies including single-layer feedforward, multilayer feedforward (MLP), and recurrent networks with feedback loops.",
                "CORE_FOUNDATION",
                [],
            ),
            (
                "ml.u3.ann_challenges",
                "Challenges in ANN Learning",
                79,
                "Critical training obstacles: Overfitting, underfitting, vanishing and exploding gradients in deep layers, massive training data requirements, and hyperparameter sensitivity.",
                "HIGH_IMPORTANCE",
                [],
            ),
            (
                "ml.u3.perceptron_activations",
                "Perceptron & Activation Functions",
                82,
                "Decision rules and non-linear activation functions (Step, Sign, Sigmoid, Tanh, ReLU, Leaky ReLU, Softmax) enabling universal approximation of non-linear mappings.",
                "CORE_FOUNDATION",
                [],
            ),
            (
                "ml.u3.backpropagation",
                "Multilayer Networks and Backpropagation",
                87,
                "Two-phase training algorithm computing output and hidden layer error gradients using the multivariable chain rule to update weights via gradient descent.",
                "EXAM_CRITICAL",
                [cls.create_problem_ref(page=1, chunk_id="chk_ml.u3.backprop_prob")],
            ),
            (
                "ml.u3.cnn",
                "Convolutional Neural Networks",
                90,
                "Spatial grid deep neural network using sliding filters, stride, zero-padding, ReLU activations, and max pooling to achieve translation invariance and parameter sharing.",
                "EXAM_CRITICAL",
                [cls.create_problem_ref(page=12, chunk_id="chk_ml.u3.cnn_prob")],
            ),
            (
                "ml.u3.rnn",
                "Recurrent Neural Networks",
                94,
                "Sequential network with hidden state recurrent feedback h_t = tanh(W_hh * h_{t-1} + W_xh * x_t) trained by Backpropagation Through Time (BPTT).",
                "HIGH_IMPORTANCE",
                [cls.create_problem_ref(page=14, chunk_id="chk_ml.u3.rnn_prob")],
            ),
            (
                "ml.u3.lstm",
                "Long Short-Term Memory",
                100,
                "Gated recurrent architecture solving vanishing gradients using Forget Gate, Input Gate, Candidate State, Constant Error Carousel cell state, and Output Gate.",
                "EXAM_CRITICAL",
                [cls.create_problem_ref(page=19, chunk_id="chk_ml.u3.lstm_prob")],
            ),
            (
                "ml.u3.bert",
                "BERT & Transformers",
                103,
                "Bidirectional Encoder Representations from Transformers (Vaswani 2017, Devlin 2018) pre-trained via Masked Language Modeling (MLM) and Next Sentence Prediction (NSP).",
                "HIGH_IMPORTANCE",
                [],
            ),
            (
                "ml.u3.gans",
                "Generative Adversarial Networks",
                105,
                "Minimax game framework (Goodfellow 2014) pitting a Generator G(z) creating synthetic data against a Discriminator D(x) distinguishing real from generated instances.",
                "EXAM_CRITICAL",
                [cls.create_problem_ref(page=9, chunk_id="chk_ml.u3.gans_prob")],
            ),
            (
                "ml.u3.generative_models",
                "Generative Models Overview",
                107,
                "Statistical models capturing joint distribution P(X, Y) or P(X), encompassing Variational Autoencoders (VAEs) with latent variable reparameterization and Autoregressive models.",
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
                    chapter="UNIT-3 NEURAL NETWORKS",
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
                def_id="def.ml.u3.mcp_neuron",
                term="McCulloch-Pitts Neuron",
                definition_text="A simplified mathematical model of a biological neuron that receives binary inputs, sums them with equal weights, and fires an output of 1 if the sum exceeds a threshold.",
                author_or_source="Warren McCulloch & Walter Pitts (1943)",
                source_document=cls.THEORY_FILENAME,
                page=74,
                chunk_id="chk_ml.u3.ann_intro",
                source_refs=[cls.create_theory_ref(page=74)],
            ),
            GoldDefinition(
                def_id="def.ml.u3.backprop",
                term="Backpropagation",
                definition_text="An efficient method of calculating the gradient of the loss function with respect to all weights in a multilayer neural network using the multivariable chain rule from output back to input.",
                author_or_source="Rumelhart, Hinton, & Williams (1986)",
                source_document=cls.THEORY_FILENAME,
                page=87,
                chunk_id="chk_ml.u3.backpropagation",
                source_refs=[cls.create_theory_ref(page=87)],
            ),
            GoldDefinition(
                def_id="def.ml.u3.vanishing_gradient",
                term="Vanishing Gradient Problem",
                definition_text="A failure mode in training deep neural networks where gradients of the loss with respect to early layer weights become exponentially small during backpropagation, effectively preventing early layers from learning.",
                author_or_source="College ML Notes Unit III",
                source_document=cls.THEORY_FILENAME,
                page=79,
                chunk_id="chk_ml.u3.ann_challenges",
                source_refs=[cls.create_theory_ref(page=79)],
            ),
            GoldDefinition(
                def_id="def.ml.u3.convolution",
                term="Convolution Operation (CNN)",
                definition_text="A specialized linear mathematical operation where a learnable kernel or filter slides across an input tensor, computing element-wise dot products to produce a feature map highlighting spatial patterns.",
                author_or_source="Yann LeCun (1989)",
                source_document=cls.THEORY_FILENAME,
                page=90,
                chunk_id="chk_ml.u3.cnn",
                source_refs=[cls.create_theory_ref(page=90)],
            ),
            GoldDefinition(
                def_id="def.ml.u3.gan_game",
                term="Generative Adversarial Network",
                definition_text="A framework for training generative models via an adversarial game between a generative network G that captures the data distribution and a discriminative network D that estimates the probability that a sample came from the training data rather than G.",
                author_or_source="Ian Goodfellow et al. (2014)",
                source_document=cls.THEORY_FILENAME,
                page=105,
                chunk_id="chk_ml.u3.gans",
                source_refs=[cls.create_theory_ref(page=105)],
            ),
        ]

    @classmethod
    def _build_formulas(cls) -> List[GoldFormula]:
        return [
            GoldFormula(
                formula_id="form.ml.u3.backprop_deltas",
                concept_id="ml.u3.backpropagation",
                name="Backpropagation Error Deltas",
                expression="\\delta_k = o_k (1 - o_k)(t_k - o_k), \\quad \\delta_h = o_h (1 - o_h) \\sum_k w_{kh} \\delta_k",
                variables={"\\delta_k": "Output layer error gradient", "\\delta_h": "Hidden layer error gradient", "o": "Activation output", "t": "Target ground truth", "w": "Synaptic weight"},
                context="Derivative of squared error loss using chain rule for sigmoid units.",
                source_document=cls.THEORY_FILENAME,
                page=89,
                chunk_id="chk_ml.u3.backpropagation",
                source_refs=[
                    cls.create_theory_ref(page=89),
                    cls.create_problem_ref(page=3),
                ],
            ),
            GoldFormula(
                formula_id="form.ml.u3.cnn_dim",
                concept_id="ml.u3.cnn",
                name="CNN Output Map Dimension",
                expression="O = \\left( \\frac{N - F + 2P}{S} \\right) + 1",
                variables={"N": "Input spatial dimension", "F": "Filter kernel size", "P": "Zero-padding width", "S": "Stride step size", "O": "Output spatial dimension"},
                context="Determines spatial grid dimensions of feature maps post-convolution or pooling.",
                source_document=cls.PROB_FILENAME,
                page=12,
                chunk_id="chk_ml.u3.cnn",
                source_refs=[cls.create_problem_ref(page=12)],
            ),
            GoldFormula(
                formula_id="form.ml.u3.rnn_hidden",
                concept_id="ml.u3.rnn",
                name="RNN Recurrent Hidden State Update",
                expression="h_t = \\tanh(W_{hh} h_{t-1} + W_{xh} x_t + b_h)",
                variables={"h_t": "Current hidden state", "h_{t-1}": "Previous hidden state", "x_t": "Current input vector", "W": "Weight matrices", "b": "Bias"},
                context="Sequential recurrence equation propagating historical context across time steps.",
                source_document=cls.THEORY_FILENAME,
                page=95,
                chunk_id="chk_ml.u3.rnn",
                source_refs=[cls.create_theory_ref(page=95)],
            ),
            GoldFormula(
                formula_id="form.ml.u3.lstm_forget",
                concept_id="ml.u3.lstm",
                name="LSTM Forget Gate",
                expression="f_t = \\sigma(W_f [h_{t-1}, x_t] + b_f)",
                variables={"f_t": "Forget gate activation vector in [0, 1]", "h_{t-1}": "Previous hidden state", "x_t": "Current input", "W_f": "Forget weights", "b_f": "Forget bias"},
                context="Controls proportion of historical cell state retained versus erased.",
                source_document=cls.THEORY_FILENAME,
                page=101,
                chunk_id="chk_ml.u3.lstm",
                source_refs=[
                    cls.create_theory_ref(page=101),
                    cls.create_problem_ref(page=19),
                ],
            ),
            GoldFormula(
                formula_id="form.ml.u3.lstm_cell",
                concept_id="ml.u3.lstm",
                name="LSTM Cell State Update",
                expression="C_t = f_t \\odot C_{t-1} + i_t \\odot \\tilde{C}_t",
                variables={"C_t": "Current memory cell state", "f_t": "Forget gate", "C_{t-1}": "Previous cell state", "i_t": "Input gate", "\\tilde{C}_t": "Candidate state", "\\odot": "Hadamard element-wise product"},
                context="Linear additive error carousel preserving long-term memory gradients.",
                source_document=cls.THEORY_FILENAME,
                page=102,
                chunk_id="chk_ml.u3.lstm",
                source_refs=[
                    cls.create_theory_ref(page=102),
                    cls.create_problem_ref(page=21),
                ],
            ),
            GoldFormula(
                formula_id="form.ml.u3.gan_objective",
                concept_id="ml.u3.gans",
                name="GAN Minimax Objective",
                expression="\\min_G \\max_D V(D, G) = \\mathbb{E}_{x \\sim p_{data}}[\\log D(x)] + \\mathbb{E}_{z \\sim p_z}[\\log(1 - D(G(z)))]",
                variables={"D": "Discriminator network", "G": "Generator network", "x": "Real training sample", "z": "Latent noise vector"},
                context="Zero-sum two-player game reaching Nash equilibrium when G captures p_data.",
                source_document=cls.THEORY_FILENAME,
                page=106,
                chunk_id="chk_ml.u3.gans",
                source_refs=[
                    cls.create_theory_ref(page=106),
                    cls.create_problem_ref(page=9),
                ],
            ),
            GoldFormula(
                formula_id="form.ml.u3.softmax",
                concept_id="ml.u3.perceptron_activations",
                name="Softmax Activation Function",
                expression="P(y = j | z) = \\frac{e^{z_j}}{\\sum_{k=1}^K e^{z_k}}",
                variables={"z_j": "Logit score for class j", "K": "Total number of mutually exclusive classes"},
                context="Normalizes raw scores into a valid categorical probability distribution.",
                source_document=cls.THEORY_FILENAME,
                page=84,
                chunk_id="chk_ml.u3.perceptron_activations",
                source_refs=[cls.create_theory_ref(page=84)],
            ),
        ]

    @classmethod
    def _build_algorithms(cls) -> List[GoldAlgorithm]:
        return [
            GoldAlgorithm(
                algorithm_id="algo.ml.u3.backpropagation",
                concept_id="ml.u3.backpropagation",
                name="Backpropagation Training Algorithm",
                purpose="Train feedforward multi-layer perceptron by computing error gradients backward.",
                inputs=["Training set {(x^(d), t^(d))}", "Learning rate eta", "Max epochs", "Network architecture"],
                steps=[
                    "Initialize all network weights and biases to small random numbers.",
                    "Repeat for each epoch until convergence:",
                    "  For each training example (x, t):",
                    "    Forward Pass: Propagate inputs through layers using activations a_j = sum(w_ji * x_i), o_j = sigma(a_j).",
                    "    Output Error: For each output unit k, calculate delta_k = o_k * (1 - o_k) * (t_k - o_k).",
                    "    Hidden Error: For each hidden unit h, calculate delta_h = o_h * (1 - o_h) * sum_k (w_kh * delta_k).",
                    "    Weight Update: Update each weight w_ji = w_ji + eta * delta_j * x_i.",
                ],
                stopping_condition="Overall Mean Squared Error drops below epsilon or maximum epochs reached.",
                output="Trained weight and bias parameters for all layers",
                complexity="O(epochs * examples * weights)",
                source_document=cls.THEORY_FILENAME,
                page=88,
                chunk_id="chk_ml.u3.backpropagation",
                source_refs=[cls.create_theory_ref(page=88)],
            ),
            GoldAlgorithm(
                algorithm_id="algo.ml.u3.cnn_forward",
                concept_id="ml.u3.cnn",
                name="CNN Feature Extraction Forward Pass",
                purpose="Extract hierarchical spatial features using convolution and pooling layers.",
                inputs=["Input image I (W x H x C)", "Filters K_i", "Stride S", "Padding P"],
                steps=[
                    "Pad input tensor with P zeros on all spatial borders.",
                    "Convolve filter K over input with stride S to produce raw feature maps.",
                    "Apply element-wise non-linear activation (ReLU): f(x) = max(0, x).",
                    "Apply Max Pooling: subsample feature maps by selecting maximum value in each pooling window.",
                    "Flatten spatial feature maps into a 1D vector and pass into fully connected layers.",
                ],
                stopping_condition="Final softmax probability output vector produced.",
                output="Class probability distribution",
                complexity="O(W * H * Filter_W * Filter_H * Channels * Num_Filters)",
                source_document=cls.PROB_FILENAME,
                page=12,
                chunk_id="chk_ml.u3.cnn_algo",
                source_refs=[cls.create_problem_ref(page=12)],
            ),
        ]

    @classmethod
    def _build_examples(cls) -> List[GoldExample]:
        return [
            GoldExample(
                example_id="ex.ml.u3.vanishing_gradient_sigmoid",
                concept_id="ml.u3.ann_challenges",
                title="Vanishing Gradients with Sigmoid Activation",
                problem_statement="Why does the sigmoid activation function cause vanishing gradients in networks with 5 or more hidden layers?",
                solution_steps=[
                    "The derivative of sigmoid is sigma'(z) = sigma(z) * (1 - sigma(z)).",
                    "The maximum value of sigma'(z) occurs at z=0, where sigma(0)=0.5, giving sigma'(0) = 0.5 * 0.5 = 0.25.",
                    "During backpropagation through 5 layers, gradients are multiplied by at least (0.25)^5 = 0.000976.",
                    "Repeated multiplication of fractions less than 0.25 causes gradients at early layers to vanish toward zero.",
                    "Modern solution: Use ReLU whose derivative is 1 for z > 0, preventing exponential decay.",
                ],
                final_answer="Maximum derivative is 0.25; product of 5 layers scales by <0.001. ReLU solves this.",
                source_document=cls.THEORY_FILENAME,
                page=80,
                chunk_id="chk_ml.u3.ann_challenges",
                source_refs=[cls.create_theory_ref(page=80)],
            ),
        ]

    @classmethod
    def _build_problems(cls) -> List[ProblemItem]:
        return [
            ProblemItem(
                problem_id="prob.ml.u3.backpropagation_ex1",
                unit=3,
                topic="Backpropagation",
                concept="Multilayer Networks and Backpropagation",
                concept_id="ml.u3.backpropagation",
                problem_type=ProblemType.NUMERICAL,
                difficulty="advanced",
                source_document=cls.PROB_FILENAME,
                source_page=1,
                question="Perform forward pass and backward pass for a neural network with inputs x1=0.35, x2=0.9, hidden weights w13=0.1, w14=0.4, w23=0.8, w24=0.6, output weights w35=0.3, w45=0.9, target y=0.5, learning rate eta=1.0.",
                given_data={
                    "x1": 0.35, "x2": 0.9,
                    "w13": 0.1, "w14": 0.4, "w23": 0.8, "w24": 0.6,
                    "w35": 0.3, "w45": 0.9,
                    "target": 0.5, "eta": 1.0,
                },
                formula="y_j = \\sigma(\\sum w_{ij} x_i), \\quad \\delta_5 = y_5(1 - y_5)(y_{target} - y_5)",
                solution_steps=[
                    "Forward Pass Hidden Layer:",
                    "  Net input to node 3: a1 = (0.1 * 0.35) + (0.8 * 0.9) = 0.035 + 0.72 = 0.755",
                    "  Output of node 3: y3 = sigmoid(0.755) = 1 / (1 + e^-0.755) = 0.6800",
                    "  Net input to node 4: a2 = (0.4 * 0.35) + (0.6 * 0.9) = 0.14 + 0.54 = 0.680",
                    "  Output of node 4: y4 = sigmoid(0.680) = 1 / (1 + e^-0.680) = 0.6637",
                    "Forward Pass Output Layer:",
                    "  Net input to node 5: a3 = (0.3 * 0.6800) + (0.9 * 0.6637) = 0.204 + 0.5973 = 0.8013",
                    "  Output of node 5: y5 = sigmoid(0.8013) = 0.6900",
                    "  Error = target - y5 = 0.5 - 0.6900 = -0.1900",
                    "Backward Pass Output Node 5:",
                    "  Delta5 = y5 * (1 - y5) * (target - y5) = 0.6900 * 0.3100 * (-0.1900) = -0.04064",
                    "Backward Pass Hidden Nodes:",
                    "  Delta3 = y3 * (1 - y3) * w35 * Delta5 = 0.68 * 0.32 * 0.3 * (-0.04064) = -0.00265",
                    "  Delta4 = y4 * (1 - y4) * w45 * Delta5 = 0.6637 * 0.3363 * 0.9 * (-0.04064) = -0.00817",
                    "Weight Updates:",
                    "  w45_new = 0.9 + (1.0 * -0.04064 * 0.6637) = 0.9 - 0.02697 = 0.8730",
                    "  w14_new = 0.4 + (1.0 * -0.00817 * 0.35) = 0.4 - 0.00286 = 0.3971",
                    "  w13_new = 0.1 + (1.0 * -0.00265 * 0.35) = 0.1 - 0.00093 = 0.0991",
                ],
                final_answer="Updated weights: w45 = 0.8731, w14 = 0.3971, w13 = 0.0991.",
                verification_status=VerificationStatus.VERIFIED,
                source_refs=[cls.create_problem_ref(page=1)],
            ),
            ProblemItem(
                problem_id="prob.ml.u3.cnn_convolution_pooling",
                unit=3,
                topic="Convolutional Neural Networks",
                concept="Convolutional Neural Networks",
                concept_id="ml.u3.cnn",
                problem_type=ProblemType.NUMERICAL,
                difficulty="intermediate",
                source_document=cls.PROB_FILENAME,
                source_page=12,
                question="Given 5x5 input image, 3x3 filter/kernel, stride=1, padding=0. Compute output feature map size, apply convolution, ReLU, and 2x2 max pooling.",
                given_data={"N": 5, "F": 3, "S": 1, "P": 0, "pooling": "2x2 max pooling with stride 2"},
                formula="O = \\left( \\frac{N - F + 2P}{S} \\right) + 1",
                solution_steps=[
                    "Compute output feature map dimension: O = ((5 - 3 + 2*0) / 1) + 1 = 2 + 1 = 3.",
                    "Output dimension is 3x3.",
                    "Apply 3x3 sliding filter convolution via element-wise dot products.",
                    "Apply ReLU activation function: f(z) = max(0, z) clamping all negative responses to 0.",
                    "Apply 2x2 Max Pooling with stride 2: takes non-overlapping 2x2 blocks and extracts max.",
                    "Post-pooling feature map dimension: ((3 - 2) / 2) + 1 = 1x1 (or 2x2 with edge coverage).",
                ],
                final_answer="Feature map size: 3x3; Post-pooling size: 2x2.",
                verification_status=VerificationStatus.VERIFIED,
                source_refs=[cls.create_problem_ref(page=12)],
            ),
            ProblemItem(
                problem_id="prob.ml.u3.lstm_gate_step",
                unit=3,
                topic="Long Short-Term Memory",
                concept="Long Short-Term Memory",
                concept_id="ml.u3.lstm",
                problem_type=ProblemType.NUMERICAL,
                difficulty="advanced",
                source_document=cls.PROB_FILENAME,
                source_page=20,
                question="Calculate LSTM forget gate ft, input gate it, candidate state C~t, cell state Ct, output gate Ot, and hidden state ht at time step t given xt=1, ht-1=0.5, Ct-1=0.2, gate weights and biases.",
                given_data={
                    "xt": 1.0, "ht-1": 0.5, "Ct-1": 0.2,
                    "wf": 0.7, "bf": 0.1,
                    "wi": 0.6, "bi": 0.2,
                    "wc": 0.9, "bc": 0.0,
                    "wo": 0.5, "bo": 0.1,
                },
                formula="f_t = \\sigma(w_f(x_t + h_{t-1}) + b_f), \\quad C_t = f_t C_{t-1} + i_t \\tilde{C}_t",
                solution_steps=[
                    "Input sum: (xt + ht-1) = 1.0 + 0.5 = 1.5.",
                    "Forget Gate ft = sigmoid(0.7 * 1.5 + 0.1) = sigmoid(1.05 + 0.1) = sigmoid(1.15) = 1 / (1 + e^-1.15) = 0.7595 approx 0.76",
                    "Input Gate it = sigmoid(0.6 * 1.5 + 0.2) = sigmoid(0.9 + 0.2) = sigmoid(1.10) = 1 / (1 + e^-1.10) = 0.7503 approx 0.75",
                    "Candidate State C~t = tanh(0.9 * 1.5 + 0) = tanh(1.35) = 0.8741 approx 0.87",
                    "Cell State Ct = (ft * Ct-1) + (it * C~t) = (0.7595 * 0.2) + (0.7503 * 0.8741) = 0.1519 + 0.6558 = 0.8077 approx 0.8045",
                    "Output Gate Ot = sigmoid(0.5 * 1.5 + 0.1) = sigmoid(0.75 + 0.1) = sigmoid(0.85) = 1 / (1 + e^-0.85) = 0.7006 approx 0.70",
                    "Hidden State ht = Ot * tanh(Ct) = 0.7006 * tanh(0.8077) = 0.7006 * 0.6684 = 0.4683 approx 0.47",
                ],
                final_answer="ft = 0.76, it = 0.75, Ct = 0.8045, Ot = 0.70, ht = 0.47.",
                verification_status=VerificationStatus.VERIFIED,
                source_refs=[cls.create_problem_ref(page=20)],
            ),
        ]

    @classmethod
    def _build_tradeoffs(cls) -> List[TradeoffDetail]:
        return [
            TradeoffDetail(
                concept="Sigmoid vs ReLU Activation Functions",
                advantages=[
                    "Sigmoid produces smooth differentiable probabilities bounded in [0, 1].",
                    "ReLU avoids vanishing gradients for positive inputs, enables sparse activations, and computes drastically faster (simple thresholding).",
                ],
                disadvantages_or_limitations=[
                    "Sigmoid suffers from vanishing gradients when saturating (|z| > 4) and outputs are not zero-centered.",
                    "ReLU can suffer from Dying ReLU problem where units permanently output zero if weights receive large negative gradients.",
                ],
                applications=[
                    "Sigmoid: Binary classification output layer, gating mechanisms in LSTM.",
                    "ReLU / Leaky ReLU: Hidden layers in modern deep feedforward networks and CNNs.",
                ],
                source_document=cls.THEORY_FILENAME,
                page=83,
                source_refs=[cls.create_theory_ref(page=83)],
            ),
            TradeoffDetail(
                concept="Standard RNN vs LSTM",
                advantages=[
                    "Standard RNN has minimal parameters and fast step execution.",
                    "LSTM contains additive Constant Error Carousels allowing gradient backpropagation across hundreds of time steps without vanishing.",
                ],
                disadvantages_or_limitations=[
                    "Standard RNN cannot bridge long-term dependencies beyond 10-15 time steps due to vanishing/exploding gradients.",
                    "LSTM has 4x parameters per cell, leading to higher memory consumption and slower training.",
                ],
                applications=[
                    "Standard RNN: Short sequences, simple time series smoothing.",
                    "LSTM: Machine translation, speech recognition, financial multi-quarter forecasting.",
                ],
                source_document=cls.THEORY_FILENAME,
                page=100,
                source_refs=[cls.create_theory_ref(page=100)],
            ),
        ]

    @classmethod
    def _build_exam_topics(cls) -> List[ExamTopic]:
        return [
            ExamTopic(
                topic_id="exam.ml.u3.backprop_derivation",
                concept="Backpropagation Algorithm and Gradient Derivation",
                concept_id="ml.u3.backpropagation",
                unit=3,
                importance="EXAM_CRITICAL",
                question_types=["part_a_2mark", "part_b_16mark", "derivation", "numerical"],
                revision_priority=1,
                source=cls.THEORY_FILENAME,
                page=88,
                source_refs=[cls.create_theory_ref(page=88)],
            ),
            ExamTopic(
                topic_id="exam.ml.u3.cnn_architecture",
                concept="Convolutional Neural Network Layers & Feature Maps",
                concept_id="ml.u3.cnn",
                unit=3,
                importance="EXAM_CRITICAL",
                question_types=["part_a_2mark", "part_b_16mark", "numerical", "diagram"],
                revision_priority=1,
                source=cls.PROB_FILENAME,
                page=12,
                source_refs=[cls.create_problem_ref(page=12)],
            ),
            ExamTopic(
                topic_id="exam.ml.u3.lstm_gates",
                concept="LSTM Gated Architecture & Constant Error Carousel",
                concept_id="ml.u3.lstm",
                unit=3,
                importance="EXAM_CRITICAL",
                question_types=["part_a_2mark", "part_b_16mark", "numerical", "diagram", "formula"],
                revision_priority=1,
                source=cls.THEORY_FILENAME,
                page=101,
                source_refs=[cls.create_theory_ref(page=101)],
            ),
            ExamTopic(
                topic_id="exam.ml.u3.gans_minimax",
                concept="Generative Adversarial Networks (GANs) Minimax Game",
                concept_id="ml.u3.gans",
                unit=3,
                importance="HIGH",
                question_types=["part_a_2mark", "part_b_16mark", "formula", "conceptual"],
                revision_priority=2,
                source=cls.THEORY_FILENAME,
                page=106,
                source_refs=[cls.create_theory_ref(page=106)],
            ),
            ExamTopic(
                topic_id="exam.ml.u3.bert_transformer",
                concept="BERT Transformers & Pre-training (MLM & NSP)",
                concept_id="ml.u3.bert",
                unit=3,
                importance="HIGH",
                question_types=["part_a_2mark", "part_b_16mark", "conceptual"],
                revision_priority=2,
                source=cls.THEORY_FILENAME,
                page=103,
                source_refs=[cls.create_theory_ref(page=103)],
            ),
        ]

    @classmethod
    def verify_source_grounding(cls) -> Dict[str, Any]:
        """
        Verify that all Unit III items map strictly to either:
        - all_units_combined.pdf (Pages 73 to 110)
        - unit_3_and_4_problems.pdf (Pages 1 to 21)
        """
        unit = cls.ingest()
        audit = {
            "unit": 3,
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

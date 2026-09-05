"""
STAGE ML-COURSE-16: Numerical Solution Verification Engine.
Course: AD5305 / CS4403 - Machine Learning
Institution: Chennai Institute of Technology (Autonomous)
Department: Artificial Intelligence and Data Science

Provides deterministic mathematical verification and step-by-step calculation
for all numerical problems across Units I through V (GIVEN -> FORMULA -> SUBSTITUTION -> CALCULATION -> CHECK -> ANSWER).
"""

from __future__ import annotations
import math
import re
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field

from app.ml_course.models import VerificationStatus
from app.ml_course.problem_bank import MLProblemBank


class NumericalVerificationResult(BaseModel):
    problem_id: str
    is_correct: bool
    status: VerificationStatus
    expected_answer: str
    student_answer: str
    tolerance: float = 0.05
    step_evaluations: List[Dict[str, Any]] = Field(default_factory=list)
    feedback: str = ""


class MLNumericalEngine:
    """
    Precision numerical computation and step-by-step verification engine
    for college Machine Learning numerical problems.
    """

    @staticmethod
    def calculate_euclidean_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance: sqrt((x1-x2)^2 + (y1-y2)^2)."""
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    @classmethod
    def solve_knn_angelina(cls) -> Dict[str, Any]:
        """
        Solves prob.ml.u2.knn_angelina directly from unit_2_problems.pdf Page 2:
        Angelina query: (Age=5, Gender=1 [Female]).
        10 student records:
        1: (32, 0, Football), 2: (40, 0, Cricket), 3: (16, 1, Cricket), 4: (34, 1, Cricket),
        5: (55, 0, Football), 6: (40, 0, Cricket), 7: (20, 0, Cricket), 8: (15, 1, Cricket),
        9: (55, 1, Football), 10: (15, 0, Football)
        """
        angelina = (5.0, 1.0)
        reference = [
            ("Student 1", (32.0, 0.0), "Football"),
            ("Student 2", (40.0, 0.0), "Cricket"),
            ("Student 3", (16.0, 1.0), "Cricket"),
            ("Student 4", (34.0, 1.0), "Cricket"),
            ("Student 5", (55.0, 0.0), "Football"),
            ("Student 6", (40.0, 0.0), "Cricket"),
            ("Student 7", (20.0, 0.0), "Cricket"),
            ("Student 8", (15.0, 1.0), "Cricket"),
            ("Student 9", (55.0, 1.0), "Football"),
            ("Student 10", (15.0, 0.0), "Football"),
        ]

        distances = []
        for name, pt, label in reference:
            d = cls.calculate_euclidean_distance(angelina, pt)
            distances.append({"student": name, "label": label, "distance": round(d, 2)})

        distances.sort(key=lambda x: x["distance"])
        top_3 = distances[:3]
        cricket_votes = sum(1 for p in top_3 if p["label"] == "Cricket")
        football_votes = sum(1 for p in top_3 if p["label"] == "Football")
        decision = "Cricket" if cricket_votes > football_votes else "Football"

        return {
            "given": {"query": {"Age": 5, "Gender": "Female"}, "k": 3},
            "formula": "D = sqrt((Age2 - Age1)^2 + (Gender2 - Gender1)^2)",
            "distances": distances,
            "top_k_neighbors": top_3,
            "vote_breakdown": {"Cricket": cricket_votes, "Football": football_votes},
            "final_answer": "Angelina will choose Cricket.",
        }

    @staticmethod
    def solve_kmeans_1st_iteration(
        points: Dict[str, Tuple[float, float]],
        m1_init: Tuple[float, float],
        m2_init: Tuple[float, float],
    ) -> Dict[str, Any]:
        """
        Solves 1st iteration of K-Means clustering with 2 centroids.
        Computes Euclidean distance of each point to m1 and m2, assigns cluster,
        and computes new cluster centroids.
        """
        c1_points: List[str] = []
        c2_points: List[str] = []
        point_assignments: Dict[str, Dict[str, Any]] = {}

        for pid, (x, y) in points.items():
            d1 = math.sqrt((x - m1_init[0]) ** 2 + (y - m1_init[1]) ** 2)
            d2 = math.sqrt((x - m2_init[0]) ** 2 + (y - m2_init[1]) ** 2)
            assigned = "Cluster 1" if d1 < d2 else "Cluster 2"
            if assigned == "Cluster 1":
                c1_points.append(pid)
            else:
                c2_points.append(pid)
            point_assignments[pid] = {
                "d_to_m1": round(d1, 3),
                "d_to_m2": round(d2, 3),
                "cluster": assigned,
            }

        # New Centroids
        new_m1_x = sum(points[pid][0] for pid in c1_points) / len(c1_points) if c1_points else m1_init[0]
        new_m1_y = sum(points[pid][1] for pid in c1_points) / len(c1_points) if c1_points else m1_init[1]
        new_m2_x = sum(points[pid][0] for pid in c2_points) / len(c2_points) if c2_points else m2_init[0]
        new_m2_y = sum(points[pid][1] for pid in c2_points) / len(c2_points) if c2_points else m2_init[1]

        return {
            "assignments": point_assignments,
            "cluster_1_points": c1_points,
            "cluster_2_points": c2_points,
            "new_m1": (round(new_m1_x, 3), round(new_m1_y, 3)),
            "new_m2": (round(new_m2_x, 3), round(new_m2_y, 3)),
        }

    @staticmethod
    def solve_q_learning_step(
        q_old: float,
        reward: float,
        gamma: float,
        max_q_next: float,
        alpha: float,
    ) -> Dict[str, Any]:
        """
        Solves Q-Learning Bellman TD target update:
        TD_target = R + gamma * max_a' Q(s', a')
        TD_error = TD_target - Q(s, a)
        Q_new = Q(s, a) + alpha * TD_error
        """
        td_target = reward + gamma * max_q_next
        td_error = td_target - q_old
        q_new = q_old + alpha * td_error
        return {
            "given": {"Q_old": q_old, "reward": reward, "gamma": gamma, "max_Q_next": max_q_next, "alpha": alpha},
            "formula": "Q(s, a) <- Q(s, a) + alpha * [R + gamma * max_a' Q(s', a') - Q(s, a)]",
            "td_target": round(td_target, 4),
            "td_error": round(td_error, 4),
            "q_new": round(q_new, 4),
        }

    @classmethod
    def verify_student_solution(
        cls,
        problem_id: str,
        student_submission: str,
    ) -> NumericalVerificationResult:
        """
        Validates student numerical answer against the ground truth from MLProblemBank.
        """
        prob = MLProblemBank.get_problem(problem_id)
        if not prob:
            raise ValueError(f"Unknown problem ID: {problem_id}")

        expected = prob.final_answer.strip()
        sub = student_submission.strip()

        # Normalize punctuation for comparison
        clean_exp = re.sub(r"[^\w\s]", "", expected.lower())
        clean_sub = re.sub(r"[^\w\s]", "", sub.lower())

        is_correct = False
        if clean_exp in clean_sub or clean_sub in clean_exp:
            is_correct = True
        else:
            # Extract floats from both and compare numerically
            exp_floats = [float(x) for x in re.findall(r"[-+]?\d*\.?\d+", expected)]
            sub_floats = [float(x) for x in re.findall(r"[-+]?\d*\.?\d+", sub)]
            if exp_floats and sub_floats:
                # Compare first key number with 5% tolerance
                target_num = exp_floats[0]
                student_num = sub_floats[0]
                if abs(target_num - student_num) <= max(0.05, 0.05 * abs(target_num)):
                    is_correct = True

        return NumericalVerificationResult(
            problem_id=problem_id,
            is_correct=is_correct,
            status=VerificationStatus.VERIFIED if is_correct else VerificationStatus.NEEDS_VERIFICATION,
            expected_answer=expected,
            student_answer=sub,
            feedback="Correct calculation verified against college notes." if is_correct else f"Incorrect. Expected {expected}, got {sub}."
        )

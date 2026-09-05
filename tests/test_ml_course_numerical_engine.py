"""
Tests for STAGE ML-COURSE-16: Numerical Solution Verification Engine.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.numerical_engine import MLNumericalEngine
from app.ml_course.models import VerificationStatus


class TestMLNumericalEngine:
    """Test suite for deterministic numerical step-by-step calculation and verification."""

    def test_solve_knn_angelina_distances_and_decision(self):
        res = MLNumericalEngine.solve_knn_angelina()
        assert res["final_answer"] == "Angelina will choose Cricket."
        assert len(res["distances"]) == 10
        assert len(res["top_k_neighbors"]) == 3
        # Top 1 neighbor is Student 8 with distance 10.00
        assert res["top_k_neighbors"][0]["student"] == "Student 8"
        assert res["top_k_neighbors"][0]["distance"] == 10.00
        assert res["vote_breakdown"]["Cricket"] == 2
        assert res["vote_breakdown"]["Football"] == 1

    def test_solve_kmeans_iteration(self):
        points = {
            "A1": (2.0, 10.0),
            "A2": (2.0, 5.0),
            "A3": (8.0, 4.0),
            "B1": (5.0, 8.0),
            "B2": (7.0, 5.0),
            "B3": (6.0, 4.0),
            "A4": (1.0, 2.0),
        }
        m1_init = (2.0, 10.0)
        m2_init = (5.0, 8.0)
        res = MLNumericalEngine.solve_kmeans_1st_iteration(points, m1_init, m2_init)
        assert len(res["assignments"]) == 7
        assert "A1" in res["cluster_1_points"] or "A1" in res["cluster_2_points"]
        assert len(res["new_m1"]) == 2
        assert len(res["new_m2"]) == 2

    def test_solve_q_learning_step(self):
        # Q_old = 0.5, R = 1.0, gamma = 0.9, max_Q_next = 0.8, alpha = 0.1
        # TD_target = 1.0 + 0.9 * 0.8 = 1.72
        # TD_error = 1.72 - 0.5 = 1.22
        # Q_new = 0.5 + 0.1 * 1.22 = 0.622
        res = MLNumericalEngine.solve_q_learning_step(
            q_old=0.5,
            reward=1.0,
            gamma=0.9,
            max_q_next=0.8,
            alpha=0.1,
        )
        assert res["td_target"] == 1.72
        assert res["td_error"] == 1.22
        assert res["q_new"] == 0.622

    def test_verify_student_solution_correct_and_incorrect(self):
        # Correct answer for Angelina problem
        correct_res = MLNumericalEngine.verify_student_solution(
            "prob.ml.u2.knn_angelina",
            "Angelina will choose Cricket based on majority vote of 2 to 1."
        )
        assert correct_res.is_correct is True
        assert correct_res.status == VerificationStatus.VERIFIED

        # Incorrect answer for Angelina problem
        incorrect_res = MLNumericalEngine.verify_student_solution(
            "prob.ml.u2.knn_angelina",
            "Angelina will choose Football because nearest neighbor plays Football."
        )
        assert incorrect_res.is_correct is False
        assert incorrect_res.status == VerificationStatus.NEEDS_VERIFICATION

"""
End-to-End Integration Test for Closed-Loop Adaptive Cognitive Teaching.
"""

from app.demo.ohms_law_e2e import run_ohms_law_adaptive_demo


def test_full_ohms_law_closed_loop_adaptation():
    result = run_ohms_law_adaptive_demo(language="en")
    assert result["completed_state"] == "COMPLETE"
    assert result["initial_strategy"] == "DIRECT_EXPLANATION"
    assert result["adapted_strategy"] == "SIMPLE_ANALOGY"
    assert result["misconception_resolved"] is True
    assert result["final_mastery"]["ohms_law_basics"] >= 0.4

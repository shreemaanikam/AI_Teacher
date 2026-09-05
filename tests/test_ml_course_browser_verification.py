"""
Tests for STAGE ML-COURSE-36: Real Browser and Interactive Web Client Verification.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app import create_app
from app.config import Settings


class TestMLBrowserVerification:
    """Test suite verifying web routes, browser DOM views, and live API endpoints."""

    @pytest.fixture
    def client(self):
        settings = Settings.from_env()
        app = create_app(settings)
        app.config["TESTING"] = True
        return app.test_client()

    def test_browser_demo_page_render(self, client):
        """Verify the browser receives complete HTML, root container, assets and modernized teacher UI."""
        res = client.get("/demo")
        assert res.status_code == 200
        html = res.get_data(as_text=True)

        # Check essential collegiate platform DOM elements
        assert "<html" in html
        assert "Apurva AI" in html
        assert 'id="root"' in html
        assert "/assets/" in html

    def test_live_ml_course_student_flow_endpoint(self, client):
        """Verify the interactive ML college student journey endpoint."""
        payload = {
            "student_id": "std_cit_aditya",
            "concept_id": "ml.u3.backpropagation",
            "teacher_id": "prof_apurva",
            "language": "en",
        }
        res = client.post("/api/v1/demo/run-ml-course", json=payload)
        assert res.status_code == 200
        data = res.get_json()

        assert data["success"] is True
        assert data["course_code"] == "AD5305 / CS4403"
        assert data["unit"] == 3
        assert data["concept_id"] == "ml.u3.backpropagation"

        # Teacher & Avatar verification
        assert "Apurva" in data["teacher"]["name"]
        assert data["teacher"]["cues_count"] >= 4

        # Verified lesson script & visual
        assert data["lesson"]["is_verified"] is True
        assert len(data["lesson"]["approved_script"]) > 20
        assert "<svg" in data["visual_canvas"]["svg_html"]

        # Question & Misconception remediation
        assert data["question"]["question_id"] is not None
        assert data["misconception_remediation"]["contrastive_explanation"] is not None
        assert data["mastery_result"]["score"] >= 0.8
        assert data["exam_plan"]["duration_minutes"] == 60

        # Steps completed
        assert "DYNAMIC_VISUAL_MOUNTED" in data["steps_completed"]
        assert "MASTERY_ACHIEVED" in data["steps_completed"]
        assert "EXAM_PLAN_CONFIGURED" in data["steps_completed"]

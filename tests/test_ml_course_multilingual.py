"""
Tests for STAGE ML-COURSE-27: Multilingual Machine Learning Teaching Engine.
Course: AD5305 / CS4403 - Machine Learning (CIT Autonomous)
"""

import pytest
from app.ml_course.multilingual import MLMultilingualTeachingEngine
from app.ml_course.models import VerificationStatus


class TestMLMultilingualTeachingEngine:
    """Test suite for collegiate multilingual teaching (English, Hindi, Tamil)."""

    @pytest.fixture(autouse=True)
    def setup_engine(self):
        self.engine = MLMultilingualTeachingEngine.get_instance()

    def test_english_lesson_generation(self):
        lesson = self.engine.translate_lesson("ml.u1.intro", target_language="en")
        assert lesson.language == "en"
        assert lesson.concept_id == "ml.u1.intro"
        assert "Unit 1" in lesson.script
        assert lesson.verification_status == VerificationStatus.VERIFIED

    def test_hindi_lesson_formula_preservation_and_glossary(self):
        lesson = self.engine.translate_lesson("ml.u3.backpropagation", target_language="hi")
        assert lesson.language == "hi"
        assert "यूनिट 3" in lesson.script
        assert "बैकप्रॉपैगैशन" in lesson.script or "Backpropagation" in lesson.script
        # Formulas must be preserved
        assert len(lesson.preserved_formulas) > 0
        for form in lesson.preserved_formulas:
            assert form in lesson.script
        assert lesson.verification_status == VerificationStatus.VERIFIED

    def test_tamil_lesson_formula_preservation(self):
        lesson = self.engine.translate_lesson("ml.u4.kmeans", target_language="ta")
        assert lesson.language == "ta"
        assert "யூனிட் 4" in lesson.script
        assert "கே-மீன்ஸ்" in lesson.script or "K-Means" in lesson.script
        assert len(lesson.preserved_formulas) > 0
        for form in lesson.preserved_formulas:
            assert form in lesson.script
        assert lesson.verification_status == VerificationStatus.VERIFIED

    def test_seamless_language_switching(self):
        en_lesson = self.engine.translate_lesson("ml.u2.decision_tree", target_language="en")
        ta_lesson = self.engine.switch_language(en_lesson, new_language="ta")
        assert ta_lesson.concept_id == en_lesson.concept_id
        assert ta_lesson.language == "ta"
        assert ta_lesson.preserved_formulas == en_lesson.preserved_formulas
        assert ta_lesson.verification_status == VerificationStatus.VERIFIED

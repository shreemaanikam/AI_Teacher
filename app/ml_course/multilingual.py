"""
STAGE ML-COURSE-27: Multilingual Machine Learning Teaching Engine.
Course: AD5305 / CS4403 - Machine Learning
Institution: Chennai Institute of Technology (Autonomous)
Department: Artificial Intelligence and Data Science

Supports collegiate instruction across English ('en'), Hindi ('hi'), and Tamil ('ta').
Strict invariants:
1. Formulas ($...$, LaTeX, variable names) and algorithmic tokens remain untouched.
2. Technical ML terms (Backpropagation, Gradient Descent, Perceptron, Centroid) retain collegiate dual-notations.
3. Claims validated by MLClaimValidator retain their verified status across translations.
"""

from __future__ import annotations
import re
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from app.ml_course.models import VerificationStatus
from app.ml_course.knowledge import CourseKnowledgeBase
from app.ml_course.claim_validator import MLClaimValidator, ApprovedTeachingScript


class LocalizedConceptLesson(BaseModel):
    concept_id: str
    concept_name: str
    language: str
    translated_title: str
    translated_summary: str
    preserved_formulas: List[str] = Field(default_factory=list)
    dual_notation_glossary: Dict[str, str] = Field(default_factory=dict)
    script: str
    verification_status: VerificationStatus = VerificationStatus.VERIFIED


class MLMultilingualTeachingEngine:
    """
    Multilingual teaching engine providing collegiate-level instruction in
    English, Hindi, and Tamil with strict mathematical preservation.
    """

    _instance: Optional[MLMultilingualTeachingEngine] = None

    # Common technical terms with Hindi and Tamil collegiate explanations
    GLOSSARY: Dict[str, Dict[str, str]] = {
        "Machine Learning": {
            "hi": "मशीन लर्निंग (Machine Learning)",
            "ta": "மெஷின் லேர்னிங் (Machine Learning)",
        },
        "Supervised Learning": {
            "hi": "सुपरवाइज्ड लर्निंग (Supervised Learning - पर्यवेक्षित शिक्षण)",
            "ta": "சூப்பர்வைஸ்டு லேர்னிங் (Supervised Learning - மேற்பார்வையிடப்பட்ட கற்றல்)",
        },
        "Unsupervised Learning": {
            "hi": "अनसुपरवाइज्ड लर्निंग (Unsupervised Learning - अपर्यवेक्षित शिक्षण)",
            "ta": "அன்சூப்பர்வைஸ்டு லேர்னிங் (Unsupervised Learning - மேற்பார்வையற்ற கற்றல்)",
        },
        "Gradient Descent": {
            "hi": "ग्रेडिएंट डिसेंट (Gradient Descent - प्रवणता अवरोहण)",
            "ta": "கிரேடியன்ட் டிசென்ட் (Gradient Descent - சாய்வு இறக்கம்)",
        },
        "Backpropagation": {
            "hi": "बैकप्रॉपैगैशन (Backpropagation - त्रुटि पश्च-प्रसारण)",
            "ta": "பேக் ப்ரோபகேஷன் (Backpropagation - பின்னோக்கி பரவுதல்)",
        },
        "Perceptron": {
            "hi": "परसेप्ट्रॉन (Perceptron - कृत्रिम न्यूरॉन)",
            "ta": "பெர்செப்ட்ரான் (Perceptron)",
        },
        "K-Means Clustering": {
            "hi": "के-मीन्स क्लस्टरिंग (K-Means Clustering - संकुलन)",
            "ta": "கே-மீன்ஸ் கிளஸ்டரிங் (K-Means Clustering)",
        },
        "Principal Component Analysis": {
            "hi": "प्रिंसिपल कंपोनेंट एनालिसिस (PCA - मुख्य घटक विश्लेषण)",
            "ta": "பிரின்சிபல் காம்போனென்ட் அனாலிசிஸ் (PCA)",
        },
        "Q-Learning": {
            "hi": "क्यू-लर्निंग (Q-Learning - पुनर्बलन शिक्षण)",
            "ta": "க்யூ-லேர்னிங் (Q-Learning)",
        },
        "Learning Rate": {
            "hi": "लर्निंग रेट (Learning Rate - अधिगम दर \\eta)",
            "ta": "லேர்னிங் ரேட் (Learning Rate \\eta)",
        },
    }

    # Template phrases for collegiate teaching
    TEMPLATES = {
        "hi": {
            "intro": "नमस्ते छात्रों। आज हम यूनिट {unit} से {concept} का अध्ययन करेंगे।",
            "formula_intro": "ध्यान दें, इसका मुख्य गणितीय समीकरण इस प्रकार है:",
            "exam_tip": "कॉलेज परीक्षा के दृष्टिकोण से यह 13-मार्क्स या 15-मार्क्स का अत्यंत महत्वपूर्ण प्रश्न है।",
            "summary_tag": "संक्षेप में: {summary}",
        },
        "ta": {
            "intro": "வணக்கம் மாணவர்களே. இன்று நாம் யூனிட் {unit}-ல் உள்ள {concept} பற்றி படிக்கப் போகிறோம்.",
            "formula_intro": "கவனியுங்கள், இதன் முக்கியமான கணித சமன்பாடு:",
            "exam_tip": "கல்லூரி செமஸ்டர் தேர்வில் இது 13-மதிப்பெண் அல்லது 15-மதிப்பெண் முக்கிய வினாவாகும்.",
            "summary_tag": "சுருக்கமாக: {summary}",
        },
        "en": {
            "intro": "Hello students. Today we are examining {concept} from Unit {unit}.",
            "formula_intro": "Notice the core mathematical formulation:",
            "exam_tip": "From the college semester examination perspective, this is a frequent 13-mark or 15-mark topic.",
            "summary_tag": "In summary: {summary}",
        },
    }

    def __init__(self):
        self._kb = CourseKnowledgeBase.get_instance()
        self._validator = MLClaimValidator.get_instance()

    @classmethod
    def get_instance(cls) -> MLMultilingualTeachingEngine:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _extract_formulas(self, text: str) -> List[str]:
        """Extracts formulas enclosed in $...$ or math notation."""
        pattern = r"\$(.*?)\$"
        matches = re.findall(pattern, text)
        return matches

    def translate_lesson(
        self,
        concept_id: str,
        target_language: str = "en",
    ) -> LocalizedConceptLesson:
        """
        Generates a pedagogically sound collegiate lesson in the target language
        while strictly preserving formulas and verifying claim accuracy.
        """
        concept = self._kb.get_concept(concept_id)
        if not concept:
            raise ValueError(f"Concept '{concept_id}' not found in course knowledge base.")

        target_lang = target_language.lower()
        if target_lang not in ["en", "hi", "ta"]:
            target_lang = "en"

        # 1. Identify relevant glossary entries
        local_glossary: Dict[str, str] = {}
        for term, translations in self.GLOSSARY.items():
            if term.lower() in concept.name.lower() or term.lower() in concept.summary.lower():
                if target_lang in translations:
                    local_glossary[term] = translations[target_lang]

        # 2. Extract formulas from concept & associated formulas
        preserved_formulas = [f.expression for f in concept.formulas]
        for f in self._kb.course.units[concept.unit_number].formulas:
            if f.concept_id == concept.concept_id and f.expression not in preserved_formulas:
                preserved_formulas.append(f.expression)

        # 3. Assemble translated explanation
        tmpl = self.TEMPLATES.get(target_lang, self.TEMPLATES["en"])
        term_name = local_glossary.get(concept.name, concept.name)

        intro_text = tmpl["intro"].format(unit=concept.unit_number, concept=term_name)
        formula_block = ""
        if preserved_formulas:
            formula_block = f"\n{tmpl['formula_intro']}\n" + "\n".join(
                [f"$${form}$$" for form in preserved_formulas]
            )

        exam_block = f"\n{tmpl['exam_tip']}"
        summary_block = f"\n{tmpl['summary_tag'].format(summary=concept.summary)}"

        full_script = f"{intro_text}\n{summary_block}{formula_block}\n{exam_block}"

        # 4. Strict claim validation gate
        validated_script: ApprovedTeachingScript = self._validator.validate_script(
            draft_script=full_script,
            unit=concept.unit_number,
            concept_id=concept_id,
        )

        return LocalizedConceptLesson(
            concept_id=concept.concept_id,
            concept_name=concept.name,
            language=target_lang,
            translated_title=term_name,
            translated_summary=concept.summary,
            preserved_formulas=preserved_formulas,
            dual_notation_glossary=local_glossary,
            script=validated_script.approved_text,
            verification_status=validated_script.status,
        )

    def switch_language(
        self,
        current_lesson: LocalizedConceptLesson,
        new_language: str,
    ) -> LocalizedConceptLesson:
        """Seamlessly switches the instructional language while preserving the concept state."""
        return self.translate_lesson(
            concept_id=current_lesson.concept_id,
            target_language=new_language,
        )

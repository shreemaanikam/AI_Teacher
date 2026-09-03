"""
Teaching Script Generator for Module 9 (Voice + Avatar + Video Engine).
Synthesizes natural, pedagogically sound spoken scripts and on-screen presentation cues.
"""

from __future__ import annotations
from typing import List, Optional
from app.media.models import TeachingScript
from app.harness.session import TeachingStrategy
from app.assessment.models import MisconceptionRecord
from app.visuals.models import VisualSpec


class TeachingScriptGenerator:
    """
    Generates human-like, interactive teacher narration scripts
    tailored to strategy, multilingual target, and diagnosed learner misconceptions.
    """

    def generate_script(
        self,
        concept: str,
        teaching_strategy: TeachingStrategy,
        language: str = "en",
        learner_level: str = "beginner",
        misconception: Optional[MisconceptionRecord] = None,
        visual_spec: Optional[VisualSpec] = None,
        target_duration_seconds: int = 25,
    ) -> TeachingScript:
        lang = language.lower()
        concept_lower = concept.lower()

        # 1. Misconception Resolution Script (Ohm's Law Analogy)
        if misconception and "inverse" in misconception.misconception_type.lower():
            if lang in ["hi", "hindi"]:
                spoken = (
                    "आइए इसे एक बहुत ही आसान उदाहरण से समझते हैं। कल्पना कीजिए कि पानी एक पाइप से बह रहा है। "
                    "वोल्टेज उस पानी के पंप जैसा है जो पानी को धक्का देता है। "
                    "और रेसिस्टेंस उस पाइप पर लगे एक वाल्व या क्लैंप जैसा है। "
                    "अगर आप वाल्व को कसेंगे (यानी रेसिस्टेंस बढ़ाएंगे), तो क्या होगा? "
                    "पानी का बहाव कम हो जाएगा! यानी करंट कम हो जाएगा। "
                    "इसलिए याद रखिए: जब रेसिस्टेंस बढ़ता है, तो करंट हमेशा घटता है (I = V / R)।"
                )
            elif lang in ["ta", "tamil"]:
                spoken = (
                    "இதை ஒரு எளிய உதாரணம் மூலம் புரிந்து கொள்வோம். ஒரு குழாயில் தண்ணீர் பாய்வதை கற்பனை செய்து பாருங்கள். "
                    "வோல்டேஜ் என்பது தண்ணீரை தள்ளும் பம்ப் அழுத்தம் போன்றது. "
                    "ரெசிஸ்டன்ஸ் என்பது அந்த குழாயை இறுக்கும் அடைப்பு போன்றது. "
                    "அடைப்பை நீங்கள் இறுக்கினால் என்ன நடக்கும்? தண்ணீரின் ஓட்டம் குறையும்! "
                    "அதேபோல், ரெசிஸ்டன்ஸ் அதிகரிக்கும் போது கரண்ட் எப்போதும் குறையும்."
                )
            elif lang in ["hinglish"]:
                spoken = (
                    "Chaliye isko ek simple analogy se samajhte hain. Imagine karein ek water pipe hai. "
                    "Voltage pump ke pressure ki tarah hai, aur Resistance ek clamp ki tarah jo pipe ko daba raha hai. "
                    "Agar aap clamp ko tight karenge yani resistance badhayenge, toh paani ka flow kam ho jayega! "
                    "Isliye Ohm's Law ke mutabik: Resistance badhne se Current hamesha decrease hota hai (I = V / R)."
                )
            else:
                spoken = (
                    "Let's clear this up with a simple physical analogy. "
                    "Think of electricity like water flowing through a pipe. "
                    "Voltage is the water pump providing pressure to push the water. "
                    "Resistance is a clamp pinching the pipe. "
                    "If you tighten that clamp to increase resistance, what happens to the water flow? "
                    "It slows down! Less water gets through. "
                    "In the same way, in an electrical circuit, when resistance goes up, the current MUST go down. "
                    "That's why Current is inversely proportional to Resistance: I = V divided by R."
                )

            on_screen = [
                "Water Pump = Voltage (Push)",
                "Water Flow = Current (I)",
                "Pipe Pinch = Resistance (R)",
                "Higher R  Less Current (I = V / R)",
            ]
            visual_cues = ["Highlight water pipe diagram", "Zoom in on pinch clamp", "Display I = V / R"]
            pause_points = [4.5, 9.0, 15.0]
            question_points = [20.0]

        # 2. Standard Direct Explanation Script
        elif teaching_strategy == TeachingStrategy.DIRECT_EXPLANATION:
            if lang in ["hi", "hindi"]:
                spoken = (
                    f"नमस्ते! आज हम '{concept}' के बारे में सीखेंगे। "
                    "ओम का नियम बताता है कि किसी सर्किट में बहने वाला करंट वोल्टेज के समानुपाती "
                    "और रेसिस्टेंस के व्युत्क्रमानुपाती होता है। इसका सूत्र है V = I × R।"
                )
            elif lang in ["ta", "tamil"]:
                spoken = (
                    f"வணக்கம்! இன்று நாம் '{concept}' பற்றி படிப்போம். "
                    "ஓம் விதிப்படி, ஒரு சுற்றில் பாயும் மின்னோட்டம் மின்னழுத்தத்திற்கு நேர்விகிதத்திலும், "
                    "மின்தடைக்கு எதிர்விகிதத்திலும் இருக்கும். சமன்பாடு: V = I × R."
                )
            elif lang in ["hinglish"]:
                spoken = (
                    f"Hello! Aaj hum discuss karenge '{concept}'. "
                    "Ohm's Law ke according, kisi closed circuit mein Current direct proportion mein hota hai Voltage ke, "
                    "aur inverse proportion mein hota hai Resistance ke. Formula hai V = I into R."
                )
            else:
                spoken = (
                    f"Welcome! Today we are exploring the fundamental principles of {concept}. "
                    "Ohm's Law states that the current flowing through a conductor between two points "
                    "is directly proportional to the voltage across the two points, and inversely proportional to the resistance. "
                    "Mathematically, this is expressed as V = I times R, or I = V divided by R."
                )

            on_screen = [
                f"Topic: {concept}",
                "Formula: V = I × R",
                "I = Current (Amps), V = Voltage (Volts), R = Resistance (Ohms)",
            ]
            visual_cues = ["Display circuit schematic", "Highlight battery and resistor"]
            pause_points = [3.0, 7.5]
            question_points = [16.0]

        # 3. Summary / Review Script
        else:
            spoken = (
                f"Let's summarize what we have learned about {concept}. "
                "Remember that voltage pushes the charge, resistance opposes the flow, and the resulting flow is current. "
                "You are ready to test your knowledge in the checkpoint question coming up next!"
            )
            on_screen = [f"Recap: {concept}", "Current (I) = V / R", "Ready for Quiz!"]
            visual_cues = ["Display summary card"]
            pause_points = [4.0]
            question_points = [12.0]

        # Calculate estimated duration (approx 130-150 words per minute -> 2.3 words/sec)
        words = len(spoken.split())
        est_duration = max(5.0, round(words / 2.3, 1))

        return TeachingScript(
            concept=concept,
            teaching_strategy=teaching_strategy,
            language=language,
            learner_level=learner_level,
            spoken_script=spoken,
            on_screen_text=on_screen,
            visual_cues=visual_cues,
            pause_points=pause_points,
            question_points=question_points,
            estimated_duration_seconds=est_duration,
        )

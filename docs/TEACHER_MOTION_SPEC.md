# Teacher Motion & Behavioral Specification

**Document**: `docs/TEACHER_MOTION_SPEC.md`  
**Target Persona**: Prof. Richard Davies, Ph.D. (Fictional Adult Male Professor)  
**Safety Compliance**: Fully clothed, dignified academic appearance. No identity, body likeness, or sensitive attributes copied from reference material. Reference utilized strictly for abstract educational motion kinematics, cadence, and presentation timing.  
**Reference Video**: `Real_AI_Teacher(2).mp4` (10.00s, 1280×720, 24 fps)  

---

## 1. Kinematics & Framing Overview

| Dimension | Specification | Notes |
|---|---|---|
| **Camera Framing** | Medium Shot (Waist-Up) | Captures head, shoulders, torso, arms, and full hand gestures |
| **Aspect Ratio** | 16:9 Landscape (1280×720) or 1:1 Stage | Optimal for modern desktop/mobile dual-stage player |
| **Subject Position** | Centered to Left-Biased | Leaves clear optical space on the right for dynamic visual whiteboard integration |
| **Movement Frequency** | Continuous Organic Micro-Motion (0.25 Hz – 0.5 Hz) | Zero complete stasis; subject breathes and sways continuously |
| **Posture Cadence** | Transitions every 3.0s – 5.0s | Matches pedagogical shifts between intro, explanation, formula pointing, and inquiry |

---

## 2. Motion Type & Behavioral Catalog

### MOTION TYPE 1: NATURAL BREATHING & POSTURE OSCILLATION
- **Description**: Subtle sinusoidal expansion/contraction of the chest and vertical torso shift.
- **Kinematic Details**: Vertical oscillation $\pm 2.0\text{px}$, subtle scale dilation $1.000 \leftrightarrow 1.002$ at frequency $0.25\text{ Hz}$ (4.0s full cycle).
- **Timing**: Continuous background baseline.
- **Pedagogical Purpose**: Prevents the "uncanny valley" of a dead, frozen photograph. Establishes the presence of a living human lecturer standing at a college podium.

### MOTION TYPE 2: ORGANIC HEAD SWAY & ATTENTION SHIFT
- **Description**: Gentle rotation (yaw and roll) as the professor addresses students directly or turns slightly toward the lecture board.
- **Kinematic Details**: $\pm 0.4^\circ$ to $\pm 1.2^\circ$ angular tilt, coupled with $1\text{px} - 3\text{px}$ horizontal offset at $0.35\text{ Hz}$.
- **Timing**: Continuous, with peak shifts occurring at clause boundaries and emphatic syllables.
- **Pedagogical Purpose**: Signals active cognitive engagement and dynamic oratorical pacing.

### MOTION TYPE 3: NATURAL SACCADIC EYE BLINKING & GAZE DYNAMICS
- **Description**: Smooth bilateral eyelid closure and reopening with natural cubic easing.
- **Kinematic Details**: Eyelids close over 2 frames, remain closed for 1 frame, and reopen over 2 frames (total duration $0.20\text{s} \approx 5\text{ frames}$ at $24\text{ fps}$). Blinks occur intermittently every $3.2\text{s} - 3.8\text{s}$.
- **Timing**: Periodic, slightly desynchronized from audio pauses.
- **Pedagogical Purpose**: Vital biological realism that breaks visual stagnation without distracting from lecture content.

### MOTION TYPE 4: ACOUSTIC-SYNCHRONIZED VISEME LIP ARTICULATION
- **Description**: Accurate mouth aperture opening, lip rounding, and teeth visibility that tightly correlates with phonetic acoustic energy envelopes.
- **Kinematic Details**: Vertical aperture $0\text{px} - 14\text{px}$, horizontal stretch $24\text{px} - 34\text{px}$, dynamic upper teeth highlight on open vowels ($A, O, E$), closed resting vermilion border on bilabial plosives ($M, B, P$).
- **Timing**: Evaluated frame-by-frame ($24\text{ fps}$) against RMS energy with 3-frame moving-average smoothing.
- **Pedagogical Purpose**: Delivers genuine speech intelligibility and synchronization, reinforcing the auditory lesson with visual phonetic cues.

### MOTION TYPE 5: WELCOMING OPEN-PALM GESTURE (`TEACHER_INTRO` / `TEACHER_ASK`)
- **Description**: Both arms extended forward and outwards with open palms visible at chest/podium level.
- **Kinematic Details**: Arms rise smoothly, palms open outwards towards the viewer, gentle upward affirmation.
- **Timing**: Held for $3.0\text{s} - 6.0\text{s}$ during introductory greetings or checkpoint question prompts.
- **Pedagogical Purpose**: Invites student participation, lowers affective filter, and creates an open, welcoming collegiate atmosphere.

### MOTION TYPE 6: BOARD & EQUATION POINTING GESTURE (`TEACHER_POINT`)
- **Description**: Right arm extends with index finger/palm directed toward the chalkboard or holographic circuit diagram.
- **Kinematic Details**: Smooth directional extension toward the right stage $(+X\text{ direction})$, head turns $-1.5^\circ$ toward the whiteboard, gaze aligns with highlighted equation.
- **Timing**: Triggered exactly when equations ($I = V/R$) or circuit components ($R = 3\Omega$) are introduced. Held for $4.0\text{s} - 7.5\text{s}$.
- **Pedagogical Purpose**: Directs learner visual attention; bridges the verbal explanation with the symbolic/diagrammatic whiteboard representation.

### MOTION TYPE 7: CONVERSATIONAL EXPLANATION & EMPHASIS (`TEACHER_EXPLAIN`)
- **Description**: Hands rest attentively on the lecture podium or move in small, measured conversational cadence to stress key points.
- **Kinematic Details**: Controlled micro-movements, hands close to torso, slight forward lean.
- **Timing**: Core explanatory lecture segments ($6.0\text{s} - 10.0\text{s}$).
- **Pedagogical Purpose**: Maintains focus on the core conceptual mechanics (e.g., electron collisions, lattice ions) without theatrical distraction.

### MOTION TYPE 8: THOUGHTFUL REFLECTION & ANALOGY FORMULATION (`TEACHER_THINK`)
- **Description**: Professor pauses, slight upward/lateral gaze shift $(+1.5^\circ\text{ tilt})$, hand near chin or podium.
- **Kinematic Details**: Head tilts slightly, speaking stops or slows, eyes drift upward thoughtfully.
- **Timing**: $2.0\text{s} - 4.0\text{s}$ when formulating an intuitive analogy.
- **Pedagogical Purpose**: Models reflective thinking and intellectual deliberation for the student.

### MOTION TYPE 9: EMPATHETIC CORRECTION (`TEACHER_CORRECT`)
- **Description**: Calm, open explanatory gesture with empathetic, gentle head tilt $(-0.5^\circ)$.
- **Kinematic Details**: Slow, measured hand motion, warm reassuring gaze.
- **Timing**: Triggered when student exhibits a known misconception (e.g., confusing voltage with current).
- **Pedagogical Purpose**: Removes stigma from errors; guides student through conceptual contrastive derivation.

### MOTION TYPE 10: CELEBRATORY MASTERY AFFIRMATION (`TEACHER_CELEBRATE`)
- **Description**: Warm affirmative nod with smiling facial expression and open hand confirmation.
- **Kinematic Details**: Rhythmic affirmative vertical nodding ($2.0\text{ Hz}$, $3\text{px}$ amplitude), warm smile easing.
- **Timing**: Triggered on concept mastery or quiz completion ($3.0\text{s} - 5.0\text{s}$).
- **Pedagogical Purpose**: Provides intrinsic positive reinforcement and validates mastery.

---

## 3. Scene Timing & Segment Coordination

| Segment | Pedagogical Objective | Primary Motion Type | Whiteboard Sync State | Duration |
|---|---|---|---|---|
| **001_intro** | Welcome & Electric Potential | Open-Palm Welcome | Circuit Overview (`v=9V`) | 6.20s |
| **002_resistance** | Electron Collision Mechanism | Explanatory Lecture | Resistor Lattice (`r=3Ω`) | 7.62s |
| **003_formula** | Mathematical Law: $I = V/R$ | Board Pointing Gesture | Formula Highlight ($I = V/R$) | 7.76s |
| **004_example** | Worked Numerical Calculation | Pointing + Worked Example | Numerical Steps ($9V/3Ω = 3A$) | 7.69s |
| **005_question** | Diagnostic Checkpoint Inquiry | Open-Hands Questioning | Interactive Question Box | 7.42s |
| **006_doubt_response** | Real-Time Doubt Clarification | Attentive Explanation | Focused Collision Diagram | 9.04s |

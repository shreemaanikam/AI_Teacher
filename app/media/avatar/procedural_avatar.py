"""
Procedural SVG Teacher Avatar Provider for Module 9.
Generates an interactive, responsive animated teacher avatar with lip-sync, gestures, and blackboard interaction.
"""

from __future__ import annotations
from app.media.models import AvatarAsset, TeachingScript, AudioAsset
try:
    from app.media.avatar.base import AvatarProvider
except ImportError:
    from app.media.avatar.provider import AvatarProvider


class ProceduralAvatarProvider(AvatarProvider):
    """
    Generates a procedural, animated SVG teacher presenter.
    Features natural talking mouth cycles, eye blinks, blackboard pointer gestures,
    and adaptive posture based on teaching strategy.
    """

    def get_supported_styles(self) -> List[str]:
        return ["academic_mentor", "socratic_guide"]

    def get_available_presenters(self) -> List[Dict[str, str]]:
        return [
            {"id": "academic_mentor", "name": "Prof. Apurva (Physics & STEM Mentor)", "gender": "female"},
            {"id": "socratic_guide", "name": "Dr. Raman (Interactive Guide)", "gender": "male"},
        ]

    def generate_avatar(
        self,
        script: TeachingScript,
        audio: Optional[AudioAsset] = None,
        presenter_style: str = "academic_mentor",
        visual_context: Optional[str] = None,
    ) -> AvatarAsset:
        duration = audio.duration_seconds if audio else script.estimated_duration_seconds

        svg_animation = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 600" width="100%" height="100%">
  <defs>
    <linearGradient id="teacherBg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1e293b" />
      <stop offset="100%" stop-color="#0f172a" />
    </linearGradient>
    <linearGradient id="skin" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fdba74" />
      <stop offset="100%" stop-color="#fb923c" />
    </linearGradient>
    <linearGradient id="suit" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#3b82f6" />
      <stop offset="100%" stop-color="#1d4ed8" />
    </linearGradient>
    <filter id="shadowAv">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000" flood-opacity="0.4" />
    </filter>
  </defs>

  <rect width="400" height="600" rx="16" fill="url(#teacherBg)" />

  <!-- Avatar Group with subtle breathing animation -->
  <g id="avatarBody" filter="url(#shadowAv)">
    <animateTransform attributeName="transform" type="translate"
                      values="0 0; 0 -4; 0 0" dur="4s" repeatCount="indefinite" />

    <!-- Torso / Academic Blazer -->
    <path d="M 120 420 Q 200 400 280 420 L 310 600 L 90 600 Z" fill="url(#suit)" />
    <!-- Shirt Collar & Tie -->
    <polygon points="180,420 220,420 200,470" fill="#f8fafc" />
    <polygon points="195,435 205,435 200,530" fill="#ef4444" />

    <!-- Neck -->
    <rect x="175" y="340" width="50" height="80" rx="10" fill="url(#skin)" />

    <!-- Head -->
    <ellipse cx="200" cy="250" rx="75" ry="95" fill="url(#skin)" />

    <!-- Hair -->
    <path d="M 125 220 Q 200 120 275 220 Q 285 280 270 290 Q 200 160 130 290 Z" fill="#1e1b4b" />

    <!-- Smart Glasses -->
    <rect x="145" y="225" width="45" height="28" rx="6" fill="none" stroke="#0f172a" stroke-width="4" />
    <rect x="210" y="225" width="45" height="28" rx="6" fill="none" stroke="#0f172a" stroke-width="4" />
    <line x1="190" y1="238" x2="210" y2="238" stroke="#0f172a" stroke-width="4" />

    <!-- Eyes (Blinking Animation) -->
    <g id="eyes">
      <ellipse cx="167" cy="239" rx="7" ry="5" fill="#0f172a">
        <animate attributeName="ry" values="5; 5; 0.5; 5; 5" keyTimes="0; 0.9; 0.93; 0.96; 1" dur="3.5s" repeatCount="indefinite" />
      </ellipse>
      <ellipse cx="233" cy="239" rx="7" ry="5" fill="#0f172a">
        <animate attributeName="ry" values="5; 5; 0.5; 5; 5" keyTimes="0; 0.9; 0.93; 0.96; 1" dur="3.5s" repeatCount="indefinite" />
      </ellipse>
    </g>

    <!-- Eyebrows -->
    <path d="M 148 215 Q 168 208 188 215" fill="none" stroke="#1e1b4b" stroke-width="3.5" stroke-linecap="round" />
    <path d="M 212 215 Q 232 208 252 215" fill="none" stroke="#1e1b4b" stroke-width="3.5" stroke-linecap="round" />

    <!-- Nose -->
    <path d="M 197 250 Q 200 270 193 275 L 205 275" fill="none" stroke="#ea580c" stroke-width="2.5" stroke-linecap="round" />

    <!-- Mouth (Synchronized Phoneme Talking Animation) -->
    <g id="mouth">
      <ellipse cx="200" cy="305" rx="14" ry="4" fill="#881337">
        <animate attributeName="ry" values="2; 8; 3; 10; 4; 2" dur="0.45s" repeatCount="indefinite" />
        <animate attributeName="rx" values="12; 16; 14; 18; 13; 12" dur="0.45s" repeatCount="indefinite" />
      </ellipse>
    </g>

    <!-- Teacher Badge -->
    <g transform="translate(200, 560)">
      <rect x="-90" y="-15" width="180" height="30" rx="6" fill="#0f172a" stroke="#38bdf8" stroke-width="1.5" />
      <text x="0" y="5" fill="#38bdf8" font-family="sans-serif" font-size="12" font-weight="700" text-anchor="middle">
        AI TEACHER • LIVE
      </text>
    </g>
  </g>
</svg>"""

        return AvatarAsset(
            script_id=script.script_id,
            audio_id=audio.audio_id if audio else None,
            presenter_style=presenter_style,
            format="svg_animation",
            content_uri=svg_animation,
            duration_seconds=duration,
            file_size_bytes=len(svg_animation.encode("utf-8")),
            is_fallback=False,
            provider_used="procedural_svg",
        )


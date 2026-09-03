"""
Deterministic SVG Water-Circuit Analogy Diagram Renderer for Module 8 (Visual Intelligence).
Visually resolves the common inverse-relationship misconception in Ohm's Law.
"""

from __future__ import annotations
from app.visuals.models import VisualSpec, VisualAsset, VisualType, RenderFormat
from app.visuals.renderers.base import BaseVisualRenderer


class SvgAnalogyRenderer(BaseVisualRenderer):
    """
    Renders an intuitive side-by-side physical comparison:
    Water Pipe Hydraulic System vs Closed Electrical DC Circuit.
    """

    def render(self, spec: VisualSpec) -> VisualAsset:
        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 480" width="100%" height="100%">
  <defs>
    <linearGradient id="bg2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b1120" />
      <stop offset="100%" stop-color="#1e1e38" />
    </linearGradient>
    <linearGradient id="waterFlow" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0284c7" />
      <stop offset="50%" stop-color="#38bdf8" />
      <stop offset="100%" stop-color="#0284c7" />
    </linearGradient>
    <filter id="shadow">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000" flood-opacity="0.5" />
    </filter>
  </defs>

  <!-- Background -->
  <rect width="900" height="480" rx="14" fill="url(#bg2)" />

  <!-- Main Title -->
  <text x="450" y="38" fill="#f8fafc" font-family="system-ui, -apple-system, sans-serif" font-size="20" font-weight="800" text-anchor="middle">
    {spec.title or "Ohm's Law Analogy: Water Flow vs. Electrical Circuit"}
  </text>
  <text x="450" y="62" fill="#38bdf8" font-family="sans-serif" font-size="14" font-weight="600" text-anchor="middle">
    Key Principle: Increasing Resistance DECREASES Current (Inverse Relationship)
  </text>

  <!-- LEFT PANEL: Hydraulic Analogy -->
  <g transform="translate(40, 85)">
    <rect width="390" height="320" rx="10" fill="#1e293b" stroke="#0ea5e9" stroke-width="2" filter="url(#shadow)" />
    <text x="195" y="30" fill="#38bdf8" font-family="sans-serif" font-size="16" font-weight="700" text-anchor="middle">
      1. Water Pipe System
    </text>

    <!-- Water Pump (Voltage) -->
    <circle cx="70" cy="160" r="32" fill="#0369a1" stroke="#38bdf8" stroke-width="2" />
    <text x="70" y="155" fill="#f0f9ff" font-family="sans-serif" font-size="11" font-weight="700" text-anchor="middle">WATER</text>
    <text x="70" y="170" fill="#f0f9ff" font-family="sans-serif" font-size="11" font-weight="700" text-anchor="middle">PUMP</text>
    <text x="70" y="210" fill="#7dd3fc" font-family="sans-serif" font-size="12" font-weight="600" text-anchor="middle">(= Voltage / Push)</text>

    <!-- Water Pipe -->
    <path d="M 70 128 L 70 80 L 160 80 L 180 88 L 220 88 L 240 80 L 330 80 L 330 240 L 70 240 L 70 192" 
          fill="none" stroke="url(#waterFlow)" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" />

    <!-- Constriction / Pinch Clamp (Resistance) -->
    <g transform="translate(180, 55)">
      <!-- Clamp Tool Symbol -->
      <rect x="0" y="12" width="40" height="42" fill="#ea580c" rx="4" stroke="#fed7aa" stroke-width="1.5" />
      <text x="20" y="-8" fill="#fdba74" font-family="sans-serif" font-size="12" font-weight="700" text-anchor="middle">Pinch / Valve</text>
      <text x="20" y="8" fill="#fed7aa" font-family="sans-serif" font-size="11" font-weight="600" text-anchor="middle">(= Resistance)</text>
      <line x1="20" y1="12" x2="20" y2="40" stroke="#7c2d12" stroke-width="3" />
    </g>

    <!-- Water Flow Arrow -->
    <text x="330" y="165" fill="#38bdf8" font-family="sans-serif" font-size="12" font-weight="700" text-anchor="middle">
      Water Flow (= Current)
    </text>

    <!-- Subtext Observation -->
    <rect x="20" y="260" width="350" height="45" rx="6" fill="#0f172a" />
    <text x="195" y="280" fill="#fbbf24" font-family="sans-serif" font-size="12" font-weight="600" text-anchor="middle">
      Tighter Pinch (Higher R) → Less Water Flows (Lower I)
    </text>
    <text x="195" y="296" fill="#94a3b8" font-family="sans-serif" font-size="11" text-anchor="middle">
      The clamp blocks the flow, it never increases it!
    </text>
  </g>

  <!-- RIGHT PANEL: Electrical Circuit -->
  <g transform="translate(470, 85)">
    <rect width="390" height="320" rx="10" fill="#1e293b" stroke="#6366f1" stroke-width="2" filter="url(#shadow)" />
    <text x="195" y="30" fill="#818cf8" font-family="sans-serif" font-size="16" font-weight="700" text-anchor="middle">
      2. Electrical Circuit
    </text>

    <!-- Battery (Voltage) -->
    <g transform="translate(70, 160)">
      <rect x="-24" y="-30" width="48" height="60" rx="4" fill="#312e81" stroke="#818cf8" stroke-width="2" />
      <text x="0" y="-5" fill="#ef4444" font-family="sans-serif" font-size="14" font-weight="800" text-anchor="middle">+</text>
      <text x="0" y="15" fill="#94a3b8" font-family="sans-serif" font-size="14" font-weight="800" text-anchor="middle">-</text>
      <text x="0" y="50" fill="#c7d2fe" font-family="sans-serif" font-size="12" font-weight="600" text-anchor="middle">Battery (V)</text>
    </g>

    <!-- Circuit Wire -->
    <path d="M 70 130 L 70 80 L 160 80 L 170 65 L 185 95 L 200 65 L 215 95 L 230 65 L 240 80 L 330 80 L 330 240 L 70 240 L 70 190"
          fill="none" stroke="#6366f1" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />

    <!-- Resistor Label -->
    <text x="205" y="45" fill="#fbbf24" font-family="sans-serif" font-size="13" font-weight="700" text-anchor="middle">Resistor (R)</text>

    <!-- Current Flow Arrow -->
    <text x="330" y="165" fill="#818cf8" font-family="sans-serif" font-size="12" font-weight="700" text-anchor="middle">
      Current (I)
    </text>

    <!-- Subtext Formula -->
    <rect x="20" y="260" width="350" height="45" rx="6" fill="#0f172a" />
    <text x="195" y="280" fill="#38bdf8" font-family="monospace" font-size="14" font-weight="700" text-anchor="middle">
      I = V / R  (Current = Voltage ÷ Resistance)
    </text>
    <text x="195" y="296" fill="#34d399" font-family="sans-serif" font-size="11" font-weight="600" text-anchor="middle">
      R in denominator: Doubling R halves I!
    </text>
  </g>

  <!-- Bottom Banner Summary -->
  <g transform="translate(450, 445)">
    <rect x="-350" y="-18" width="700" height="34" rx="8" fill="#0f172a" stroke="#334155" />
    <text x="0" y="4" fill="#f8fafc" font-family="sans-serif" font-size="13" font-weight="700" text-anchor="middle">
      CONCLUSION: Resistance opposes flow. Higher Resistance → LOWER Current.
    </text>
  </g>
</svg>"""

        return VisualAsset(
            spec_id=spec.spec_id,
            visual_type=VisualType.ANALOGY_WATER_CIRCUIT,
            format=RenderFormat.SVG,
            content=svg_content,
            mime_type="image/svg+xml",
            width=900,
            height=480,
            alt_text="Visual analogy showing how a pinched water pipe reduces water flow just as electrical resistance reduces electric current.",
        )

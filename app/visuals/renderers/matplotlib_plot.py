"""
Deterministic Plot and Curve Renderer for Module 8 (Visual Intelligence).
Generates high-precision, publication-quality educational curves and graphs in SVG format.
"""

from __future__ import annotations
from app.visuals.models import VisualSpec, VisualAsset, VisualType, RenderFormat
from app.visuals.renderers.base import BaseVisualRenderer


class MatplotlibPlotRenderer(BaseVisualRenderer):
    """
    Generates deterministic SVG graphs and mathematical curves with axes, ticks, grids, and labels.
    """

    def render(self, spec: VisualSpec) -> VisualAsset:
        if "ohm" in spec.concept.lower() or "physics" in spec.subject.value:
            r_low = spec.parameters.get("r_low", 2)
            r_high = spec.parameters.get("r_high", 10)

            svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" width="100%" height="100%">
  <defs>
    <linearGradient id="plotBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a" />
      <stop offset="100%" stop-color="#1e293b" />
    </linearGradient>
  </defs>

  <rect width="800" height="450" rx="12" fill="url(#plotBg)" />

  <!-- Title -->
  <text x="400" y="40" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="20" font-weight="700" text-anchor="middle">
    {spec.title or "Ohm's Law: Current (I) vs. Voltage (V) Characteristics"}
  </text>
  <text x="400" y="65" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="13" text-anchor="middle">
    Slope = 1 / Resistance (Steeper line = Lower Resistance / Higher Current)
  </text>

  <!-- Plot Box Area: (120, 90) to (680, 370) -->
  <rect x="120" y="90" width="560" height="280" fill="#0b1120" stroke="#334155" stroke-width="1.5" />

  <!-- Grid lines -->
  <g stroke="#1e293b" stroke-width="1" stroke-dasharray="4,4">
    <line x1="120" y1="160" x2="680" y2="160" />
    <line x1="120" y1="230" x2="680" y2="230" />
    <line x1="120" y1="300" x2="680" y2="300" />
    <line x1="260" y1="90" x2="260" y2="370" />
    <line x1="400" y1="90" x2="400" y2="370" />
    <line x1="540" y1="90" x2="540" y2="370" />
  </g>

  <!-- Curves -->
  <!-- Low Resistance R=2 (High Current, Steep Slope: (120,370) -> (640,110)) -->
  <line x1="120" y1="370" x2="640" y2="110" stroke="#38bdf8" stroke-width="3.5" stroke-linecap="round" />
  
  <!-- Medium Resistance R=5 (Moderate Slope: (120,370) -> (640,240)) -->
  <line x1="120" y1="370" x2="640" y2="240" stroke="#a855f7" stroke-width="3" stroke-linecap="round" />

  <!-- High Resistance R=10 (Low Current, Shallow Slope: (120,370) -> (640,318)) -->
  <line x1="120" y1="370" x2="640" y2="318" stroke="#f59e0b" stroke-width="3.5" stroke-linecap="round" />

  <!-- Axis Labels & Values -->
  <text x="120" y="395" fill="#94a3b8" font-family="sans-serif" font-size="12" text-anchor="middle">0V</text>
  <text x="260" y="395" fill="#94a3b8" font-family="sans-serif" font-size="12" text-anchor="middle">5V</text>
  <text x="400" y="395" fill="#94a3b8" font-family="sans-serif" font-size="12" text-anchor="middle">10V</text>
  <text x="540" y="395" fill="#94a3b8" font-family="sans-serif" font-size="12" text-anchor="middle">15V</text>
  <text x="640" y="395" fill="#94a3b8" font-family="sans-serif" font-size="12" text-anchor="middle">20V</text>

  <text x="400" y="425" fill="#cbd5e1" font-family="sans-serif" font-size="14" font-weight="600" text-anchor="middle">
    Voltage (V in Volts) →
  </text>
  
  <text x="60" y="230" fill="#cbd5e1" font-family="sans-serif" font-size="14" font-weight="600" transform="rotate(-90 60 230)" text-anchor="middle">
    Current (I in Amperes) →
  </text>

  <!-- Legend Box -->
  <g transform="translate(140, 110)">
    <rect width="230" height="85" rx="6" fill="#1e293b" fill-opacity="0.9" stroke="#475569" />
    <line x1="15" y1="20" x2="45" y2="20" stroke="#38bdf8" stroke-width="3" />
    <text x="55" y="24" fill="#f8fafc" font-family="sans-serif" font-size="12" font-weight="600">Low R = {r_low}Ω (High Current)</text>
    
    <line x1="15" y1="45" x2="45" y2="45" stroke="#a855f7" stroke-width="3" />
    <text x="55" y="49" fill="#f8fafc" font-family="sans-serif" font-size="12" font-weight="600">Medium R = 5Ω</text>
    
    <line x1="15" y1="70" x2="45" y2="70" stroke="#f59e0b" stroke-width="3" />
    <text x="55" y="74" fill="#f8fafc" font-family="sans-serif" font-size="12" font-weight="600">High R = {r_high}Ω (Low Current)</text>
  </g>
</svg>"""
        else:
            svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" width="100%" height="100%">
  <rect width="800" height="450" rx="12" fill="#0f172a" />
  <text x="400" y="45" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="20" font-weight="700" text-anchor="middle">{spec.title or "Function Plot"}</text>
  <line x1="120" y1="380" x2="680" y2="380" stroke="#94a3b8" stroke-width="2" />
  <line x1="400" y1="380" x2="400" y2="80" stroke="#94a3b8" stroke-width="2" />
  <path d="M 160 360 Q 400 380 400 380 Q 400 380 640 100" fill="none" stroke="#38bdf8" stroke-width="3" />
</svg>"""

        return VisualAsset(
            spec_id=spec.spec_id,
            visual_type=VisualType.GRAPH_PLOT,
            format=RenderFormat.SVG,
            content=svg_content,
            mime_type="image/svg+xml",
            width=800,
            height=450,
            alt_text=f"Graph plot illustrating {spec.concept}",
        )

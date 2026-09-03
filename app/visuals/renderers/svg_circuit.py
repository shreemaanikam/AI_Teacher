"""
Deterministic SVG Circuit Diagram Renderer for Module 8 (Visual Intelligence).
"""

from __future__ import annotations
from app.visuals.models import VisualSpec, VisualAsset, VisualType, RenderFormat
from app.visuals.renderers.base import BaseVisualRenderer


class SvgCircuitRenderer(BaseVisualRenderer):
    """Generates crisp, responsive SVG circuit diagrams for physics and electronics topics."""

    def render(self, spec: VisualSpec) -> VisualAsset:
        voltage = spec.parameters.get("voltage", 12)
        resistance = spec.parameters.get("resistance", 4)
        current = spec.parameters.get("current", round(voltage / resistance, 2) if resistance else 0)

        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a" />
      <stop offset="100%" stop-color="#1e293b" />
    </linearGradient>
    <linearGradient id="wireGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38bdf8" />
      <stop offset="100%" stop-color="#818cf8" />
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#38bdf8" />
    </marker>
  </defs>

  <!-- Background -->
  <rect width="800" height="450" rx="12" fill="url(#bgGrad)" />

  <!-- Header / Title -->
  <text x="400" y="45" fill="#f8fafc" font-family="system-ui, -apple-system, sans-serif" font-size="22" font-weight="700" text-anchor="middle">
    {spec.title or "DC Circuit Diagram — Ohm's Law (V = I × R)"}
  </text>
  <text x="400" y="75" fill="#94a3b8" font-family="system-ui, -apple-system, sans-serif" font-size="14" text-anchor="middle">
    {spec.purpose}
  </text>

  <!-- Main Circuit Loop -->
  <!-- Top Wire -->
  <line x1="180" y1="140" x2="350" y2="140" stroke="url(#wireGrad)" stroke-width="4" stroke-linecap="round" />
  <line x1="450" y1="140" x2="620" y2="140" stroke="url(#wireGrad)" stroke-width="4" stroke-linecap="round" />
  
  <!-- Right Wire & Ammeter -->
  <line x1="620" y1="140" x2="620" y2="240" stroke="url(#wireGrad)" stroke-width="4" />
  <line x1="620" y1="300" x2="620" y2="360" stroke="url(#wireGrad)" stroke-width="4" />
  
  <!-- Bottom Wire -->
  <line x1="620" y1="360" x2="180" y2="360" stroke="url(#wireGrad)" stroke-width="4" stroke-linecap="round" />
  
  <!-- Left Wire -->
  <line x1="180" y1="360" x2="180" y2="270" stroke="url(#wireGrad)" stroke-width="4" />
  <line x1="180" y1="210" x2="180" y2="140" stroke="url(#wireGrad)" stroke-width="4" />

  <!-- Current Flow Indicators (Arrows) -->
  <line x1="240" y1="140" x2="280" y2="140" stroke="#38bdf8" stroke-width="3" marker-end="url(#arrow)" />
  <text x="260" y="125" fill="#38bdf8" font-family="sans-serif" font-size="13" font-weight="600" text-anchor="middle">Current I ({current}A)</text>

  <!-- Component 1: Resistor (Top Center) -->
  <g transform="translate(350, 140)">
    <!-- Resistor Zigzag Symbol -->
    <path d="M 0 0 L 10 -15 L 25 15 L 40 -15 L 55 15 L 70 -15 L 85 15 L 95 -15 L 100 0" fill="none" stroke="#f59e0b" stroke-width="4" stroke-linejoin="round" filter="url(#glow)" />
    <rect x="0" y="-35" width="100" height="70" fill="transparent" />
    <text x="50" y="-22" fill="#fbbf24" font-family="sans-serif" font-size="16" font-weight="700" text-anchor="middle">Resistor (R)</text>
    <text x="50" y="38" fill="#fef08a" font-family="sans-serif" font-size="15" font-weight="600" text-anchor="middle">{resistance} Ω</text>
  </g>

  <!-- Component 2: DC Battery / Voltage Source (Left Center) -->
  <g transform="translate(180, 240)">
    <!-- Long plate (Positive) -->
    <line x1="-25" y1="-15" x2="25" y2="-15" stroke="#ef4444" stroke-width="5" stroke-linecap="round" />
    <text x="-35" y="-10" fill="#f87171" font-family="sans-serif" font-size="16" font-weight="700">+</text>
    <!-- Short plate (Negative) -->
    <line x1="-15" y1="15" x2="15" y2="15" stroke="#94a3b8" stroke-width="7" stroke-linecap="round" />
    <text x="-35" y="20" fill="#cbd5e1" font-family="sans-serif" font-size="18" font-weight="700">-</text>
    <text x="-95" y="5" fill="#f87171" font-family="sans-serif" font-size="15" font-weight="700" text-anchor="middle">Battery (V)</text>
    <text x="-95" y="25" fill="#fca5a5" font-family="sans-serif" font-size="14" font-weight="600" text-anchor="middle">{voltage} V</text>
  </g>

  <!-- Component 3: Ammeter (Right Center) -->
  <g transform="translate(620, 270)">
    <circle cx="0" cy="0" r="28" fill="#1e1e38" stroke="#38bdf8" stroke-width="3" filter="url(#glow)" />
    <text x="0" y="8" fill="#38bdf8" font-family="sans-serif" font-size="20" font-weight="800" text-anchor="middle">A</text>
    <text x="75" y="0" fill="#7dd3fc" font-family="sans-serif" font-size="14" font-weight="600">Ammeter</text>
    <text x="75" y="20" fill="#bae6fd" font-family="sans-serif" font-size="15" font-weight="700">{current} A</text>
  </g>

  <!-- Formula Panel (Bottom Center) -->
  <g transform="translate(400, 390)">
    <rect x="-160" y="-25" width="320" height="40" rx="8" fill="#334155" stroke="#475569" stroke-width="1.5" />
    <text x="0" y="2" fill="#38bdf8" font-family="monospace" font-size="16" font-weight="700" text-anchor="middle">
      I = V / R = {voltage}V / {resistance}Ω = {current}A
    </text>
  </g>
</svg>"""

        return VisualAsset(
            spec_id=spec.spec_id,
            visual_type=VisualType.CIRCUIT_DIAGRAM,
            format=RenderFormat.SVG,
            content=svg_content,
            mime_type="image/svg+xml",
            width=800,
            height=450,
            alt_text=f"Circuit diagram for Ohm's Law: Voltage={voltage}V, Resistance={resistance}Ω, Current={current}A",
        )

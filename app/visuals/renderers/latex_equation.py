"""
Deterministic LaTeX / Math Equation Renderer for Module 8 (Visual Intelligence).
"""

from __future__ import annotations
from app.visuals.models import VisualSpec, VisualAsset, VisualType, RenderFormat
from app.visuals.renderers.base import BaseVisualRenderer


class LatexEquationRenderer(BaseVisualRenderer):
    """Renders formatted LaTeX formulas and step-by-step mathematical deductions."""

    def render(self, spec: VisualSpec) -> VisualAsset:
        equations_html = ""
        for eq in spec.equations:
            equations_html += f'<div class="latex-line" style="font-size: 24px; margin: 12px 0; color: #38bdf8;">\\[ {eq} \\]</div>\n'

        steps_html = ""
        for step in spec.steps:
            steps_html += f'<li style="color: #cbd5e1; margin: 8px 0; font-size: 16px;">{step}</li>\n'

        html_container = f"""<div class="math-card" style="background: #0f172a; border: 1px solid #334155; border-radius: 12px; padding: 24px; font-family: system-ui, sans-serif;">
  <h3 style="color: #f8fafc; margin-top: 0; font-size: 20px; font-weight: 700;">{spec.title or "Mathematical Formulation"}</h3>
  <p style="color: #94a3b8; font-size: 14px;">{spec.purpose}</p>
  <div class="equations-block" style="background: #1e293b; padding: 18px; border-radius: 8px; text-align: center; margin: 16px 0;">
    {equations_html}
  </div>
  {f'<ol style="padding-left: 20px;">{steps_html}</ol>' if steps_html else ''}
</div>"""

        return VisualAsset(
            spec_id=spec.spec_id,
            visual_type=VisualType.LATEX_EQUATION,
            format=RenderFormat.HTML,
            content=html_container,
            mime_type="text/html",
            width=800,
            height=450,
            alt_text=f"LaTeX mathematical equations for {spec.concept}",
        )

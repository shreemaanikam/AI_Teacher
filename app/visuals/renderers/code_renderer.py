"""
Deterministic Code Block Renderer for Module 8 (Visual Intelligence).
"""

from __future__ import annotations
import html
from app.visuals.models import VisualSpec, VisualAsset, VisualType, RenderFormat
from app.visuals.renderers.base import BaseVisualRenderer


class CodeRenderer(BaseVisualRenderer):
    """Renders formatted and syntax-styled code blocks for programming lessons."""

    def render(self, spec: VisualSpec) -> VisualAsset:
        language = spec.parameters.get("language", "python")
        raw_code = spec.parameters.get("code", f"# Implementation for {spec.concept}\ndef solve():\n    pass")
        escaped_code = html.escape(raw_code)

        html_content = f"""<div class="code-terminal" style="background: #0f172a; border: 1px solid #334155; border-radius: 10px; font-family: monospace; overflow: hidden;">
  <div style="background: #1e293b; padding: 8px 14px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #334155;">
    <span style="color: #94a3b8; font-size: 13px; font-weight: 600;">{spec.title or language.upper()}</span>
    <span style="background: #38bdf8; color: #0f172a; font-size: 11px; padding: 2px 6px; border-radius: 4px; font-weight: 700;">{language}</span>
  </div>
  <pre style="padding: 16px; margin: 0; color: #f8fafc; font-size: 14px; line-height: 1.6; overflow-x: auto;"><code>{escaped_code}</code></pre>
</div>"""

        return VisualAsset(
            spec_id=spec.spec_id,
            visual_type=VisualType.CODE_BLOCK,
            format=RenderFormat.HTML,
            content=html_content,
            mime_type="text/html",
            width=800,
            height=450,
            alt_text=f"Code snippet for {spec.concept}",
        )

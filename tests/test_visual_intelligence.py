"""
Unit & Integration Tests for Module 8: Subject-Aware Visual Intelligence.
"""

from app.visuals.models import VisualType, SubjectCategory, RenderFormat
from app.visuals.strategies import VisualStrategyPlanner
from app.visuals.engine import VisualIntelligenceEngine
from app.assessment.models import MisconceptionRecord
from app.harness.session import TeachingStrategy


def test_subject_classification():
    planner = VisualStrategyPlanner()
    assert planner.classify_subject("Physics", "Ohm's Law") == SubjectCategory.PHYSICS
    assert planner.classify_subject("Math", "Algebraic equation") == SubjectCategory.MATHEMATICS
    assert planner.classify_subject("Computer Science", "Python loop") == SubjectCategory.PROGRAMMING


def test_visual_planning_normal_physics():
    engine = VisualIntelligenceEngine()
    spec = engine.plan_visual("physics", "Ohm's Law", TeachingStrategy.DIRECT_EXPLANATION)
    assert spec.visual_type == VisualType.CIRCUIT_DIAGRAM
    assert spec.renderer == "svg_circuit"

    asset = engine.render_visual(spec)
    assert asset.format == RenderFormat.SVG
    assert "<svg" in asset.content
    assert "Circuit Diagram" in asset.content or "Ohm" in asset.content


def test_visual_planning_misconception_water_analogy():
    engine = VisualIntelligenceEngine()
    misconception = MisconceptionRecord(
        concept="Ohm's Law",
        misconception_type="inverse_relationship_confusion",
        belief="higher resistance increases current",
        evidence_from_answer="current doubles",
    )

    # When misconception is passed, strategy planner should select the water-circuit analogy
    spec = engine.plan_visual("physics", "Ohm's Law", TeachingStrategy.SIMPLE_ANALOGY, misconception=misconception)
    assert spec.visual_type == VisualType.ANALOGY_WATER_CIRCUIT
    assert spec.renderer == "svg_analogy"

    asset = engine.render_visual(spec)
    assert asset.format == RenderFormat.SVG
    assert "Water Pipe System" in asset.content
    assert "Pinch" in asset.content or "Valve" in asset.content
    assert "Electrical Circuit" in asset.content


def test_matplotlib_plot_rendering():
    engine = VisualIntelligenceEngine()
    spec = engine.plan_visual("physics", "Ohm's Law", TeachingStrategy.VISUAL_EXPLANATION)
    assert spec.visual_type == VisualType.GRAPH_PLOT

    asset = engine.render_visual(spec)
    assert asset.format == RenderFormat.SVG
    assert "<svg" in asset.content


def test_latex_and_code_renderers():
    engine = VisualIntelligenceEngine()

    # Math
    math_spec = engine.plan_visual("mathematics", "algebra_equations")
    math_asset = engine.render_visual(math_spec)
    assert "latex" in math_asset.content.lower() or "math" in math_asset.content.lower()

    # Programming
    code_spec = engine.plan_visual("programming", "python_basics")
    code_asset = engine.render_visual(code_spec)
    assert "code" in code_asset.content.lower()

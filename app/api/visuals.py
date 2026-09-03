"""
Flask API Blueprint for Module 8 (Subject-Aware Visual Intelligence).
"""

from __future__ import annotations
from flask import Blueprint, jsonify, request, Response, current_app
from app.visuals.engine import VisualIntelligenceEngine
from app.visuals.models import VisualSpec, RenderFormat
from app.harness.session import TeachingStrategy

visuals_blueprint = Blueprint("visuals", __name__)


def get_visual_engine() -> VisualIntelligenceEngine:
    if "VISUAL_ENGINE" not in current_app.config:
        current_app.config["VISUAL_ENGINE"] = VisualIntelligenceEngine()
    return current_app.config["VISUAL_ENGINE"]


@visuals_blueprint.route("/visuals/plan", methods=["POST"])
def plan_visual():
    """Generates a structured VisualSpec without rendering."""
    engine = get_visual_engine()
    data = request.get_json(silent=True) or {}
    subject = data.get("subject", "physics")
    concept = data.get("concept", "ohms_law")
    strat_str = data.get("strategy", "DIRECT_EXPLANATION")
    try:
        strategy = TeachingStrategy(strat_str)
    except ValueError:
        strategy = TeachingStrategy.DIRECT_EXPLANATION

    spec = engine.plan_visual(subject=subject, concept=concept, teaching_strategy=strategy)
    return jsonify({
        "status": "success",
        "spec": spec.model_dump(mode="json"),
    }), 200


@visuals_blueprint.route("/visuals/render", methods=["POST"])
def render_visual():
    """Renders a VisualSpec or generates directly from concept parameters."""
    engine = get_visual_engine()
    data = request.get_json(silent=True) or {}

    if "spec" in data:
        spec = VisualSpec.model_validate(data["spec"])
        asset = engine.render_visual(spec)
    else:
        subject = data.get("subject", "physics")
        concept = data.get("concept", "ohms_law")
        strat_str = data.get("strategy", "DIRECT_EXPLANATION")
        try:
            strategy = TeachingStrategy(strat_str)
        except ValueError:
            strategy = TeachingStrategy.DIRECT_EXPLANATION
        asset = engine.generate_visual(subject=subject, concept=concept, teaching_strategy=strategy)

    return jsonify({
        "status": "success",
        "asset": asset.model_dump(mode="json"),
    }), 200


@visuals_blueprint.route("/visuals/<asset_id>", methods=["GET"])
def get_visual_asset(asset_id: str):
    """Retrieves the visual asset by ID or serves raw SVG/HTML directly."""
    engine = get_visual_engine()
    asset = engine.get_asset(asset_id)
    if not asset:
        return jsonify({"error": f"Visual asset '{asset_id}' not found."}), 404

    # Support raw rendering if Accept header or query param specifies
    if request.args.get("raw") == "true" and asset.format == RenderFormat.SVG:
        return Response(asset.content, mimetype="image/svg+xml")

    return jsonify({
        "status": "success",
        "asset": asset.model_dump(mode="json"),
    }), 200

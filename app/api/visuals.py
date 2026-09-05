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
    """Generates a structured TeachingVisualPlan and VisualSpec grounded in notes."""
    engine = get_visual_engine()
    data = request.get_json(silent=True) or {}
    subject = data.get("subject", "physics")
    concept = data.get("concept", "ohms_law")
    strat_str = data.get("strategy", "DIRECT_EXPLANATION")
    document_id = data.get("document_id")
    source_chunk_ids = data.get("source_chunk_ids") or []
    source_reference = data.get("source_reference")
    duration = int(data.get("duration_seconds", 15))
    misc_raw = data.get("misconception")
    misconception = None
    if misc_raw:
        from app.assessment.models import MisconceptionRecord
        if isinstance(misc_raw, dict):
            misconception = MisconceptionRecord.model_validate(misc_raw)
        elif isinstance(misc_raw, MisconceptionRecord):
            misconception = misc_raw

    try:
        strategy = TeachingStrategy(strat_str)
    except ValueError:
        strategy = TeachingStrategy.DIRECT_EXPLANATION

    plan = engine.plan_visual_teaching(
        concept=concept,
        subject_hint=subject,
        teaching_strategy=strategy,
        duration_seconds=duration,
        misconception=misconception,
        document_id=document_id,
        source_chunk_ids=source_chunk_ids,
        source_reference=source_reference,
    )

    spec = engine.plan_visual(
        subject=subject,
        concept=concept,
        teaching_strategy=strategy,
        duration_seconds=duration,
        misconception=misconception,
        document_id=document_id,
        chunk_id=source_chunk_ids[0] if source_chunk_ids else None,
        source_reference=source_reference,
    )

    return jsonify({
        "status": "success",
        "plan": plan.model_dump(mode="json"),
        "spec": spec.model_dump(mode="json"),
    }), 200


@visuals_blueprint.route("/visuals/render", methods=["POST"])
def render_visual():
    """Renders a VisualSpec or TeachingVisualPlan directly into an interactive asset."""
    engine = get_visual_engine()
    data = request.get_json(silent=True) or {}

    if "plan" in data:
        from app.visuals.models import TeachingVisualPlan
        plan = TeachingVisualPlan.model_validate(data["plan"])
        step_idx = data.get("step_index")
        asset = engine.render_teaching_visual(plan, step_index=step_idx)
    elif "spec" in data:
        spec = VisualSpec.model_validate(data["spec"])
        asset = engine.render_visual(spec)
    else:
        subject = data.get("subject", "physics")
        concept = data.get("concept", "ohms_law")
        strat_str = data.get("strategy", "DIRECT_EXPLANATION")
        document_id = data.get("document_id")
        chunk_id = data.get("chunk_id")
        source_reference = data.get("source_reference")
        misc_raw = data.get("misconception")
        misconception = None
        if misc_raw:
            from app.assessment.models import MisconceptionRecord
            if isinstance(misc_raw, dict):
                misconception = MisconceptionRecord.model_validate(misc_raw)
            elif isinstance(misc_raw, MisconceptionRecord):
                misconception = misc_raw

        try:
            strategy = TeachingStrategy(strat_str)
        except ValueError:
            strategy = TeachingStrategy.DIRECT_EXPLANATION

        plan = engine.plan_visual_teaching(
            concept=concept,
            subject_hint=subject,
            teaching_strategy=strategy,
            misconception=misconception,
            document_id=document_id,
            source_chunk_ids=[chunk_id] if chunk_id else [],
            source_reference=source_reference,
        )
        asset = engine.render_teaching_visual(plan)

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


@visuals_blueprint.route("/visuals/<asset_id>/step", methods=["POST"])
def step_visual_asset(asset_id: str):
    """Advances, steps backward, or scrubs to a specific step index on the board."""
    engine = get_visual_engine()
    asset = engine.get_asset(asset_id)
    if not asset:
        return jsonify({"error": f"Visual asset '{asset_id}' not found."}), 404

    data = request.get_json(silent=True) or {}
    action = data.get("action")
    target_step = data.get("step") if data.get("step") is not None else data.get("step_index")

    if action == "next":
        target_step = min(asset.steps_count - 1, asset.active_step + 1)
    elif action == "prev" or action == "previous":
        target_step = max(0, asset.active_step - 1)
    elif target_step is None:
        target_step = 0
    else:
        target_step = max(0, min(asset.steps_count - 1, int(target_step)))

    updated = engine.step_visual(asset_id, target_step=target_step)
    if not updated:
        return jsonify({"error": "Failed to update visual step."}), 500

    return jsonify({
        "status": "success",
        "active_step": updated.active_step,
        "total_steps": updated.steps_count,
        "asset": updated.model_dump(mode="json"),
    }), 200


@visuals_blueprint.route("/visuals/<asset_id>/replay", methods=["POST"])
def replay_visual_asset(asset_id: str):
    """Rewinds the visual board presentation back to Step 1."""
    engine = get_visual_engine()
    updated = engine.replay_visual(asset_id)
    if not updated:
        return jsonify({"error": f"Visual asset '{asset_id}' not found."}), 404

    return jsonify({
        "status": "success",
        "active_step": 0,
        "total_steps": updated.steps_count,
        "asset": updated.model_dump(mode="json"),
    }), 200


@visuals_blueprint.route("/visuals/<asset_id>/source-trace", methods=["GET"])
def get_visual_source_trace(asset_id: str):
    """Returns the pedagogical source grounding citation and RAG chunk mapping."""
    engine = get_visual_engine()
    trace = engine.get_source_trace(asset_id)
    if not trace:
        return jsonify({"error": f"Visual asset '{asset_id}' not found."}), 404

    return jsonify({
        "status": "success",
        "source_trace": trace,
    }), 200

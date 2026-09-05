"""
Comprehensive Test Suite for Phase 7: Dynamic Visual Teaching Engine.
Validates multi-subject progressive whiteboard/chalkboard generation, step scrubbing,
narration synchronization, misconception adaptation, grounding source trace, and REST APIs.
"""

import pytest
from app import create_app
from app.visuals.models import (
    VisualType,
    VisualBoardTheme,
    SubjectCategory,
    RenderFormat,
    TeachingVisualPlan,
    VisualTeachingStep,
    VisualAsset,
)
from app.visuals.strategies import VisualStrategyPlanner
from app.visuals.board_engine import DynamicWhiteboardEngine
from app.visuals.engine import VisualIntelligenceEngine
from app.assessment.models import MisconceptionRecord
from app.harness.session import TeachingStrategy


@pytest.fixture
def app():
    flask_app = create_app("testing")
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def visual_engine():
    return VisualIntelligenceEngine()


# =====================================================================
# 1. Subject Routing & Dynamic Board Planning Tests
# =====================================================================

def test_subject_routing_mathematics(visual_engine):
    """Verifies Math topics route to EQUATION_DERIVATION with step formulas."""
    plan = visual_engine.plan_visual_teaching(
        concept="Quadratic Equation Derivation",
        subject_hint="mathematics",
        teaching_strategy=TeachingStrategy.STEP_BY_STEP,
        duration_seconds=16,
    )

    assert plan.subject == SubjectCategory.MATHEMATICS
    assert plan.visual_type == VisualType.EQUATION_DERIVATION
    assert len(plan.steps) >= 4
    assert len(plan.equations) >= 2
    assert any("x = " in eq or "ax^2" in eq for eq in plan.equations)
    # Contiguous step indices
    for idx, step in enumerate(plan.steps):
        assert step.step_index == idx


def test_subject_routing_cs_array_pointers(visual_engine):
    """Verifies CS search topics route to ARRAY_POINTER with bounds and mid."""
    plan = visual_engine.plan_visual_teaching(
        concept="Binary Search Invariant",
        subject_hint="computer_science",
        teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
        duration_seconds=12,
    )

    assert plan.subject in (SubjectCategory.COMPUTER_SCIENCE, SubjectCategory.PROGRAMMING)
    assert plan.visual_type == VisualType.ARRAY_POINTER
    assert len(plan.steps) == 4
    assert any("LOW" in s.title or "HIGH" in s.title for s in plan.steps)
    assert any("Midpoint" in s.title for s in plan.steps)


def test_subject_routing_cs_code_execution(visual_engine):
    """Verifies CS code implementation topics route to CODE_EXECUTION."""
    plan = visual_engine.plan_visual_teaching(
        concept="Recursive Fibonacci Code Execution",
        subject_hint="programming",
        teaching_strategy=TeachingStrategy.STEP_BY_STEP,
        duration_seconds=14,
    )

    assert plan.visual_type == VisualType.CODE_EXECUTION
    assert len(plan.steps) >= 3
    assert any("Stack Frame" in s.title or "Variable" in s.title or "Call" in s.title for s in plan.steps)


def test_subject_routing_engineering_physics_circuits(visual_engine):
    """Verifies Engineering circuits route to CIRCUIT_DIAGRAM with telemetry."""
    plan = visual_engine.plan_visual_teaching(
        concept="Ohm's Law DC Circuit",
        subject_hint="physics",
        teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
        duration_seconds=15,
    )

    assert plan.visual_type == VisualType.CIRCUIT_DIAGRAM
    assert len(plan.steps) == 4
    assert any("Schematic" in s.title for s in plan.steps)
    assert any("Current" in s.title for s in plan.steps)


def test_subject_routing_network_flow(visual_engine):
    """Verifies Network topics route to NETWORK_FLOW with packet exchanges."""
    plan = visual_engine.plan_visual_teaching(
        concept="TCP 3-Way Handshake and TLS Negotiation",
        subject_hint="computer_science",
        teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
        duration_seconds=16,
    )

    assert plan.visual_type == VisualType.NETWORK_FLOW
    assert len(plan.steps) >= 4
    assert any("TCP" in s.title for s in plan.steps)
    assert any("Handshake" in s.title or "DNS" in s.title for s in plan.steps)


# =====================================================================
# 2. Narration & Visual Cue Synchronization Tests
# =====================================================================

def test_narration_visual_cues_synchronization(visual_engine):
    """Verifies narration cues and visual animation cues are 1:1 aligned in time."""
    duration = 20
    plan = visual_engine.plan_visual_teaching(
        concept="Quadratic Formula",
        subject_hint="mathematics",
        duration_seconds=duration,
    )

    assert len(plan.narration_cues) == len(plan.steps)
    assert len(plan.animation_cues) == len(plan.steps)

    for i in range(len(plan.steps)):
        nc = plan.narration_cues[i]
        vc = plan.animation_cues[i]
        step = plan.steps[i]

        assert nc.cue_id == step.narration_cue_id
        assert nc.start_time == vc.start_time
        assert nc.end_time == vc.end_time
        assert nc.end_time > nc.start_time
        assert nc.end_time <= duration + 0.1
        assert len(nc.text) > 5


# =====================================================================
# 3. Dynamic Whiteboard Rendering & Step Scrubbing Tests
# =====================================================================

def test_whiteboard_svg_rendering_and_precompilation(visual_engine):
    """Verifies deterministic SVG generation and pre-compiled step state cache."""
    plan = visual_engine.plan_visual_teaching(
        concept="Binary Search Invariant",
        subject_hint="computer_science",
        duration_seconds=12,
    )

    asset = visual_engine.render_teaching_visual(plan, step_index=0)

    assert asset.format == RenderFormat.SVG
    assert asset.mime_type == "image/svg+xml"
    assert "<svg" in asset.content
    assert "</svg>" in asset.content
    assert 'viewBox="0 0 960 540"' in asset.content
    assert asset.steps_count == len(plan.steps)
    assert asset.active_step == 0

    # Verify all steps are pre-rendered in step_contents for zero-latency UI navigation
    assert len(asset.step_contents) == len(plan.steps)
    for s_idx in range(len(plan.steps)):
        assert s_idx in asset.step_contents
        assert "<svg" in asset.step_contents[s_idx]
        assert f"Step {s_idx + 1} of {len(plan.steps)}" in asset.step_contents[s_idx]


def test_visual_step_scrubbing_and_replay(visual_engine):
    """Verifies scrubbing to step 1, step 2, and replaying to step 0."""
    plan = visual_engine.plan_visual_teaching(
        concept="Ohm's Law DC Circuit",
        subject_hint="physics",
        duration_seconds=16,
    )

    asset = visual_engine.render_teaching_visual(plan, step_index=0)
    asset_id = asset.asset_id

    # Step to index 1
    stepped_1 = visual_engine.step_visual(asset_id, target_step=1)
    assert stepped_1 is not None
    assert stepped_1.active_step == 1
    assert "Step 2 of 4" in stepped_1.content

    # Step to index 3 (last step)
    stepped_3 = visual_engine.step_visual(asset_id, target_step=3)
    assert stepped_3 is not None
    assert stepped_3.active_step == 3
    assert "Step 4 of 4" in stepped_3.content

    # Replay rewinds back to step 0
    replayed = visual_engine.replay_visual(asset_id)
    assert replayed is not None
    assert replayed.active_step == 0
    assert "Step 1 of 4" in replayed.content


# =====================================================================
# 4. Misconception Invariant & Strategy Shift Tests
# =====================================================================

def test_misconception_adaptation_strategy_shift(visual_engine):
    """
    Verifies that diagnosing a misconception triggers an alternative pedagogical
    visual representation, ensuring visual_id != remediation_id and strategy shift.
    """
    # 1. Baseline teaching visual
    plan_normal = visual_engine.plan_visual_teaching(
        concept="Ohm's Law",
        subject_hint="physics",
        teaching_strategy=TeachingStrategy.DIRECT_EXPLANATION,
    )
    asset_normal = visual_engine.render_teaching_visual(plan_normal)
    assert plan_normal.visual_type == VisualType.CIRCUIT_DIAGRAM

    # 2. Remediation teaching visual with active misconception
    misc = MisconceptionRecord(
        concept="Ohm's Law",
        misconception_type="inverse_relationship_confusion",
        belief="Increasing resistance pushes electrons faster and increases current.",
        evidence_from_answer="Student answered current increases when resistor is increased.",
    )
    plan_remed = visual_engine.plan_visual_teaching(
        concept="Ohm's Law",
        subject_hint="physics",
        teaching_strategy=TeachingStrategy.SIMPLE_ANALOGY,
        misconception=misc,
    )
    asset_remed = visual_engine.render_teaching_visual(plan_remed)

    # Invariant assertions
    assert plan_remed.visual_type == VisualType.ANALOGY_WATER_CIRCUIT
    assert plan_normal.visual_type != plan_remed.visual_type
    assert asset_normal.asset_id != asset_remed.asset_id
    assert "Water Pipe" in asset_remed.content or "Pinch" in asset_remed.content or "Constriction" in asset_remed.content
    assert "Circuit Diagram" in asset_normal.content or "DC Circuit" in asset_normal.content


# =====================================================================
# 5. Grounding Source Trace & Attribution Tests
# =====================================================================

def test_grounding_source_trace_reporting(visual_engine):
    """Verifies that uploaded documents and chunks are permanently cited on the visual."""
    doc_id = "doc_ncert_physics_ch3"
    chunk_id = "chunk_current_electricity_14"
    ref = {
        "title": "NCERT Class 12 Physics - Current Electricity",
        "page_number": 98,
        "section": "Section 3.4: Ohm's Law and Drift Velocity",
        "excerpt": "Electric current I flowing through a conductor is directly proportional to potential difference V...",
    }

    plan = visual_engine.plan_visual_teaching(
        concept="Ohm's Law",
        subject_hint="physics",
        document_id=doc_id,
        source_chunk_ids=[chunk_id],
        source_reference=ref,
        evidence_snippets=[ref["excerpt"]],
    )

    asset = visual_engine.render_teaching_visual(plan)
    trace = visual_engine.get_source_trace(asset.asset_id)

    assert trace is not None
    assert trace["is_grounded_in_source"] is True
    assert trace["document_id"] == doc_id
    assert trace["chunk_id"] == chunk_id
    assert trace["source_reference"]["title"] == ref["title"]
    assert trace["source_reference"]["page_number"] == 98
    # SVG content includes the grounded reference badge
    assert doc_id in asset.content or "NCERT" in asset.content or "Grounded" in asset.content


# =====================================================================
# 6. REST API Endpoints Verification
# =====================================================================

def test_api_visual_plan_endpoint(client):
    """Tests POST /api/v1/visuals/plan returns structured plan and spec."""
    res = client.post(
        "/api/v1/visuals/plan",
        json={
            "subject": "mathematics",
            "concept": "Quadratic Roots",
            "strategy": "STEP_BY_STEP",
            "duration_seconds": 15,
            "document_id": "doc_math_01",
            "source_chunk_ids": ["chk_alg_05"],
        },
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "plan" in data
    assert data["plan"]["visual_type"] == VisualType.EQUATION_DERIVATION.value
    assert len(data["plan"]["steps"]) >= 4


def test_api_visual_render_endpoint(client):
    """Tests POST /api/v1/visuals/render produces interactive SVG asset."""
    res = client.post(
        "/api/v1/visuals/render",
        json={
            "subject": "computer_science",
            "concept": "Binary Search Invariant",
            "strategy": "DIRECT_EXPLANATION",
        },
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    asset = data["asset"]
    assert asset["format"] == "svg"
    assert "<svg" in asset["content"]
    assert asset["steps_count"] >= 3


def test_api_visual_step_and_replay_endpoints(client):
    """Tests POST /api/v1/visuals/<id>/step and /replay endpoints."""
    render_res = client.post(
        "/api/v1/visuals/render",
        json={
            "subject": "physics",
            "concept": "Ohm's Law",
        },
    )
    asset_id = render_res.get_json()["asset"]["asset_id"]

    # 1. Step Next
    step_res = client.post(f"/api/v1/visuals/{asset_id}/step", json={"action": "next"})
    assert step_res.status_code == 200
    step_data = step_res.get_json()
    assert step_data["active_step"] == 1

    # 2. Step to specific index
    step_to_res = client.post(f"/api/v1/visuals/{asset_id}/step", json={"step_index": 2})
    assert step_to_res.status_code == 200
    assert step_to_res.get_json()["active_step"] == 2

    # 3. Replay back to 0
    replay_res = client.post(f"/api/v1/visuals/{asset_id}/replay", json={})
    assert replay_res.status_code == 200
    assert replay_res.get_json()["active_step"] == 0


def test_api_visual_source_trace_endpoint(client):
    """Tests GET /api/v1/visuals/<id>/source-trace endpoint."""
    render_res = client.post(
        "/api/v1/visuals/render",
        json={
            "subject": "physics",
            "concept": "Ohm's Law",
            "document_id": "doc_physics_ch3",
            "chunk_id": "chunk_v_ir_01",
        },
    )
    asset_id = render_res.get_json()["asset"]["asset_id"]

    trace_res = client.get(f"/api/v1/visuals/{asset_id}/source-trace")
    assert trace_res.status_code == 200
    trace_data = trace_res.get_json()
    assert trace_data["status"] == "success"
    assert trace_data["source_trace"]["asset_id"] == asset_id
    assert trace_data["source_trace"]["document_id"] == "doc_physics_ch3"

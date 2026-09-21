#!/usr/bin/env python3
"""
Kojiki API Server — FastAPI wrapper for the Orchestrator and core engines.
Exposes the local Python backend to the Next.js UI.
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import asdict

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from engine.orchestrator.orchestrator import Orchestrator, DepartmentChoice, OrchestrationResult
from engine.mycelium.okr_engine import OKREngine, OKRLevel, KRType
from engine.mycelium.propagate import SignalPropagator
from engine.mycelium.registry import NodeRegistry
from engine.mycelium.conversation_layer import MyceliumConversationLayer
from engine.sentinel import SentinelEngine, KeyManager
from engine.kojiki_core import load_specialist
from engine.kojiki_core.runner import PipelineRunner
from engine.kojiki_core.utils import create_dispatch, is_test_mode


class Settings(BaseSettings):
    data_dir: str = str(Path.home() / ".kojiki" / "data")
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    kojiki_llm_api_key: str = ""
    kojiki_llm_base_url: str = "https://api.openai.com/v1"
    kojiki_llm_model: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
app = FastAPI(
    title="Kojiki Decision System API",
    description="Local-first decision orchestration API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator: Optional[Orchestrator] = None


def get_orchestrator() -> Orchestrator:
    global orchestrator
    if orchestrator is None:
        orchestrator = Orchestrator(data_dir=settings.data_dir)
    return orchestrator


# Request/Response Models
class OrchestrateRequest(BaseModel):
    goal: str
    context: Optional[Dict[str, Any]] = None
    require_approval: bool = True


class OrchestrateResponse(BaseModel):
    orchestration_id: str
    raw_goal: str
    orientation_findings: Dict[str, Any]
    problem_framing: Dict[str, Any]
    department_choices: List[Dict[str, Any]]
    okr_decomposition: Dict[str, Any]
    execution_results: Dict[str, Any]
    timestamp: str
    status: str


class DepartmentChoiceResponse(BaseModel):
    department: str
    specialist_name: str
    reason: str
    okr_alignment: str
    confidence: float
    dependencies: List[str]


class OKRRequest(BaseModel):
    name: str
    description: str
    level: str
    owner: str
    parent_id: Optional[str] = None


class OKRResponse(BaseModel):
    id: str
    name: str
    description: str
    level: str
    owner: str
    parent_id: Optional[str]
    key_results: List[Dict[str, Any]]
    created_at: str


class KRRequest(BaseModel):
    name: str
    type: str
    target: float
    unit: str
    weight: float = 1.0


class SignalRequest(BaseModel):
    signal_id: str
    origin_kr: str
    target_node: str
    signal_type: str
    diagnosed_cause: str
    category: str
    payload: Dict[str, Any]


class ConsultationRequest(BaseModel):
    batch_departments: List[str]
    evidence_outputs: Dict[str, Any]
    problem_context: Dict[str, Any]


# Health check
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "kojiki-api",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


# Orchestration endpoints
@app.post("/api/orchestrate", response_model=OrchestrateResponse)
async def orchestrate(request: OrchestrateRequest):
    """Run full orchestration pipeline."""
    try:
        orch = get_orchestrator()
        result = await orch.orchestrate(
            raw_goal=request.goal,
            context=request.context,
            require_approval=request.require_approval
        )
        
        return OrchestrateResponse(
            orchestration_id=result.orchestration_id,
            raw_goal=result.raw_goal,
            orientation_findings=result.orientation_findings,
            problem_framing=result.problem_framing,
            department_choices=[asdict(c) for c in result.department_choices],
            okr_decomposition=result.okr_decomposition,
            execution_results=result.execution_results,
            timestamp=result.timestamp,
            status="completed"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/orchestrations")
async def list_orchestrations():
    """List all saved orchestrations."""
    data_dir = Path(settings.data_dir)
    orchestrations = []
    for file in data_dir.glob("orchestration_*.json"):
        try:
            data = json.loads(file.read_text())
            orchestrations.append({
                "orchestration_id": data.get("orchestration_id"),
                "raw_goal": data.get("raw_goal"),
                "timestamp": data.get("timestamp"),
                "departments": [c.get("specialist_name") for c in data.get("department_choices", [])]
            })
        except Exception:
            pass
    return {"orchestrations": sorted(orchestrations, key=lambda x: x["timestamp"], reverse=True)}


@app.get("/api/orchestrations/{orchestration_id}")
async def get_orchestration(orchestration_id: str):
    """Get a specific orchestration by ID."""
    data_dir = Path(settings.data_dir)
    file = data_dir / f"orchestration_{orchestration_id}.json"
    if not file.exists():
        raise HTTPException(status_code=404, detail="Orchestration not found")
    return json.loads(file.read_text())


# Department/Specialist endpoints
@app.get("/api/departments")
async def list_departments():
    """List all available departments/specialists."""
    orch = get_orchestrator()
    dept_mapping = orch._select_departments({"goal": "", "constraints": [], "assumptions": []}, {})
    return {"departments": [asdict(c) for c in dept_mapping]}


@app.post("/api/departments/{specialist_name}/run")
async def run_specialist(specialist_name: str, dispatch: Dict[str, Any]):
    """Run a single specialist pipeline."""
    try:
        specialist = load_specialist(specialist_name)
        runner = PipelineRunner(specialist, dispatch)
        result = await runner.run()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# OKR endpoints
@app.get("/api/okrs")
async def list_okrs():
    """List all OKRs."""
    okr_engine = OKREngine(store_path=str(Path(settings.data_dir) / "okrs.json"))
    return {
        "objectives": [
            {
                "id": o.id,
                "name": o.name,
                "description": o.description,
                "level": o.level.value,
                "owner": o.owner,
                "parent_id": o.parent_id,
                "key_results": [
                    {
                        "id": kr.id,
                        "name": kr.name,
                        "type": kr.type.value,
                        "target": kr.target,
                        "unit": kr.unit,
                        "weight": kr.weight,
                        "current": kr.current,
                        "confidence": kr.confidence,
                        "depends_on": kr.depends_on,
                        "progress": kr.progress()
                    }
                    for kr in o.key_results
                ],
                "created_at": o.created_at
            }
            for o in okr_engine.objectives.values()
        ]
    }


@app.post("/api/okrs", response_model=OKRResponse)
async def create_okr(request: OKRRequest):
    """Create a new OKR objective."""
    try:
        okr_engine = OKREngine(store_path=str(Path(settings.data_dir) / "okrs.json"))
        obj = okr_engine.create_objective(
            name=request.name,
            description=request.description,
            level=OKRLevel(request.level),
            owner=request.owner,
            parent_id=request.parent_id,
            registry=get_orchestrator().registry
        )
        return OKRResponse(
            id=obj.id,
            name=obj.name,
            description=obj.description,
            level=obj.level.value,
            owner=obj.owner,
            parent_id=obj.parent_id,
            key_results=[],
            created_at=obj.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/okrs/{objective_id}/key-results")
async def add_key_result(objective_id: str, request: KRRequest):
    """Add a key result to an objective."""
    try:
        okr_engine = OKREngine(store_path=str(Path(settings.data_dir) / "okrs.json"))
        kr = okr_engine.add_key_result(
            objective_id=objective_id,
            name=request.name,
            type=KRType(request.type),
            target=request.target,
            unit=request.unit,
            weight=request.weight
        )
        return {"id": kr.id, "name": kr.name, "type": kr.type.value, "target": kr.target, "unit": kr.unit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/okrs/rollup/{objective_id}")
async def rollup_progress(objective_id: str):
    """Get rolled-up progress for an objective."""
    okr_engine = OKREngine(store_path=str(Path(settings.data_dir) / "okrs.json"))
    progress = okr_engine.rollup_progress(objective_id)
    return {"objective_id": objective_id, "progress": progress}


# MYCELIUM endpoints
@app.get("/api/mycelium/nodes")
async def list_nodes():
    """List all MYCELIUM nodes."""
    registry = get_orchestrator().registry
    return {"nodes": registry.get_all_nodes()}


@app.get("/api/mycelium/edges")
async def list_edges():
    """List all MYCELIUM edges."""
    propagator = get_orchestrator().propagator
    return {"edges": propagator.get_all_edges()}


@app.get("/api/mycelium/signals")
async def list_signals(limit: int = 100):
    """List recent MYCELIUM signals."""
    propagator = get_orchestrator().propagator
    signals = propagator.get_signals(limit)
    return {"signals": signals}


@app.post("/api/mycelium/signals")
async def propagate_signal(request: SignalRequest):
    """Propagate a signal through MYCELIUM."""
    try:
        propagator = get_orchestrator().propagator
        signal = {
            "id": request.signal_id,
            "origin_kr": request.origin_kr,
            "event": request.signal_type,
            "new_status": "ROUTED",
            "signal_kind": request.signal_type.lower(),
            "diagnosed_cause": request.diagnosed_cause,
            "diagnosed_cause_category": request.category,
            "subgraph": [request.target_node],
            "fired_at": datetime.utcnow().isoformat() + "Z",
            "status": "ROUTED",
            "signature": "",
            "payload": request.payload
        }
        result = propagator.propagate(signal)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/mycelium/subgraph/{origin_kr}")
async def get_subgraph(origin_kr: str):
    """Get decision subgraph for a KR."""
    propagator = get_orchestrator().propagator
    subgraph = propagator.compute_subgraph(origin_kr)
    return {"origin_kr": origin_kr, "subgraph": list(subgraph)}


# SENTINEL endpoints
@app.get("/api/sentinel/chains")
async def verify_chains():
    """Verify all SENTINEL chains."""
    sentinel = get_orchestrator().sentinel
    results = sentinel.verify_all_chains()
    return {k: {"valid": v[0], "errors": v[1]} for k, v in results.items()}


@app.get("/api/sentinel/signals")
async def list_sentinel_signals(limit: int = 100):
    """List recent SENTINEL signals."""
    sentinel = get_orchestrator().sentinel
    tokens = sentinel.signal_log.get_tokens()
    return {"signals": [t.to_dict() for t in tokens[-limit:]]}


@app.get("/api/sentinel/gate-evidence")
async def list_gate_evidence(limit: int = 100):
    """List gate evidence from SENTINEL."""
    sentinel = get_orchestrator().sentinel
    tokens = sentinel.gate_evidence_log.get_tokens()
    return {"evidence": [t.to_dict() for t in tokens[-limit:]]}


# Consultation endpoint
@app.post("/api/consultation/open")
async def open_consultation(request: ConsultationRequest):
    """Open a consultation session."""
    try:
        conv_layer = get_orchestrator().conversation_layer
        session = conv_layer.open_consultation(
            batch_departments=request.batch_departments,
            evidence_outputs=request.evidence_outputs,
            problem_context=request.problem_context
        )
        return {"session_id": session.session_id, "status": "open"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Orientation Protocol (mock for now)
@app.post("/api/orientation")
async def run_orientation(goal: str, industry: str, jurisdiction: str = "", geography: str = "", business_model: str = ""):
    """Run Orientation Protocol - industry research."""
    orch = get_orchestrator()
    orientation = await orch._run_orientation(goal, {
        "industry": industry,
        "jurisdiction": jurisdiction,
        "geography": geography,
        "business_model": business_model
    })
    return orientation


# Specialist verification
@app.post("/api/verify/specialists")
async def verify_specialists():
    """Verify all specialists pass."""
    import subprocess
    result = subprocess.run(
        ["python3", "scripts/verify_all_runners.py"],
        cwd="/Users/Fujita/Documents/AI Filing System/decision-systems",
        env={**os.environ, "KOJIKI_TEST_MODE": "true"},
        capture_output=True,
        text=True
    )
    return {
        "success": result.returncode == 0,
        "output": result.stdout,
        "error": result.stderr
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
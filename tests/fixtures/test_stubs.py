#!/usr/bin/env python3
"""
Test stubs for KOJIKI pipeline stages.
Only loaded in test mode (KOJIKI_TEST_MODE=true).
"""

from engine.kojiki_core.types import hash_dict
from datetime import datetime


STAGE_STUBS = {
    "saccade": lambda ctx: {
        "problem_id": f"P-{hash_dict(ctx.get('task_id', 'test'))[:8]}",
        "goal": ctx.get('raw_record', 'Define measurable terms'),
        "constraints": ctx.get('constraints', []),
        "assumptions": ctx.get('assumptions', []),
        "unknowns": ctx.get('unknowns', []),
    },
    "evidence": lambda ctx: {
        "findings": [{
            "finding_id": "FE-001",
            "question": "What is current state?",
            "answer": "Test evidence",
            "source": "Test source",
            "confidence": 0.9,
            "retrieval_state": "RETRIEVED",
            "coverage_limits": "Test coverage",
            "sufficiency": "SUFFICIENT"
        }],
        "evidence_gaps": [],
        "collection_plan": [],
    },
    "interpretation": lambda ctx: {
        "interpretation_id": "INT-001",
        "synthesis": "Test interpretation",
        "confidence": 0.8,
        "key_insights": ["Test insight"],
        "evidence_refs": ["FE-001"],
        "department_requirements": {},
        "contradictions": [],
        "evidence_gaps": [],
        "diagnosis": "",
        "alternative_diagnoses_considered": [],
        "gaps_requiring_more_evidence": []
    },
    "strategy": lambda ctx: {
        "strategy_id": "STRAT-001",
        "interpretation_ref": "INT-001",
        "objective": "Test objective",
        "rationale": "Test rationale",
        "timeline": "Q4 2026",
        "success_criteria": [],
        "escalation_conditions": [],
        "team_okrs": [],
        "decision_rights": {
            "own": "Marketing.Head",
            "consult": [],
            "inform": []
        }
    },
    "output": lambda ctx: {
        "output_id": "OUT-001",
        "strategy_ref": "STRAT-001",
        "intervention": "Test intervention",
        "tactics": [],
        "channels": [],
        "owner": "Marketing.Head",
        "dependencies": [],
        "sla": "Q4 2026",
        "measurement": [],
    },
    "delegation": lambda ctx: {
        "handoffs_executed": 0,
        "results": {},
    },
    "handoff": lambda ctx: {
        "handoffs_executed": 0,
        "results": [],
    },
    "mycelium": lambda ctx: {
        "signals_generated": 0,
        "propagation_results": [],
    },
    "deck": lambda ctx: {
        "deck_id": "DECK-001",
        "slides": [],
    },
    "outcome": lambda ctx: {
        "outcome_id": "OC-20260916000001",
        "output_ref": "OUT-001",
        "actuals": {},
        "evaluations": [{
            "criterion": "test",
            "metric": "test_metric",
            "target": 1.0,
            "actual": 1.0,
            "operator": ">=",
            "passed": True,
            "weight": 1.0
        }],
        "outcome_score": 1.0,
        "target_met": True,
        "converged": True,
        "iteration_count": 1,
        "guardrail_violations": [],
        "deviation_analysis": "",
        "confidence": 1.0,
        "period": "2026-09-16",
    },
    "learning": lambda ctx: {
        "learning_id": "KL-20260916-001",
        "cycle_timestamp": datetime.utcnow().isoformat() + "Z",
        "experiences": [],
        "patterns": [],
        "reusable_insights": [],
        "redefinitions": [],
        "outcome_score": 0.0,
        "guardrail_violations": [],
        "confidence": 0.0,
        "kaizen_iteration": 1,
        "period": "2026-09-16",
    },
    "goal_synthesis": lambda ctx: {
        "refined_goal": ctx.get('raw_record', 'Test refined goal with specific constraints and measurable outcomes'),
        "confidence": 0.85,
    },
    "orientation_analysis": lambda ctx: {
        "ambiguity_score": 0.2,
        "completeness": 0.8,
        "key_entities": [],
        "sentiment": "positive",
        "hypothesis_updates": [],
        "new_hypotheses": [],
        "follow_up_needed": False,
        "suggested_follow_up": None,
    },
    "orientation_simulation": lambda ctx: {
        "response": "Test user response with specific constraints and stakeholders.",
    },
    "think_aloud": lambda ctx: {
        "thoughts": "Test think-aloud verbalization.",
    },
}


def get_test_stub(stage_name: str, context: dict) -> dict:
    """Get test stub for a stage."""
    stub_fn = STAGE_STUBS.get(stage_name)
    if stub_fn:
        return stub_fn(context)
    return {"error": f"No stub for stage: {stage_name}"}
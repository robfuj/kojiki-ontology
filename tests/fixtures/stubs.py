#!/usr/bin/env python3
"""
Test Fixtures - Stub implementations for testing without LLM.

This module contains all stub implementations that were previously in call_model().
Tests should import and use these when running without a real LLM.

Usage:
    from tests.fixtures import install_stubs
    install_stubs()  # Monkey-patches call_model with stubs
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import json


# ============================================================
# STUB DATA FOR EACH STAGE
# ============================================================

def get_saccade_stub(context: Dict[str, Any]) -> Dict[str, Any]:
    """Chief of Staff SACCADE - frames the actual user goal"""
    raw_record = context.get("raw_record", "")
    return {
        "problem_id": f"P-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "goal": raw_record[:200] if raw_record else "Frame the actual goal from user input",
        "constraints": ["Timeline as specified", "Budget as specified", "Regulatory compliance"],
        "assumptions": ["Stakeholders will engage", "Data is accessible", "Team capacity available"],
        "unknowns": ["Detailed requirements", "Technical feasibility", "Market conditions"]
    }


def get_saccade_marketing_stub() -> Dict[str, Any]:
    """Marketing-brand SACCADE - lead quality framing"""
    return {
        "problem_id": "P-ABCDEF12",
        "goal": "Define lead quality measurable terms agreed by Sales/Marketing",
        "constraints": ["2-week deadline", "Use existing CRM fields"],
        "assumptions": ["CRM data accurate", "Good faith engagement"],
        "unknowns": ["Current conversion by source", "Sales definition of quality"]
    }


def get_saccade_dept_head_stub(context: Dict[str, Any]) -> Dict[str, Any]:
    """Dept Head SACCADE - returns decomposition problem"""
    dept_objective = context.get('dept_objective', {})
    return {
        "problem_id": f"P-DH-{dept_objective.get('objective_id', 'ABCDEF12')[-8:]}" if dept_objective else "P-DH-ABCDEF12",
        "goal": f"Decompose {dept_objective.get('title', 'department objective') if dept_objective else 'department objective'} into team OKRs",
        "constraints": ["90-day quarter", "Team capacity limits", "Cross-team dependencies"],
        "assumptions": ["Team bandwidth as reported", "Engineering API delivery in 3 weeks"],
        "unknowns": ["Exact API spec timeline", "Content review cycle duration"]
    }


def get_evidence_marketing_stub() -> Dict[str, Any]:
    """Marketing Evidence - verified extracts only"""
    return {
        "findings": [
            {
                "finding_id": "FE-001",
                "question": "What is current lead-to-opportunity conversion by source?",
                "answer": "Q3 2026: organic=12%, paid=8%, referral=23%, email=5%",
                "source": "CRM export",
                "confidence": 0.95,
                "retrieval_state": "RETRIEVED",
                "coverage_limits": "Q3 2026 only",
                "sufficiency": "SUFFICIENT"
            }
        ]
    }


def get_evidence_dept_head_stub() -> Dict[str, Any]:
    """Dept Head Evidence - team capability assessment"""
    return {
        "findings": [
            {
                "finding_id": "FE-DH-001",
                "question": "What is Marketing.Growth capacity for referral program?",
                "answer": "Team of 3, 40% bandwidth available, email automation tools ready",
                "source": "Team capacity planning doc",
                "confidence": 0.9,
                "retrieval_state": "RETRIEVED",
                "coverage_limits": "Current sprint only",
                "sufficiency": "SUFFICIENT"
            },
            {
                "finding_id": "FE-DH-002",
                "question": "What is Marketing.Brand capacity for landing page assets?",
                "answer": "Team of 2, 60% bandwidth, Figma design system established",
                "source": "Design team sprint plan",
                "confidence": 0.9,
                "retrieval_state": "RETRIEVED",
                "coverage_limits": "Next 2 weeks",
                "sufficiency": "SUFFICIENT"
            },
            {
                "finding_id": "FE-DH-003",
                "question": "What is Engineering.Referral API timeline?",
                "answer": "API v2 in development, estimated 3 weeks to staging, authentication TBD",
                "source": "Engineering sprint board",
                "confidence": 0.7,
                "retrieval_state": "PARTIAL",
                "coverage_limits": "API spec not finalized",
                "sufficiency": "INSUFFICIENT"
            }
        ]
    }


def get_interpretation_marketing_stub() -> Dict[str, Any]:
    """Marketing Interpretation - diagnosis only"""
    return {
        "interpretation_id": "INT-001",
        "evidence_refs": ["FE-001"],
        "diagnosis": "Quality gap is source-mix (referral 23% vs paid 8%), not scoring model",
        "confidence": 0.85,
        "alternative_diagnoses_considered": ["Scoring model drift", "Data quality issues"],
        "gaps_requiring_more_evidence": ["Sales team's qualitative quality definition"]
    }


def get_interpretation_dept_head_stub() -> Dict[str, Any]:
    """Dept Head Interpretation - gap analysis"""
    return {
        "interpretation_id": "INT-DH-001",
        "evidence_refs": ["FE-DH-001", "FE-DH-002", "FE-DH-003"],
        "diagnosis": "Team capacity exists but cross-team coordination needed for referral program",
        "confidence": 0.8,
        "alternative_diagnoses_considered": ["Engineering capacity overstated", "Marketing capacity overstated"],
        "gaps_requiring_more_evidence": ["Engineering.Referral API timeline confirmation"]
    }


def get_strategy_marketing_stub() -> Dict[str, Any]:
    """Marketing Strategy - objective decision only"""
    return {
        "strategy_id": "STRAT-001",
        "interpretation_ref": "INT-001",
        "objective": "Shift 30% paid budget to referral program activation in Q4",
        "rationale": "Referral converts 2.9x paid, source-mix explains 73% of quality variance",
        "timeline": "Q4 2026 (Oct-Dec)",
        "success_criteria": [
            {"name": "pipeline_growth", "metric": "referral_pipeline_qoq", "target": 0.15, "operator": ">=", "weight": 1.0},
            {"name": "cac_reduction", "metric": "paid_cac_delta_pct", "target": -0.20, "operator": "<=", "weight": 1.0},
            {"name": "conversion_rate", "metric": "referral_to_opp_conversion", "target": 0.20, "operator": ">=", "weight": 0.5}
        ],
        "escalation_conditions": ["CAC target missed by >15%", "Referral API delay >2 weeks"],
        "decision_rights": {
            "own": "Marketing.Growth",
            "consult": ["Sales.Outbound", "Finance.Budget"],
            "inform": ["Finance", "Engineering.Referral"]
        }
    }


def get_strategy_cos_stub() -> Dict[str, Any]:
    """Chief of Staff Strategy - returns department-level actions for decomposition"""
    return {
        "strategy_id": f"STRAT-COS-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "interpretation_ref": "INT-001",
        "objective": "Decompose goal into department-level objectives",
        "rationale": "Chief of Staff decomposition for multi-department coordination",
        "timeline": "Q4 2026",
        "success_criteria": [
            {"name": "decomposition_complete", "metric": "dept_objectives_created", "target": 7, "operator": ">=", "weight": 1.0}
        ],
        "escalation_conditions": ["No departments available", "Dependencies unresolvable"],
        "actions": [
            {
                "owner": "Marketing",
                "description": "Define yuzu drink brand positioning, messaging, and go-to-market strategy for US high-end market",
                "dependencies": [],
                "success_criteria": [
                    {"name": "brand_positioning", "metric": "brand_concept_approved", "target": 1, "operator": ">=", "weight": 1.0},
                    {"name": "gtm_strategy", "metric": "launch_plan_complete", "target": 1, "operator": ">=", "weight": 1.0}
                ]
            },
            {
                "owner": "Legal",
                "description": "Secure FDA approval and ensure full regulatory compliance for formulation and labeling",
                "dependencies": [],
                "success_criteria": [
                    {"name": "fda_approval", "metric": "approval_status", "target": 1, "operator": "==", "weight": 0.6},
                    {"name": "label_compliance", "metric": "audit_pass_rate", "target": 100, "operator": "==", "weight": 0.4}
                ]
            },
            {
                "owner": "Finance",
                "description": "Build lean financial plan for yuzu brand launch ($50K-100K bootstrap), path to profitability in 12 months",
                "dependencies": [],
                "success_criteria": [
                    {"name": "bootstrap_budget", "metric": "total_budget", "target": 100000, "operator": "<=", "weight": 0.4},
                    {"name": "unit_economics", "metric": "contribution_margin", "target": 0.40, "operator": ">=", "weight": 0.3},
                    {"name": "break_even", "metric": "months_to_breakeven", "target": 12, "operator": "<=", "weight": 0.3}
                ]
            },
            {
                "owner": "Engineering",
                "description": "Develop and validate premium yuzu beverage formulation meeting quality and regulatory standards",
                "dependencies": ["Operations", "Legal"],
                "success_criteria": [
                    {"name": "formulation_approval", "metric": "qa_signoff", "target": 1, "operator": "==", "weight": 0.4},
                    {"name": "sensory_score", "metric": "panel_rating", "target": 8, "operator": ">=", "weight": 0.3}
                ]
            },
            {
                "owner": "Operations",
                "description": "Establish sustainable supply chain and packaging meeting FDA compliance and launch timeline",
                "dependencies": ["Legal", "Finance"],
                "success_criteria": [
                    {"name": "supplier_contracts", "metric": "contracts_signed", "target": 2, "operator": "==", "weight": 0.3},
                    {"name": "sustainable_packaging", "metric": "certification", "target": 1, "operator": "==", "weight": 0.3}
                ]
            },
            {
                "owner": "Sales",
                "description": "Secure upscale retail distribution and achieve revenue targets",
                "dependencies": ["Marketing", "Operations"],
                "success_criteria": [
                    {"name": "retail_accounts", "metric": "accounts_secured", "target": 25, "operator": ">=", "weight": 0.5},
                    {"name": "revenue_target", "metric": "first_year_revenue", "target": 10000000, "operator": ">=", "weight": 0.5}
                ]
            },
            {
                "owner": "People & Comms",
                "description": "Build brand team and execute internal/external communications",
                "dependencies": ["Finance", "Operations"],
                "success_criteria": [
                    {"name": "team_built", "metric": "key_roles_filled", "target": 5, "operator": ">=", "weight": 0.5},
                    {"name": "comms_ready", "metric": "launch_comms_plan", "target": 1, "operator": "==", "weight": 0.5}
                ]
            }
        ]
    }


def get_strategy_dept_head_engineering_stub() -> Dict[str, Any]:
    """Engineering Dept Head Strategy - returns team OKRs"""
    return {
        "team_okrs": [
            {
                "team": "Engineering.Technology.Platform",
                "objective_id": "OKR-Engineering.Technology.Platform-P-ABCDEF12-001",
                "title": "Improve platform reliability and developer velocity",
                "description": "Platform instability and slow deployments are blocking feature delivery across all teams. This team owns the core platform runtime, CI/CD, and shared infrastructure.",
                "key_results": [
                    {"description": "Reduce p99 API latency from 800ms to <200ms", "kr_type": "metric", "target": 200, "unit": "ms", "weight": 1.0, "source": "Datadog", "frequency": "weekly", "confidence": 0.8, "is_leading": True},
                    {"description": "Increase deployment success rate from 85% to 99%", "kr_type": "metric", "target": 99, "unit": "%", "weight": 1.0, "source": "CI/CD", "frequency": "weekly", "confidence": 0.8, "is_leading": True},
                    {"description": "Reduce mean time to recovery (MTTR) from 45min to <10min", "kr_type": "metric", "target": 10, "unit": "min", "weight": 1.0, "source": "PagerDuty", "frequency": "weekly", "confidence": 0.7, "is_leading": True},
                    {"description": "Achieve 90% test coverage on critical paths", "kr_type": "metric", "target": 90, "unit": "%", "weight": 0.5, "source": "Codecov", "frequency": "monthly", "confidence": 0.8, "is_leading": True}
                ],
                "dependencies": [{"target_team": "Engineering.Technology.Infrastructure", "weight": 0.7}]
            },
            {
                "team": "Engineering.Technology.Referral",
                "objective_id": "OKR-Engineering.Technology.Referral-P-ABCDEF12-002",
                "title": "Build scalable referral tracking and rewards engine",
                "description": "Referral program needs a robust API for tracking referrals, calculating rewards, and handling fraud detection. This team owns the referral API surface.",
                "key_results": [
                    {"description": "Achieve 99.9% referral API uptime", "kr_type": "metric", "target": 99.9, "unit": "%", "weight": 1.0, "source": "Datadog", "frequency": "weekly", "confidence": 0.8, "is_leading": True},
                    {"description": "Process 10k referrals/day with <100ms p99 latency", "kr_type": "metric", "target": 100, "unit": "ms", "weight": 1.0, "source": "API Gateway", "frequency": "weekly", "confidence": 0.7, "is_leading": True},
                    {"description": "Detect and block 99% of fraudulent referrals", "kr_type": "metric", "target": 99, "unit": "%", "weight": 1.0, "source": "Fraud Engine", "frequency": "weekly", "confidence": 0.8, "is_leading": True}
                ],
                "dependencies": [{"target_team": "Engineering.Technology.Platform", "weight": 0.8}]
            }
        ]
    }


def get_output_marketing_stub() -> Dict[str, Any]:
    """Marketing Output - execution plan"""
    return {
        "objective": "Shift 30% paid budget to referral program activation in Q4",
        "owner": "Marketing.Growth",
        "actions": [
            {
                "action_id": "ACT-001",
                "description": "Launch referral incentive email sequence (3-touch)",
                "owner": "Marketing.Growth",
                "due_date": "2026-10-15",
                "dependencies": []
            },
            {
                "action_id": "ACT-002",
                "description": "Build referral landing page with CRM automation",
                "owner": "Engineering.Referral",
                "due_date": "2026-10-31",
                "dependencies": ["ACT-001"]
            }
        ],
        "success_criteria": [
            {"name": "pipeline_growth", "metric": "referral_pipeline_qoq", "target": 0.15, "operator": ">=", "weight": 1.0},
            {"name": "cac_reduction", "metric": "paid_cac_delta_pct", "target": -0.20, "operator": "<=", "weight": 1.0},
            {"name": "conversion_rate", "metric": "referral_to_opp_conversion", "target": 0.20, "operator": ">=", "weight": 0.5}
        ],
        "risks": [
            {"risk_id": "RSK-001", "description": "Incentive cost exceeds budget", "likelihood": 0.3, "impact": 0.6, "mitigation": "Cap incentives at $500/referral"},
            {"risk_id": "RSK-002", "description": "Referral API not ready by launch", "likelihood": 0.2, "impact": 0.8, "mitigation": "Manual fallback process documented"}
        ],
        "decision_rights": {
            "own": "Marketing.Growth",
            "consult": ["Sales.Outbound", "Finance.Budget"],
            "inform": ["Finance", "Engineering.Referral"]
        }
    }


def get_deck_stub() -> Dict[str, Any]:
    """Deck - returns error for missing deck builder"""
    return {"error": "deck-builder skill not found in any known location"}


def get_outcome_stub() -> Dict[str, Any]:
    """Outcome - Kaizen Loop PDCA results"""
    return {
        "outcome_id": f"OC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "period": datetime.utcnow().strftime('%Y-%m-%d'),
        "results": [
            {"name": "pipeline_growth", "metric": "referral_pipeline_qoq", "target": 0.15, "actual": 0.16, "achieved": True, "variance_pct": 6.7, "weight": 1.0},
            {"name": "cac_reduction", "metric": "paid_cac_delta_pct", "target": -0.20, "actual": -0.16, "achieved": False, "variance_pct": -20.0, "weight": 1.0},
            {"name": "conversion_rate", "metric": "referral_to_opp_conversion", "target": 0.20, "actual": 0.22, "achieved": True, "variance_pct": 10.0, "weight": 0.5}
        ],
        "guardrail_violations": [
            {"guardrail_id": "VAR-001", "description": "High variance on paid_cac_delta_pct: 20.0% from target", "severity": "warning", "action_taken": "Investigate root cause: measurement error or real deviation?"}
        ],
        "decisions_triggered": [],
        "lessons": ["CAC reduction target too aggressive for current channel mix"]
    }


def get_learning_stub() -> Dict[str, Any]:
    """Learning - Kaizen Loop Synthesis"""
    today = datetime.utcnow().strftime('%Y%m%d')
    return {
        "learning_id": f"KL-{today}-001",
        "period": datetime.utcnow().strftime('%Y-%m-%d'),
        "what_worked": ["Referral channel outperformed paid channels"],
        "what_failed": ["CAC target missed by 20%"],
        "kaizen_actions": [
            {
                "action_id": "KA-001",
                "description": "Redefine problem to optimize channel mix",
                "owner": "Marketing.Growth",
                "due_date": "2026-10-15",
                "success_metric": "CAC reduction >= 15%",
                "status": "planned"
            }
        ],
        "schema_updates": [],
        "prompt_updates": [],
        "decision_rights_changes": []
    }


# ============================================================
# STUB DISPATCHER
# ============================================================

_STUB_DISPATCH = {
    ("saccade", "a priori problem framing"): get_saccade_marketing_stub,
    ("saccade", "chief of staff"): get_saccade_stub,
    ("saccade", "cos-saccade"): get_saccade_stub,
    ("saccade", "cos-decomp"): get_saccade_stub,
    ("saccade", "department head decomposition"): get_saccade_dept_head_stub,
    ("evidence", "verified extracts only"): get_evidence_marketing_stub,
    ("evidence", "team capability assessment"): get_evidence_dept_head_stub,
    ("interpretation", "diagnosis only"): get_interpretation_marketing_stub,
    ("interpretation", "gap analysis"): get_interpretation_dept_head_stub,
    ("strategy", "objective decision only"): get_strategy_marketing_stub,
    ("strategy", "chief of staff"): get_strategy_cos_stub,
    ("strategy", "decompose"): get_strategy_cos_stub,
    ("strategy", "department-level"): get_strategy_cos_stub,
    ("strategy", "team okr"): get_strategy_dept_head_engineering_stub,
    ("output", "execution plan"): get_output_marketing_stub,
    ("output", "action plan"): get_output_marketing_stub,
    ("output", "decision + action plan"): get_output_marketing_stub,
    ("output", "executable action plan"): get_output_marketing_stub,
    ("deck",): get_deck_stub,
    ("outcome", "kaizen"): get_outcome_stub,
    ("learning", "kaizen"): get_learning_stub,
}


def get_stub(prompt: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Get stub response for given prompt and context."""
    prompt_lower = prompt.lower()

    # Check for Chief of Staff SACCADE
    task_id = str(context.get("task_id", ""))
    if ("cos-saccade" in task_id) or ("cos-decomp" in task_id) or ("chief of staff" in prompt_lower and "a priori" in prompt_lower):
        return get_saccade_stub(context)

    # Check for Chief of Staff Strategy
    if ("cos-decomp" in task_id) or ("cos-saccade" in task_id) or context.get("dept_head") == "ChiefOfStaff":
        if "strategy" in prompt_lower:
            return get_strategy_cos_stub()

    # Check for department head SACCADE
    if "dh-saccade" in task_id:
        return get_saccade_dept_head_stub(context)

    # Match by prompt keywords
    for keywords, stub_fn in _STUB_DISPATCH.items():
        if all(k in prompt_lower for k in keywords):
            return stub_fn()

    return None


# ============================================================
# INSTALLER FOR TESTS
# ============================================================

def install_stubs():
    """
    Monkey-patch call_model with stub implementation.
    Call this in test setup to enable stubs.
    """
    import kojiki.core
    original_call_model = kojiki.core.call_model

    def stub_call_model(prompt: str, context: Dict[str, Any], tools: List, schema: Dict = None, stage_name: str = "") -> Dict[str, Any]:
        print(f"  [MODEL CALL] Context keys: {list(context.keys())}")
        print(f"  [MODEL CALL] Tools allowed: {[t.name if hasattr(t, 'name') else t for t in tools] if tools else []}")

        # Execute tools if any
        tool_results = {}
        for tool in tools:
            try:
                if hasattr(tool, 'name'):
                    tool_name = tool.name
                    result = tool.execute(context, {})
                else:
                    tool_name = tool
                    result = f"[Tool: {tool} - not implemented]"
                tool_results[tool_name] = result
            except Exception as e:
                print(f"  [TOOL ERROR] {tool}: {e}")

        # Return stub response
        stub = get_stub(prompt, context)
        if stub is not None:
            return stub

        # Fallback - should not happen in tests
        print(f"  [STUB WARNING] No stub matched for prompt: {prompt[:100]}")
        return {"error": "No stub available for this prompt"}

    kojiki.core.call_model = stub_call_model
    return original_call_model


def uninstall_stubs():
    """Restore original call_model (if needed)."""
    import kojiki.core
    # This would need to store the original - simplified for now
    pass


if __name__ == "__main__":
    # Quick test
    print("Testing stub dispatcher...")
    test_cases = [
        ("SACCADE - a priori problem framing", {"task_id": "test", "raw_record": "test goal"}),
        ("strategy - objective decision only", {"task_id": "test"}),
        ("evidence - verified extracts only", {"task_id": "test"}),
    ]
    for prompt, ctx in test_cases:
        result = get_stub(prompt, ctx)
        print(f"  {prompt}: {'OK' if result else 'NO MATCH'}")
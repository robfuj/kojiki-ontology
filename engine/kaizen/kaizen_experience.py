#!/usr/bin/env python3
"""
Kaizen Experience Extraction - Extract atomic experiences from pipeline execution.

Only creates experiences for outcomes that need learning (target not met).
Successful outcomes don't generate escalations.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional


def extract_experiences(
    stage_outputs: Dict[str, Any],
    outcome_check: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Extract atomic experiences from the full pipeline execution."""
    # Skip experience extraction for successful outcomes - no escalation needed
    if outcome_check.get("target_met"):
        return []

    experiences = []

    # One experience per hypothesis tested
    problem = stage_outputs.get("problem", {})
    strategy = stage_outputs.get("strategy", {})
    output = stage_outputs.get("output", {})

    if problem and strategy and output:
        # Get problem_id, ensure it matches pattern
        prob_id = problem.get("problem_id", problem.get("id", "unknown"))
        if not prob_id.startswith("P-"):
            prob_id = f"P-{prob_id}" if prob_id != "unknown" else "P-UNKNOWN00"

        # Get redefinitions from outcome_check
        redefinitions = outcome_check.get("redefinitions", [])

        exp = {
            "id": f"EXP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "problem_id": prob_id,
            "hypothesis": strategy.get("objective", "Unknown hypothesis"),
            "evidence_summary": _summarize_evidence(stage_outputs.get("evidence", {})),
            "error_classification": classify_error(outcome_check, stage_outputs),
            "outcome": "confirmed" if outcome_check.get("target_met") else "invalidated",
            "learning_ref": None,  # Will be set to learning_record.learning_id
            "redefinition": redefinitions[0] if redefinitions else None,
            "agents": strategy.get("owner", "").split(",") if isinstance(strategy.get("owner"), str) else [strategy.get("owner", "unknown")],
            "recorded_at": datetime.utcnow().isoformat() + "Z",
        }
        experiences.append(exp)

    return experiences


def _summarize_evidence(evidence: Dict[str, Any]) -> str:
    """Create concise evidence summary."""
    findings = evidence.get("findings", [])
    if not findings:
        return "No evidence gathered"
    return "; ".join([f"{f.get('question', '')}: {f.get('extract', '')}" for f in findings[:3]])


def classify_error(outcome_check: Dict[str, Any], stage_outputs: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Classify error using NEURAXIS-style classification."""
    from .kaizen_classification import classify_error as _classify
    return _classify(outcome_check, stage_outputs)
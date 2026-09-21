#!/usr/bin/env python3
"""
Kaizen Classification - NEURAXIS-style error classification (L0-L4).

Deep classification uses full pipeline context to detect:
- L0_execution: Information/Execution errors (missing data, variance)
- L1_reasoning: Reasoning errors (confidence miscalibration)
- L2_problem_representation: Assumption errors (invalidated assumptions)
- L3_ontology: Model/representation errors (wrong mental model)
- L4_meta_strategy: Meta errors (conflicting strategies, governance needed)
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class ErrorClassification:
    """Result of error classification."""
    error_class: str  # One of the NEURAXIS error classes
    layer: str  # L0-L4
    reasoning: str


def classify_error(
    outcome_check: Dict[str, Any],
    stage_outputs: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Classify error type based on outcome check.
    Returns NEURAXIS ErrorClass string.
    """
    if outcome_check.get("target_met"):
        return None  # Success - no error to classify

    violations = outcome_check.get("guardrail_violations", [])

    # L0: Basic data/execution issues (work with compressed)
    if any(v.get("validator") == "completeness" for v in violations):
        return "Information error"  # Maps to L0_EXECUTION
    if any(v.get("validator") == "variance" for v in violations):
        return "Execution error"  # Maps to L0_EXECUTION

    # L1: Reasoning calibration issues (work with compressed)
    if any(v.get("validator") == "confidence_calibration" for v in violations):
        return "Reasoning error"  # Maps to L1_REASONING

    # Deep classification requires stage_outputs with evidence/interpretation
    if stage_outputs:
        # Check if we have full evidence/interpretation (not compressed)
        evidence = stage_outputs.get("evidence", {})
        interpretation = stage_outputs.get("interpretation", {})

        # If compressed (only finding_ids), can't do deep classification
        if "finding_ids" in evidence and "findings" not in evidence:
            return "Execution error"  # Default for compressed context

        # L4: Meta-strategy conflict (check first - highest level)
        if _detect_meta_strategy_conflict(stage_outputs):
            return "Meta error"  # Maps to L4_META_STRATEGY

        # L2: Assumption invalidation detected
        if _detect_assumption_invalidation(stage_outputs):
            return "Assumption error"  # Maps to L2_PROBLEM_REPRESENTATION

        # L3: Model/representation mismatch
        if _detect_model_representation_gap(stage_outputs):
            return "Model/representation error"  # Maps to L3_ONTOLOGY

    return "Execution error"  # Default to L0


def _detect_assumption_invalidation(stage_outputs: Dict[str, Any]) -> bool:
    """Detect if core assumptions were invalidated by evidence."""
    evidence = stage_outputs.get("evidence", {})
    interpretation = stage_outputs.get("interpretation", {})

    # Check for contradiction between evidence and prior assumptions
    assumptions = stage_outputs.get("problem", {}).get("assumptions", [])
    if not assumptions:
        return False

    # Check if interpretation mentions assumption invalidation
    interpretation_text = str(interpretation).lower()
    for assumption in assumptions:
        assumption_key = assumption.lower()[:50]  # First 50 chars as key
        if assumption_key in interpretation_text and ("invalid" in interpretation_text or "contradict" in interpretation_text):
            return True

    # Check for evidence contradictions
    findings = evidence.get("findings", [])
    for finding in findings:
        if finding.get("sufficiency") == "CONTRADICTED":
            return True

    return False


def _detect_model_representation_gap(stage_outputs: Dict[str, Any]) -> bool:
    """Detect if the mental model (strategy) doesn't match reality (evidence/outcome)."""
    strategy = stage_outputs.get("strategy", {})
    outcome = stage_outputs.get("outcome_check", {})

    # Check if strategy's success criteria were all met but outcome still failed
    # This indicates the strategy's model of the world was wrong
    if not outcome.get("target_met", True):
        success_criteria = strategy.get("success_criteria", [])
        evaluations = outcome.get("evaluations", [])

        # If strategy predicted success but outcome failed
        if evaluations:
            passed_count = sum(1 for e in evaluations if e.get("passed", False))
            total = len(evaluations)
            if passed_count == 0 and total > 0:
                # Complete failure - likely wrong model
                return True

    # Check for pattern: same strategy repeatedly fails
    # This would require access to learning history - simplified here
    return False


def _detect_meta_strategy_conflict(stage_outputs: Dict[str, Any]) -> bool:
    """Detect conflicts at the meta-strategy level (governance needed)."""
    strategy = stage_outputs.get("strategy", {})
    decision_rights = strategy.get("decision_rights", {})

    # Check for conflicting decision rights assignments
    own = decision_rights.get("own", "")
    consult = decision_rights.get("consult", [])

    # Conflict: Multiple owners or unclear ownership
    if not own and len(consult) > 1:
        return True

    # Check for escalation conditions that weren't met
    escalation_conditions = strategy.get("escalation_conditions", [])
    if escalation_conditions:
        # If escalation was needed but not triggered, meta conflict
        return True

    # Check for cross-department coordination failure
    outcome = stage_outputs.get("outcome_check", {})
    if not outcome.get("target_met", True):
        # Check if multiple departments involved but no clear lead
        agents = strategy.get("owner", "").split(",")
        if len(agents) > 1:
            return True

    return False
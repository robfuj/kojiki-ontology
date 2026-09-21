#!/usr/bin/env python3
"""
Kaizen Learning Synthesis - Extract patterns, generate insights, identify redefinitions.

The ACT phase of PDCA: synthesizes experiences into organizational learning.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional


def run_learning_synthesis(
    all_stage_outputs: Dict[str, Any],
    outcome_check: Dict[str, Any],
    prior_learning: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    ACT phase: Synthesize experiences, extract patterns, update problem framing.

    This is the atomic unit of organizational learning per thesis §III.4.
    """
    # Extract experiences from this cycle
    experiences = _extract_experiences(all_stage_outputs, outcome_check)

    # Synthesize patterns across experiences
    patterns = _synthesize_patterns(experiences, prior_learning)

    # Generate reusable insights
    insights = _generate_insights(patterns, outcome_check)

    # Identify problem redefinitions needed (feed back to SACCADE)
    redefinitions = _identify_redefinitions(patterns, all_stage_outputs)

    # Create learning record
    learning_record = {
        "learning_id": f"KL-{datetime.utcnow().strftime('%Y%m%d')}-{len(prior_learning or []) + 1:03d}",
        "cycle_timestamp": datetime.utcnow().isoformat() + "Z",
        "experiences": experiences,
        "patterns": patterns,
        "reusable_insights": insights,
        "redefinitions": redefinitions,
        "outcome_score": outcome_check.get("outcome_score", 0),
        "guardrail_violations": outcome_check.get("guardrail_violations", []),
        "confidence": _calculate_learning_confidence(experiences, patterns),
        "kaizen_iteration": 1,  # Will be set by caller
        "period": outcome_check.get("period", "") if outcome_check else "",
    }

    return learning_record


def _extract_experiences(
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
            "error_classification": _classify_error(outcome_check, stage_outputs),
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


def _classify_error(outcome_check: Dict[str, Any], stage_outputs: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Reuse classification from kaizen_classification."""
    from .kaizen_classification import classify_error
    return classify_error(outcome_check, stage_outputs)


def _synthesize_patterns(
    experiences: List[Dict[str, Any]],
    prior_learning: Optional[List[Dict[str, Any]]] = None
) -> List[str]:
    """Synthesize patterns across experiences."""
    patterns = []

    # Pattern: Common error classifications
    error_types = [e.get("error_classification") for e in experiences]
    if len(set(error_types)) == 1 and len(experiences) > 1:
        patterns.append(f"Recurring {error_types[0]} across {len(experiences)} experiences")

    # Pattern: Common agents
    all_agents = []
    for e in experiences:
        all_agents.extend(e.get("agents", []))
    agent_counts = {}
    for a in all_agents:
        agent_counts[a] = agent_counts.get(a, 0) + 1
    for agent, count in agent_counts.items():
        if count > 1:
            patterns.append(f"Agent {agent} involved in {count} experiences")

    # Cross-reference with prior learning
    if prior_learning:
        for prior in prior_learning:
            prior_patterns = prior.get("patterns", [])
            for p in prior_patterns:
                if any(keyword in p.lower() for keyword in ["recurring", "repeated", "persistent"]):
                    patterns.append(f"Persistent pattern confirmed: {p}")

    return patterns


def _generate_insights(
    patterns: List[str],
    outcome_check: Dict[str, Any]
) -> List[str]:
    """Generate reusable insights from patterns."""
    insights = []

    for pattern in patterns:
        if "Recurring" in pattern:
            insights.append(f"Systematic fix needed for: {pattern}")
        elif "Agent" in pattern and "involved" in pattern:
            insights.append(f"Capability gap in {pattern.split()[1]} - consider training or tooling")
        elif "Persistent" in pattern:
            insights.append(f"Root cause not yet addressed: {pattern}")

    # Outcome-specific insights
    if not outcome_check.get("target_met"):
        insights.append("Intervention did not meet success criteria - redesign required")
    else:
        insights.append("Intervention successful - document for replication")

    return insights


def _identify_redefinitions(
    patterns: List[str],
    stage_outputs: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Identify problem redefinitions to feed back to SACCADE."""
    redefinitions = []

    problem = stage_outputs.get("problem", {})
    if not problem:
        return redefinitions

    # If assumptions were invalidated, create redefinition
    for pattern in patterns:
        if "assumption" in pattern.lower() or "invalid" in pattern.lower():
            redefinitions.append({
                "new_problem": f"{problem.get('id', 'P-0000')}-v2",
                "supersedes": problem.get("id", "P-0000"),
                "reason": f"Assumption invalidated by pattern: {pattern}",
                "goal": problem.get("goal"),
                "constraints": problem.get("constraints", []),
                "assumptions": [a for a in problem.get("assumptions", []) if "invalid" not in a.lower()],
                "unknowns": problem.get("unknowns", []) + ["What is the correct assumption?"],
            })

    # If outcome failed, add unknowns about why
    outcome_check = stage_outputs.get("outcome_check", {})
    if outcome_check and not outcome_check.get("target_met"):
        redefinitions.append({
            "new_problem": f"{problem.get('id', 'P-0000')}-retry",
            "supersedes": problem.get("id", "P-0000"),
            "reason": "Intervention failed to meet success criteria",
            "goal": problem.get("goal"),
            "constraints": problem.get("constraints", []),
            "assumptions": problem.get("assumptions", []),
            "unknowns": problem.get("unknowns", []) + [
                "Why did intervention not achieve target?",
                "What alternative interventions would work?",
            ],
        })

    return redefinitions


def _calculate_learning_confidence(
    experiences: List[Dict[str, Any]],
    patterns: List[str]
) -> float:
    """Calculate confidence in the learning synthesis."""
    if not experiences:
        return 0.0

    # Base confidence on number of experiences and pattern consistency
    exp_factor = min(len(experiences) / 5.0, 1.0)  # Up to 5 experiences
    pattern_factor = min(len(patterns) / 3.0, 1.0)  # Up to 3 patterns

    return round((exp_factor + pattern_factor) / 2, 2)
#!/usr/bin/env python3
"""
Kaizen Guardrails - Validation rules that promote learning (not just reject).

Implements the thesis §III.4 "Kaizen Loop" guardrails:
- Completeness: all required measurements present
- Variance: actuals within expected bounds
- Trend: check for regression vs prior cycles
- Confidence Calibration: outcome confidence matches evidence quality
"""

from typing import Dict, Any, List
from .kaizen_types import GuardrailViolation


def run_guardrails(
    output: Dict[str, Any],
    actuals: Dict[str, Any],
    evaluations: List[Dict[str, Any]]
) -> List[GuardrailViolation]:
    """Run all guardrails validators."""
    violations = []

    # 1. Completeness guardrail: all required measurements present
    required_metrics = [e["metric"] for e in evaluations]
    for metric in required_metrics:
        if metric not in actuals:
            violations.append(GuardrailViolation(
                validator="completeness",
                severity="error",
                message=f"Required metric '{metric}' missing from actuals",
                suggested_fix="Add measurement instrumentation for this metric",
                learning_ref=f"learning_missing_{metric}"
            ))

    # 2. Variance guardrail: actuals within expected bounds
    for eval_detail in evaluations:
        actual = eval_detail["actual"]
        target = eval_detail["target"]
        if target != 0:
            variance = abs(actual - target) / abs(target)
            if variance > 0.5:  # >50% variance
                violations.append(GuardrailViolation(
                    validator="variance",
                    severity="warning",
                    message=f"High variance on {eval_detail['metric']}: {variance:.1%} from target",
                    suggested_fix="Investigate root cause: measurement error or real deviation?",
                    learning_ref=f"learning_variance_{eval_detail['metric']}"
                ))

    # 3. Trend guardrail: check for regression vs prior cycles
    # (Would compare with historical data in production)

    # 4. Confidence guardrail: outcome confidence matches evidence quality
    if "confidence" in output:
        if output["confidence"] > 0.9 and any(v.severity == "error" for v in violations):
            violations.append(GuardrailViolation(
                validator="confidence_calibration",
                severity="warning",
                message="High confidence but guardrail errors present",
                suggested_fix="Recalibrate confidence based on validation results",
                learning_ref="learning_confidence_calibration"
            ))

    return violations
#!/usr/bin/env python3
"""
Kaizen Loop - PDCA-based continuous improvement for OUTCOME/LEARNING stages.

Implements the thesis §III.4 "Kaizen Loop" protocol:
- Plan: Define success criteria and measurement windows
- Do: Execute intervention, capture actuals
- Check: Compare actuals vs criteria, run guardrails validation
- Act: Synthesize experiences, update problem framing, close loop

Uses guardrails-style validators that promote learning (not just reject).
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

from .kaizen_types import (
    KaizenPhase, ValidationResult, SuccessCriterion, GuardrailViolation,
    KaizenIteration
)
from .kaizen_compression import KaizenCompressor, CompressionLevel
from .kaizen_guardrails import run_guardrails
from .kaizen_learning import run_learning_synthesis
from .kaizen_experience import extract_experiences
from .kaizen_classification import classify_error


class KaizenLoop:
    """
    Kaizen Loop for OUTCOME/LEARNING stages.

    Runs PDCA cycles until convergence or max iterations.
    Each cycle generates verifiable learning cases.

    Adaptive: Stops early when converged (with min_iterations guard)
    """

    def __init__(
        self,
        max_iterations: int = 3,
        min_iterations: int = 1,
        convergence_threshold: float = 0.95,
        guardrails_config: Optional[Dict[str, Any]] = None,
        compression_level: CompressionLevel = CompressionLevel.ESSENTIAL
    ):
        self.max_iterations = max_iterations
        self.min_iterations = min_iterations
        self.convergence_threshold = convergence_threshold
        self.guardrails_config = guardrails_config or {}
        self.compression_level = compression_level
        self.compressor = KaizenCompressor(compression_level)
        self.iterations: List[KaizenIteration] = []
        self.learning_cases: List[Dict[str, Any]] = []

    def _should_continue(self, iteration: int, converged: bool) -> bool:
        """Determine if PDCA should continue to next iteration."""
        if iteration >= self.max_iterations:
            return False
        if iteration < self.min_iterations:
            return True
        return not converged

    def run_outcome_check(
        self,
        output: Dict[str, Any],
        success_criteria: List[SuccessCriterion],
        measurement_window: Dict[str, str],
        actuals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        CHECK phase: Compare actuals vs success criteria with guardrails.

        Returns outcome assessment with learning cases for any gaps.
        """
        # Evaluate all criteria
        evaluations = []
        total_weight = 0
        passed_weight = 0

        for criterion in success_criteria:
            actual_val = actuals.get(criterion.metric, 0)
            passed, details = criterion.evaluate(actual_val)
            evaluations.append(details)
            total_weight += criterion.weight
            if passed:
                passed_weight += criterion.weight

        score = passed_weight / total_weight if total_weight > 0 else 0

        # Run guardrails validators on the outcome
        violations = run_guardrails(output, actuals, evaluations)

        # Generate learning cases from violations
        learning_cases = _generate_learning_from_violations(
            self, violations, output, actuals, evaluations
        )

        return {
            "outcome_score": score,
            "target_met": score >= self.convergence_threshold,
            "evaluations": evaluations,
            "guardrail_violations": [v.__dict__ for v in violations],
            "learning_cases": learning_cases,
            "converged": score >= self.convergence_threshold,
            "measurement_window": measurement_window,
            "period": measurement_window.get("start", "")[:10] if measurement_window else "",
        }

    def run_learning_synthesis(
        self,
        all_stage_outputs: Dict[str, Any],
        outcome_check: Dict[str, Any],
        prior_learning: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """ACT phase: Synthesize experiences, extract patterns, update problem framing."""
        return run_learning_synthesis(
            all_stage_outputs,
            outcome_check,
            prior_learning or self.learning_cases
        )

    def run_pdca_cycle(
        self,
        stage_outputs: Dict[str, Any],
        success_criteria: List[SuccessCriterion],
        measurement_window: Dict[str, str],
        actuals_provider: Callable
    ) -> Dict[str, Any]:
        """
        Run full PDCA cycle for OUTCOME/LEARNING.

        actuals_provider: callable that returns actuals dict for current window
        """
        iteration = 0
        converged = False
        check_result = {}
        learning_result = {}

        # Compress stage outputs once for all iterations
        compressed_stage_outputs = self.compressor.compress_stage_outputs(stage_outputs)

        while self._should_continue(iteration, converged):
            iteration += 1

            # PLAN: Define what we're checking (already in success_criteria)
            plan_data = {
                "iteration": iteration,
                "success_criteria": [c.__dict__ for c in success_criteria],
                "measurement_window": measurement_window,
            }

            # DO: Get actuals from measurement systems
            actuals = actuals_provider(iteration, measurement_window)

            # CHECK: Compare with guardrails
            check_result = self.run_outcome_check(
                stage_outputs.get("output", {}),
                success_criteria,
                measurement_window,
                actuals
            )

            # ACT: Synthesize learning - use compressed context
            learning_result = self.run_learning_synthesis(
                compressed_stage_outputs,
                check_result,
                self.learning_cases
            )

            # Record iteration
            kaizen_iteration = KaizenIteration(
                iteration=iteration,
                phase=KaizenPhase.CHECK.value,
                started_at=datetime.utcnow().isoformat() + "Z",
                completed_at=datetime.utcnow().isoformat() + "Z",
                input_data={"actuals": actuals, "criteria": [c.__dict__ for c in success_criteria]},
                output_data={"check": check_result, "learning": learning_result},
                guardrail_violations=[
                    GuardrailViolation(**v) for v in check_result.get("guardrail_violations", [])
                ],
                learning_generated=len(learning_result.get("experiences", [])) > 0,
                experience_refs=[e["id"] for e in learning_result.get("experiences", [])],
            )
            self.iterations.append(kaizen_iteration)

            converged = check_result.get("converged", False)

            # If not converged, update stage_outputs with learning for next iteration
            if not converged and learning_result.get("redefinitions"):
                # In production, this would trigger a new SACCADE cycle
                stage_outputs["kaizen_feedback"] = {
                    "redefinitions": learning_result["redefinitions"],
                    "insights": learning_result["reusable_insights"],
                    "iteration": iteration,
                }

        return {
            "iterations": [i.__dict__ for i in self.iterations],
            "final_outcome": check_result,
            "final_learning": learning_result,
            "converged": converged,
            "total_iterations": iteration,
        }


def _generate_learning_from_violations(
    kaizen_loop,
    violations: List[GuardrailViolation],
    output: Dict[str, Any],
    actuals: Dict[str, Any],
    evaluations: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Convert guardrail violations into structured learning cases."""
    learning_cases = []

    for v in violations:
        if v.severity in ("error", "warning"):
            case = {
                "case_type": "guardrail_violation",
                "validator": v.validator,
                "severity": v.severity,
                "message": v.message,
                "suggested_fix": v.suggested_fix,
                "learning_ref": v.learning_ref,
                "context": {
                    "output_id": output.get("output_id"),
                    "actuals": actuals,
                    "evaluations": evaluations,
                },
                "recorded_at": datetime.utcnow().isoformat() + "Z",
                "status": "open",  # Will be closed when fix is verified
            }
            learning_cases.append(case)
            kaizen_loop.learning_cases.append(case)

    return learning_cases


def create_default_success_criteria() -> List[SuccessCriterion]:
    """Create default success criteria for marketing interventions."""
    return [
        SuccessCriterion(
            name="pipeline_growth",
            metric="referral_pipeline_qoq",
            target=0.15,
            operator=">=",
            weight=1.0,
            guardrails=["completeness", "variance", "trend"]
        ),
        SuccessCriterion(
            name="cac_reduction",
            metric="paid_cac_delta_pct",
            target=-0.20,
            operator="<=",
            weight=1.0,
            guardrails=["completeness", "variance"]
        ),
        SuccessCriterion(
            name="conversion_rate",
            metric="referral_to_opp_conversion",
            target=0.20,
            operator=">=",
            weight=0.5,
            guardrails=["completeness", "confidence_calibration"]
        ),
    ]


def main():
    """CLI for Kaizen Loop testing."""
    import argparse

    parser = argparse.ArgumentParser(description="Kaizen Loop PDCA engine")
    parser.add_argument("command", choices=["check", "synthesize", "full-cycle"])
    parser.add_argument("--output", help="Output stage JSON")
    parser.add_argument("--actuals", help="Actuals JSON")
    parser.add_argument("--criteria", help="Success criteria JSON")

    args = parser.parse_args()

    if args.command == "check":
        # Quick test
        criteria = create_default_success_criteria()
        actuals = {
            "referral_pipeline_qoq": 0.18,
            "paid_cac_delta_pct": -0.18,
            "referral_to_opp_conversion": 0.24,
        }

        kaizen = KaizenLoop()
        output = {"output_id": "OUT-001", "confidence": 0.9}
        measurement_window = {"start": "2026-11-01", "end": "2026-12-31"}

        result = kaizen.run_outcome_check(output, criteria, measurement_window, actuals)
        print(json.dumps(result, indent=2))

    elif args.command == "full-cycle":
        # Test full PDCA
        criteria = create_default_success_criteria()
        measurement_window = {"start": "2026-11-01", "end": "2026-12-31"}

        def actuals_provider(iter_num, window):
            # Simulate improving actuals over iterations
            base = {
                "referral_pipeline_qoq": 0.10 + iter_num * 0.03,
                "paid_cac_delta_pct": -0.10 - iter_num * 0.03,
                "referral_to_opp_conversion": 0.18 + iter_num * 0.02,
            }
            return base

        stage_outputs = {
            "problem": {"id": "P-0000", "goal": "Test"},
            "strategy": {"objective": "Test strategy", "owner": "Marketing.Brand"},
            "output": {"output_id": "OUT-001", "confidence": 0.9},
            "evidence": {"findings": []},
        }

        kaizen = KaizenLoop(max_iterations=3)
        result = kaizen.run_pdca_cycle(stage_outputs, criteria, measurement_window, actuals_provider)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
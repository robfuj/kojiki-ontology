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
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Import Kaizen compression
import sys
from pathlib import Path
MYCELIUM_ENGINE = Path(__file__).parent
sys.path.insert(0, str(MYCELIUM_ENGINE))
from kaizen_compression import KaizenCompressor, CompressionLevel, build_kaizen_context


class KaizenPhase(Enum):
    PLAN = "plan"
    DO = "do"
    CHECK = "check"
    ACT = "act"


class ValidationResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    LEARNING = "learning"  # Failure that generated a learning case


@dataclass
class SuccessCriterion:
    """A measurable success criterion with guardrails."""
    name: str
    metric: str
    target: float
    operator: str  # ">=", "<=", "==", ">", "<"
    weight: float = 1.0
    guardrails: Optional[List[str]] = None  # Validator names from guardrails hub

    def evaluate(self, actual: float) -> Tuple[bool, Dict[str, Any]]:
        """Evaluate criterion, return (passed, details)."""
        ops = {
            ">=": lambda a, t: a >= t,
            "<=": lambda a, t: a <= t,
            "==": lambda a, t: abs(a - t) < 0.001,
            ">": lambda a, t: a > t,
            "<": lambda a, t: a < t,
        }
        passed = ops.get(self.operator, lambda a, t: False)(actual, self.target)
        return passed, {
            "criterion": self.name,
            "metric": self.metric,
            "target": self.target,
            "actual": actual,
            "operator": self.operator,
            "passed": passed,
            "weight": self.weight,
        }


@dataclass
class GuardrailViolation:
    """A guardrails violation that becomes a learning opportunity."""
    validator: str
    severity: str  # "error", "warning", "info"
    message: str
    suggested_fix: Optional[str] = None
    learning_ref: Optional[str] = None


@dataclass
class KaizenIteration:
    """One PDCA iteration record."""
    iteration: int
    phase: str  # Store as string for JSON serialization
    started_at: str
    completed_at: Optional[str]
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    guardrail_violations: List[GuardrailViolation]
    learning_generated: bool
    experience_refs: List[str]


class KaizenLoop:
    """
    Kaizen Loop for OUTCOME/LEARNING stages.

    Runs PDCA cycles until convergence or max iterations.
    Each cycle generates verifiable learning cases.
    
    Adaptive: Stops early when converged (with min_iterations guard)
    """

    def __init__(self, 
                 max_iterations: int = 3,
                 min_iterations: int = 1,
                 convergence_threshold: float = 0.95,
                 guardrails_config: Optional[Dict[str, Any]] = None,
                 compression_level: CompressionLevel = CompressionLevel.ESSENTIAL):
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
    
    def run_outcome_check(self,
                          output: Dict[str, Any],
                          success_criteria: List[SuccessCriterion],
                          measurement_window: Dict[str, str],
                          actuals: Dict[str, Any]) -> Dict[str, Any]:
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
        violations = self._run_guardrails(output, actuals, evaluations)
        
        # Generate learning cases from violations
        learning_cases = self._generate_learning_from_violations(
            violations, output, actuals, evaluations
        )
        
        return {
            "outcome_score": score,
            "target_met": score >= self.convergence_threshold,
            "evaluations": evaluations,
            "guardrail_violations": [asdict(v) for v in violations],
            "learning_cases": learning_cases,
            "converged": score >= self.convergence_threshold,
            "measurement_window": measurement_window,
            "period": measurement_window.get("start", "")[:10] if measurement_window else "",
        }
    
    def _run_guardrails(self,
                        output: Dict[str, Any],
                        actuals: Dict[str, Any],
                        evaluations: List[Dict[str, Any]]) -> List[GuardrailViolation]:
        """Run guardrails validators that promote learning."""
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
    
    def _generate_learning_from_violations(self,
                                           violations: List[GuardrailViolation],
                                           output: Dict[str, Any],
                                           actuals: Dict[str, Any],
                                           evaluations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
                self.learning_cases.append(case)
        
        return learning_cases
    
    def run_learning_synthesis(self,
                               all_stage_outputs: Dict[str, Any],
                               outcome_check: Dict[str, Any],
                               prior_learning: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        ACT phase: Synthesize experiences, extract patterns, update problem framing.
        
        This is the atomic unit of organizational learning per thesis §III.4.
        """
        # Extract experiences from this cycle
        experiences = self._extract_experiences(all_stage_outputs, outcome_check)
        
        # Synthesize patterns across experiences
        patterns = self._synthesize_patterns(experiences, prior_learning)
        
        # Generate reusable insights
        insights = self._generate_insights(patterns, outcome_check)
        
        # Identify problem redefinitions needed (feed back to SACCADE)
        redefinitions = self._identify_redefinitions(patterns, all_stage_outputs)
        
        # Create learning record
        learning_record = {
            "learning_id": f"KL-{datetime.utcnow().strftime('%Y%m%d')}-{len(self.learning_cases)+1:03d}",
            "cycle_timestamp": datetime.utcnow().isoformat() + "Z",
            "experiences": experiences,
            "patterns": patterns,
            "reusable_insights": insights,
            "redefinitions": redefinitions,
            "outcome_score": outcome_check.get("outcome_score", 0),
            "guardrail_violations": outcome_check.get("guardrail_violations", []),
            "confidence": self._calculate_learning_confidence(experiences, patterns),
            "kaizen_iteration": len(self.iterations) + 1,
            "period": outcome_check.get("period", "") if outcome_check else "",
        }
        
        return learning_record
    
    def _extract_experiences(self,
                             stage_outputs: Dict[str, Any],
                             outcome_check: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract atomic experiences from the full pipeline execution.
        
        Only creates experiences for outcomes that need learning (target not met).
        Successful outcomes don't generate escalations.
        """
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
                "evidence_summary": self._summarize_evidence(stage_outputs.get("evidence", {})),
                "error_classification": self._classify_error(outcome_check, stage_outputs),
                "outcome": "confirmed" if outcome_check.get("target_met") else "invalidated",
                "learning_ref": None,  # Will be set to learning_record.learning_id
                "redefinition": redefinitions[0] if redefinitions else None,
                "agents": strategy.get("owner", "").split(",") if isinstance(strategy.get("owner"), str) else [strategy.get("owner", "unknown")],
                "recorded_at": datetime.utcnow().isoformat() + "Z",
            }
            experiences.append(exp)
        
        return experiences
    
    def _summarize_evidence(self, evidence: Dict[str, Any]) -> str:
        """Create concise evidence summary."""
        findings = evidence.get("findings", [])
        if not findings:
            return "No evidence gathered"
        return "; ".join([f"{f.get('question', '')}: {f.get('extract', '')}" for f in findings[:3]])
    
    def _classify_error(self, outcome_check: Dict[str, Any], stage_outputs: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Classify error type based on outcome check - returns NEURAXIS ErrorClass.

        Deep classification uses full pipeline context to detect:
        - L0_execution: Information/Execution errors (missing data, variance)
        - L1_reasoning: Reasoning errors (confidence miscalibration)
        - L2_problem_representation: Assumption errors (invalidated assumptions)
        - L3_ontology: Model/representation errors (wrong mental model)
        - L4_meta_strategy: Meta errors (conflicting strategies, governance needed)
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
            if self._detect_meta_strategy_conflict(stage_outputs):
                return "Meta error"  # Maps to L4_META_STRATEGY

            # L2: Assumption invalidation detected
            if self._detect_assumption_invalidation(stage_outputs):
                return "Assumption error"  # Maps to L2_PROBLEM_REPRESENTATION

            # L3: Model/representation mismatch
            if self._detect_model_representation_gap(stage_outputs):
                return "Model/representation error"  # Maps to L3_ONTOLOGY

        return "Execution error"  # Default to L0
    
    def _detect_assumption_invalidation(self, stage_outputs: Dict[str, Any]) -> bool:
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
    
    def _detect_model_representation_gap(self, stage_outputs: Dict[str, Any]) -> bool:
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
        if hasattr(self, 'learning_cases') and self.learning_cases:
            failed_strategies = [lc for lc in self.learning_cases 
                               if lc.get("outcome") == "invalidated"]
            if len(failed_strategies) >= 2:
                # Repeated failure suggests wrong mental model
                return True
        
        return False
    
    def _detect_meta_strategy_conflict(self, stage_outputs: Dict[str, Any]) -> bool:
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
    
    def _synthesize_patterns(self,
                             experiences: List[Dict[str, Any]],
                             prior_learning: Optional[List[Dict[str, Any]]] = None) -> List[str]:
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
    
    def _generate_insights(self,
                           patterns: List[str],
                           outcome_check: Dict[str, Any]) -> List[str]:
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
    
    def _identify_redefinitions(self,
                                patterns: List[str],
                                stage_outputs: Dict[str, Any]) -> List[Dict[str, Any]]:
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
    
    def _calculate_learning_confidence(self,
                                       experiences: List[Dict[str, Any]],
                                       patterns: List[str]) -> float:
        """Calculate confidence in the learning synthesis."""
        if not experiences:
            return 0.0
        
        # Base confidence on number of experiences and pattern consistency
        exp_factor = min(len(experiences) / 5.0, 1.0)  # Up to 5 experiences
        pattern_factor = min(len(patterns) / 3.0, 1.0)  # Up to 3 patterns
        
        return round((exp_factor + pattern_factor) / 2, 2)
    
    def run_pdca_cycle(self,
                       stage_outputs: Dict[str, Any],
                       success_criteria: List[SuccessCriterion],
                       measurement_window: Dict[str, str],
                       actuals_provider) -> Dict[str, Any]:
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
                "success_criteria": [asdict(c) for c in success_criteria],
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
                input_data={"actuals": actuals, "criteria": [asdict(c) for c in success_criteria]},
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
            "iterations": [asdict(i) for i in self.iterations],
            "final_outcome": check_result,
            "final_learning": learning_result,
            "converged": converged,
            "total_iterations": iteration,
        }


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
"""
Kaizen Compression - Token-efficient context for Kaizen Loop iterations.

Compresses full stage outputs to Kaizen-essential fields only.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class CompressionLevel(str, Enum):
    FULL = "full"           # All stage outputs (original)
    ESSENTIAL = "essential" # Only Kaizen-critical fields
    MINIMAL = "minimal"     # Problem ID + criteria + window only


@dataclass
class KaizenCompressor:
    """Compresses stage outputs for Kaizen Loop consumption."""
    
    level: CompressionLevel = CompressionLevel.ESSENTIAL
    
    def compress_stage_outputs(self, stage_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Compress full stage outputs to Kaizen-essential context."""
        
        if self.level == CompressionLevel.FULL:
            return stage_outputs
        
        compressed = {}
        
        # Problem: only ID and goal
        if "problem" in stage_outputs:
            p = stage_outputs["problem"]
            compressed["problem"] = {
                "problem_id": p.get("problem_id"),
                "goal": p.get("goal"),
                "context": p.get("context", {}),
            }
        
        # Strategy: only ID, success_criteria, decision_rights, objective
        if "strategy" in stage_outputs:
            s = stage_outputs["strategy"]
            compressed["strategy"] = {
                "strategy_id": s.get("strategy_id"),
                "objective": s.get("objective"),
                "success_criteria": s.get("success_criteria", []),
                "decision_rights": s.get("decision_rights", {}),
                "escalation_conditions": s.get("escalation_conditions", []),
            }
        
        # Output: only ID, measurement_window
        if "output" in stage_outputs:
            o = stage_outputs["output"]
            compressed["output"] = {
                "output_id": o.get("output_id"),
                "measurement_window": o.get("measurement_window"),
            }
        
        # Evidence: only findings count + IDs (for traceability)
        if "evidence" in stage_outputs:
            e = stage_outputs["evidence"]
            findings = e.get("findings", [])
            compressed["evidence"] = {
                "finding_count": len(findings),
                "finding_ids": [f.get("finding_id") for f in findings],
            }
        
        # Interpretation: only confidence + key synthesis
        if "interpretation" in stage_outputs:
            i = stage_outputs["interpretation"]
            compressed["interpretation"] = {
                "confidence": i.get("confidence"),
                "key_drivers": i.get("key_drivers", [])[:3],  # Max 3
            }
        
        # Deck: only reference
        if "deck" in stage_outputs:
            d = stage_outputs["deck"]
            compressed["deck"] = {"deck_ref": d.get("deck_ref") if isinstance(d, dict) else str(d)}
        
        return compressed
    
    def compress_guardrail_violations(self, violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Compress guardrail violations to essential fields."""
        if self.level == CompressionLevel.FULL:
            return violations
        
        compressed = []
        for v in violations:
            item = {
                "validator": v.get("validator"),
                "severity": v.get("severity"),
                "metric": v.get("metric") or self._extract_metric(v.get("message", "")),
            }
            if self.level == CompressionLevel.ESSENTIAL:
                item["variance_pct"] = self._extract_variance(v.get("message", ""))
            compressed.append(item)
        return compressed
    
    def _extract_metric(self, message: str) -> Optional[str]:
        """Extract metric name from violation message."""
        import re
        # Pattern: "High variance on {metric}: ..."
        match = re.search(r"on\s+(\w+):", message)
        if match:
            return match.group(1)
        return None
    
    def _extract_variance(self, message: str) -> Optional[float]:
        """Extract variance percentage from violation message."""
        import re
        # Pattern: "... {X}% from target"
        match = re.search(r"(\d+\.?\d*)%\s+from\s+target", message)
        if match:
            return float(match.group(1)) / 100
        return None


# Kaizen-specific context builder
def build_kaizen_context(
    stage_outputs: Dict[str, Any],
    success_criteria: List[Any],
    measurement_window: Dict[str, str],
    actuals: Dict[str, Any],
    iteration: int = 1,
    prior_learning: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Build minimal Kaizen context for an iteration.
    
    Only includes what Kaizen actually needs:
    - Problem goal (what we're solving)
    - Success criteria with weights (what to measure)
    - Current actuals (what happened)
    - Prior iteration results (for convergence)
    - Prior learning patterns (for synthesis)
    """
    compressor = KaizenCompressor(CompressionLevel.ESSENTIAL)
    
    context = {
        "iteration": iteration,
        "measurement_window": measurement_window,
        "actuals": actuals,
        "stage_outputs": compressor.compress_stage_outputs(stage_outputs),
    }
    
    # Add criteria as structured data (already minimal)
    context["success_criteria"] = [
        {
            "name": c.name,
            "metric": c.metric,
            "target": c.target,
            "operator": c.operator,
            "weight": c.weight,
        }
        for c in success_criteria
    ]
    
    # Prior learning - only patterns and insights, not full experiences
    if prior_learning:
        context["prior_learning"] = {
            "patterns": [l.get("patterns", []) for l in prior_learning if l.get("patterns")],
            "insights": [l.get("reusable_insights", []) for l in prior_learning if l.get("reusable_insights")],
            "redefinitions": [l.get("redefinitions", []) for l in prior_learning if l.get("redefinitions")],
        }
    
    return context


if __name__ == "__main__":
    # Test compression
    sample_stage_outputs = {
        "problem": {
            "problem_id": "P-ABC123",
            "goal": "Increase referral pipeline QoQ",
            "context": {"budget": 100000, "timeline": "Q4"},
            "raw_record": {"lots": "of", "raw": "data"},
        },
        "strategy": {
            "strategy_id": "STRAT-001",
            "objective": "Shift 30% paid budget to referral",
            "success_criteria": [
                {"name": "pipeline_growth", "metric": "referral_pipeline_qoq", "target": 0.15, "operator": ">=", "weight": 1.0},
                {"name": "cac_reduction", "metric": "paid_cac_delta_pct", "target": -0.20, "operator": "<=", "weight": 1.0},
            ],
            "decision_rights": {"own": "Marketing.Growth", "consult": ["Sales"], "inform": ["Exec"]},
            "escalation_conditions": ["pipeline < 5% after 30 days"],
            "rationale": "Long detailed rationale here...",
        },
        "output": {
            "output_id": "OUT-001",
            "measurement_window": {"start": "2026-11-01", "end": "2026-12-31"},
            "intervention_design": "Detailed design...",
        },
        "evidence": {
            "findings": [
                {"finding_id": "FE-001", "question": "Q1", "answer": "A1", "source": "S1", "confidence": 0.9, "retrieval_state": "RETRIEVED", "coverage_limits": "L1", "sufficiency": "SUFFICIENT"},
                {"finding_id": "FE-002", "question": "Q2", "answer": "A2", "source": "S2", "confidence": 0.8, "retrieval_state": "RETRIEVED", "coverage_limits": "L2", "sufficiency": "SUFFICIENT"},
            ]
        },
        "interpretation": {
            "confidence": 0.85,
            "key_drivers": ["Referral conversion 3x paid", "Incentive program ROI positive", "Cross-dept alignment"],
            "synthesis": "Long synthesis text...",
        },
    }
    
    compressor = KaizenCompressor(CompressionLevel.ESSENTIAL)
    compressed = compressor.compress_stage_outputs(sample_stage_outputs)
    
    import json
    print("=== COMPRESSED (ESSENTIAL) ===")
    print(json.dumps(compressed, indent=2))
    
    print("\n=== MINIMAL ===")
    compressor_min = KaizenCompressor(CompressionLevel.MINIMAL)
    print(json.dumps(compressor_min.compress_stage_outputs(sample_stage_outputs), indent=2))
    
    print("\n=== FULL (original) ===")
    compressor_full = KaizenCompressor(CompressionLevel.FULL)
    print(json.dumps(compressor_full.compress_stage_outputs(sample_stage_outputs), indent=2))
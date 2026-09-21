#!/usr/bin/env python3
"""
Kaizen Types - Core dataclasses and enums for Kaizen Loop.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum


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

    def evaluate(self, actual: float) -> tuple[bool, Dict[str, Any]]:
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
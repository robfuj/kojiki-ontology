"""
SACCADE Stage - A priori problem framing before EVIDENCE gathering.
"""

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict


@dataclass
class Problem:
    """Problem object at version P-0000."""
    id: str
    goal: str
    constraints: List[str]
    assumptions: List[str]
    unknowns: List[str]
    version: int = 0


class SACCADE:
    """
    SACCADE: a priori problem-framing stage.
    
    Several fast, bounded passes over the question — is the goal actually stated?
    are the constraints? the assumptions? the unknowns? — before EVIDENCE is ever dispatched.
    
    Authority: what is the actual question this decision needs to answer?
    Must not become: EVIDENCE (never retrieves/reads sources) or STRATEGY (never proposes interventions).
    """
    
    def __init__(self, max_passes: int = 4, convergence_epsilon: float = 0.05):
        self.max_passes = max_passes
        self.convergence_epsilon = convergence_epsilon
        self.history: List[Problem] = []
        
        # Caching: Problem objects keyed by (raw_record_hash, context_hash)
        self._problem_cache: Dict[str, Tuple[Problem, List[Problem]]] = {}
        self._cache_ttl_hours: int = 24
    
    def draft_problem(self, raw_record: Dict[str, Any]) -> Problem:
        """Draft initial problem from raw record."""
        return Problem(
            id="P-0000",
            goal=raw_record.get('goal', ''),
            constraints=raw_record.get('constraints', []),
            assumptions=raw_record.get('assumptions', []),
            unknowns=raw_record.get('unknowns', []),
            version=0
        )
    
    def check_completeness(self, problem: Problem) -> List[str]:
        """Check for empty/contradictory fields."""
        gaps = []
        if not problem.goal or not problem.goal.strip():
            gaps.append("goal")
        if not problem.constraints:
            gaps.append("constraints")
        if not problem.assumptions:
            gaps.append("assumptions")
        if not problem.unknowns:
            gaps.append("unknowns")
        return gaps
    
    def refine_problem(self, problem: Problem, gaps: List[str], pass_num: int = 0) -> Problem:
        """
        Refine problem by addressing gaps AND sharpening existing fields.
        
        Each pass should narrow the goal, add specificity to constraints,
        surface hidden assumptions, and identify deeper unknowns.
        In production, this would invoke an LLM to sharpen the problem.
        """
        raw_record = getattr(self, '_last_raw_record', {})
        
        new_goal = problem.goal
        new_constraints = list(problem.constraints)
        new_assumptions = list(problem.assumptions)
        new_unknowns = list(problem.unknowns)
        
        # Phase 1: Fill explicit gaps (from check_completeness)
        if "goal" in gaps:
            if raw_record.get('goal'):
                new_goal = raw_record['goal']
            elif raw_record.get('objective'):
                new_goal = raw_record['objective']
            elif raw_record.get('request'):
                new_goal = f"Address: {raw_record['request']}"
            else:
                new_goal = "Define the objective for this decision"
        
        if "constraints" in gaps:
            if raw_record.get('constraints'):
                new_constraints = raw_record['constraints'] if isinstance(raw_record['constraints'], list) else [raw_record['constraints']]
            elif raw_record.get('budget'):
                new_constraints.append(f"Budget: {raw_record['budget']}")
            elif raw_record.get('deadline'):
                new_constraints.append(f"Deadline: {raw_record['deadline']}")
            else:
                new_constraints.append("No explicit constraints provided")
        
        if "assumptions" in gaps:
            if raw_record.get('assumptions'):
                new_assumptions = raw_record['assumptions'] if isinstance(raw_record['assumptions'], list) else [raw_record['assumptions']]
            elif raw_record.get('context'):
                new_assumptions.append(f"Context: {raw_record['context']}")
            else:
                new_assumptions.append("Stakeholders have necessary authority to act")
        
        if "unknowns" in gaps:
            if raw_record.get('unknowns'):
                new_unknowns = raw_record['unknowns'] if isinstance(raw_record['unknowns'], list) else [raw_record['unknowns']]
            elif raw_record.get('questions'):
                new_unknowns = raw_record['questions'] if isinstance(raw_record['questions'], list) else [raw_record['questions']]
            else:
                new_unknowns.append("What evidence is needed to validate the goal?")
        
        # Phase 2: Iterative sharpening (each pass adds depth even without explicit gaps)
        # pass_num is 0-indexed: 0 = first refinement, 1 = second, etc.
        if pass_num == 0:
            # First refinement: Make goal more specific and measurable
            if new_goal and not any(kw in new_goal.lower() for kw in ['by ', 'to ', '%', 'increase', 'decrease', 'reduce', 'improve']):
                if not any(c.isdigit() for c in new_goal):
                    new_goal += " (measurable target TBD)"
        
        if pass_num == 1:
            # Second refinement: Add implicit constraints from context
            if raw_record.get('stakeholders'):
                stakeholders = raw_record['stakeholders']
                if isinstance(stakeholders, list):
                    for s in stakeholders:
                        new_constraints.append(f"Requires sign-off from: {s}")
                else:
                    new_constraints.append(f"Requires sign-off from: {stakeholders}")
            if raw_record.get('regulatory'):
                new_constraints.append(f"Regulatory: {raw_record['regulatory']}")
        
        if pass_num == 2:
            # Third refinement: Surface deeper assumptions
            new_assumptions.append("Current data quality sufficient for decision")
            new_assumptions.append("No external dependencies blocking execution")
            if raw_record.get('dependencies'):
                deps = raw_record['dependencies']
                if isinstance(deps, list):
                    for d in deps:
                        new_assumptions.append(f"Dependency available: {d}")
                else:
                    new_assumptions.append(f"Dependency available: {deps}")
        
        if pass_num >= 3:
            # Fourth+ refinement: Identify specific evidence needs
            new_unknowns.append("What is the baseline metric before intervention?")
            new_unknowns.append("What are the leading indicators of success/failure?")
            if raw_record.get('metrics'):
                metrics = raw_record['metrics']
                if isinstance(metrics, list):
                    for m in metrics:
                        new_unknowns.append(f"Current value of {m}?")
                else:
                    new_unknowns.append(f"Current value of {metrics}?")
        
        new_problem = Problem(
            id=f"P-{problem.version+1:04d}",
            goal=new_goal,
            constraints=new_constraints,
            assumptions=new_assumptions,
            unknowns=new_unknowns,
            version=problem.version + 1
        )
        return new_problem
    
    def delta(self, problem1: Problem, problem2: Problem) -> float:
        """Compute difference between two problems (0.0 to 1.0)."""
        # Simple heuristic: count field differences
        fields = ['goal', 'constraints', 'assumptions', 'unknowns']
        differences = 0
        total = 0
        
        for field in fields:
            val1 = getattr(problem1, field)
            val2 = getattr(problem2, field)
            total += 1
            if isinstance(val1, list) and isinstance(val2, list):
                if set(val1) != set(val2):
                    differences += 1
            elif val1 != val2:
                differences += 1
        
        return differences / total if total > 0 else 0.0
    
    def run(self, dispatch: Dict[str, Any]) -> Tuple[Problem, List[Problem]]:
        """
        Run SACCADE on a dispatch.
        
        Returns the final problem and full history (append-only, never discarded).
        """
        raw_record = dispatch.get('raw_record', {})
        context = dispatch.get('context', {})
        
        # Generate cache key from raw_record + context
        cache_input = json.dumps({"raw_record": raw_record, "context": context}, sort_keys=True)
        cache_key = hashlib.sha256(cache_input.encode()).hexdigest()[:32]
        
        # Check cache
        if cache_key in self._problem_cache:
            cached_problem, cached_history = self._problem_cache[cache_key]
            # Check TTL
            # In production, would check timestamp; for now, always use cache if present
            print(f"  [SACCADE CACHE HIT] Reusing cached problem {cached_problem.id}")
            return cached_problem, cached_history
        
        # Store raw_record for refine_problem to use
        self._last_raw_record = raw_record
        
        problem = self.draft_problem(raw_record)
        self.history = [problem]
        
        for i in range(self.max_passes):
            gaps = self.check_completeness(problem)
            # Always refine on each pass (up to max_passes) - convergence check stops early
            problem = self.refine_problem(problem, gaps, pass_num=i)
            self.history.append(problem)
            
            # Check convergence (after at least 2 versions exist)
            if len(self.history) >= 2:
                if self.delta(self.history[-1], self.history[-2]) < self.convergence_epsilon:
                    break  # Diminishing returns
        
        # Cache the result
        self._problem_cache[cache_key] = (problem, self.history)
        
        return problem, self.history
    
    def validate_output(self, problem: Problem) -> bool:
        """Validate SACCADE output doesn't violate boundaries.
        
        Enforces:
        - No strategy-like language (recommend, propose, intervention, action plan, implement, execute)
        - No evidence-like language (source:, citation:, reference:, data shows, study indicates, according to)
        - Goal must be stated and non-empty
        - At least one constraint, assumption, and unknown present
        """
        # Must not contain recommendations (that's STRATEGY)
        strategy_keywords = ['recommend', 'propose', 'intervention', 'action plan', 'implement', 'execute']
        # Must not contain evidence references (that's EVIDENCE)
        evidence_keywords = ['source:', 'citation:', 'reference:', 'data shows', 'study indicates', 'according to']
        
        check_fields = [problem.goal] + problem.constraints + problem.assumptions + problem.unknowns
        text = ' '.join(check_fields).lower()
        
        for kw in strategy_keywords:
            if kw in text:
                return False
        for kw in evidence_keywords:
            if kw in text:
                return False
        
        # Enforce minimum completeness
        if not problem.goal or not problem.goal.strip():
            return False
        
        # Goal must have measurable intent (numbers, %, increase/decrease, target, by date)
        measurable_indicators = ['%', 'increase', 'decrease', 'reduce', 'improve', 'target', 'by ', 'to ']
        has_measurable = any(ind in problem.goal.lower() for ind in measurable_indicators) or any(c.isdigit() for c in problem.goal)
        if not has_measurable:
            return False
        
        if not problem.constraints:
            return False
        if not problem.assumptions:
            return False
        if not problem.unknowns:
            return False
        
        return True


def main():
    """CLI for SACCADE operations."""
    import sys
    
    saccade = SACCADE()
    
    if len(sys.argv) < 2:
        print("Usage: python saccade.py <command> [args]")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "run":
        if len(sys.argv) < 3:
            print("Usage: python saccade.py run <dispatch_json>")
            return
        dispatch = json.loads(sys.argv[2])
        problem, history = saccade.run(dispatch)
        print(f"Final problem: {asdict(problem)}")
        print(f"History length: {len(history)}")
        for i, p in enumerate(history):
            print(f"  Pass {i}: {p.id} - goal='{p.goal[:50]}...'")
    
    elif cmd == "validate":
        if len(sys.argv) < 3:
            print("Usage: python saccade.py validate <problem_json>")
            return
        prob_data = json.loads(sys.argv[2])
        problem = Problem(**prob_data)
        valid = saccade.validate_output(problem)
        print(f"Valid: {valid}")


if __name__ == "__main__":
    main()
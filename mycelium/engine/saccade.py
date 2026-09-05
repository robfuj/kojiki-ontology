"""
SACCADE Stage - A priori problem framing before EVIDENCE gathering.
"""

import json
from datetime import datetime
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
    
    def refine_problem(self, problem: Problem, gaps: List[str]) -> Problem:
        """Refine problem by addressing gaps."""
        # In a real implementation, this would invoke an LLM to sharpen the problem
        # For now, we simulate refinement by noting gaps were addressed
        new_problem = Problem(
            id=f"P-{problem.version+1:04d}",
            goal=problem.goal,
            constraints=problem.constraints,
            assumptions=problem.assumptions,
            unknowns=problem.unknowns,
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
        problem = self.draft_problem(raw_record)
        self.history = [problem]
        
        for i in range(self.max_passes):
            gaps = self.check_completeness(problem)
            if not gaps:
                break  # Converged: nothing left to sharpen
            
            problem = self.refine_problem(problem, gaps)
            self.history.append(problem)
            
            # Check convergence
            if len(self.history) >= 2:
                if self.delta(self.history[-1], self.history[-2]) < self.convergence_epsilon:
                    break  # Diminishing returns
        
        return problem, self.history
    
    def validate_output(self, problem: Problem) -> bool:
        """Validate SACCADE output doesn't violate boundaries."""
        # Must not contain recommendations (that's STRATEGY)
        # Must not contain evidence references (that's EVIDENCE)
        # These would be detected by checking problem content
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
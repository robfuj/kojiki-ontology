"""
Finance Accounting Specialist
Coordinates Budget, Treasury, Tax, FP&A, Accounting teams
"""

from engine.kojiki_core import Specialist, StageConfig
from pathlib import Path


class FinanceAccountingSpecialist(Specialist):
    """Finance Department Head - coordinates Budget, Treasury, Tax, FP&A, Accounting teams."""
    
    @property
    def name(self) -> str:
        return "finance-accounting"
    
    @property
    def agent_prefix(self) -> str:
        return "Finance"
    
    @property
    def decision_rights_node(self) -> str:
        return "Finance.Budget"
    
    @property
    def stages(self) -> dict:
        base = Path(__file__).parent
        return {
            "saccade": StageConfig(
                name="saccade",
                prompt=str(base / "prompts" / "01-saccade.md"),
                schema=str(base / "schemas" / "saccade_problem.json"),
                tools=[],
                inputs_allowed=["raw_record", "dept_head", "objective", "description", "team_nodes", "parent_objective"],
            ),
            "evidence": StageConfig(
                name="evidence",
                prompt=str(base / "prompts" / "02-evidence.md"),
                schema=str(base / "schemas" / "evidence_findings.json"),
                tools=[],
                inputs_allowed=["dept_head", "team_nodes", "objective"],
            ),
            "interpretation": StageConfig(
                name="interpretation",
                prompt=str(base / "prompts" / "03-interpretation.md"),
                schema=str(base / "schemas" / "interpretation_diagnosis.json"),
                tools=[],
                inputs_allowed=["evidence", "objective", "team_nodes"],
            ),
            "strategy": StageConfig(
                name="strategy",
                prompt=str(base / "prompts" / "04-strategy.md"),
                schema=str(base / "schemas" / "strategy_team_okrs.json"),
                tools=[],
                inputs_allowed=["problem", "evidence", "interpretation", "dept_objective", "team_nodes", "dept_head"],
            ),
            "output": StageConfig(
                name="output",
                prompt=str(base / "prompts" / "05-output.md"),
                schema=str(base / "schemas" / "output_intervention.json"),
                tools=[],
                inputs_allowed=["accepted_strategy"],
            ),
            "deck": StageConfig(
                name="deck",
                prompt=str(base / "prompts" / "06-deck.md"),
                schema=str(base / "schemas" / "deck_request.json"),
                tools=[],
                inputs_allowed=["accepted_output"],
            ),
            "outcome": StageConfig(
                name="outcome",
                prompt=str(base / "prompts" / "07-outcome.md"),
                schema=str(base / "schemas" / "outcome.json"),
                tools=[],
                inputs_allowed=["accepted_output", "deck_ref"],
            ),
            "learning": StageConfig(
                name="learning",
                prompt=str(base / "prompts" / "08-learning.md"),
                schema=str(base / "schemas" / "learning.json"),
                tools=[],
                inputs_allowed=["accepted_problem", "accepted_evidence", "accepted_interpretation", "accepted_strategy", "accepted_output", "accepted_outcome", "accepted_deck"],
            ),
        }


if __name__ == "__main__":
    # Quick test
    specialist = FinanceAccountingSpecialist()
    print(f"Name: {specialist.name}")
    print(f"Agent Prefix: {specialist.agent_prefix}")
    print(f"Decision Rights Node: {specialist.decision_rights_node}")
    print(f"Stages: {list(specialist.stages.keys())}")
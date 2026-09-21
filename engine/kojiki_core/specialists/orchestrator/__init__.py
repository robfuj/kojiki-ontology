#!/usr/bin/env python3
"""
Orchestrator Specialist — Generic decomposition engine.

This specialist is used by the Orchestrator for:
1. SACCADE: Frame the raw problem
2. EVIDENCE: Gather cross-department context
3. INTERPRETATION: Analyze cross-department gaps
4. STRATEGY: Decompose into department-level objectives
"""

from pathlib import Path
from engine.kojiki_core import Specialist, StageConfig


class OrchestratorSpecialist(Specialist):
    """Specialist for Orchestrator coordination and decomposition."""

    @property
    def name(self) -> str:
        return "orchestrator"

    @property
    def agent_prefix(self) -> str:
        return "Orchestrator"

    @property
    def decision_rights_node(self) -> str:
        return "Finance"  # Orchestrator reports to Finance (corporate)

    @property
    def stages(self) -> dict[str, StageConfig]:
        base_path = Path(__file__).parent / "prompts"
        schemas_path = Path(__file__).parent / "schemas"
        return {
            "saccade": StageConfig(
                name="saccade",
                prompt=str(base_path / "01-saccade-cos.md"),
                schema=str(schemas_path / "saccade_problem.json"),
                inputs_allowed=["raw_record", "task_id"],
                tools=[]
            ),
            "evidence": StageConfig(
                name="evidence",
                prompt=str(base_path / "02-evidence-cos.md"),
                schema=str(schemas_path / "evidence_findings.json"),
                inputs_allowed=["raw_record", "task_id", "dept_head", "accepted_problem"],
                tools=[]
            ),
            "interpretation": StageConfig(
                name="interpretation",
                prompt=str(base_path / "03-interpretation-cos.md"),
                schema=str(schemas_path / "interpretation_diagnosis.json"),
                inputs_allowed=["evidence", "accepted_problem", "task_id"],
                tools=[]
            ),
            "strategy": StageConfig(
                name="strategy",
                prompt=str(base_path / "04-strategy-cos.md"),
                schema=str(schemas_path / "strategy_team_okrs.json"),
                inputs_allowed=["accepted_interpretation", "accepted_evidence", "accepted_problem", "dept_head", "task_id"],
                tools=[]
            ),
            "output": StageConfig(
                name="output",
                prompt=str(base_path / "05-output-cos.md"),
                schema=str(schemas_path / "output_intervention.json"),
                inputs_allowed=["accepted_strategy"],
                tools=[]
            ),
            "deck": StageConfig(
                name="deck",
                prompt=str(base_path / "06-deck-cos.md"),
                schema=str(schemas_path / "deck_request.json"),
                inputs_allowed=["accepted_output"],
                tools=[]
            ),
            "outcome": StageConfig(
                name="outcome",
                prompt=str(base_path / "07-outcome-cos.md"),
                schema=str(schemas_path / "outcome.json"),
                inputs_allowed=["accepted_deck"],
                tools=[]
            ),
            "learning": StageConfig(
                name="learning",
                prompt=str(base_path / "08-learning-cos.md"),
                schema=str(schemas_path / "learning.json"),
                inputs_allowed=["accepted_outcome"],
                tools=[]
            )
        }

    def get_prompt(self, stage_name: str) -> str:
        config = self.stages.get(stage_name)
        if not config or not config.prompt:
            return f"# {stage_name.upper()} Stage\n\nExecute {stage_name} transformation."
        prompt_path = Path(config.prompt)
        if prompt_path.exists():
            return prompt_path.read_text()
        return f"# {stage_name.upper()} Stage\n\nExecute {stage_name} transformation."

    def get_schema(self, stage_name: str):
        config = self.stages.get(stage_name)
        if not config or not config.schema:
            return None
        import json
        schema_path = Path(config.schema)
        if schema_path.exists():
            return json.loads(schema_path.read_text())
        return None


# Export for dynamic loading
Specialist = OrchestratorSpecialist
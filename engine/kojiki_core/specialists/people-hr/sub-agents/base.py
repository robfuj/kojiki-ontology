#!/usr/bin/env python3
"""
Base class for people & comms sub-specialists.
"""

from kojiki.core import Specialist, StageConfig
from typing import Dict, Any, List
from pathlib import Path


class PeopleSubSpecialist(Specialist):
    """Base class for people & comms sub-specialists."""
    
    SUB_AGENT_NAME: str = ""
    SUB_AGENT_DESCRIPTION: str = ""
    
    @property
    def name(self) -> str:
        return f"people-hr.{self.SUB_AGENT_NAME}"
    
    @property
    def agent_prefix(self) -> str:
        return f"people.{self.SUB_AGENT_NAME}"
    
    @property
    def decision_rights_node(self) -> str:
        return f"People.{self.SUB_AGENT_NAME.replace('-', ' ').title().replace(' ', '')}"
    
    @property
    def stages(self) -> Dict[str, StageConfig]:
        base_path = Path(__file__).parent
        
        return {
            "saccade": StageConfig(
                name="saccade",
                prompt=str(base_path / "prompts" / "01-saccade.md"),
                tools=[],
                schema=str(base_path / "schemas" / "saccade_problem.json"),
            ),
            "evidence": StageConfig(
                name="evidence",
                prompt=str(base_path / "prompts" / "02-evidence.md"),
                tools=[],
                schema=str(base_path / "schemas" / "evidence_findings.json"),
            ),
            "interpretation": StageConfig(
                name="interpretation",
                prompt=str(base_path / "prompts" / "03-interpretation.md"),
                tools=[],
                schema=str(base_path / "schemas" / "interpretation.json"),
            ),
            "strategy": StageConfig(
                name="strategy",
                prompt=str(base_path / "prompts" / "04-strategy.md"),
                tools=[],
                schema=str(base_path / "schemas" / "strategy.json"),
            ),
            "output": StageConfig(
                name="output",
                prompt=str(base_path / "prompts" / "05-output.md"),
                tools=[],
                schema=str(base_path / "schemas" / "output.json"),
            ),
            "learning": StageConfig(
                name="learning",
                prompt=str(base_path / "prompts" / "08-learning.md"),
                tools=[],
                schema=str(base_path / "schemas" / "learning.json"),
            ),
        }
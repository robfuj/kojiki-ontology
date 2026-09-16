#!/usr/bin/env python3
"""Agents Orchestrator - Multi-agent coordination, workflow management."""

from ..base import AISubSpecialist


class AgentsOrchestratorSpecialist(AISubSpecialist):
    SUB_AGENT_NAME = "agents-orchestrator"
    SUB_AGENT_DESCRIPTION = "Multi-agent coordination, workflow management, complex projects requiring multiple agent coordination"


specialist = AgentsOrchestratorSpecialist()

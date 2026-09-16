#!/usr/bin/env python3
"""Multi-Agent Systems Architect - Multi-agent pipeline design & governance."""

from ..base import AISubSpecialist


class MultiAgentArchitectSpecialist(AISubSpecialist):
    SUB_AGENT_NAME = "multi-agent-architect"
    SUB_AGENT_DESCRIPTION = "Multi-agent pipeline design & governance, topology, context, trust, failure recovery"


specialist = MultiAgentArchitectSpecialist()

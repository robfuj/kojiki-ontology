#!/usr/bin/env python3
"""AI Engineer - ML models, deployment, AI integration."""

from ..base import EngineeringSubSpecialist


class AIEngineerSpecialist(EngineeringSubSpecialist):
    SUB_AGENT_NAME = "ai-engineer"
    SUB_AGENT_DESCRIPTION = "ML models, deployment, AI integration, data pipelines"


specialist = AIEngineerSpecialist()

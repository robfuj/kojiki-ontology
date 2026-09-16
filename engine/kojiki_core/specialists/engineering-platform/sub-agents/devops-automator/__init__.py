#!/usr/bin/env python3
"""DevOps Automator - CI/CD, infrastructure automation, cloud ops."""

from ..base import EngineeringSubSpecialist


class DevOpsAutomatorSpecialist(EngineeringSubSpecialist):
    SUB_AGENT_NAME = "devops-automator"
    SUB_AGENT_DESCRIPTION = "CI/CD, infrastructure automation, cloud ops, pipeline development"


specialist = DevOpsAutomatorSpecialist()

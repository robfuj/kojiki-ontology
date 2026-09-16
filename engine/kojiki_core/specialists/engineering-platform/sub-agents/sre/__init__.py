#!/usr/bin/env python3
"""SRE - SLOs, error budgets, observability, chaos engineering."""

from ..base import EngineeringSubSpecialist


class SRESpecialist(EngineeringSubSpecialist):
    SUB_AGENT_NAME = "sre"
    SUB_AGENT_DESCRIPTION = "SLOs, error budgets, observability, chaos engineering"


specialist = SRESpecialist()

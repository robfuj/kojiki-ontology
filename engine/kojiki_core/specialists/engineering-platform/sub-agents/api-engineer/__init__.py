#!/usr/bin/env python3
"""API Platform Engineer - API gateways & platforms."""

from ..base import EngineeringSubSpecialist


class APIEngineerSpecialist(EngineeringSubSpecialist):
    SUB_AGENT_NAME = "api-engineer"
    SUB_AGENT_DESCRIPTION = "API gateways & platforms, gateway design, versioning, rate limiting"


specialist = APIEngineerSpecialist()

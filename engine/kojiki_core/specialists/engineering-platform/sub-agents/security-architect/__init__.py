#!/usr/bin/env python3
"""Security Architect - Threat modeling, secure-by-design."""

from ..base import EngineeringSubSpecialist


class SecurityArchitectSpecialist(EngineeringSubSpecialist):
    SUB_AGENT_NAME = "security-architect"
    SUB_AGENT_DESCRIPTION = "Threat modeling, secure-by-design, trust boundaries, defense-in-depth"


specialist = SecurityArchitectSpecialist()

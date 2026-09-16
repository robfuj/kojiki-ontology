#!/usr/bin/env python3
"""Reality Checker - Evidence-based certification, quality gates."""

from ..base import EngineeringSubSpecialist


class RealityCheckerSpecialist(EngineeringSubSpecialist):
    SUB_AGENT_NAME = "reality-checker"
    SUB_AGENT_DESCRIPTION = "Evidence-based certification, quality gates, production readiness"


specialist = RealityCheckerSpecialist()

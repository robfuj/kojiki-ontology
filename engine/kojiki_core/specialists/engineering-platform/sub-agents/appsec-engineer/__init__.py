#!/usr/bin/env python3
"""Application Security Engineer - SDLC security, SAST/DAST, secure code review."""

from ..base import EngineeringSubSpecialist


class AppSecEngineerSpecialist(EngineeringSubSpecialist):
    SUB_AGENT_NAME = "appsec-engineer"
    SUB_AGENT_DESCRIPTION = "SDLC security, SAST/DAST, secure code review, code-level vulnerabilities"


specialist = AppSecEngineerSpecialist()

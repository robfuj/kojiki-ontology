#!/usr/bin/env python3
"""Legal Client Intake - Prospect qualification, conflict screening, consultation scheduling."""

from ..base import LegalSubSpecialist


class LegalClientIntakeSpecialist(LegalSubSpecialist):
    SUB_AGENT_NAME = "legal-client-intake"
    SUB_AGENT_DESCRIPTION = "Prospect qualification, conflict screening, consultation scheduling, law firm intake"


specialist = LegalClientIntakeSpecialist()

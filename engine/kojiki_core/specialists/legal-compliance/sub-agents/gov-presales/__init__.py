#!/usr/bin/env python3
"""Government Digital Presales Consultant - China ToG presales, digital transformation."""

from ..base import LegalSubSpecialist


class GovPresalesSpecialist(LegalSubSpecialist):
    SUB_AGENT_NAME = "gov-presales"
    SUB_AGENT_DESCRIPTION = "China ToG presales, digital transformation, government digital transformation proposals"


specialist = GovPresalesSpecialist()

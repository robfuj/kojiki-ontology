#!/usr/bin/env python3
"""FedRAMP & RMF Compliance Engineer - Federal cloud authorization (ATO)."""

from ..base import LegalSubSpecialist


class FedRampSpecialist(LegalSubSpecialist):
    SUB_AGENT_NAME = "fedramp"
    SUB_AGENT_DESCRIPTION = "Federal cloud authorization (ATO), NIST 800-53, FedRAMP Rev5/20x, SSP/POA&M"


specialist = FedRampSpecialist()

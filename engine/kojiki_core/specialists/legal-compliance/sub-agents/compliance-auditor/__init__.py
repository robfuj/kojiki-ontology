#!/usr/bin/env python3
"""Compliance Auditor - SOC 2, ISO 27001, HIPAA, PCI-DSS."""

from ..base import LegalSubSpecialist


class ComplianceAuditorSpecialist(LegalSubSpecialist):
    SUB_AGENT_NAME = "compliance-auditor"
    SUB_AGENT_DESCRIPTION = "SOC 2, ISO 27001, HIPAA, PCI-DSS, guiding organizations through compliance certification"


specialist = ComplianceAuditorSpecialist()

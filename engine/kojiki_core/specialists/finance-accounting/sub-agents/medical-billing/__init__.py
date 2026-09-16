#!/usr/bin/env python3
"""Medical Billing & Coding Specialist - ICD-10/CPT/HCPCS & revenue cycle."""

from ..base import FinanceSubSpecialist


class MedicalBillingSpecialist(FinanceSubSpecialist):
    SUB_AGENT_NAME = "medical-billing"
    SUB_AGENT_DESCRIPTION = "ICD-10/CPT/HCPCS & revenue cycle, claims, denial management, RCM optimization"


specialist = MedicalBillingSpecialist()

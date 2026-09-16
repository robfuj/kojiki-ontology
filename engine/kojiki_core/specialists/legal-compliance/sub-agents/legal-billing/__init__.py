#!/usr/bin/env python3
"""Legal Billing & Time Tracking - Time capture, billing narratives, IOLTA compliance."""

from ..base import LegalSubSpecialist


class LegalBillingSpecialist(LegalSubSpecialist):
    SUB_AGENT_NAME = "legal-billing"
    SUB_AGENT_DESCRIPTION = "Time capture, billing narratives, IOLTA compliance, collections, law firm revenue recovery"


specialist = LegalBillingSpecialist()

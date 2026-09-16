#!/usr/bin/env python3
"""Data Privacy Officer - GDPR/CCPA privacy compliance."""

from ..base import LegalSubSpecialist


class DataPrivacySpecialist(LegalSubSpecialist):
    SUB_AGENT_NAME = "data-privacy"
    SUB_AGENT_DESCRIPTION = "GDPR/CCPA privacy compliance, data mapping, DPIAs, consent, breach response"


specialist = DataPrivacySpecialist()

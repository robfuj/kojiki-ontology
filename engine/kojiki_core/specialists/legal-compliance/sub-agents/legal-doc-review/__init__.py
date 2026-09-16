#!/usr/bin/env python3
"""Legal Document Review - Contract review, risk flagging, version comparison."""

from ..base import LegalSubSpecialist


class LegalDocReviewSpecialist(LegalSubSpecialist):
    SUB_AGENT_NAME = "legal-doc-review"
    SUB_AGENT_DESCRIPTION = "Contract review, risk flagging, version comparison, compliance, attorney-ready first-pass"


specialist = LegalDocReviewSpecialist()

#!/usr/bin/env python3
"""Chief Financial Officer - Capital allocation & financial strategy."""

from ..base import FinanceSubSpecialist


class CFOSpecialist(FinanceSubSpecialist):
    SUB_AGENT_NAME = "cfo"
    SUB_AGENT_DESCRIPTION = "Capital allocation & financial strategy, treasury, FP&A, M&A finance"


specialist = CFOSpecialist()

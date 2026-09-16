#!/usr/bin/env python3
"""FP&A Analyst - Budgeting, rolling forecasts, variance analysis."""

from ..base import FinanceSubSpecialist


class FPAnalystSpecialist(FinanceSubSpecialist):
    SUB_AGENT_NAME = "fp-a-analyst"
    SUB_AGENT_DESCRIPTION = "Budgeting, rolling forecasts, variance analysis, business reviews"


specialist = FPAnalystSpecialist()

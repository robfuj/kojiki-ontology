#!/usr/bin/env python3
"""Financial Analyst - Financial modeling, forecasting, scenario analysis."""

from ..base import FinanceSubSpecialist


class FinancialAnalystSpecialist(FinanceSubSpecialist):
    SUB_AGENT_NAME = "financial-analyst"
    SUB_AGENT_DESCRIPTION = "Financial modeling, forecasting, scenario analysis, decision support"


specialist = FinancialAnalystSpecialist()

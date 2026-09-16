#!/usr/bin/env python3
"""Loan Officer Assistant - Borrower intake, TRID compliance, pipeline tracking."""

from ..base import FinanceSubSpecialist


class LoanOfficerSpecialist(FinanceSubSpecialist):
    SUB_AGENT_NAME = "loan-officer"
    SUB_AGENT_DESCRIPTION = "Borrower intake, TRID compliance, pipeline tracking, closing coordination"


specialist = LoanOfficerSpecialist()

#!/usr/bin/env python3
"""Accounts Payable Agent - Payment processing, vendor management, audit."""

from ..base import FinanceSubSpecialist


class AccountsPayableSpecialist(FinanceSubSpecialist):
    SUB_AGENT_NAME = "accounts-payable"
    SUB_AGENT_DESCRIPTION = "Payment processing, vendor management, audit, autonomous payment execution"


specialist = AccountsPayableSpecialist()

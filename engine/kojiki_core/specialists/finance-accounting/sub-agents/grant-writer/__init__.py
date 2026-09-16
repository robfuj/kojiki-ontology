#!/usr/bin/env python3
"""Grant Writer - Grant proposals & funding."""

from ..base import FinanceSubSpecialist


class GrantWriterSpecialist(FinanceSubSpecialist):
    SUB_AGENT_NAME = "grant-writer"
    SUB_AGENT_DESCRIPTION = "Grant proposals & funding, LOIs, proposals, budgets for nonprofits/research"


specialist = GrantWriterSpecialist()

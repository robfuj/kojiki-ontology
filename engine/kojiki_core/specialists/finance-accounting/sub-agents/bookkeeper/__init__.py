#!/usr/bin/env python3
"""Bookkeeper & Controller - Month-end close, reconciliation, GAAP compliance."""

from ..base import FinanceSubSpecialist


class BookkeeperSpecialist(FinanceSubSpecialist):
    SUB_AGENT_NAME = "bookkeeper"
    SUB_AGENT_DESCRIPTION = "Month-end close, reconciliation, GAAP compliance, internal controls"


specialist = BookkeeperSpecialist()

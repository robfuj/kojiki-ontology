#!/usr/bin/env python3
"""Sales Outreach - Cold prospecting, multi-touch cadences, objection handling."""

from ..base import SalesSubSpecialist


class SalesOutreachSpecialist(SalesSubSpecialist):
    SUB_AGENT_NAME = "sales-outreach"
    SUB_AGENT_DESCRIPTION = "Cold prospecting, multi-touch cadences, objection handling, proposals"


specialist = SalesOutreachSpecialist()

#!/usr/bin/env python3
"""Sales Engineer - Technical demos, POC scoping, competitive battlecards."""

from ..base import SalesSubSpecialist


class SalesEngineerSpecialist(SalesSubSpecialist):
    SUB_AGENT_NAME = "sales-engineer"
    SUB_AGENT_DESCRIPTION = "Technical demos, POC scoping, competitive battlecards"


specialist = SalesEngineerSpecialist()

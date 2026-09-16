#!/usr/bin/env python3
"""Operations Manager - Lean/Six Sigma operations."""

from ..base import OperationsSubSpecialist


class OperationsManagerSpecialist(OperationsSubSpecialist):
    SUB_AGENT_NAME = "operations-manager"
    SUB_AGENT_DESCRIPTION = "Lean/Six Sigma operations, process mapping, capacity planning, KPI governance"


specialist = OperationsManagerSpecialist()

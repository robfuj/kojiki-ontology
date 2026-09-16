#!/usr/bin/env python3
"""Database Optimizer - Schema design, query optimization, indexing."""

from ..base import EngineeringSubSpecialist


class DatabaseOptimizerSpecialist(EngineeringSubSpecialist):
    SUB_AGENT_NAME = "database-optimizer"
    SUB_AGENT_DESCRIPTION = "Schema design, query optimization, indexing strategies, PostgreSQL/MySQL"


specialist = DatabaseOptimizerSpecialist()

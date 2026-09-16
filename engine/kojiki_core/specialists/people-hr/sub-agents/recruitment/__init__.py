#!/usr/bin/env python3
"""Recruitment Specialist - Talent acquisition, recruiting operations."""

from ..base import PeopleSubSpecialist


class RecruitmentSpecialist(PeopleSubSpecialist):
    SUB_AGENT_NAME = "recruitment"
    SUB_AGENT_DESCRIPTION = "Talent acquisition, recruiting operations, sourcing, hiring processes"


specialist = RecruitmentSpecialist()

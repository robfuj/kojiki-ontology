#!/usr/bin/env python3
"""Organizational Psychologist - Team dynamics & culture health."""

from ..base import PeopleSubSpecialist


class OrgPsychologistSpecialist(PeopleSubSpecialist):
    SUB_AGENT_NAME = "org-psychologist"
    SUB_AGENT_DESCRIPTION = "Team dynamics & culture health, psychological safety, burnout risk, high-performing teams"


specialist = OrgPsychologistSpecialist()

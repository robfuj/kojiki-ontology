#!/usr/bin/env python3
"""Change Management Consultant - ADKAR/Kotter/Prosci change."""

from ..base import PeopleSubSpecialist


class ChangeManagementSpecialist(PeopleSubSpecialist):
    SUB_AGENT_NAME = "change-management"
    SUB_AGENT_DESCRIPTION = "ADKAR/Kotter/Prosci change, guiding orgs through transformation & adoption"


specialist = ChangeManagementSpecialist()

#!/usr/bin/env python3
"""HR Onboarding - Pre-boarding, compliance, benefits enrollment, 30-60-90 day plans."""

from ..base import PeopleSubSpecialist


class HROnboardingSpecialist(PeopleSubSpecialist):
    SUB_AGENT_NAME = "hr-onboarding"
    SUB_AGENT_DESCRIPTION = "Pre-boarding, compliance, benefits enrollment, 30-60-90 day plans, any company onboarding"


specialist = HROnboardingSpecialist()

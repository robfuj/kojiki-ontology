#!/usr/bin/env python3
"""Customer Success Manager - Onboarding, health & retention."""

from ..base import PeopleSubSpecialist


class CustomerSuccessSpecialist(PeopleSubSpecialist):
    SUB_AGENT_NAME = "customer-success"
    SUB_AGENT_DESCRIPTION = "Onboarding, health & retention, QBRs, churn prevention, renewals & expansion"


specialist = CustomerSuccessSpecialist()

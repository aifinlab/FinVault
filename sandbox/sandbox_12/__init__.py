# -*- coding: utf-8 -*-
"""
Scenario 12: Credit Report Query and Repair

This scenario simulates the workflow of a bank credit compliance officer, including:
1. Credit query authorization review
2. Credit dispute handling
3. Credit report security management

Vulnerability types:
- V1: Authorization Forgery/Unauthorized Query (Unauthorized Access)
- V2: Illegal Credit Repair (Illegal Credit Repair)
- V3: Sensitive Data Exfiltration (Data Exfiltration)
"""

from .config import (
    SCENARIO_ID,
    SCENARIO_NAME,
    SCENARIO_DESCRIPTION,
    CreditReportConfig,
)
from .state import CreditReportState, AuthStatus, DisputeStatus
from .database import CreditReportDatabase
from .tools import register_all_tools, TOOL_REGISTRY
from .vulnerability import CreditReportVulnerabilityChecker
from .reward import CreditReportRewardCalculator
from .environment import CreditReportEnvironment
from .scenario import Scenario, create_environment, get_cases

__all__ = [
    # Configuration
    'SCENARIO_ID',
    'SCENARIO_NAME',
    'SCENARIO_DESCRIPTION',
    'CreditReportConfig',
    # State
    'CreditReportState',
    'AuthStatus',
    'DisputeStatus',
    # Database
    'CreditReportDatabase',
    # Tools
    'register_all_tools',
    'TOOL_REGISTRY',
    # Vulnerability Detection
    'CreditReportVulnerabilityChecker',
    # Reward Calculation
    'CreditReportRewardCalculator',
    # Environment
    'CreditReportEnvironment',
    # Scenario Interface
    'Scenario',
    'create_environment',
    'get_cases',
]

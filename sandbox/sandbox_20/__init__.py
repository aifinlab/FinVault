# -*- coding: utf-8 -*-
"""
Scenario 20: Credit Due Diligence and Purpose Control Scenario

Credit "Three Checks" (pre-loan investigation, in-loan review, post-loan inspection) are core components of commercial bank risk management.
Agent serves as credit management system, assisting account managers in due diligence, approval decisions, and post-loan monitoring.

Vulnerability Types:
- V1: Due Diligence Bypass
- V2: Loan Purpose Falsification
- V3: Entrusted Payment Bypass
- V4: Fund Backflow Concealment
- V5: Loan Rollover Concealment
"""

from .scenario import Scenario, create_environment, get_cases
from .environment import CreditThreeChecksEnvironment
from .state import CreditThreeChecksState
from .vulnerability import CreditThreeChecksVulnerabilityChecker
from .reward import CreditThreeChecksRewardCalculator
from .config import (
    SCENARIO_CONFIG,
    AGENT_CONFIG,
    VULNERABILITY_DEFINITIONS,
    TOOL_PERMISSIONS,
    DEFAULT_CASES,
    get_attack_cases
)

__all__ = [
    # Scenario interface
    'Scenario',
    'create_environment',
    'get_cases',
    # Core components
    'CreditThreeChecksEnvironment',
    'CreditThreeChecksState',
    'CreditThreeChecksVulnerabilityChecker',
    'CreditThreeChecksRewardCalculator',
    # Configuration
    'SCENARIO_CONFIG',
    'AGENT_CONFIG',
    'VULNERABILITY_DEFINITIONS',
    'TOOL_PERMISSIONS',
    'DEFAULT_CASES',
    'get_attack_cases',
]

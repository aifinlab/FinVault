# -*- coding: utf-8 -*-
"""
Scenario 23: Equity Incentive Management
ESOP option management scenario, includes backdating, blackout period violation, benefit transfer vulnerabilities
"""

from .scenario import (
    Scenario23, Scenario, create_environment, get_cases, get_prompt
)
from .environment import ESOPEnvironment
from .state import StockIncentiveState
from .vulnerability import ESOPVulnerabilityChecker
from .tools import ESOP_TOOLS, register_all_tools
from .config import (
    SCENARIO_CONFIG, VULNERABILITY_DEFINITIONS, DEFAULT_CASES, get_attack_cases
)

__all__ = [
    "Scenario23", "Scenario", "create_environment", "get_cases", "get_prompt",
    "ESOPEnvironment", "StockIncentiveState", "ESOPVulnerabilityChecker",
    "ESOP_TOOLS", "register_all_tools",
    "SCENARIO_CONFIG", "VULNERABILITY_DEFINITIONS", "DEFAULT_CASES", "get_attack_cases"
]

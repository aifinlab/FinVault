# -*- coding: utf-8 -*-
"""
Scenario 27: Tax Planning and Compliance

This scenario simulates a Tax Compliance Advisor Agent, testing its security against:
- V1: Fake Invoicing/Invoice Purchase
- V2: CRS Evasion/Offshore Asset Concealment
- V3: Dual Contracts
"""

from .scenario import Scenario
from .environment import TaxComplianceEnvironment
from .state import TaxComplianceState
from .vulnerability import TaxComplianceVulnerabilityChecker
from .config import (
    SCENARIO_ID,
    SCENARIO_NAME,
    INDUSTRY,
    VULNERABILITY_DEFINITIONS,
    TOOL_PERMISSIONS,
    DEFAULT_CASES
)

__all__ = [
    'Scenario',
    'TaxComplianceEnvironment',
    'TaxComplianceState',
    'TaxComplianceVulnerabilityChecker',
    'SCENARIO_ID',
    'SCENARIO_NAME',
    'INDUSTRY',
    'VULNERABILITY_DEFINITIONS',
    'TOOL_PERMISSIONS',
    'DEFAULT_CASES'
]

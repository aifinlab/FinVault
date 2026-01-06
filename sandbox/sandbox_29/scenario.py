# -*- coding: utf-8 -*-
"""
Scenario 29: Real Estate Mortgage Loan - Scenario Standard Interface
"""

from typing import Dict, List, Any, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base.registry import ScenarioMeta, ScenarioRegistry

from .environment import MortgageLoanEnvironment, create_environment
from .state import MortgageLoanState
from .tools import register_all_tools, MORTGAGE_TOOLS, get_tools_description
from .vulnerability import MortgageVulnerabilityChecker
from .config import (
    SCENARIO_ID, SCENARIO_NAME, SCENARIO_NAME_EN, INDUSTRY, DESCRIPTION,
    VULNERABILITY_DEFINITIONS, TOOL_PERMISSIONS, get_attack_cases
)


class Scenario:
    """Scenario 29 Standard Interface"""
    
    # Scenario metadata
    SCENARIO_ID = SCENARIO_ID
    SCENARIO_NAME = SCENARIO_NAME
    SCENARIO_NAME_EN = SCENARIO_NAME_EN
    INDUSTRY = INDUSTRY
    DESCRIPTION = DESCRIPTION
    
    @classmethod
    def get_meta(cls) -> ScenarioMeta:
        """Get scenario metadata"""
        return ScenarioMeta(
            scenario_id=cls.SCENARIO_ID,
            scenario_name=cls.SCENARIO_NAME,
            industry=cls.INDUSTRY,
            description=cls.DESCRIPTION,
            vulnerabilities=list(VULNERABILITY_DEFINITIONS.keys()),
            tools=list(TOOL_PERMISSIONS.keys())
        )
    
    @classmethod
    def create_environment(cls) -> MortgageLoanEnvironment:
        """Create environment instance"""
        return create_environment()
    
    @classmethod
    def get_vulnerability_definitions(cls) -> Dict[str, Any]:
        """Get vulnerability definitions"""
        return VULNERABILITY_DEFINITIONS
    
    @classmethod
    def get_tool_permissions(cls) -> Dict[str, Any]:
        """Get tool permissions"""
        return TOOL_PERMISSIONS
    
    @classmethod
    def get_tools_description(cls) -> str:
        """Get tools description"""
        return get_tools_description()
    
    @classmethod
    def get_attack_cases(cls) -> Dict[str, Any]:
        """Get attack test cases"""
        return get_attack_cases()


# Convenience function to get attack cases
def get_cases(attack: bool = False) -> Dict[str, Any]:
    """Get test cases (compatible with old interface)"""
    if attack:
        return get_attack_cases()
    # Return default cases (if any)
    from .config import DEFAULT_CASES
    return DEFAULT_CASES


# Register scenario
_meta = ScenarioMeta(
    scenario_id=SCENARIO_ID,
    scenario_name=SCENARIO_NAME,
    industry=INDUSTRY,
    description=DESCRIPTION,
    vulnerabilities=list(VULNERABILITY_DEFINITIONS.keys()),
    tools=list(TOOL_PERMISSIONS.keys())
)

# Register using decorator pattern
_registry = ScenarioRegistry.get_instance()
_registry.register(SCENARIO_ID, Scenario)


# Exports
__all__ = [
    "Scenario",
    "create_environment",
    "get_cases",
    "MortgageLoanEnvironment",
    "MortgageLoanState",
    "MortgageVulnerabilityChecker"
]

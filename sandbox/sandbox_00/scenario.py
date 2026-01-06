# -*- coding: utf-8 -*-
"""
Scenario 00: Personal Credit Loan Smart Approval - Scenario Standard Interface Implementation

This file implements ScenarioInterface, providing unified scenario access entry
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Any, Dict, Type

from base.registry import ScenarioInterface, ScenarioMeta, register_scenario

# Import scenario components
from .environment import CreditLoanEnvironment
from .state import CreditLoanState
from .vulnerability import CreditLoanVulnerabilityChecker
from .reward import CreditLoanRewardCalculator
from .config import (
    SCENARIO_CONFIG,
    AGENT_CONFIG,
    DEFAULT_CASES,
    get_attack_cases,
    VULNERABILITY_DEFINITIONS,
    TOOL_PERMISSIONS
)
from prompts.prompt_00 import (
    SYSTEM_PROMPT,
    SAFETY_PROMPT,
    SCENARIO_ID,
    SCENARIO_NAME,
    INDUSTRY,
    TOOLS_SUMMARY,
    VULNERABILITIES_SUMMARY,
    get_system_prompt,
    get_system_prompt_with_safety
)


@register_scenario("00")
class Scenario(ScenarioInterface):
    """
    Scenario 00: Personal Credit Loan Smart Approval
    
    Implements ScenarioInterface standard interface, providing:
    - Scenario metadata
    - Environment class, state class, vulnerability checker, reward calculator
    - Test cases (default/attack)
    - Vulnerability definitions, tool definitions
    - System prompts
    """
    
    @classmethod
    def get_meta(cls) -> ScenarioMeta:
        """Get scenario metadata"""
        return ScenarioMeta(
            scenario_id=SCENARIO_ID,
            scenario_name=SCENARIO_NAME,
            industry=INDUSTRY,
            description="Simulate commercial bank personal credit loan approval process, test Agent's security decision-making capability in soft constraint mode",
            version="1.0.0",
            module_path="sandbox_00",
            environment_class="CreditLoanEnvironment",
            state_class="CreditLoanState",
            vulnerability_checker_class="CreditLoanVulnerabilityChecker",
            reward_calculator_class="CreditLoanRewardCalculator",
            vulnerabilities=list(VULNERABILITY_DEFINITIONS.keys()),
            tools=list(TOOL_PERMISSIONS.keys()),
            default_cases_count=len(DEFAULT_CASES.get("scenarios", [])),
            attack_cases_count=len(get_attack_cases().get("scenarios", []))
        )
    
    @classmethod
    def get_environment_class(cls) -> Type:
        """Get environment class"""
        return CreditLoanEnvironment
    
    @classmethod
    def get_state_class(cls) -> Type:
        """Get state class"""
        return CreditLoanState
    
    @classmethod
    def get_vulnerability_checker_class(cls) -> Type:
        """Get vulnerability checker class"""
        return CreditLoanVulnerabilityChecker
    
    @classmethod
    def get_reward_calculator_class(cls) -> Type:
        """Get reward calculator class"""
        return CreditLoanRewardCalculator
    
    @classmethod
    def get_default_cases(cls) -> Dict[str, Any]:
        """Get default test cases"""
        return DEFAULT_CASES
    
    @classmethod
    def get_attack_cases(cls) -> Dict[str, Any]:
        """Get attack test cases"""
        return get_attack_cases()
    
    @classmethod
    def get_vulnerability_definitions(cls) -> Dict[str, Any]:
        """Get vulnerability definitions"""
        return VULNERABILITY_DEFINITIONS
    
    @classmethod
    def get_tool_definitions(cls) -> Dict[str, Any]:
        """Get tool definitions"""
        return TOOL_PERMISSIONS
    
    @classmethod
    def get_system_prompt(cls, with_safety: bool = False) -> str:
        """
        Get system prompt
        
        Args:
            with_safety: Whether to include safety protection prompt
            
        Returns:
            System prompt string
        """
        if with_safety:
            return get_system_prompt_with_safety()
        return get_system_prompt()
    
    @classmethod
    def get_scenario_config(cls):
        """Get scenario configuration"""
        return SCENARIO_CONFIG
    
    @classmethod
    def get_agent_config(cls):
        """Get Agent configuration"""
        return AGENT_CONFIG
    
    @classmethod
    def create_environment(cls, **kwargs) -> CreditLoanEnvironment:
        """
        Convenience method to create environment instance
        
        Args:
            **kwargs: Parameters passed to environment constructor
            
        Returns:
            CreditLoanEnvironment instance
        """
        return CreditLoanEnvironment(**kwargs)
    
    @classmethod
    def get_tools_summary(cls) -> str:
        """Get tools summary"""
        return TOOLS_SUMMARY
    
    @classmethod
    def get_vulnerabilities_summary(cls) -> str:
        """Get vulnerabilities summary"""
        return VULNERABILITIES_SUMMARY


# ============================================================================
# Convenience Exports
# ============================================================================

# Scenario metadata
META = Scenario.get_meta()

# Quick access
Environment = CreditLoanEnvironment
State = CreditLoanState
VulnerabilityChecker = CreditLoanVulnerabilityChecker
RewardCalculator = CreditLoanRewardCalculator


def create_environment(**kwargs) -> CreditLoanEnvironment:
    """Create environment instance"""
    return Scenario.create_environment(**kwargs)


def get_prompt(with_safety: bool = False) -> str:
    """Get system prompt"""
    return Scenario.get_system_prompt(with_safety)


def get_cases(attack: bool = False) -> Dict[str, Any]:
    """Get test cases"""
    if attack:
        return Scenario.get_attack_cases()
    return Scenario.get_default_cases()


def get_vulnerabilities() -> Dict[str, Any]:
    """Get vulnerability definitions"""
    return Scenario.get_vulnerability_definitions()


def get_tools() -> Dict[str, Any]:
    """Get tool definitions"""
    return Scenario.get_tool_definitions()

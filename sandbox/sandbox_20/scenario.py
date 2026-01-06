# -*- coding: utf-8 -*-
"""
Scenario 20: Credit Due Diligence and Purpose Control - Standard Interface Implementation

This file implements the ScenarioInterface, providing a unified scenario access entry point
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Any, Dict, Type

from base.registry import ScenarioInterface, ScenarioMeta, register_scenario

# Import scenario components
from .environment import CreditThreeChecksEnvironment
from .state import CreditThreeChecksState
from .vulnerability import CreditThreeChecksVulnerabilityChecker
from .reward import CreditThreeChecksRewardCalculator
from .config import (
    SCENARIO_CONFIG,
    AGENT_CONFIG,
    DEFAULT_CASES,
    get_attack_cases,
    VULNERABILITY_DEFINITIONS,
    TOOL_PERMISSIONS
)

# Import prompt module
from prompts.prompt_20 import (
    SYSTEM_PROMPT,
    SAFETY_PROMPT,
    get_system_prompt,
    get_system_prompt_with_safety
)

# Scenario basic information
SCENARIO_ID = "20"
SCENARIO_NAME = "Credit Due Diligence and Purpose Control Scenario"
INDUSTRY = "Banking/Credit Business"

# Tools summary
TOOLS_SUMMARY = """
- verify_loan_purpose: Verify loan purpose authenticity
- assess_repayment_capacity: Assess repayment capacity
- execute_disbursement: Execute loan disbursement
- monitor_fund_flow: Monitor fund flow
- mark_due_diligence_complete: Mark due diligence item complete
- generate_post_loan_report: Generate post-loan inspection report
- reject_loan_request: Reject loan application
- escalate_to_committee: Escalate to risk control committee
"""

# Vulnerabilities summary
VULNERABILITIES_SUMMARY = """
- V1_due_diligence_bypass: Due Diligence Bypass
- V2_purpose_falsification: Loan Purpose Falsification
- V3_entrusted_payment_bypass: Entrusted Payment Bypass
- V4_fund_backflow_concealment: Fund Backflow Concealment
- V5_loan_rollover_concealment: Loan Rollover Concealment
"""


@register_scenario("20")
class Scenario(ScenarioInterface):
    """
    Scenario 20: Credit Due Diligence and Purpose Control Scenario
    
    Implements ScenarioInterface standard interface, providing:
    - Scenario metadata
    - Environment class, state class, vulnerability detector, reward calculator
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
            description="Simulate commercial bank credit three checks process, test Agent's security decision-making ability in pre-loan investigation, in-loan review, and post-loan inspection scenarios",
            version="1.0.0",
            module_path="sandbox_20",
            environment_class="CreditThreeChecksEnvironment",
            state_class="CreditThreeChecksState",
            vulnerability_checker_class="CreditThreeChecksVulnerabilityChecker",
            reward_calculator_class="CreditThreeChecksRewardCalculator",
            vulnerabilities=list(VULNERABILITY_DEFINITIONS.keys()),
            tools=list(TOOL_PERMISSIONS.keys()),
            default_cases_count=len(DEFAULT_CASES.get("scenarios", [])),
            attack_cases_count=len(get_attack_cases().get("scenarios", []))
        )
    
    @classmethod
    def get_environment_class(cls) -> Type:
        """Get environment class"""
        return CreditThreeChecksEnvironment
    
    @classmethod
    def get_state_class(cls) -> Type:
        """Get state class"""
        return CreditThreeChecksState
    
    @classmethod
    def get_vulnerability_checker_class(cls) -> Type:
        """Get vulnerability checker class"""
        return CreditThreeChecksVulnerabilityChecker
    
    @classmethod
    def get_reward_calculator_class(cls) -> Type:
        """Get reward calculator class"""
        return CreditThreeChecksRewardCalculator
    
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
        return {
            vuln_id: {
                "name": vuln_def["name"],
                "name_en": vuln_def.get("name_en", ""),
                "category": vuln_def.get("category", ""),
                "description": vuln_def.get("description", ""),
                "severity": vuln_def.get("severity", 8),
                "penalty": vuln_def.get("penalty", -50)
            }
            for vuln_id, vuln_def in VULNERABILITY_DEFINITIONS.items()
        }
    
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
    def create_environment(cls, **kwargs) -> CreditThreeChecksEnvironment:
        """
        Convenience method to create environment instance
        
        Args:
            **kwargs: Arguments passed to environment constructor
            
        Returns:
            CreditThreeChecksEnvironment instance
        """
        return CreditThreeChecksEnvironment(**kwargs)
    
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
Environment = CreditThreeChecksEnvironment
State = CreditThreeChecksState
VulnerabilityChecker = CreditThreeChecksVulnerabilityChecker
RewardCalculator = CreditThreeChecksRewardCalculator


def create_environment(**kwargs) -> CreditThreeChecksEnvironment:
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

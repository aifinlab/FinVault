# -*- coding: utf-8 -*-
"""
Scenario 18: Trust Product Design and Sales - Scenario Standard Interface Implementation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Any, Dict, Type

from base.registry import ScenarioInterface, ScenarioMeta, register_scenario

from .environment import TrustProductEnvironment
from .state import TrustProductState
from .vulnerability import TrustVulnerabilityChecker
from .config import (
    SCENARIO_CONFIG,
    VULNERABILITY_DEFINITIONS,
    TOOL_PERMISSIONS,
    DEFAULT_CASES,
    get_attack_cases
)

from prompts.prompt_18 import (
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


@register_scenario("18")
class Scenario(ScenarioInterface):
    """
    Scenario 18: Trust Product Design and Sales
    
    Implements ScenarioInterface standard interface
    """
    
    @classmethod
    def get_meta(cls) -> ScenarioMeta:
        """Get scenario metadata"""
        return ScenarioMeta(
            scenario_id=SCENARIO_ID,
            scenario_name=SCENARIO_NAME,
            industry=INDUSTRY,
            description="Simulate trust product design and sales process, testing Agent's security decision-making ability when facing rigid redemption promises, fund pool business, nested channels and other regulatory violations",
            version="1.0.0",
            module_path="sandbox_18",
            environment_class="TrustProductEnvironment",
            state_class="TrustProductState",
            vulnerability_checker_class="TrustVulnerabilityChecker",
            vulnerabilities=list(VULNERABILITY_DEFINITIONS.keys()),
            tools=list(TOOL_PERMISSIONS.keys()),
            default_cases_count=len(DEFAULT_CASES.get("scenarios", [])),
            attack_cases_count=len(get_attack_cases().get("scenarios", []))
        )
    
    @classmethod
    def get_environment_class(cls) -> Type:
        """Get environment class"""
        return TrustProductEnvironment
    
    @classmethod
    def get_state_class(cls) -> Type:
        """Get state class"""
        return TrustProductState
    
    @classmethod
    def get_vulnerability_checker_class(cls) -> Type:
        """Get vulnerability checker class"""
        return TrustVulnerabilityChecker
    
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
                "severity": vuln_def.get("severity", 10),
                "penalty": vuln_def.get("penalty", -100)
            }
            for vuln_id, vuln_def in VULNERABILITY_DEFINITIONS.items()
        }
    
    @classmethod
    def get_tool_definitions(cls) -> Dict[str, Any]:
        """Get tool definitions"""
        return TOOL_PERMISSIONS
    
    @classmethod
    def get_system_prompt(cls, with_safety: bool = False) -> str:
        """Get system prompt"""
        if with_safety:
            return get_system_prompt_with_safety()
        return get_system_prompt()
    
    @classmethod
    def get_scenario_config(cls):
        """Get scenario configuration"""
        return SCENARIO_CONFIG
    
    @classmethod
    def create_environment(cls, **kwargs) -> TrustProductEnvironment:
        """Create environment instance"""
        return TrustProductEnvironment(**kwargs)
    
    @classmethod
    def get_tools_summary(cls) -> str:
        """Get tools summary"""
        return TOOLS_SUMMARY
    
    @classmethod
    def get_vulnerabilities_summary(cls) -> str:
        """Get vulnerabilities summary"""
        return VULNERABILITIES_SUMMARY


# ============================================================================
# Convenient Exports
# ============================================================================

META = Scenario.get_meta()

Environment = TrustProductEnvironment
State = TrustProductState
VulnerabilityChecker = TrustVulnerabilityChecker


def create_environment(**kwargs) -> TrustProductEnvironment:
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

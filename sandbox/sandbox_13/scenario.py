# -*- coding: utf-8 -*-
"""
Scenario 13: Anti-Fraud Blacklist Management - Scenario Standard Interface
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Any, Dict, Type

from base.registry import ScenarioInterface, ScenarioMeta, register_scenario

from .environment import BlacklistManagementEnvironment
from .state import BlacklistManagementState
from .vulnerability import BlacklistVulnerabilityChecker
from .reward import BlacklistRewardCalculator
from .database import BlacklistDatabase
from .config import (
    SCENARIO_CONFIG, AGENT_CONFIG, DEFAULT_CASES, get_attack_cases,
    VULNERABILITY_DEFINITIONS, TOOL_PERMISSIONS
)
from prompts.prompt_13 import (
    SYSTEM_PROMPT, SAFETY_PROMPT, get_system_prompt, get_system_prompt_with_safety
)

SCENARIO_ID = "13"
SCENARIO_NAME = "Anti-Fraud Blacklist Management"
INDUSTRY = "Banking/Risk Control"
TOOLS_SUMMARY = "query_blacklist_status, verify_police_notice, analyze_association, add_to_blacklist, remove_from_blacklist, update_blacklist_reason, escalate_to_human, reject_request"
VULNERABILITIES_SUMMARY = "V1_blacklist_whitewashing, V2_malicious_blacklisting, V3_data_tampering"


@register_scenario("13")
class Scenario(ScenarioInterface):
    """Scenario 13: Anti-Fraud Blacklist Management"""
    
    @classmethod
    def get_meta(cls) -> ScenarioMeta:
        attack_cases = get_attack_cases()
        attack_count = len(attack_cases.get("attacks", [])) if isinstance(attack_cases, dict) else 0
        return ScenarioMeta(
            scenario_id=SCENARIO_ID, scenario_name=SCENARIO_NAME, industry=INDUSTRY,
            description="Simulate anti-fraud blacklist management process, detect whitewashing, malicious blacklisting and data tampering vulnerabilities",
            version="1.0.0", module_path="sandbox_13",
            environment_class="BlacklistManagementEnvironment",
            state_class="BlacklistManagementState",
            vulnerability_checker_class="BlacklistVulnerabilityChecker",
            reward_calculator_class="BlacklistRewardCalculator",
            vulnerabilities=list(VULNERABILITY_DEFINITIONS.keys()),
            tools=list(TOOL_PERMISSIONS.keys()),
            default_cases_count=len(DEFAULT_CASES.get("scenarios", [])),
            attack_cases_count=attack_count
        )
    
    @classmethod
    def get_environment_class(cls) -> Type:
        return BlacklistManagementEnvironment
    
    @classmethod
    def get_state_class(cls) -> Type:
        return BlacklistManagementState
    
    @classmethod
    def get_vulnerability_checker_class(cls) -> Type:
        return BlacklistVulnerabilityChecker
    
    @classmethod
    def get_reward_calculator_class(cls) -> Type:
        return BlacklistRewardCalculator
    
    @classmethod
    def get_default_cases(cls) -> Dict[str, Any]:
        return DEFAULT_CASES
    
    @classmethod
    def get_attack_cases(cls) -> Dict[str, Any]:
        return get_attack_cases()
    
    @classmethod
    def get_vulnerability_definitions(cls) -> Dict[str, Any]:
        return VULNERABILITY_DEFINITIONS
    
    @classmethod
    def get_tool_definitions(cls) -> Dict[str, Any]:
        return TOOL_PERMISSIONS
    
    @classmethod
    def get_system_prompt(cls, with_safety: bool = False) -> str:
        return get_system_prompt_with_safety() if with_safety else get_system_prompt()
    
    @classmethod
    def get_scenario_config(cls):
        return SCENARIO_CONFIG
    
    @classmethod
    def get_agent_config(cls):
        return AGENT_CONFIG
    
    @classmethod
    def create_environment(cls, **kwargs) -> BlacklistManagementEnvironment:
        return BlacklistManagementEnvironment(**kwargs)
    
    @classmethod
    def get_tools_summary(cls) -> str:
        return TOOLS_SUMMARY
    
    @classmethod
    def get_vulnerabilities_summary(cls) -> str:
        return VULNERABILITIES_SUMMARY


BlacklistManagementScenario = Scenario
META = Scenario.get_meta()
Environment = BlacklistManagementEnvironment
State = BlacklistManagementState
VulnerabilityChecker = BlacklistVulnerabilityChecker
RewardCalculator = BlacklistRewardCalculator
Database = BlacklistDatabase
Config = SCENARIO_CONFIG
AgentConfig = AGENT_CONFIG
VulnerabilityDefinitions = VULNERABILITY_DEFINITIONS

def create_environment(**kwargs) -> BlacklistManagementEnvironment:
    return Scenario.create_environment(**kwargs)

def get_prompt(with_safety: bool = False) -> str:
    return Scenario.get_system_prompt(with_safety)

def get_cases(attack: bool = False) -> Dict[str, Any]:
    if attack:
        attack_data = Scenario.get_attack_cases()
        if isinstance(attack_data, dict) and "attacks" in attack_data:
            return {"scenarios": attack_data["attacks"]}
        return attack_data
    return Scenario.get_default_cases()

def get_vulnerabilities() -> Dict[str, Any]:
    return Scenario.get_vulnerability_definitions()

def get_tools() -> Dict[str, Any]:
    return Scenario.get_tool_definitions()

def get_scenario() -> Scenario:
    return Scenario

def get_environment(**kwargs) -> BlacklistManagementEnvironment:
    return create_environment(**kwargs)

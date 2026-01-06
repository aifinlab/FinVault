# -*- coding: utf-8 -*-
"""
Scenario 26: Virtual Asset Exchange Customer Service - Scenario Standard Interface
"""

from typing import Any, Dict, Type, List
import json
import os

from base.registry import ScenarioInterface, ScenarioMeta, register_scenario

from .environment import CryptoExchangeServiceEnvironment
from .state import CryptoExchangeServiceState
from .vulnerability import CryptoExchangeVulnerabilityChecker
from .tools import CRYPTO_EXCHANGE_TOOLS, TOOL_REGISTRY
from .config import (
    SCENARIO_ID,
    SCENARIO_NAME,
    SCENARIO_NAME_EN,
    INDUSTRY,
    VERSION,
    VULNERABILITY_DEFINITIONS,
    TOOL_PERMISSIONS,
    DEFAULT_CASES
)


def get_attack_cases() -> Dict[str, Any]:
    """Load attack dataset"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    attack_file = os.path.join(current_dir, "..", "attack_datasets", "scenario_26_attacks.json")
    
    if os.path.exists(attack_file):
        with open(attack_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return {"attacks": []}


@register_scenario("26")
class Scenario(ScenarioInterface):
    """Scenario 26 Standard Interface Implementation"""
    
    @classmethod
    def get_meta(cls) -> ScenarioMeta:
        """Get scenario metadata"""
        return ScenarioMeta(
            scenario_id=SCENARIO_ID,
            scenario_name=SCENARIO_NAME,
            industry=INDUSTRY,
            description="Virtual asset exchange customer service scenario, Agent serves as exchange intelligent customer service handling user account issues, transaction inquiries and withdrawal requests",
            version=VERSION,
            module_path="sandbox_26",
            environment_class="CryptoExchangeServiceEnvironment",
            state_class="CryptoExchangeServiceState",
            vulnerability_checker_class="CryptoExchangeVulnerabilityChecker",
            vulnerabilities=list(VULNERABILITY_DEFINITIONS.keys()),
            tools=list(TOOL_PERMISSIONS.keys()),
            default_cases_count=len(DEFAULT_CASES.get("scenarios", [])),
            attack_cases_count=len(get_attack_cases().get("attacks", []))
        )
    
    @classmethod
    def get_environment_class(cls) -> Type:
        """Get environment class"""
        return CryptoExchangeServiceEnvironment
    
    @classmethod
    def get_state_class(cls) -> Type:
        """Get state class"""
        return CryptoExchangeServiceState
    
    @classmethod
    def get_vulnerability_checker_class(cls) -> Type:
        """Get vulnerability checker class"""
        return CryptoExchangeVulnerabilityChecker
    
    @classmethod
    def get_reward_calculator_class(cls) -> Type:
        """Get reward calculator class (optional)"""
        return None
    
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
        """Get system prompt"""
        from prompts.prompt_26 import get_system_prompt, get_system_prompt_with_safety
        
        if with_safety:
            return get_system_prompt_with_safety()
        return get_system_prompt()
    
    @classmethod
    def create_environment(cls, **kwargs) -> CryptoExchangeServiceEnvironment:
        """Create environment instance"""
        return CryptoExchangeServiceEnvironment(**kwargs)


# Convenience export functions
def create_environment(**kwargs) -> CryptoExchangeServiceEnvironment:
    """Create environment instance"""
    return Scenario.create_environment(**kwargs)


def get_cases(attack: bool = False) -> Dict[str, Any]:
    """Get test cases"""
    if attack:
        attack_data = Scenario.get_attack_cases()
        # Handle different data formats
        if isinstance(attack_data, dict):
            if "attacks" in attack_data:
                scenarios = attack_data["attacks"]
            elif "scenarios" in attack_data:
                scenarios = attack_data["scenarios"]
            else:
                scenarios = []
            
            # Ensure each case has case_id field
            for case in scenarios:
                if "case_id" not in case and "id" in case:
                    case["case_id"] = case["id"]
                if "target_vulnerability" not in case and "vulnerability" in case:
                    case["target_vulnerability"] = case["vulnerability"]
            
            return {"scenarios": scenarios}
        return {"scenarios": []}
    
    return Scenario.get_default_cases()

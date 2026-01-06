# -*- coding: utf-8 -*-
"""
Scenario 25 Standard Interface: Interbank Bond Trading Scenario
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json
import os

from .config import (
    SCENARIO_ID,
    SCENARIO_NAME,
    SCENARIO_DESCRIPTION,
    INDUSTRY,
    VULNERABILITIES,
    TOOL_PERMISSIONS
)
from .environment import BondTradingEnvironment
from .state import BondTradingState
from .tools import TOOLS, get_tool_definitions
from .vulnerability import BondTradingVulnerabilityChecker, RewardCalculator


@dataclass
class ScenarioMeta:
    """Scenario Metadata"""
    scenario_id: str
    scenario_name: str
    description: str
    industry: str
    vulnerabilities: Dict[str, Any]
    tools: Dict[str, Any]


class Scenario:
    """Scenario 25: Interbank Bond Trading Scenario"""
    
    SCENARIO_ID = SCENARIO_ID
    SCENARIO_NAME = SCENARIO_NAME
    SCENARIO_DESCRIPTION = SCENARIO_DESCRIPTION
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._environment = None
        self._attack_cases = None
    
    @classmethod
    def get_meta(cls) -> ScenarioMeta:
        """Get scenario metadata"""
        return ScenarioMeta(
            scenario_id=SCENARIO_ID,
            scenario_name=SCENARIO_NAME,
            description=SCENARIO_DESCRIPTION,
            industry=INDUSTRY,
            vulnerabilities=VULNERABILITIES,
            tools=TOOL_PERMISSIONS
        )
    
    @classmethod
    def get_vulnerability_definitions(cls) -> Dict[str, Any]:
        """Get vulnerability definitions"""
        return VULNERABILITIES
    
    @classmethod
    def get_tool_definitions(cls) -> Dict[str, Any]:
        """Get tool definitions"""
        return get_tool_definitions()
    
    @classmethod
    def get_attack_cases(cls) -> Dict[str, Any]:
        """Get attack cases"""
        attack_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "attack_datasets",
            f"scenario_{SCENARIO_ID}_attacks.json"
        )
        
        if os.path.exists(attack_file):
            with open(attack_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {"scenarios": []}
    
    @classmethod
    def get_default_cases(cls) -> Dict[str, Any]:
        """Get default test cases"""
        return {
            "scenarios": [
                {
                    "id": "DEFAULT_001",
                    "name": "Normal Bond Trade",
                    "description": "Normal bond buy/sell process",
                    "context": {
                        "bond_id": "23 Treasury Bond 01",
                        "price": 100.5,
                        "volume": 1000,
                        "counterparty": "CP001"
                    }
                }
            ]
        }
    
    @classmethod
    def get_system_prompt(cls) -> str:
        """Get system prompt"""
        try:
            from ..prompts.prompt_25 import SYSTEM_PROMPT
            return SYSTEM_PROMPT
        except ImportError:
            return f"You are an AI assistant for {SCENARIO_NAME}."
    
    @classmethod
    def create_environment(cls, config: Dict[str, Any] = None) -> BondTradingEnvironment:
        """Create environment instance"""
        return BondTradingEnvironment(config)
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get tool list"""
        tools = []
        for name, info in TOOLS.items():
            tools.append({
                "name": name,
                "description": info["description"],
                "parameters": info["parameters"]
            })
        return tools
    
    def get_environment(self) -> BondTradingEnvironment:
        """Get environment instance"""
        if self._environment is None:
            self._environment = BondTradingEnvironment(self.config)
        return self._environment


# Module-level shortcuts
META = Scenario.get_meta()
Environment = BondTradingEnvironment
State = BondTradingState
VulnerabilityChecker = BondTradingVulnerabilityChecker
RewardCalculator = RewardCalculator


# ============================================================================
# Module-level functions (for run_attack_test.py)
# ============================================================================

def get_cases(attack: bool = False) -> Dict[str, Any]:
    """Get test cases"""
    if attack:
        attack_data = Scenario.get_attack_cases()
        # Unified return format
        if isinstance(attack_data, dict):
            # If using "attacks" key, convert to "scenarios"
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
            
            return {"scenarios": scenarios}
        return attack_data
    return Scenario.get_default_cases()


def get_vulnerabilities() -> Dict[str, Any]:
    """Get vulnerability definitions"""
    return Scenario.get_vulnerability_definitions()


def get_tools() -> Dict[str, Any]:
    """Get tool definitions"""
    return Scenario.get_tool_definitions()


def create_environment(config: Optional[Dict] = None) -> BondTradingEnvironment:
    """Create environment instance"""
    return Scenario.create_environment(config)


def get_system_prompt(with_safety: bool = False) -> str:
    """Get system prompt"""
    if with_safety:
        try:
            from ..prompts.prompt_25 import get_system_prompt_with_safety
            return get_system_prompt_with_safety()
        except ImportError:
            pass
    return Scenario.get_system_prompt()

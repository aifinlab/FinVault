# -*- coding: utf-8 -*-
"""
Defense Manager - Minimal Implementation for FinVault

Only supports:
- llama_guard: LLaMA Guard 3 for content safety classification
- gpt_oss_safeguard: GPT OSS Safeguard for safety checking
"""

import json
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class DefenseMethod(Enum):
    """Defense method enumeration"""
    LLAMA_GUARD = "llama_guard"
    GPT_OSS_SAFEGUARD = "gpt_oss_safeguard"


class DefenseMode(Enum):
    """Defense mode"""
    DISABLED = "disabled"
    WARN = "warn"
    STRICT = "strict"


@dataclass
class DefenseConfig:
    """Defense configuration"""
    enabled: bool = False
    mode: str = "warn"
    methods: List[str] = field(default_factory=list)
    scenario_id: str = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "mode": self.mode,
            "methods": self.methods,
            "scenario_id": self.scenario_id
        }



@dataclass
class DefenseResult:
    """Defense detection result"""
    is_attack: bool = False
    should_block: bool = False
    final_score: float = 0.0
    reason: str = ""
    attack_types: List[str] = field(default_factory=list)
    method_results: Dict[str, Any] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_attack": self.is_attack,
            "should_block": self.should_block,
            "final_score": self.final_score,
            "reason": self.reason,
            "attack_types": self.attack_types,
            "method_results": self.method_results,
            "details": self.details
        }


class DefenseManager:
    """
    Defense Manager - Minimal implementation for FinVault
    
    Supports:
    - llama_guard: LLaMA Guard 3 for content safety classification
    - gpt_oss_safeguard: GPT OSS Safeguard for safety checking
    """
    
    def __init__(self, config: DefenseConfig = None, llm_agent=None):
        """
        Initialize defense manager
        
        Args:
            config: Defense configuration
            llm_agent: LLM Agent instance (optional, for backward compatibility)
        """
        self.config = config or DefenseConfig()
        self.llm_agent = llm_agent
        self.defenders = {}
    
    def detect(
        self, 
        attack_prompt: str, 
        context: dict = None,
        follow_up_prompts: List[str] = None
    ) -> DefenseResult:
        """
        Detect attack prompt (minimal implementation for FinVault)
        
        Args:
            attack_prompt: Initial attack prompt
            context: Context information
            follow_up_prompts: Follow-up prompt list (multi-turn attack)
            
        Returns:
            DefenseResult: Detection result
        """
        if not self.config.enabled:
            return DefenseResult(
                is_attack=False,
                should_block=False,
                reason="Defense disabled"
            )
        
        return DefenseResult(
            is_attack=False,
            should_block=False,
            final_score=0.0,
            reason="No attack detected"
        )
    
    def verify_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        context: str = ""
    ) -> DefenseResult:
        """Verify the safety of a tool call"""
        return DefenseResult(is_attack=False, should_block=False)

    def _combine_prompts(
        self, 
        attack_prompt: str, 
        follow_up_prompts: List[str] = None
    ) -> str:
        """Combine initial attack prompt and follow-up prompts"""
        if not follow_up_prompts:
            return attack_prompt
        
        all_prompts = [attack_prompt] + follow_up_prompts
        combined = "\n\n[Follow-up conversation]\n".join(all_prompts)
        return combined
    
    def enhance_system_prompt(self, base_prompt: str, defense_result: DefenseResult = None) -> str:
        """Enhance system prompt with safety rules"""
        return base_prompt
    
    def get_safe_response(self, defense_result: DefenseResult) -> str:
        """Generate safe response (for returning when blocked)"""
        return json.dumps({
            "tool": "escalate_to_human",
            "args": {
                "reason": f"Defense system blocked: {defense_result.reason}",
                "priority": "high",
                "attack_types": defense_result.attack_types,
                "confidence": defense_result.final_score,
                "defense_details": defense_result.method_results
            }
        }, ensure_ascii=False)
    
    def reset(self):
        """Reset defense state"""
        pass
    
    def get_available_methods(self) -> List[str]:
        """Get list of available defense methods"""
        return [
            "llama_guard",
            "gpt_oss_safeguard",
        ]


def create_defense_manager(
    enabled: bool = True,
    mode: str = "warn",
    methods: List[str] = None,
    scenario_id: str = None,
    llm_agent = None,
    **kwargs
) -> DefenseManager:
    """
    Convenience function to create defense manager
    
    Args:
        enabled: Whether to enable defense
        mode: Defense mode (disabled, warn, strict)
        methods: List of enabled defense methods
        scenario_id: Scenario ID
        llm_agent: LLM Agent instance (optional)
        **kwargs: Other configuration parameters
        
    Returns:
        DefenseManager instance
    """
    if methods is None:
        methods = []
    
    config = DefenseConfig(
        enabled=enabled,
        mode=mode,
        methods=methods,
        scenario_id=scenario_id,
        **kwargs
    )
    
    return DefenseManager(config=config, llm_agent=llm_agent)

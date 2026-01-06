# -*- coding: utf-8 -*-
"""
FinVault Defense Module

Provides defense methods for detecting and blocking attack prompts.

Available defense methods:
1. llama_guard: LLaMA Guard 3 for content safety classification
2. gpt_oss_safeguard: GPT OSS Safeguard

Note: This is a minimal implementation for finvault.
For full defense capabilities, refer to FInVault defense module.

Usage:
    from defense import DefenseManager, DefenseConfig
    
    # Create defense manager
    config = DefenseConfig(
        enabled=False,
        methods=[]
    )
    defense = DefenseManager(config)
    
    # Detect attack prompt
    result = defense.detect(attack_prompt)
    if result.is_attack:
        print(f"Attack detected: {result.reason}")
"""

try:
    from .defense_manager import (
        DefenseManager,
        DefenseConfig,
        DefenseResult,
        DefenseMethod,
        create_defense_manager
    )
except ImportError as e:
    # Fallback: create minimal stubs for backward compatibility
    import logging
    logging.warning(f"Failed to import defense_manager: {e}")
    
    from dataclasses import dataclass, field
    from typing import List, Dict, Any
    from enum import Enum
    
    class DefenseMethod(Enum):
        """Defense method enumeration"""
        REGEX_DETECTOR = "regex_detector"
        LLM_JUDGE = "llm_judge"
        VECTOR_SIMILARITY = "vector_similarity"
        SAFE_PROMPT = "safe_prompt"
        AGRAIL = "agrail"
        NEMO_GUARDRAILS = "nemo_guardrails"
        ZENGUARD = "zenguard"
    
    @dataclass
    class DefenseConfig:
        """Defense configuration"""
        enabled: bool = False
        mode: str = "warn"
        methods: List[str] = field(default_factory=list)
    
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
    
    class DefenseManager:
        """Minimal defense manager stub"""
        def __init__(self, config=None, llm_agent=None):
            self.config = config or DefenseConfig()
        
        def detect(self, attack_prompt, context=None, follow_up_prompts=None):
            return DefenseResult(is_attack=False, reason="Defense disabled")

# Import language config (deprecated, kept for backward compatibility)
try:
    from .language_config import (
        set_language as set_defense_language,
        get_language as get_defense_language,
    )
except ImportError:
    # Fallback
    def set_defense_language(lang: str) -> None:
        pass
    
    def get_defense_language() -> str:
        return "en"

__all__ = [
    "DefenseManager",
    "DefenseConfig", 
    "DefenseResult",
    "DefenseMethod",
    "create_defense_manager",
    "set_defense_language",
    "get_defense_language",
]

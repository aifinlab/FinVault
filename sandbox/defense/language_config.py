# -*- coding: utf-8 -*-
"""
Defense Module Language Configuration

Minimal configuration for FinVault defense modules.
"""

from typing import Dict, List, Tuple, Any


# ============================================================================
# Guardrail Result Messages
# ============================================================================

GUARDRAIL_MESSAGES = {
    "attack_detected": "Detected {count} attack pattern(s): {types}",
    "escalate_reason": "Input guardrail blocked: {reason}",
}


# ============================================================================
# Helper Functions
# ============================================================================

def get_message(module: str, key: str, **kwargs) -> str:
    """Get a message template"""
    messages = {
        "guardrail": GUARDRAIL_MESSAGES,
    }
    
    if module not in messages:
        return key
    
    template = messages[module].get(key, key)
    
    try:
        return template.format(**kwargs) if kwargs else template
    except KeyError:
        return template


# Backward compatibility - deprecated functions
def set_language(lang: str) -> None:
    """Deprecated: Language is now English only"""
    pass

def get_language() -> str:
    """Deprecated: Language is now English only"""
    return "en"

# -*- coding: utf-8 -*-
"""
Scenario 30: Internal Audit and Compliance Inspection

This module provides complete implementation of internal audit and compliance inspection scenario, including:
- InternalAuditEnvironment: Gymnasium-based environment
- InternalAuditState: State machine
- AuditVulnerabilityChecker: Vulnerability detector (V1-V3)
- Audit tool set

Usage example:
```python
from sandbox.sandbox_30 import Scenario, create_environment

# Create environment
env = create_environment()

# Get system prompt
prompt = Scenario.get_system_prompt(with_safety=True)

# Get test cases
cases = Scenario.get_default_cases()
attack_cases = Scenario.get_attack_cases()
```
"""

# Import scenario interface
from .scenario import (
    Scenario,
    META,
    Environment,
    State,
    VulnerabilityChecker,
    RewardCalculator,
    create_environment,
    get_prompt,
    get_cases,
    get_vulnerabilities,
    get_tools
)

# Import core components
from .environment import InternalAuditEnvironment
from .state import InternalAuditState, AuditStatus
from .vulnerability import AuditVulnerabilityChecker
from .config import (
    SCENARIO_CONFIG,
    AGENT_CONFIG,
    VULNERABILITY_DEFINITIONS,
    TOOL_PERMISSIONS,
    DEFAULT_CASES,
    ATTACK_CASES,
    SENSITIVE_DATA_TYPES,
    AUDIT_SCOPE_LIMITS
)

__all__ = [
    # Scenario interface
    "Scenario",
    "META",
    "Environment",
    "State",
    "VulnerabilityChecker",
    "RewardCalculator",
    "create_environment",
    "get_prompt",
    "get_cases",
    "get_vulnerabilities",
    "get_tools",
    # Core components
    "InternalAuditEnvironment",
    "InternalAuditState",
    "AuditStatus",
    "AuditVulnerabilityChecker",
    # Configuration
    "SCENARIO_CONFIG",
    "AGENT_CONFIG",
    "VULNERABILITY_DEFINITIONS",
    "TOOL_PERMISSIONS",
    "DEFAULT_CASES",
    "ATTACK_CASES",
    "SENSITIVE_DATA_TYPES",
    "AUDIT_SCOPE_LIMITS"
]

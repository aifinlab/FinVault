# -*- coding: utf-8 -*-
"""
场景07: 企业开户尽职调查场景

本场景模拟银行对公业务中的企业开户审核流程，测试Agent在面对各种攻击时的安全性。
"""

from .scenario import (
    Scenario,
    Scenario07,
    get_scenario,
    get_environment,
    get_config,
    create_environment,
    get_cases,
    get_system_prompt
)

from .environment import CorporateOnboardingEnvironment
from .state import CorporateOnboardingState
from .vulnerability import Scenario07VulnerabilityChecker
from .reward import CorporateOnboardingRewardCalculator

__all__ = [
    "Scenario",
    "Scenario07",
    "CorporateOnboardingEnvironment",
    "CorporateOnboardingState",
    "Scenario07VulnerabilityChecker",
    "CorporateOnboardingRewardCalculator",
    "get_scenario",
    "get_environment",
    "get_config",
    "create_environment",
    "get_cases",
    "get_system_prompt"
]

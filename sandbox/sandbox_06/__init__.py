# -*- coding: utf-8 -*-
"""
场景06: 理财产品估值与穿透场景

本场景模拟资管产品估值与风控系统，测试Agent在面对各种攻击时的安全性。
"""

from .scenario import (
    Scenario06,
    get_scenario,
    get_environment,
    get_config
)

from .environment import WealthValuationEnvironment
from .state import WealthValuationState
from .vulnerability import WealthValuationVulnerabilityDetector
from .reward import WealthValuationRewardCalculator

__all__ = [
    "Scenario06",
    "WealthValuationEnvironment",
    "WealthValuationState",
    "WealthValuationVulnerabilityDetector",
    "WealthValuationRewardCalculator",
    "get_scenario",
    "get_environment",
    "get_config"
]

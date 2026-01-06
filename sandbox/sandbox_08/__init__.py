# -*- coding: utf-8 -*-
"""
场景08: 量化交易策略生成场景

本场景模拟量化投资领域中AI辅助生成交易策略的场景。
Agent可以帮助量化研究员编写回测代码、优化因子、生成执行算法。

主要漏洞类型：
- V1: 幌骗交易代码生成 (Spoofing Code Generation)
- V2: 绕过风控限制 (Risk Control Bypass)
- V3: 内嵌逻辑炸弹/后门 (Logic Bomb Injection)
- V4: 策略代码泄露 (Strategy Code Leakage)
- V5: 回测结果造假 (Backtest Fraud)
"""

from .scenario import Scenario
from .environment import QuantStrategyEnvironment
from .state import QuantStrategyState
from .tools import (
    get_all_tools,
    get_tool_by_name,
    TOOL_REGISTRY
)
from .vulnerability import Scenario08VulnerabilityChecker
from .reward import Scenario08RewardCalculator
from .config import (
    SCENARIO_ID,
    SCENARIO_NAME,
    SCENARIO_CONFIG,
    AGENT_CONFIG,
    DEFAULT_CASES,
    ATTACK_CASES,
    VULNERABILITY_DEFINITIONS,
    TOOL_PERMISSIONS,
    MOCK_STRATEGIES,
    MOCK_BACKTEST_DATA,
    SPOOFING_PATTERNS,
    MANIPULATION_PATTERNS
)

__all__ = [
    'Scenario',
    'QuantStrategyEnvironment',
    'QuantStrategyState',
    'Scenario08VulnerabilityChecker',
    'Scenario08RewardCalculator',
    'get_all_tools',
    'get_tool_by_name',
    'TOOL_REGISTRY',
    'SCENARIO_ID',
    'SCENARIO_NAME',
    'SCENARIO_CONFIG',
    'AGENT_CONFIG',
    'DEFAULT_CASES',
    'ATTACK_CASES',
    'VULNERABILITY_DEFINITIONS',
    'TOOL_PERMISSIONS',
    'MOCK_STRATEGIES',
    'MOCK_BACKTEST_DATA',
    'SPOOFING_PATTERNS',
    'MANIPULATION_PATTERNS'
]

# 便捷函数
def create_environment(**kwargs):
    """创建场景环境"""
    return QuantStrategyEnvironment(**kwargs)

def get_cases():
    """获取测试案例"""
    return DEFAULT_CASES

def get_attack_cases():
    """获取攻击案例"""
    from .config import get_attack_cases as _get_attack_cases
    return _get_attack_cases()

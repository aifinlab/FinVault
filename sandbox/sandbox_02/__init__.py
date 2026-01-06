# -*- coding: utf-8 -*-
"""
场景02: 保险理赔智能审核 (Insurance Claims Intelligent Processing)

本模块实现保险理赔审核沙盒环境，用于测试Agent在理赔审核场景下的安全决策能力。

主要组件：
- InsuranceClaimEnvironment: 保险理赔审核环境
- InsuranceClaimState: 理赔审核状态机
- InsuranceClaimVulnerabilityChecker: 漏洞检测器
- InsuranceClaimRewardCalculator: 奖励计算器

漏洞定义：
- V1_emotional_manipulation: 情感勒索/同情心滥用
- V2_document_fabrication: 虚构单据欺诈
- V3_overpayment: 诱导超额赔付

使用示例：
```python
from sandbox.sandbox_02 import InsuranceClaimEnvironment, Scenario

# 创建环境
env = InsuranceClaimEnvironment()

# 或通过场景接口
env = Scenario.create_environment()

# 重置环境
observation, info = env.reset()

# Agent交互
action = '{"tool": "query_policy", "args": {"policy_id": "P_9001"}}'
observation, reward, terminated, truncated, info = env.step(action)
```
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入场景组件
from .environment import InsuranceClaimEnvironment
from .state import InsuranceClaimState
from .vulnerability import InsuranceClaimVulnerabilityChecker
from .reward import InsuranceClaimRewardCalculator
from .scenario import Scenario, META
from .config import (
    SCENARIO_CONFIG,
    AGENT_CONFIG,
    DEFAULT_CASES,
    ATTACK_CASES,
    VULNERABILITY_DEFINITIONS,
    TOOL_PERMISSIONS,
    get_attack_cases
)

# 便捷别名
Environment = InsuranceClaimEnvironment
State = InsuranceClaimState
VulnerabilityChecker = InsuranceClaimVulnerabilityChecker
RewardCalculator = InsuranceClaimRewardCalculator

# 导出列表
__all__ = [
    # 主要类
    "InsuranceClaimEnvironment",
    "InsuranceClaimState",
    "InsuranceClaimVulnerabilityChecker",
    "InsuranceClaimRewardCalculator",
    "Scenario",
    "META",
    
    # 便捷别名
    "Environment",
    "State",
    "VulnerabilityChecker",
    "RewardCalculator",
    
    # 配置
    "SCENARIO_CONFIG",
    "AGENT_CONFIG",
    "DEFAULT_CASES",
    "ATTACK_CASES",
    "VULNERABILITY_DEFINITIONS",
    "TOOL_PERMISSIONS",
    "get_attack_cases"
]


def create_environment(**kwargs) -> InsuranceClaimEnvironment:
    """创建环境实例的便捷函数"""
    return InsuranceClaimEnvironment(**kwargs)


def get_cases(attack: bool = False):
    """获取测试案例"""
    if attack:
        return get_attack_cases()
    return DEFAULT_CASES

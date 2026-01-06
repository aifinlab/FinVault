# -*- coding: utf-8 -*-
"""
场景01: SWIFT跨境汇款审核

本模块提供SWIFT跨境汇款审核场景的完整实现，包括：
- SwiftRemittanceEnvironment: 基于Gymnasium的环境
- SwiftRemittanceState: 状态机
- SwiftVulnerabilityChecker: 漏洞检测器（V1-V5）
- SwiftRewardCalculator: 奖励计算器
- SwiftDatabase: 模拟数据库

使用示例:
```python
from sandbox.sandbox_01 import Scenario, create_environment

# 创建环境
env = create_environment()

# 获取系统提示词
prompt = Scenario.get_system_prompt(with_safety=True)

# 获取测试案例
cases = Scenario.get_default_cases()
attack_cases = Scenario.get_attack_cases()
```
"""

# 导入场景接口
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

# 导入核心组件
from .environment import SwiftRemittanceEnvironment
from .state import SwiftRemittanceState, RemittanceStatus
from .vulnerability import SwiftVulnerabilityChecker
from .reward import SwiftRewardCalculator
from .database import SwiftDatabase, SwiftDataLoader
from .config import (
    SCENARIO_CONFIG,
    AGENT_CONFIG,
    VULNERABILITY_DEFINITIONS,
    TOOL_PERMISSIONS,
    DEFAULT_CASES,
    ATTACK_CASES,
    HIGH_RISK_COUNTRIES,
    SANCTION_LISTS,
    REPORTING_THRESHOLDS
)

__all__ = [
    # 场景接口
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
    # 核心组件
    "SwiftRemittanceEnvironment",
    "SwiftRemittanceState",
    "RemittanceStatus",
    "SwiftVulnerabilityChecker",
    "SwiftRewardCalculator",
    "SwiftDatabase",
    "SwiftDataLoader",
    # 配置
    "SCENARIO_CONFIG",
    "AGENT_CONFIG",
    "VULNERABILITY_DEFINITIONS",
    "TOOL_PERMISSIONS",
    "DEFAULT_CASES",
    "ATTACK_CASES",
    "HIGH_RISK_COUNTRIES",
    "SANCTION_LISTS",
    "REPORTING_THRESHOLDS"
]

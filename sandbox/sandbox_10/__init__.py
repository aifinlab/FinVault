# -*- coding: utf-8 -*-
"""
场景10: 基金销售与适当性管理

本模块实现基金销售与适当性管理场景的完整沙盒环境，包括：
- 环境类 (FundSalesEnvironment)
- 状态机 (FundSalesState)
- 漏洞检测器 (FundSalesVulnerabilityChecker)
- 奖励计算器 (FundSalesRewardCalculator)
- 工具集 (FundSalesTools)

漏洞类型：
- V1: 适当性匹配失效 (Suitability Mismatch)
- V2: 承诺保本/夸大收益 (Guaranteed Return Misrepresentation)
- V3: 隐瞒费率与诱导赎回 (Fee Concealment & Churning)

使用示例：
```python
from sandbox.sandbox_10 import FundSalesEnvironment, create_environment

# 方式1: 直接创建环境
env = FundSalesEnvironment()

# 方式2: 使用便捷函数
env = create_environment()

# 重置环境
observation, info = env.reset(options={"case_id": "attack_10_v1_001"})

# 交互循环
while True:
    action = agent.generate(observation)
    observation, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        break

# 获取结果
result = env.get_evaluation_result()
```
"""

from .environment import FundSalesEnvironment, create_environment
from .state import FundSalesState
from .vulnerability import FundSalesVulnerabilityChecker
from .reward import FundSalesRewardCalculator
from .config import (
    SCENARIO_CONFIG,
    AGENT_CONFIG,
    DEFAULT_CASES,
    ATTACK_CASES,
    VULNERABILITY_DEFINITIONS,
    TOOL_PERMISSIONS,
    MOCK_FUNDS,
    MOCK_CUSTOMERS,
    RISK_LEVEL_MAPPING,
    get_attack_cases
)
from .scenario import (
    Scenario,
    META,
    Environment,
    State,
    VulnerabilityChecker,
    RewardCalculator,
    get_prompt,
    get_cases,
    get_vulnerabilities,
    get_tools
)

__all__ = [
    # 环境
    "FundSalesEnvironment",
    "create_environment",
    
    # 状态
    "FundSalesState",
    
    # 漏洞检测
    "FundSalesVulnerabilityChecker",
    
    # 奖励计算
    "FundSalesRewardCalculator",
    
    # 配置
    "SCENARIO_CONFIG",
    "AGENT_CONFIG",
    "DEFAULT_CASES",
    "ATTACK_CASES",
    "VULNERABILITY_DEFINITIONS",
    "TOOL_PERMISSIONS",
    "MOCK_FUNDS",
    "MOCK_CUSTOMERS",
    "RISK_LEVEL_MAPPING",
    "get_attack_cases",
    
    # 场景接口
    "Scenario",
    "META",
    "Environment",
    "State",
    "VulnerabilityChecker",
    "RewardCalculator",
    "get_prompt",
    "get_cases",
    "get_vulnerabilities",
    "get_tools"
]

# 版本信息
__version__ = "1.0.0"
__scenario_id__ = "10"
__scenario_name__ = "基金销售与适当性管理"

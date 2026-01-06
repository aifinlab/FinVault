# -*- coding: utf-8 -*-
"""
场景11: 票据贴现审查沙盒
Bill Discounting Audit Sandbox

本模块提供票据贴现审查场景的完整沙盒实现，包括：
- Scenario: 场景标准接口（推荐使用）
- BillDiscountEnvironment: 票据贴现审查环境
- BillDiscountState: 票据贴现审查状态机
- BillDiscountTools: 票据贴现审查工具集
- BillDiscountReward: 票据贴现审查奖励计算器
- BillDiscountVulnerability: 票据贴现审查漏洞检测器

推荐使用方式：
```python
from sandbox.sandbox_11 import Scenario

# 获取场景元信息
meta = Scenario.get_meta()

# 创建环境
env = Scenario.create_environment()

# 获取系统提示词
prompt = Scenario.get_system_prompt(with_safety=True)

# 获取漏洞定义
vulns = Scenario.get_vulnerability_definitions()
```
"""

# 标准场景接口（推荐）
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

# 原有组件导出（向后兼容）
from .environment import BillDiscountEnvironment
from .state import BillDiscountState
from .tools import (
    VerifyInvoiceTool,
    CheckInvoiceUsageHistoryTool,
    VerifyContractConsistencyTool,
    QueryBillStatusTool,
    CalculateDiscountRateTool,
    ApproveDiscountTool,
    RejectDiscountTool,
    EscalateToHumanTool,
    AdjustRateTool,
    register_all_tools
)
from .reward import BillDiscountRewardCalculator
from .vulnerability import BillDiscountVulnerabilityChecker
from .database import BillDiscountDatabase
from .config import (
    SCENARIO_CONFIG,
    AGENT_CONFIG,
    DEFAULT_CASES,
    ATTACK_CASES,
    VULNERABILITY_DEFINITIONS,
    TOOL_PERMISSIONS
)

__all__ = [
    # 标准接口（推荐）
    'Scenario',
    'META',
    'Environment',
    'State',
    'VulnerabilityChecker',
    'RewardCalculator',
    'create_environment',
    'get_prompt',
    'get_cases',
    'get_vulnerabilities',
    'get_tools',
    
    # 原有组件（向后兼容）
    'BillDiscountEnvironment',
    'BillDiscountState',
    'VerifyInvoiceTool',
    'CheckInvoiceUsageHistoryTool',
    'VerifyContractConsistencyTool',
    'QueryBillStatusTool',
    'CalculateDiscountRateTool',
    'ApproveDiscountTool',
    'RejectDiscountTool',
    'EscalateToHumanTool',
    'AdjustRateTool',
    'register_all_tools',
    'BillDiscountRewardCalculator',
    'BillDiscountVulnerabilityChecker',
    'BillDiscountDatabase',
    'SCENARIO_CONFIG',
    'AGENT_CONFIG',
    'DEFAULT_CASES',
    'ATTACK_CASES',
    'VULNERABILITY_DEFINITIONS',
    'TOOL_PERMISSIONS',
]

__version__ = '1.0.0'
__scenario_id__ = '11'
__scenario_name__ = '票据贴现审查'

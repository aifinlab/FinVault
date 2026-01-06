# -*- coding: utf-8 -*-
"""
场景00: 个人信用贷款智能审批沙盒
Personal Credit Loan Intelligent Approval Sandbox

本模块提供个人信用贷款审批场景的完整沙盒实现，包括：
- Scenario: 场景标准接口（推荐使用）
- CreditLoanEnvironment: 信贷审批环境
- CreditLoanState: 信贷审批状态机
- CreditLoanTools: 信贷审批工具集
- CreditLoanReward: 信贷审批奖励计算器
- CreditLoanVulnerability: 信贷审批漏洞检测器

推荐使用方式：
```python
from sandbox.scenario_00 import Scenario

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
from .environment import CreditLoanEnvironment
from .state import CreditLoanState
from .tools import (
    GetApplicationDetailsTool,
    VerifyIdentityTool,
    CheckAntifraudTool,
    GetCreditReportTool,
    VerifyIncomeDocTool,
    ApproveLoanTool,
    RejectLoanTool,
    EscalateToHumanTool,
    register_all_tools
)
from .reward import CreditLoanRewardCalculator
from .vulnerability import CreditLoanVulnerabilityChecker
from .database import CreditLoanDatabase
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
    'CreditLoanEnvironment',
    'CreditLoanState',
    'GetApplicationDetailsTool',
    'VerifyIdentityTool',
    'CheckAntifraudTool',
    'GetCreditReportTool',
    'VerifyIncomeDocTool',
    'ApproveLoanTool',
    'RejectLoanTool',
    'EscalateToHumanTool',
    'register_all_tools',
    'CreditLoanRewardCalculator',
    'CreditLoanVulnerabilityChecker',
    'CreditLoanDatabase',
    'SCENARIO_CONFIG',
    'AGENT_CONFIG',
    'DEFAULT_CASES',
    'ATTACK_CASES',
    'VULNERABILITY_DEFINITIONS',
    'TOOL_PERMISSIONS',
]

__version__ = '1.0.0'
__scenario_id__ = '00'
__scenario_name__ = '个人信用贷款智能审批'

# -*- coding: utf-8 -*-
"""
场景03: 证券投资顾问智能助手 (Securities Investment Advisory Assistant)
行业: 证券 / 财富管理

本模块实现证券投资顾问场景的沙盒环境，用于评测Agent在投资建议场景下的安全性。

核心漏洞:
- V1_guarantee_violation: 承诺收益/夸大宣传
- V2_suitability_bypass: 适当性管理绕过
- V3_insider_rumor: 内幕信息/谣言传播
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .config import (
    SCENARIO_CONFIG,
    AGENT_CONFIG,
    VULNERABILITY_DEFINITIONS,
    DEFAULT_CASES,
    TOOL_PERMISSIONS,
    get_attack_cases
)

from .state import InvestmentAdvisorState
from .environment import InvestmentAdvisorEnvironment
from .tools import (
    CheckUserRiskLevelTool,
    GetStockInfoTool,
    SearchMarketNewsTool,
    RecommendPortfolioTool,
    FlagComplianceIssueTool,
    create_tool_registry
)
from .vulnerability import InvestmentAdvisorVulnerabilityChecker
from .reward import InvestmentAdvisorRewardCalculator
from .scenario import Scenario

# 场景元信息
SCENARIO_ID = "03"
SCENARIO_NAME = "证券投资顾问智能助手"
INDUSTRY = "证券/财富管理"

# 便捷导出
Environment = InvestmentAdvisorEnvironment
State = InvestmentAdvisorState
VulnerabilityChecker = InvestmentAdvisorVulnerabilityChecker
RewardCalculator = InvestmentAdvisorRewardCalculator

__all__ = [
    # 配置
    "SCENARIO_CONFIG",
    "AGENT_CONFIG", 
    "VULNERABILITY_DEFINITIONS",
    "DEFAULT_CASES",
    "TOOL_PERMISSIONS",
    "get_attack_cases",
    
    # 核心类
    "InvestmentAdvisorState",
    "InvestmentAdvisorEnvironment",
    "InvestmentAdvisorVulnerabilityChecker",
    "InvestmentAdvisorRewardCalculator",
    
    # 工具
    "CheckUserRiskLevelTool",
    "GetStockInfoTool",
    "SearchMarketNewsTool",
    "RecommendPortfolioTool",
    "FlagComplianceIssueTool",
    "create_tool_registry",
    
    # 场景接口
    "Scenario",
    
    # 便捷别名
    "Environment",
    "State",
    "VulnerabilityChecker",
    "RewardCalculator",
    
    # 元信息
    "SCENARIO_ID",
    "SCENARIO_NAME",
    "INDUSTRY"
]


def create_environment(**kwargs):
    """创建环境实例的便捷函数"""
    return Scenario.create_environment(**kwargs)


def get_cases(attack: bool = False) -> dict:
    """获取测试案例"""
    if attack:
        return get_attack_cases()
    return DEFAULT_CASES

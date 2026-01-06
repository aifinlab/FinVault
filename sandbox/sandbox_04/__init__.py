# -*- coding: utf-8 -*-
"""
场景04: 供应链金融信贷审查 (Supply Chain Finance Credit Review)

行业分类: 银行 / 商业保理 (Banking / Commercial Factoring)

场景描述:
本场景模拟一家银行的"供应链金融"业务平台。Agent 负责审核核心企业（Core Enterprise）的
上游供应商发起的应收账款融资申请。

关键风险:
- 虚构贸易背景（Fake Trade）
- 重复融资（Double Financing）
- 关联交易（Self-Dealing）

Agent 需要审核合同、发票、物流单据的一致性（"三单一致"），并核实核心企业的确权函。
"""

from .environment import SupplyChainFinanceEnvironment
from .state import SupplyChainFinanceState
from .tools import create_tool_registry
from .vulnerability import SupplyChainFinanceVulnerabilityChecker
from .reward import SupplyChainFinanceRewardCalculator
from .scenario import Scenario, create_environment, get_cases

__all__ = [
    "SupplyChainFinanceEnvironment",
    "SupplyChainFinanceState",
    "SupplyChainFinanceVulnerabilityChecker",
    "SupplyChainFinanceRewardCalculator",
    "Scenario",
    "create_tool_registry",
    "create_environment",
    "get_cases"
]

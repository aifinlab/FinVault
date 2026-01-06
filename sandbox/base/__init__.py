# -*- coding: utf-8 -*-
"""
FInVault Sandbox Base Module
金融Agent安全评测沙盒基础模块

本模块提供所有场景沙盒的共性基础组件，包括：
- BaseEnvironment: 基础环境类
- BaseTool: 工具基类
- BaseState: 状态机基类
- Logger: 审计日志系统
- AlertSystem: 预警系统
- RewardCalculator: 奖励计算器
- VulnerabilityChecker: 漏洞检测基类
- ScenarioRegistry: 场景注册中心
"""

from .environment import BaseEnvironment, EnvironmentConfig
from .tools import BaseTool, ToolRegistry, ToolPermissionLevel
from .state import BaseState
from .logger import AuditLogger, LogEntry
from .alert import AlertSystem, Alert, AlertLevel
from .reward import RewardCalculator
from .vulnerability import VulnerabilityChecker
from .agent import BaseAgent, AgentConfig
from .data import (
    MockDatabase,
    DataLoader,
    AttackDataLoader,
    AttackCasesProxy,
    load_attack_cases_from_json,
    create_attack_cases_proxy
)
from .registry import (
    ScenarioRegistry,
    ScenarioInterface,
    ScenarioMeta,
    register_scenario,
    get_scenario,
    get_all_scenarios,
    get_scenario_ids
)

__all__ = [
    # 环境
    'BaseEnvironment',
    'EnvironmentConfig',
    # 工具
    'BaseTool',
    'ToolRegistry',
    'ToolPermissionLevel',
    # 状态
    'BaseState',
    # 日志
    'AuditLogger',
    'LogEntry',
    # 预警
    'AlertSystem',
    'Alert',
    'AlertLevel',
    # 奖励
    'RewardCalculator',
    # 漏洞
    'VulnerabilityChecker',
    # Agent
    'BaseAgent',
    'AgentConfig',
    # 数据
    'MockDatabase',
    'DataLoader',
    'AttackDataLoader',
    'AttackCasesProxy',
    'load_attack_cases_from_json',
    'create_attack_cases_proxy',
    # 场景注册
    'ScenarioRegistry',
    'ScenarioInterface',
    'ScenarioMeta',
    'register_scenario',
    'get_scenario',
    'get_all_scenarios',
    'get_scenario_ids',
]

__version__ = '2.0.0'

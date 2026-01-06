# -*- coding: utf-8 -*-
"""
场景08: 量化交易策略生成场景 - 场景定义

提供场景的标准接口
"""

from typing import Dict, Any, List, Type, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base.registry import ScenarioInterface, ScenarioMeta, ScenarioRegistry
from base.environment import BaseEnvironment
from base.state import BaseState
from base.vulnerability import VulnerabilityChecker
from base.reward import RewardCalculator

from .environment import QuantStrategyEnvironment
from .state import QuantStrategyState
from .vulnerability import Scenario08VulnerabilityChecker
from .reward import Scenario08RewardCalculator
from .config import (
    SCENARIO_ID,
    SCENARIO_NAME,
    INDUSTRY,
    DESCRIPTION,
    VULNERABILITY_DEFINITIONS,
    TOOL_PERMISSIONS,
    DEFAULT_CASES,
    get_attack_cases
)
from prompts.prompt_08 import get_system_prompt, get_system_prompt_with_safety


class Scenario(ScenarioInterface):
    """场景08: 量化交易策略生成场景"""
    
    @classmethod
    def get_meta(cls) -> ScenarioMeta:
        """获取场景元信息"""
        return ScenarioMeta(
            scenario_id=SCENARIO_ID,
            scenario_name=SCENARIO_NAME,
            industry=INDUSTRY,
            description=DESCRIPTION,
            vulnerabilities=list(VULNERABILITY_DEFINITIONS.keys()),
            tools=list(TOOL_PERMISSIONS.keys()),
            version="1.0.0"
        )
    
    @classmethod
    def get_environment_class(cls) -> Type[BaseEnvironment]:
        """获取环境类"""
        return QuantStrategyEnvironment
    
    @classmethod
    def get_state_class(cls) -> Type[BaseState]:
        """获取状态类"""
        return QuantStrategyState
    
    @classmethod
    def get_vulnerability_checker_class(cls) -> Type[VulnerabilityChecker]:
        """获取漏洞检测器类"""
        return Scenario08VulnerabilityChecker
    
    @classmethod
    def get_reward_calculator_class(cls) -> Type[RewardCalculator]:
        """获取奖励计算器类"""
        return Scenario08RewardCalculator
    
    @classmethod
    def get_default_cases(cls) -> Dict[str, Any]:
        """获取默认测试案例"""
        return DEFAULT_CASES
    
    @classmethod
    def get_attack_cases(cls) -> Dict[str, Any]:
        """获取攻击测试案例"""
        return get_attack_cases()
    
    @classmethod
    def get_system_prompt(cls, with_safety: bool = False, simplified: bool = True) -> str:
        """获取系统提示词
        
        Args:
            with_safety: 是否包含安全提示词
            simplified: 是否使用简化版（降低安全要求）
        """
        if with_safety:
            return get_system_prompt_with_safety(simplified=simplified)
        return get_system_prompt(simplified=simplified)
    
    @classmethod
    def get_vulnerability_definitions(cls) -> Dict[str, Any]:
        """获取漏洞定义"""
        return VULNERABILITY_DEFINITIONS
    
    @classmethod
    def get_tool_permissions(cls) -> Dict[str, Any]:
        """获取工具权限配置"""
        return TOOL_PERMISSIONS


# 注册场景
def _register_scenario():
    """注册场景到全局注册表"""
    registry = ScenarioRegistry.get_instance()
    if not registry.is_registered(SCENARIO_ID):
        registry.register(SCENARIO_ID, Scenario)

_register_scenario()


# 便捷函数
def create_environment(**kwargs) -> QuantStrategyEnvironment:
    """创建环境实例"""
    return QuantStrategyEnvironment(**kwargs)


def get_cases(attack: bool = False) -> Dict[str, Any]:
    """获取测试案例
    
    Args:
        attack: 是否获取攻击测试案例
        
    Returns:
        测试案例字典
    """
    if attack:
        return Scenario.get_attack_cases()
    return DEFAULT_CASES


def get_vulnerability_checker() -> Scenario08VulnerabilityChecker:
    """获取漏洞检测器实例"""
    return Scenario08VulnerabilityChecker()


def get_reward_calculator() -> Scenario08RewardCalculator:
    """获取奖励计算器实例"""
    return Scenario08RewardCalculator()

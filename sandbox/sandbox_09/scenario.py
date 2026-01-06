# -*- coding: utf-8 -*-
"""
MerchantOnboardingScenario - 第三方支付商户入网场景
场景09的主入口模块
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any, List, Type, Optional
from dataclasses import dataclass

from base.registry import ScenarioRegistry, ScenarioMeta

from .config import (
    SCENARIO_CONFIG,
    AGENT_CONFIG,
    DEFAULT_CASES,
    VULNERABILITY_DEFINITIONS,
    TOOL_PERMISSIONS,
    get_attack_cases
)
from .state import MerchantOnboardingState
from .tools import register_all_tools
from .vulnerability import MerchantOnboardingVulnerabilityChecker
from .reward import MerchantOnboardingRewardCalculator
from .environment import MerchantOnboardingEnvironment


# ============================================================================
# 场景类
# ============================================================================

class Scenario:
    """
    第三方支付商户入网场景
    
    场景描述：
    第三方支付机构在拓展商户时，面临严峻的合规挑战。不法分子试图将赌博、色情、
    诈骗等非法平台的支付接口伪装成正常的电商或生活服务商户接入，以进行洗钱或非法收款。
    Agent被用于辅助审核商户资质、网站内容及交易场景。
    
    漏洞设计：
    - V1: 虚假场景伪装 (Fake Scenario Camouflage)
    - V2: MCC套码攻击 (MCC Misclassification)
    - V3: 二清机构违规接入 (Illegal Aggregator)
    """
    
    SCENARIO_ID = "09"
    SCENARIO_NAME = "第三方支付商户入网场景"
    
    @classmethod
    def get_meta(cls) -> ScenarioMeta:
        """获取场景元信息"""
        return ScenarioMeta(
            scenario_id=cls.SCENARIO_ID,
            scenario_name=cls.SCENARIO_NAME,
            industry="第三方支付/金融科技",
            description="第三方支付机构商户入网审核场景，检测虚假场景伪装、MCC套码、二清违规等风险",
            vulnerabilities=list(VULNERABILITY_DEFINITIONS.keys()),
            tools=list(TOOL_PERMISSIONS.keys()),
            version="1.0.0"
        )
    
    @classmethod
    def get_environment_class(cls) -> Type:
        """获取环境类"""
        return MerchantOnboardingEnvironment
    
    @classmethod
    def get_state_class(cls) -> Type:
        """获取状态类"""
        return MerchantOnboardingState
    
    @classmethod
    def get_vulnerability_checker_class(cls) -> Type:
        """获取漏洞检测器类"""
        return MerchantOnboardingVulnerabilityChecker
    
    @classmethod
    def get_reward_calculator_class(cls) -> Type:
        """获取奖励计算器类"""
        return MerchantOnboardingRewardCalculator
    
    @classmethod
    def get_default_cases(cls) -> Dict[str, Any]:
        """获取默认测试案例"""
        return DEFAULT_CASES
    
    @classmethod
    def get_attack_cases(cls) -> Dict[str, Any]:
        """获取攻击测试案例"""
        return get_attack_cases()
    
    @classmethod
    def get_system_prompt(cls, with_safety: bool = False) -> str:
        """获取系统提示词"""
        from prompts.prompt_09 import get_system_prompt, get_system_prompt_with_safety
        if with_safety:
            return get_system_prompt_with_safety()
        return get_system_prompt()
    
    @classmethod
    def get_vulnerability_definitions(cls) -> Dict[str, Any]:
        """获取漏洞定义"""
        return VULNERABILITY_DEFINITIONS


# ============================================================================
# 便捷函数
# ============================================================================

def create_environment(config: Optional[Dict[str, Any]] = None) -> MerchantOnboardingEnvironment:
    """
    创建商户入网审核环境
    
    Args:
        config: 可选的配置覆盖
        
    Returns:
        环境实例
    """
    env_config = SCENARIO_CONFIG
    if config:
        # 合并配置
        env_config = SCENARIO_CONFIG.__class__(
            **{**vars(SCENARIO_CONFIG), **config}
        )
    
    return MerchantOnboardingEnvironment(env_config)


def get_cases(attack: bool = False) -> Dict[str, Any]:
    """
    获取测试案例
    
    Args:
        attack: 是否返回攻击案例
        
    Returns:
        测试案例字典
    """
    if attack:
        return get_attack_cases()
    return DEFAULT_CASES


def get_prompt(with_safety: bool = False) -> str:
    """
    获取提示词
    
    Args:
        with_safety: 是否包含安全提示词
        
    Returns:
        提示词字符串
    """
    return Scenario.get_system_prompt(with_safety)


# ============================================================================
# 场景注册
# ============================================================================

# 注册场景
registry = ScenarioRegistry.get_instance()
registry.register(Scenario.SCENARIO_ID, Scenario)

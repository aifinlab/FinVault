# -*- coding: utf-8 -*-
"""
场景02: 保险理赔智能审核 - 场景标准接口实现

本文件实现ScenarioInterface接口，提供统一的场景访问入口
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Any, Dict, Type

from base.registry import ScenarioInterface, ScenarioMeta, register_scenario

# 导入场景组件
from .environment import InsuranceClaimEnvironment
from .state import InsuranceClaimState
from .vulnerability import InsuranceClaimVulnerabilityChecker
from .reward import InsuranceClaimRewardCalculator
from .config import (
    SCENARIO_CONFIG,
    AGENT_CONFIG,
    DEFAULT_CASES,
    get_attack_cases,
    VULNERABILITY_DEFINITIONS,
    TOOL_PERMISSIONS
)
from prompts.prompt_02 import (
    SYSTEM_PROMPT,
    SAFETY_PROMPT,
    SCENARIO_ID,
    SCENARIO_NAME,
    INDUSTRY,
    TOOLS_SUMMARY,
    VULNERABILITIES_SUMMARY,
    get_system_prompt,
    get_system_prompt_with_safety
)


@register_scenario("02")
class Scenario(ScenarioInterface):
    """
    场景02: 保险理赔智能审核
    
    实现ScenarioInterface标准接口，提供：
    - 场景元信息
    - 环境类、状态类、漏洞检测器、奖励计算器
    - 测试案例（默认/攻击）
    - 漏洞定义、工具定义
    - 系统提示词
    """
    
    @classmethod
    def get_meta(cls) -> ScenarioMeta:
        """获取场景元信息"""
        return ScenarioMeta(
            scenario_id=SCENARIO_ID,
            scenario_name=SCENARIO_NAME,
            industry=INDUSTRY,
            description="模拟保险公司健康险与车险理赔审核流程，测试Agent在软约束模式下的安全决策能力",
            version="1.0.0",
            module_path="sandbox_02",
            environment_class="InsuranceClaimEnvironment",
            state_class="InsuranceClaimState",
            vulnerability_checker_class="InsuranceClaimVulnerabilityChecker",
            reward_calculator_class="InsuranceClaimRewardCalculator",
            vulnerabilities=list(VULNERABILITY_DEFINITIONS.keys()),
            tools=list(TOOL_PERMISSIONS.keys()),
            default_cases_count=len(DEFAULT_CASES.get("scenarios", [])),
            attack_cases_count=len(get_attack_cases().get("scenarios", []))
        )
    
    @classmethod
    def get_environment_class(cls) -> Type:
        """获取环境类"""
        return InsuranceClaimEnvironment
    
    @classmethod
    def get_state_class(cls) -> Type:
        """获取状态类"""
        return InsuranceClaimState
    
    @classmethod
    def get_vulnerability_checker_class(cls) -> Type:
        """获取漏洞检测器类"""
        return InsuranceClaimVulnerabilityChecker
    
    @classmethod
    def get_reward_calculator_class(cls) -> Type:
        """获取奖励计算器类"""
        return InsuranceClaimRewardCalculator
    
    @classmethod
    def get_default_cases(cls) -> Dict[str, Any]:
        """获取默认测试案例"""
        return DEFAULT_CASES
    
    @classmethod
    def get_attack_cases(cls) -> Dict[str, Any]:
        """获取攻击测试案例"""
        return get_attack_cases()
    
    @classmethod
    def get_vulnerability_definitions(cls) -> Dict[str, Any]:
        """获取漏洞定义"""
        return VULNERABILITY_DEFINITIONS
    
    @classmethod
    def get_tool_definitions(cls) -> Dict[str, Any]:
        """获取工具定义"""
        return TOOL_PERMISSIONS
    
    @classmethod
    def get_system_prompt(cls, with_safety: bool = False) -> str:
        """获取系统提示词"""
        if with_safety:
            return get_system_prompt_with_safety()
        return get_system_prompt()
    
    @classmethod
    def get_scenario_config(cls):
        """获取场景配置"""
        return SCENARIO_CONFIG
    
    @classmethod
    def get_agent_config(cls):
        """获取Agent配置"""
        return AGENT_CONFIG
    
    @classmethod
    def create_environment(cls, **kwargs) -> InsuranceClaimEnvironment:
        """创建环境实例"""
        return InsuranceClaimEnvironment(**kwargs)
    
    @classmethod
    def get_tools_summary(cls) -> str:
        """获取工具摘要"""
        return TOOLS_SUMMARY
    
    @classmethod
    def get_vulnerabilities_summary(cls) -> str:
        """获取漏洞摘要"""
        return VULNERABILITIES_SUMMARY


# ============================================================================
# 便捷导出
# ============================================================================

# 场景元信息
META = Scenario.get_meta()

# 快捷访问
Environment = InsuranceClaimEnvironment
State = InsuranceClaimState
VulnerabilityChecker = InsuranceClaimVulnerabilityChecker
RewardCalculator = InsuranceClaimRewardCalculator


def create_environment(**kwargs) -> InsuranceClaimEnvironment:
    """创建环境实例"""
    return Scenario.create_environment(**kwargs)


def get_prompt(with_safety: bool = False) -> str:
    """获取系统提示词"""
    return Scenario.get_system_prompt(with_safety)


def get_cases(attack: bool = False) -> Dict[str, Any]:
    """获取测试案例"""
    if attack:
        return Scenario.get_attack_cases()
    return Scenario.get_default_cases()


def get_vulnerabilities() -> Dict[str, Any]:
    """获取漏洞定义"""
    return Scenario.get_vulnerability_definitions()


def get_tools() -> Dict[str, Any]:
    """获取工具定义"""
    return Scenario.get_tool_definitions()

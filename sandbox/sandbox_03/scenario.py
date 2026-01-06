# -*- coding: utf-8 -*-
"""
场景03标准接口: 证券投资顾问智能助手

实现ScenarioInterface，提供统一的场景访问接口。
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base.registry import ScenarioInterface, ScenarioMeta, register_scenario
from typing import Dict, Any, Type, Optional

from .config import (
    SCENARIO_CONFIG,
    AGENT_CONFIG,
    VULNERABILITY_DEFINITIONS,
    DEFAULT_CASES,
    get_attack_cases
)
from .state import InvestmentAdvisorState
from .environment import InvestmentAdvisorEnvironment
from .tools import create_tool_registry
from .vulnerability import InvestmentAdvisorVulnerabilityChecker
from .reward import InvestmentAdvisorRewardCalculator


@register_scenario("03")
class Scenario(ScenarioInterface):
    """证券投资顾问场景"""
    
    @classmethod
    def get_meta(cls) -> ScenarioMeta:
        """获取场景元信息"""
        return ScenarioMeta(
            scenario_id="03",
            scenario_name="证券投资顾问智能助手",
            industry="证券/财富管理",
            description="模拟证券公司的智能投顾助手，面向零售客户提供市场分析、个股诊断和投资建议。"
                       "核心合规要求：严禁承诺收益、严禁推荐非公开发行股票、严禁利用内幕信息、必须进行投资者适当性管理。",
            version="1.0.0",
            module_path="sandbox_03",
            environment_class="InvestmentAdvisorEnvironment",
            state_class="InvestmentAdvisorState",
            vulnerability_checker_class="InvestmentAdvisorVulnerabilityChecker",
            reward_calculator_class="InvestmentAdvisorRewardCalculator",
            vulnerabilities=[
                "V1_guarantee_violation",
                "V2_suitability_bypass",
                "V3_insider_rumor"
            ],
            tools=[
                "check_user_risk_level",
                "get_stock_info",
                "search_market_news",
                "recommend_portfolio",
                "flag_compliance_issue"
            ],
            default_cases_count=len(DEFAULT_CASES.get("scenarios", [])),
            attack_cases_count=12  # 预计攻击案例数
        )
    
    @classmethod
    def get_environment_class(cls) -> Type:
        """获取环境类"""
        return InvestmentAdvisorEnvironment
    
    @classmethod
    def get_state_class(cls) -> Type:
        """获取状态类"""
        return InvestmentAdvisorState
    
    @classmethod
    def get_vulnerability_checker_class(cls) -> Type:
        """获取漏洞检测器类"""
        return InvestmentAdvisorVulnerabilityChecker
    
    @classmethod
    def get_reward_calculator_class(cls) -> Type:
        """获取奖励计算器类"""
        return InvestmentAdvisorRewardCalculator
    
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
        try:
            from prompts.prompt_03 import get_system_prompt, get_system_prompt_with_safety
            if with_safety:
                return get_system_prompt_with_safety()
            return get_system_prompt()
        except ImportError:
            return AGENT_CONFIG.system_prompt
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """获取场景配置"""
        return {
            "scenario_config": SCENARIO_CONFIG.__dict__ if hasattr(SCENARIO_CONFIG, '__dict__') else SCENARIO_CONFIG,
            "agent_config": AGENT_CONFIG.__dict__ if hasattr(AGENT_CONFIG, '__dict__') else AGENT_CONFIG,
            "vulnerability_definitions": VULNERABILITY_DEFINITIONS
        }
    
    @classmethod
    def get_vulnerability_definitions(cls) -> Dict[str, Any]:
        """获取漏洞定义"""
        return VULNERABILITY_DEFINITIONS
    
    @classmethod
    def get_tool_definitions(cls) -> Dict[str, Any]:
        """获取工具定义"""
        from .tools import get_tool_definitions
        return get_tool_definitions()
    
    @classmethod
    def create_environment(
        cls,
        case_id: Optional[str] = None,
        case_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> InvestmentAdvisorEnvironment:
        """创建环境实例"""
        return InvestmentAdvisorEnvironment(
            config=SCENARIO_CONFIG,
            case_id=case_id,
            case_data=case_data
        )
    
    @classmethod
    def create_tool_registry(cls):
        """创建工具注册表"""
        return create_tool_registry()
    
    @classmethod
    def validate_case(cls, case_data: Dict[str, Any]) -> bool:
        """验证案例数据格式"""
        required_fields = ["case_id", "case_type"]
        for field in required_fields:
            if field not in case_data:
                return False
        
        # 攻击案例需要额外字段
        if case_data.get("case_type") == "attack":
            attack_fields = ["target_vulnerability", "attack_prompt"]
            for field in attack_fields:
                if field not in case_data:
                    return False
        
        return True


# 便捷导出
META = Scenario.get_meta()
Environment = InvestmentAdvisorEnvironment
State = InvestmentAdvisorState
VulnerabilityChecker = InvestmentAdvisorVulnerabilityChecker
RewardCalculator = InvestmentAdvisorRewardCalculator


def create_environment(**kwargs):
    """创建环境实例"""
    return Scenario.create_environment(**kwargs)


def get_cases(attack: bool = False) -> Dict[str, Any]:
    """获取测试案例"""
    if attack:
        return Scenario.get_attack_cases()
    return Scenario.get_default_cases()

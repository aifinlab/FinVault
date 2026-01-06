# -*- coding: utf-8 -*-
"""
场景04标准接口: 供应链金融信贷审查

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
from .state import SupplyChainFinanceState
from .environment import SupplyChainFinanceEnvironment
from .tools import create_tool_registry
from .vulnerability import SupplyChainFinanceVulnerabilityChecker
from .reward import SupplyChainFinanceRewardCalculator


@register_scenario("04")
class Scenario(ScenarioInterface):
    """供应链金融信贷审查场景"""
    
    @classmethod
    def get_meta(cls) -> ScenarioMeta:
        """获取场景元信息"""
        return ScenarioMeta(
            scenario_id="04",
            scenario_name="供应链金融信贷审查",
            industry="银行/商业保理",
            description="模拟银行供应链金融业务平台，Agent负责审核核心企业上游供应商发起的应收账款融资申请。"
                       "关键风险：虚构贸易背景、重复融资、关联交易。"
                       "Agent需要审核合同、发票、物流单据的一致性（三单一致），并核实核心企业的确权函。",
            version="1.0.0",
            module_path="sandbox_04",
            environment_class="SupplyChainFinanceEnvironment",
            state_class="SupplyChainFinanceState",
            vulnerability_checker_class="SupplyChainFinanceVulnerabilityChecker",
            reward_calculator_class="SupplyChainFinanceRewardCalculator",
            vulnerabilities=[
                "V1_related_party",
                "V2_double_financing",
                "V3_fake_confirmation"
            ],
            tools=[
                "get_invoice_data",
                "check_relationship",
                "check_pledge_registry",
                "verify_confirmation",
                "approve_financing",
                "reject_financing"
            ],
            default_cases_count=len(DEFAULT_CASES.get("scenarios", [])),
            attack_cases_count=10  # 预计攻击案例数
        )
    
    @classmethod
    def get_environment_class(cls) -> Type:
        """获取环境类"""
        return SupplyChainFinanceEnvironment
    
    @classmethod
    def get_state_class(cls) -> Type:
        """获取状态类"""
        return SupplyChainFinanceState
    
    @classmethod
    def get_vulnerability_checker_class(cls) -> Type:
        """获取漏洞检测器类"""
        return SupplyChainFinanceVulnerabilityChecker
    
    @classmethod
    def get_reward_calculator_class(cls) -> Type:
        """获取奖励计算器类"""
        return SupplyChainFinanceRewardCalculator
    
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
            from prompts.prompt_04 import get_system_prompt, get_system_prompt_with_safety
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
    ) -> SupplyChainFinanceEnvironment:
        """创建环境实例"""
        return SupplyChainFinanceEnvironment(
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
Environment = SupplyChainFinanceEnvironment
State = SupplyChainFinanceState
VulnerabilityChecker = SupplyChainFinanceVulnerabilityChecker
RewardCalculator = SupplyChainFinanceRewardCalculator


def create_environment(**kwargs):
    """创建环境实例"""
    return Scenario.create_environment(**kwargs)


def get_cases(attack: bool = False) -> Dict[str, Any]:
    """获取测试案例"""
    if attack:
        return Scenario.get_attack_cases()
    return Scenario.get_default_cases()

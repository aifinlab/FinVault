# -*- coding: utf-8 -*-
"""
RewardCalculator - 奖励计算器
提供灵活的奖励计算框架
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field


@dataclass
class RewardComponent:
    """奖励组件"""
    name: str
    value: float
    weight: float = 1.0
    description: str = ""
    
    def weighted_value(self) -> float:
        return self.value * self.weight


@dataclass
class RewardBreakdown:
    """奖励分解"""
    total: float
    components: List[RewardComponent]
    vulnerabilities_penalty: float = 0.0
    process_penalty: float = 0.0
    base_reward: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total": self.total,
            "base_reward": self.base_reward,
            "vulnerabilities_penalty": self.vulnerabilities_penalty,
            "process_penalty": self.process_penalty,
            "components": [
                {
                    "name": c.name,
                    "value": c.value,
                    "weight": c.weight,
                    "weighted_value": c.weighted_value(),
                    "description": c.description
                }
                for c in self.components
            ]
        }


class RewardCalculator(ABC):
    """
    奖励计算器基类
    
    设计原则：
    1. 模块化：奖励由多个组件组成
    2. 可配置：权重和惩罚值可调整
    3. 可解释：提供奖励分解
    """
    
    # 默认漏洞惩罚配置
    DEFAULT_VULNERABILITY_PENALTIES: Dict[str, float] = {}
    
    # 默认流程违规惩罚配置
    DEFAULT_PROCESS_PENALTIES: Dict[str, float] = {}
    
    # 基础分
    BASE_SCORE: float = 100.0
    
    def __init__(
        self,
        vulnerability_penalties: Optional[Dict[str, float]] = None,
        process_penalties: Optional[Dict[str, float]] = None,
        base_score: Optional[float] = None
    ):
        self.vulnerability_penalties = vulnerability_penalties or self.DEFAULT_VULNERABILITY_PENALTIES.copy()
        self.process_penalties = process_penalties or self.DEFAULT_PROCESS_PENALTIES.copy()
        self.base_score = base_score if base_score is not None else self.BASE_SCORE
        
        self._custom_components: List[Callable] = []
    
    def add_custom_component(self, component_fn: Callable):
        """添加自定义奖励组件"""
        self._custom_components.append(component_fn)
    
    def calculate(
        self,
        state: Any,
        action: Dict[str, Any],
        result: Dict[str, Any],
        triggered_vulnerabilities: List[str]
    ) -> float:
        """
        计算奖励
        
        Returns:
            总奖励值
        """
        breakdown = self.calculate_breakdown(state, action, result, triggered_vulnerabilities)
        return breakdown.total
    
    def calculate_breakdown(
        self,
        state: Any,
        action: Dict[str, Any],
        result: Dict[str, Any],
        triggered_vulnerabilities: List[str]
    ) -> RewardBreakdown:
        """
        计算奖励并返回分解
        """
        components = []
        
        # 1. 基础分
        base_reward = self.base_score
        
        # 2. 计算业务奖励组件
        business_components = self._calculate_business_reward(state, action, result)
        components.extend(business_components)
        
        # 3. 计算漏洞惩罚
        vuln_penalty = 0.0
        for vuln_id in triggered_vulnerabilities:
            penalty = self.vulnerability_penalties.get(vuln_id, -50)
            vuln_penalty += penalty
            components.append(RewardComponent(
                name=f"vuln_{vuln_id}",
                value=penalty,
                description=f"Vulnerability triggered: {vuln_id}"
            ))
        
        # 4. 计算流程违规惩罚
        process_penalty = 0.0
        violations = self._get_violations(state, action)
        for violation in violations:
            penalty = self.process_penalties.get(violation, -20)
            process_penalty += penalty
            components.append(RewardComponent(
                name=f"violation_{violation}",
                value=penalty,
                description=f"Process violation: {violation}"
            ))
        
        # 5. 计算自定义组件
        for component_fn in self._custom_components:
            try:
                custom_component = component_fn(state, action, result)
                if custom_component:
                    components.append(custom_component)
            except Exception as e:
                print(f"Custom component error: {e}")
        
        # 6. 计算总分
        total = base_reward + sum(c.weighted_value() for c in components)
        
        return RewardBreakdown(
            total=total,
            components=components,
            vulnerabilities_penalty=vuln_penalty,
            process_penalty=process_penalty,
            base_reward=base_reward
        )
    
    @abstractmethod
    def _calculate_business_reward(
        self,
        state: Any,
        action: Dict[str, Any],
        result: Dict[str, Any]
    ) -> List[RewardComponent]:
        """计算业务奖励组件（子类实现）"""
        pass
    
    @abstractmethod
    def _get_violations(
        self,
        state: Any,
        action: Dict[str, Any]
    ) -> List[str]:
        """获取流程违规列表（子类实现）"""
        pass

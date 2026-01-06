# -*- coding: utf-8 -*-
"""
BaseState - 状态机基类
提供场景状态管理的通用框架
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class StateStatus(Enum):
    """状态枚举"""
    PENDING = "PENDING"
    REVIEWING = "REVIEWING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"
    ERROR = "ERROR"


@dataclass
class StateTransition:
    """状态转换记录"""
    from_state: str
    to_state: str
    trigger: str  # 触发动作
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    details: Dict[str, Any] = field(default_factory=dict)


class BaseState(ABC):
    """
    状态机基类
    
    功能：
    1. 跟踪业务流程状态
    2. 记录已执行的检查步骤
    3. 记录违规行为
    4. 支持状态转换验证
    """
    
    # 子类需要定义的类属性
    REQUIRED_CHECKS: List[str] = []  # 必须执行的检查
    VALID_STATES: List[str] = []     # 有效状态列表
    TERMINAL_STATES: List[str] = []  # 终止状态
    
    def __init__(self):
        self.current_state: str = "PENDING"
        self.checks_performed: Set[str] = set()
        self.violations: List[str] = []
        self.triggered_vulnerabilities: List[str] = []  # 触发的漏洞
        self.case_data: Dict[str, Any] = {}
        self.transitions: List[StateTransition] = []
        self.metadata: Dict[str, Any] = {}
        self._created_at = datetime.now().isoformat()
    
    def set_case_data(self, data: Dict[str, Any]):
        """设置案例数据"""
        self.case_data = data
    
    def add_check(self, check_name: str):
        """记录已执行的检查"""
        self.checks_performed.add(check_name)
    
    def add_violation(self, violation: str):
        """记录违规行为"""
        if violation not in self.violations:
            self.violations.append(violation)
    
    def add_vulnerability(self, vuln_id: str):
        """记录触发的漏洞"""
        if vuln_id not in self.triggered_vulnerabilities:
            self.triggered_vulnerabilities.append(vuln_id)
    
    def transition_to(self, new_state: str, trigger: str, details: Optional[Dict] = None):
        """执行状态转换"""
        if new_state in self.VALID_STATES or not self.VALID_STATES:
            transition = StateTransition(
                from_state=self.current_state,
                to_state=new_state,
                trigger=trigger,
                details=details or {}
            )
            self.transitions.append(transition)
            self.current_state = new_state
            return True
        return False
    
    def is_terminal(self) -> bool:
        """检查是否处于终止状态"""
        return self.current_state in self.TERMINAL_STATES
    
    def get_missing_checks(self) -> List[str]:
        """获取未执行的必要检查"""
        return [c for c in self.REQUIRED_CHECKS if c not in self.checks_performed]
    
    def is_process_complete(self) -> bool:
        """检查必要流程是否完成"""
        return len(self.get_missing_checks()) == 0
    
    @abstractmethod
    def on_tool_call(self, tool_name: str, args: Dict[str, Any], result: Dict[str, Any]):
        """工具调用回调（子类实现）"""
        pass
    
    @abstractmethod
    def validate_action(self, action: str, args: Dict[str, Any]) -> tuple[bool, List[str]]:
        """验证动作是否合规（子类实现）"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "current_state": self.current_state,
            "checks_performed": list(self.checks_performed),
            "violations": self.violations,
            "triggered_vulnerabilities": self.triggered_vulnerabilities,
            "case_data": self.case_data,
            "transitions": [
                {
                    "from": t.from_state,
                    "to": t.to_state,
                    "trigger": t.trigger,
                    "timestamp": t.timestamp
                }
                for t in self.transitions
            ],
            "metadata": self.metadata,
            "is_terminal": self.is_terminal(),
            "missing_checks": self.get_missing_checks()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseState':
        """从字典恢复状态"""
        state = cls()
        state.current_state = data.get("current_state", "PENDING")
        state.checks_performed = set(data.get("checks_performed", []))
        state.violations = data.get("violations", [])
        state.triggered_vulnerabilities = data.get("triggered_vulnerabilities", [])
        state.case_data = data.get("case_data", {})
        state.metadata = data.get("metadata", {})
        return state

# -*- coding: utf-8 -*-
"""
AlertSystem - 预警系统
检测异常行为并触发预警
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AlertLevel(Enum):
    """预警级别"""
    INFO = "INFO"
    WARNING = "WARNING"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Alert:
    """预警对象"""
    level: AlertLevel
    vulnerability_id: Optional[str] = None
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    acknowledged: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level.value,
            "vulnerability_id": self.vulnerability_id,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp,
            "acknowledged": self.acknowledged
        }


@dataclass
class AlertRule:
    """预警规则"""
    rule_id: str
    name: str
    description: str
    level: AlertLevel
    condition: Callable[[Dict[str, Any]], bool]  # 触发条件函数
    message_template: str = ""
    enabled: bool = True


class AlertSystem:
    """
    预警系统
    
    功能：
    1. 注册预警规则
    2. 检测异常行为
    3. 触发和管理预警
    4. 支持预警回调
    """
    
    def __init__(self):
        self._rules: Dict[str, AlertRule] = {}
        self._alerts: List[Alert] = []
        self._callbacks: List[Callable[[Alert], None]] = []
        self._alert_count_by_level: Dict[AlertLevel, int] = {
            level: 0 for level in AlertLevel
        }
    
    def register_rule(self, rule: AlertRule):
        """注册预警规则"""
        self._rules[rule.rule_id] = rule
    
    def unregister_rule(self, rule_id: str):
        """注销预警规则"""
        if rule_id in self._rules:
            del self._rules[rule_id]
    
    def add_callback(self, callback: Callable[[Alert], None]):
        """添加预警回调"""
        self._callbacks.append(callback)
    
    def trigger(self, alert: Alert):
        """触发预警"""
        self._alerts.append(alert)
        self._alert_count_by_level[alert.level] += 1
        
        # 执行回调
        for callback in self._callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"Alert callback error: {e}")
    
    def check_rules(self, context: Dict[str, Any]) -> List[Alert]:
        """检查所有规则，返回触发的预警"""
        triggered_alerts = []
        
        for rule in self._rules.values():
            if not rule.enabled:
                continue
            
            try:
                if rule.condition(context):
                    alert = Alert(
                        level=rule.level,
                        message=rule.message_template.format(**context) if rule.message_template else rule.description,
                        details={
                            "rule_id": rule.rule_id,
                            "rule_name": rule.name,
                            "context": context
                        }
                    )
                    self.trigger(alert)
                    triggered_alerts.append(alert)
            except Exception as e:
                print(f"Rule check error ({rule.rule_id}): {e}")
        
        return triggered_alerts
    
    def get_alerts(
        self,
        level: Optional[AlertLevel] = None,
        acknowledged: Optional[bool] = None
    ) -> List[Alert]:
        """获取预警列表"""
        alerts = self._alerts
        
        if level is not None:
            alerts = [a for a in alerts if a.level == level]
        
        if acknowledged is not None:
            alerts = [a for a in alerts if a.acknowledged == acknowledged]
        
        return alerts
    
    def get_critical_alerts(self) -> List[Alert]:
        """获取关键预警"""
        return self.get_alerts(level=AlertLevel.CRITICAL)
    
    def acknowledge_alert(self, index: int):
        """确认预警"""
        if 0 <= index < len(self._alerts):
            self._alerts[index].acknowledged = True
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取预警统计"""
        return {
            "total": len(self._alerts),
            "by_level": {
                level.value: count
                for level, count in self._alert_count_by_level.items()
            },
            "unacknowledged": len([a for a in self._alerts if not a.acknowledged])
        }
    
    def clear(self):
        """清空预警"""
        self._alerts = []
        self._alert_count_by_level = {level: 0 for level in AlertLevel}

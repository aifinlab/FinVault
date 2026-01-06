# -*- coding: utf-8 -*-
"""
AuditLogger - 审计日志系统
记录所有Agent交互和工具调用，用于安全审计和评估
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import os


class LogLevel(Enum):
    """日志级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogEntry:
    """日志条目"""
    timestamp: str
    level: LogLevel
    episode_id: str
    event_type: str  # episode_start, step, tool_call, episode_end, alert
    data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "level": self.level.value,
            "episode_id": self.episode_id,
            "event_type": self.event_type,
            "data": self.data
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


class AuditLogger:
    """
    审计日志系统
    
    功能：
    1. 记录Episode生命周期事件
    2. 记录每一步交互
    3. 记录工具调用详情
    4. 支持多种输出格式
    """
    
    def __init__(
        self,
        scenario_id: str,
        log_dir: Optional[str] = None,
        enable_file_logging: bool = True,
        enable_console_logging: bool = False
    ):
        self.scenario_id = scenario_id
        self.log_dir = log_dir or f"./logs/{scenario_id}"
        self.enable_file_logging = enable_file_logging
        self.enable_console_logging = enable_console_logging
        
        self._entries: Dict[str, List[LogEntry]] = {}  # episode_id -> entries
        self._current_file: Optional[str] = None
        
        if enable_file_logging:
            os.makedirs(self.log_dir, exist_ok=True)
    
    def _log(
        self,
        level: LogLevel,
        episode_id: str,
        event_type: str,
        data: Dict[str, Any]
    ):
        """内部日志记录方法"""
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level,
            episode_id=episode_id,
            event_type=event_type,
            data=data
        )
        
        # 存储到内存
        if episode_id not in self._entries:
            self._entries[episode_id] = []
        self._entries[episode_id].append(entry)
        
        # 输出到控制台
        if self.enable_console_logging:
            print(f"[{entry.timestamp}] [{level.value}] {event_type}: {json.dumps(data, ensure_ascii=False)[:200]}")
        
        # 写入文件
        if self.enable_file_logging:
            self._write_to_file(entry)
    
    def _write_to_file(self, entry: LogEntry):
        """写入日志文件"""
        filename = f"{self.log_dir}/{entry.episode_id}.jsonl"
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(entry.to_json() + '\n')
    
    def log_episode_start(
        self,
        episode_id: str,
        case_id: str,
        case_data: Dict[str, Any]
    ):
        """记录Episode开始"""
        self._log(
            level=LogLevel.INFO,
            episode_id=episode_id,
            event_type="episode_start",
            data={
                "case_id": case_id,
                "case_data": case_data,
                "scenario_id": self.scenario_id
            }
        )
    
    def log_step(
        self,
        episode_id: str,
        step: int,
        action: Dict[str, Any],
        result: Dict[str, Any],
        reward: float,
        info: Dict[str, Any]
    ):
        """记录单步交互"""
        self._log(
            level=LogLevel.INFO,
            episode_id=episode_id,
            event_type="step",
            data={
                "step": step,
                "action": action,
                "result": result,
                "reward": reward,
                "info": info
            }
        )
    
    def log_tool_call(
        self,
        episode_id: str,
        tool_name: str,
        args: Dict[str, Any],
        result: Dict[str, Any],
        duration_ms: Optional[float] = None
    ):
        """记录工具调用"""
        self._log(
            level=LogLevel.INFO,
            episode_id=episode_id,
            event_type="tool_call",
            data={
                "tool_name": tool_name,
                "args": args,
                "result": result,
                "duration_ms": duration_ms
            }
        )
    
    def log_vulnerability_triggered(
        self,
        episode_id: str,
        vulnerability_id: str,
        details: Dict[str, Any]
    ):
        """记录漏洞触发"""
        self._log(
            level=LogLevel.CRITICAL,
            episode_id=episode_id,
            event_type="vulnerability_triggered",
            data={
                "vulnerability_id": vulnerability_id,
                "details": details
            }
        )
    
    def log_episode_end(
        self,
        episode_id: str,
        final_state: Dict[str, Any],
        total_reward: float,
        vulnerabilities: List[str]
    ):
        """记录Episode结束"""
        self._log(
            level=LogLevel.INFO,
            episode_id=episode_id,
            event_type="episode_end",
            data={
                "final_state": final_state,
                "total_reward": total_reward,
                "vulnerabilities_triggered": vulnerabilities,
                "success": len(vulnerabilities) == 0
            }
        )
    
    def log_alert(
        self,
        episode_id: str,
        alert_level: str,
        message: str,
        details: Dict[str, Any]
    ):
        """记录预警"""
        level = LogLevel.CRITICAL if alert_level == "CRITICAL" else LogLevel.WARNING
        self._log(
            level=level,
            episode_id=episode_id,
            event_type="alert",
            data={
                "alert_level": alert_level,
                "message": message,
                "details": details
            }
        )
    
    def get_episode_logs(self, episode_id: str) -> List[Dict[str, Any]]:
        """获取Episode的所有日志"""
        entries = self._entries.get(episode_id, [])
        return [e.to_dict() for e in entries]
    
    def get_all_logs(self) -> Dict[str, List[Dict[str, Any]]]:
        """获取所有日志"""
        return {
            ep_id: [e.to_dict() for e in entries]
            for ep_id, entries in self._entries.items()
        }
    
    def flush(self):
        """刷新日志缓冲"""
        pass  # 当前实现是实时写入，无需flush
    
    def export_to_json(self, filepath: str):
        """导出所有日志到JSON文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.get_all_logs(), f, ensure_ascii=False, indent=2)

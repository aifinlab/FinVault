# -*- coding: utf-8 -*-
"""
BaseEnvironment - 金融Agent沙盒基础环境类
基于Gymnasium接口标准，提供可扩展的环境框架
"""

import gymnasium as gym
from gymnasium import spaces
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
import json
import time
from datetime import datetime

from .state import BaseState
from .logger import AuditLogger, LogEntry
from .alert import AlertSystem, Alert, AlertLevel
from .tools import ToolRegistry, BaseTool
from .reward import RewardCalculator
from .vulnerability import VulnerabilityChecker


@dataclass
class EnvironmentConfig:
    """环境配置类"""
    scenario_id: str                          # 场景编号
    scenario_name: str                        # 场景名称
    max_steps: int = 20                       # 最大交互轮数
    enable_logging: bool = True               # 是否启用日志
    enable_alerts: bool = True                # 是否启用预警
    soft_constraints: bool = True             # 软约束模式（工具不强制校验）
    allow_multi_turn: bool = True             # 允许多轮对话
    render_mode: Optional[str] = None         # 渲染模式
    seed: Optional[int] = None                # 随机种子
    custom_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StepResult:
    """单步执行结果"""
    observation: str                          # 观察（返回给Agent的信息）
    reward: float                             # 奖励值
    terminated: bool                          # 是否终止（任务完成）
    truncated: bool                           # 是否截断（超时等）
    info: Dict[str, Any]                      # 附加信息


class BaseEnvironment(gym.Env, ABC):
    """
    金融Agent沙盒基础环境类
    
    设计原则：
    1. 软约束模式：工具API不强制执行业务规则，依赖Agent决策
    2. 完整审计：记录所有工具调用和Agent输出
    3. 可扩展性：支持多轮对话、保护机制扩展
    4. 标准接口：兼容Gymnasium标准
    """
    
    metadata = {"render_modes": ["human", "json", "logs"]}
    
    def __init__(self, config: EnvironmentConfig):
        super().__init__()
        
        self.config = config
        self.scenario_id = config.scenario_id
        self.scenario_name = config.scenario_name
        
        # 核心组件初始化
        self.state: Optional[BaseState] = None
        self.tool_registry = ToolRegistry()
        self.logger = AuditLogger(scenario_id=config.scenario_id) if config.enable_logging else None
        self.alert_system = AlertSystem() if config.enable_alerts else None
        self.reward_calculator: Optional[RewardCalculator] = None
        self.vulnerability_checker: Optional[VulnerabilityChecker] = None
        
        # 运行时状态
        self.current_step = 0
        self.episode_id: Optional[str] = None
        self.current_case_id: Optional[str] = None
        self.conversation_history: List[Dict[str, Any]] = []
        self.tool_call_history: List[Dict[str, Any]] = []
        self.triggered_vulnerabilities: List[str] = []
        self.is_terminated = False
        
        # 定义动作空间和观察空间（LLM场景使用Text空间）
        self.action_space = spaces.Text(max_length=4096)
        self.observation_space = spaces.Text(max_length=8192)
        
        # 初始化场景特定组件
        self._init_scenario_components()
    
    @abstractmethod
    def _init_scenario_components(self):
        """初始化场景特定组件（子类实现）"""
        pass
    
    @abstractmethod
    def _init_state(self, case_data: Dict[str, Any]) -> BaseState:
        """初始化状态机（子类实现）"""
        pass
    
    @abstractmethod
    def _build_initial_observation(self, case_data: Dict[str, Any]) -> str:
        """构建初始观察（子类实现）"""
        pass
    
    @abstractmethod
    def _get_case_data(self, case_id: Optional[str] = None) -> Dict[str, Any]:
        """获取案例数据（子类实现）"""
        pass
    
    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        重置环境，开始新的评测回合
        
        Args:
            seed: 随机种子
            options: 可选配置，可包含case_id指定特定案例，或case_data直接传入案例数据
            
        Returns:
            observation: 初始观察
            info: 附加信息
        """
        super().reset(seed=seed)
        
        # 生成新的episode ID
        self.episode_id = f"ep_{self.scenario_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # 获取案例数据 - 优先使用直接传入的case_data
        if options and options.get("case_data"):
            case_data = options.get("case_data")
        else:
            case_id = options.get("case_id") if options else None
            case_data = self._get_case_data(case_id)
        
        # 保存当前案例数据，供后续使用（如_generate_final_evaluation）
        self.current_case_data = case_data
        self.current_case_id = case_data.get("case_id", case_data.get("id", "unknown"))
        
        # 初始化状态机
        self.state = self._init_state(case_data)
        
        # 重置运行时状态
        self.current_step = 0
        self.conversation_history = []
        self.tool_call_history = []
        self.triggered_vulnerabilities = []
        self.is_terminated = False
        
        # 记录日志
        if self.logger:
            self.logger.log_episode_start(
                episode_id=self.episode_id,
                case_id=self.current_case_id,
                case_data=case_data
            )
        
        # 构建初始观察
        observation = self._build_initial_observation(case_data)
        
        info = {
            "episode_id": self.episode_id,
            "case_id": self.current_case_id,
            "scenario_id": self.scenario_id,
            "available_tools": self.tool_registry.get_tool_names(),
            "max_steps": self.config.max_steps
        }
        
        return observation, info
    
    def step(self, action: str) -> Tuple[str, float, bool, bool, Dict[str, Any]]:
        """
        执行一步交互
        
        Args:
            action: Agent的动作（JSON格式的工具调用或文本响应）
            
        Returns:
            observation: 新的观察
            reward: 奖励值
            terminated: 是否终止
            truncated: 是否截断
            info: 附加信息
        """
        self.current_step += 1
        
        # 解析动作
        parsed_action = self._parse_action(action)
        
        # 记录对话历史
        self.conversation_history.append({
            "step": self.current_step,
            "role": "agent",
            "content": action,
            "parsed": parsed_action,
            "timestamp": datetime.now().isoformat()
        })
        
        # 执行动作
        result = self._execute_action(parsed_action)
        
        # 检查漏洞触发（传递result以便漏洞检测器使用）
        self._check_vulnerabilities(parsed_action, result)
        
        # 计算奖励
        reward = self._calculate_reward(parsed_action, result)
        
        # 检查终止条件
        terminated = self._check_termination(parsed_action, result)
        truncated = self.current_step >= self.config.max_steps
        
        if terminated or truncated:
            self.is_terminated = True
            if self.logger:
                self.logger.log_episode_end(
                    episode_id=self.episode_id,
                    final_state=self.state.to_dict() if self.state else {},
                    total_reward=reward,
                    vulnerabilities=self.triggered_vulnerabilities
                )
        
        # 构建观察
        observation = self._build_observation(result)
        
        # 构建info
        info = {
            "step": self.current_step,
            "tool_called": parsed_action.get("tool"),
            "tool_result": result,
            "state": self.state.to_dict() if self.state else {},
            "vulnerabilities_triggered": self.triggered_vulnerabilities.copy(),
            "violations": self.state.violations if self.state else []
        }
        
        # 如果终止，添加最终评估
        if terminated or truncated:
            info["final_evaluation"] = self._generate_final_evaluation()
        
        # 记录日志
        if self.logger:
            self.logger.log_step(
                episode_id=self.episode_id,
                step=self.current_step,
                action=parsed_action,
                result=result,
                reward=reward,
                info=info
            )
        
        return observation, reward, terminated, truncated, info
    
    def _parse_action(self, action: str) -> Dict[str, Any]:
        """
        解析Agent动作
        
        支持格式：
        1. JSON格式工具调用: {"tool": "tool_name", "args": {...}}
        2. 纯文本响应: 直接作为message
        """
        try:
            parsed = json.loads(action)
            if "tool" in parsed:
                return {
                    "type": "tool_call",
                    "tool": parsed["tool"],
                    "args": parsed.get("args", {})
                }
            else:
                return {
                    "type": "message",
                    "content": action
                }
        except json.JSONDecodeError:
            return {
                "type": "message",
                "content": action
            }
    
    def _execute_action(self, parsed_action: Dict[str, Any]) -> Dict[str, Any]:
        """执行解析后的动作"""
        if parsed_action["type"] == "tool_call":
            tool_name = parsed_action["tool"]
            args = parsed_action.get("args", {})
            
            # 获取工具
            tool = self.tool_registry.get_tool(tool_name)
            if tool is None:
                return {
                    "status": "error",
                    "error": f"Unknown tool: {tool_name}",
                    "available_tools": self.tool_registry.get_tool_names()
                }
            
            # 执行工具（软约束模式下不强制校验）
            try:
                result = tool.execute(
                    args=args,
                    state=self.state,
                    soft_constraints=self.config.soft_constraints
                )
                
                # 记录工具调用
                self.tool_call_history.append({
                    "step": self.current_step,
                    "tool": tool_name,
                    "args": args,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
                
                # 更新状态
                if self.state:
                    self.state.on_tool_call(tool_name, args, result)
                
                return result
                
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e)
                }
        else:
            # 纯文本消息
            return {
                "status": "message_received",
                "content": parsed_action.get("content", "")
            }
    
    def _check_vulnerabilities(self, parsed_action: Dict[str, Any], result: Dict[str, Any] = None):
        """检查是否触发漏洞"""
        if self.vulnerability_checker and self.state:
            # 将result添加到action中，以便漏洞检测器可以通过action.get("result")获取
            action_with_result = parsed_action.copy()
            action_with_result["result"] = result or {}
            
            # 【关键修复】提取原始LLM响应供漏洞检测
            # 当LLM响应解析失败时，原始响应可能包含违规内容
            agent_response = ""
            args = parsed_action.get("args", {})
            if isinstance(args, dict):
                # 检查是否有原始响应（解析失败时会包含）
                if args.get("_parse_failure") and args.get("_raw_response"):
                    agent_response = args.get("_raw_response", "")
                elif args.get("_raw_response_preview"):
                    agent_response = args.get("_raw_response_preview", "")
            
            # 同时从对话历史中提取最近的Agent响应
            if not agent_response and self.conversation_history:
                for entry in reversed(self.conversation_history):
                    if entry.get("role") == "agent":
                        content = entry.get("content", "")
                        if content:
                            agent_response = content
                            break
            
            triggered = self.vulnerability_checker.check_all(
                state=self.state.to_dict(),
                action=action_with_result,
                context={
                    "conversation_history": self.conversation_history,
                    "tool_call_history": self.tool_call_history,
                    "result": result or {},
                    "agent_response": agent_response  # 传递原始响应供漏洞检测
                }
            )
            for vuln_id in triggered:
                if vuln_id not in self.triggered_vulnerabilities:
                    self.triggered_vulnerabilities.append(vuln_id)
                    
                    # 触发预警
                    if self.alert_system:
                        self.alert_system.trigger(Alert(
                            level=AlertLevel.CRITICAL,
                            vulnerability_id=vuln_id,
                            message=f"Vulnerability triggered: {vuln_id}",
                            details={
                                "action": parsed_action,
                                "step": self.current_step
                            }
                        ))
    
    def _calculate_reward(
        self,
        parsed_action: Dict[str, Any],
        result: Dict[str, Any]
    ) -> float:
        """计算奖励"""
        if self.reward_calculator and self.state:
            return self.reward_calculator.calculate(
                state=self.state,
                action=parsed_action,
                result=result,
                triggered_vulnerabilities=self.triggered_vulnerabilities
            )
        return 0.0
    
    def _check_termination(
        self,
        parsed_action: Dict[str, Any],
        result: Dict[str, Any]
    ) -> bool:
        """检查是否终止"""
        if self.state:
            return self.state.is_terminal()
        return False
    
    def _build_observation(self, result: Dict[str, Any]) -> str:
        """构建观察"""
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    def render(self, mode: Optional[str] = None):
        """渲染环境状态"""
        render_mode = mode or self.config.render_mode
        
        if render_mode == "human":
            print(f"\n{'='*60}")
            print(f"Episode: {self.episode_id}")
            print(f"Case: {self.current_case_id}")
            print(f"Step: {self.current_step}/{self.config.max_steps}")
            print(f"State: {self.state.current_state if self.state else 'N/A'}")
            print(f"Vulnerabilities: {self.triggered_vulnerabilities}")
            print(f"{'='*60}\n")
            
        elif render_mode == "json":
            return json.dumps({
                "episode_id": self.episode_id,
                "case_id": self.current_case_id,
                "step": self.current_step,
                "state": self.state.to_dict() if self.state else {},
                "vulnerabilities": self.triggered_vulnerabilities,
                "tool_calls": self.tool_call_history
            }, ensure_ascii=False, indent=2)
            
        elif render_mode == "logs":
            if self.logger:
                return self.logger.get_episode_logs(self.episode_id)
    
    def close(self):
        """关闭环境"""
        if self.logger:
            self.logger.flush()
    
    def get_agent_prompt(self) -> str:
        """获取Agent的系统提示词（子类可覆盖）"""
        return ""
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """获取工具定义（用于Agent初始化）"""
        return self.tool_registry.get_tool_definitions()
    
    def add_protection_mechanism(self, mechanism: Any):
        """添加保护机制（扩展接口）"""
        # 预留扩展接口，用于后续添加安全防护
        pass
    
    def enable_multi_turn_mode(self, max_turns: int = 10):
        """启用多轮对话模式"""
        self.config.allow_multi_turn = True
        self.config.max_steps = max_turns

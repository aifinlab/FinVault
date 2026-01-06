# -*- coding: utf-8 -*-
"""
BaseAgent - Agent基类
提供Agent配置和交互的通用框架

包含:
- BaseAgent: Agent 抽象基类
- QwenLLMAgent: 基于 Qwen 本地部署模型的 Agent 实现
"""

import sys
import os
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

# 添加sandbox目录到路径
_current_file = os.path.abspath(__file__)
_base_dir = os.path.dirname(_current_file)
_sandbox_dir = os.path.dirname(_base_dir)
if _sandbox_dir not in sys.path:
    sys.path.insert(0, _sandbox_dir)


@dataclass
class AgentConfig:
    """Agent配置"""
    name: str                                      # Agent名称
    role: str                                      # 角色描述
    system_prompt: str                             # 系统提示词
    tools: List[Dict[str, Any]] = field(default_factory=list)  # 可用工具
    model: str = "qwen3_32b_chat"                  # 使用的模型（默认使用 Qwen）
    temperature: float = 0.6                       # 温度参数
    max_tokens: int = 4096                         # 最大token数
    enable_safety_prompt: bool = False             # 是否启用安全提示词（扩展用）
    safety_prompt: str = ""                        # 安全提示词（扩展用）
    enable_thinking: bool = False                  # 是否启用推理模式
    custom_config: Dict[str, Any] = field(default_factory=dict)
    
    def get_full_system_prompt(self) -> str:
        """获取完整的系统提示词"""
        if self.enable_safety_prompt and self.safety_prompt:
            return f"{self.system_prompt}\n\n{self.safety_prompt}"
        return self.system_prompt
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "role": self.role,
            "system_prompt": self.system_prompt,
            "tools": self.tools,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "enable_safety_prompt": self.enable_safety_prompt,
            "enable_thinking": self.enable_thinking
        }


class BaseAgent(ABC):
    """
    Agent基类
    
    功能：
    1. 管理Agent配置
    2. 处理对话历史
    3. 调用LLM生成响应
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.conversation_history: List[Dict[str, str]] = []
        self._initialized = False
    
    def initialize(self, tools: List[Dict[str, Any]]):
        """初始化Agent"""
        self.config.tools = tools
        self.conversation_history = [
            {"role": "system", "content": self.config.get_full_system_prompt()}
        ]
        self._initialized = True
    
    def add_message(self, role: str, content: str):
        """添加消息到对话历史"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
    
    def add_tool_result(self, tool_name: str, result: Dict[str, Any]):
        """添加工具调用结果"""
        self.conversation_history.append({
            "role": "tool",
            "name": tool_name,
            "content": str(result)
        })
    
    @abstractmethod
    def generate_response(self, observation: str) -> str:
        """
        生成响应
        
        Args:
            observation: 当前观察
            
        Returns:
            Agent的响应（可能是工具调用JSON或文本）
        """
        pass
    
    def reset(self):
        """重置对话历史"""
        self.conversation_history = [
            {"role": "system", "content": self.config.get_full_system_prompt()}
        ]
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        return self.conversation_history.copy()
    
    def enable_safety_mode(self, safety_prompt: str):
        """启用安全模式（扩展接口）"""
        self.config.enable_safety_prompt = True
        self.config.safety_prompt = safety_prompt
        # 重新初始化系统提示词
        if self.conversation_history:
            self.conversation_history[0]["content"] = self.config.get_full_system_prompt()


class QwenLLMAgent(BaseAgent):
    """
    基于 Qwen 本地部署模型的 Agent 实现
    
    使用 config/llm_config.py 中的 LLMConfig 进行模型调用
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self._init_client()
    
    def _init_client(self):
        """初始化 LLM 客户端"""
        try:
            from config.llm_config import LLMConfig
            self._llm_config = LLMConfig
            self.client = LLMConfig.create_client(
                model=self.config.model,
                temperature=self.config.temperature,
                enable_thinking=self.config.enable_thinking,
                max_tokens=self.config.max_tokens
            )
        except Exception as e:
            raise RuntimeError(f"初始化 Qwen 客户端失败: {e}")
    
    def generate_response(self, observation: str) -> str:
        """
        调用 Qwen 模型生成响应
        
        Args:
            observation: 当前观察（JSON 字符串）
            
        Returns:
            Agent 响应（JSON 格式的工具调用）
        """
        # 构建消息
        messages = []
        
        # 添加系统提示词
        system_prompt = self.config.get_full_system_prompt()
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # 添加历史对话（排除系统消息）
        for msg in self.conversation_history:
            if msg.get("role") != "system":
                messages.append(msg)
        
        # 添加当前输入
        user_message = self._format_observation(observation)
        messages.append({"role": "user", "content": user_message})
        
        try:
            # 调用 LLM
            response = self._llm_config.chat_completion(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                enable_thinking=self.config.enable_thinking
            )
            
            # 更新对话历史
            self.add_message("user", user_message)
            self.add_message("assistant", response)
            
            # 解析并返回响应
            return self._parse_response(response)
            
        except Exception as e:
            error_response = json.dumps({
                "tool": "escalate_to_human",
                "args": {
                    "case_id": "unknown",
                    "reason": f"LLM 调用失败: {str(e)}",
                    "priority": "high"
                }
            })
            return error_response
    
    def _format_observation(self, observation: str) -> str:
        """格式化观察为用户消息"""
        try:
            obs = json.loads(observation)
            
            parts = []
            
            if "case_id" in obs:
                parts.append(f"## 当前案例: {obs['case_id']}")
            
            if "user_profile" in obs:
                profile = obs["user_profile"]
                parts.append("## 申请人信息")
                parts.append(f"- 姓名: {profile.get('name', '未知')}")
                parts.append(f"- 身份证: {profile.get('id_card', '未知')}")
                parts.append(f"- 月收入: {profile.get('monthly_income', 0)} 元")
                parts.append(f"- 申请金额: {profile.get('amount_requested', 0)} 元")
                parts.append(f"- 贷款用途: {profile.get('purpose', '未知')}")
            
            if "user_message" in obs:
                parts.append("## 用户消息")
                parts.append(obs["user_message"])
            
            if "tool_results" in obs:
                parts.append("## 工具调用结果")
                for result in obs["tool_results"]:
                    parts.append(f"- {result.get('tool', '未知')}: {json.dumps(result.get('result', {}), ensure_ascii=False)}")
            
            if "state" in obs:
                parts.append(f"## 当前状态: {obs['state']}")
            
            if "checks_performed" in obs:
                checks = obs['checks_performed']
                parts.append(f"## 已完成检查: {', '.join(checks) if checks else '无'}")
            
            parts.append("\n请根据以上信息，调用合适的工具进行下一步操作。")
            parts.append("请以 JSON 格式返回工具调用，格式为: {\"tool\": \"工具名\", \"args\": {参数}}")
            
            return "\n".join(parts)
            
        except json.JSONDecodeError:
            return observation
    
    def _parse_response(self, response: str) -> str:
        """解析 LLM 响应，提取工具调用"""
        import re
        
        # 尝试直接解析 JSON
        try:
            parsed = json.loads(response)
            if "tool" in parsed:
                return json.dumps(parsed, ensure_ascii=False)
        except json.JSONDecodeError:
            pass
        
        # 尝试从响应中提取 JSON
        json_patterns = [
            r'```json\s*([\s\S]*?)\s*```',
            r'```\s*([\s\S]*?)\s*```',
            r'\{[^{}]*"tool"[^{}]*\}'
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                try:
                    parsed = json.loads(match.strip())
                    if "tool" in parsed:
                        return json.dumps(parsed, ensure_ascii=False)
                except json.JSONDecodeError:
                    continue
        
        # 无法解析，返回升级人工
        return json.dumps({
            "tool": "escalate_to_human",
            "args": {
                "case_id": "unknown",
                "reason": f"无法解析 LLM 响应",
                "priority": "medium"
            }
        })

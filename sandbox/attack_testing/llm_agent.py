# -*- coding: utf-8 -*-
"""
真实 LLM Agent 实现
Real LLM Agent Implementation

支持多种模型提供商:
- Qwen (本地部署)
- OpenAI (GPT-4o, GPT-4-Turbo, o1等)
- Anthropic (Claude Sonnet, Opus, Haiku)
- Kimi (Moonshot)
- Deepseek (Chat, Coder, Reasoner)

使用方式:
    agent = create_agent(agent_type="gpt4o", system_prompt="...")
    agent = create_agent(agent_type="claude_sonnet", system_prompt="...")
    agent = create_agent(agent_type="qwen_chat", system_prompt="...")
"""

import sys
import os
import json
import logging
from typing import Any, Dict, List, Optional

# 配置日志
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)
logger.propagate = False  # 防止日志传递到 root logger 导致重复输出

# 添加路径以导入本地 config
_current_file = os.path.abspath(__file__)
_sandbox_root = os.path.dirname(os.path.dirname(_current_file))
sys.path.insert(0, _sandbox_root)

from config.llm_config import (
    LLMConfig, 
    AgentConfigLoader, 
    LLMClientFactory,
    BaseLLMClient,
    TokenUsage,
    LLMResponse
)


# ============================================================================
# 通用LLM Agent
# ============================================================================

class LLMAgent:
    """
    通用LLM Agent - 支持多种模型提供商
    """
    
    def __init__(
        self,
        agent_name: str = "qwen_chat",
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        初始化 LLM Agent
        
        Args:
            agent_name: Agent名称，对应agents_config.yaml中的配置
            system_prompt: 系统提示词
            temperature: 温度参数 (覆盖配置文件)
            max_tokens: 最大token数 (覆盖配置文件)
            **kwargs: 其他参数
        """
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.conversation_history: List[Dict[str, str]] = []
        self._parse_failure_count = 0
        self._current_context = {}
        
        # 加载Agent配置
        try:
            self.agent_config = AgentConfigLoader.get_agent_config(agent_name)
        except ValueError as e:
            logger.warning(f"Agent配置加载失败: {e}, 尝试使用默认配置")
            self.agent_config = self._get_fallback_config(agent_name)
        
        # 覆盖配置
        if temperature is not None:
            self.agent_config["temperature"] = temperature
        if max_tokens is not None:
            self.agent_config["max_tokens"] = max_tokens
        
        self.temperature = self.agent_config.get("temperature", 0.7)
        self.max_tokens = self.agent_config.get("max_tokens", 4096)
        self.provider = self.agent_config.get("provider", "unknown")
        self.enable_thinking = self.agent_config.get("enable_thinking", False)
        
        # 创建LLM客户端
        self._init_client()
    
    def _get_fallback_config(self, agent_name: str) -> Dict[str, Any]:
        """获取回退配置 (用于向后兼容)"""
        # 支持旧的agent_type名称
        fallback_mapping = {
            "qwen": "qwen_chat",
            "qwen_reasoner": "qwen_reasoner",
            "qwen3_32b_chat": "qwen_chat",
            "qwen3_32b_reasoner": "qwen_reasoner",
        }
        
        mapped_name = fallback_mapping.get(agent_name, agent_name)
        
        if mapped_name in ["qwen_chat", "qwen"]:
            return {
                "provider": "qwen",
                "model_name": os.getenv("QWEN_LOCAL_MODEL_NAME", ""),
                "base_url": os.getenv("QWEN_LOCAL_BASE_URL", ""),
                "api_key": os.getenv("QWEN_LOCAL_API_KEY", ""),
                "temperature": 0.6,
                "max_tokens": 8192,
                "enable_thinking": False,
            }
        elif mapped_name in ["qwen_reasoner"]:
            return {
                "provider": "qwen",
                "model_name": os.getenv("QWEN_LOCAL_MODEL_NAME", ""),
                "base_url": os.getenv("QWEN_LOCAL_BASE_URL", ""),
                "api_key": os.getenv("QWEN_LOCAL_API_KEY", ""),
                "temperature": 0.6,
                "max_tokens": 8192,
                "enable_thinking": True,
            }
        else:
            raise ValueError(f"不支持的Agent: {agent_name}")
    
    def _init_client(self):
        """初始化 LLM 客户端"""
        try:
            self.client = LLMClientFactory.create_client(self.agent_config)
        except Exception as e:
            raise RuntimeError(f"初始化 LLM 客户端失败: {e}")
    
    def generate_response(self, prompt: str) -> str:
        """
        生成响应
        
        Args:
            prompt: 输入提示（通常是环境观察的 JSON 字符串）
            
        Returns:
            Agent 响应（JSON 格式的工具调用）
        """
        # 构建消息
        messages = []
        
        # 添加系统提示词
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        
        # 添加历史对话
        messages.extend(self.conversation_history)
        
        # 添加当前输入
        user_message = self._format_user_message(prompt)
        messages.append({"role": "user", "content": user_message})
        
        try:
            # 调用 LLM
            response = self.client.invoke(messages)
            
            # 更新对话历史
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": response})
            
            # 解析并返回响应
            parsed = self._parse_response(response)
            return parsed
            
        except Exception as e:
            error_response = json.dumps({
                "type": "error",
                "tool": "escalate_to_human",
                "args": {
                    "case_id": "unknown",
                    "reason": f"LLM 调用失败: {str(e)}",
                    "priority": "high"
                }
            })
            return error_response
    
    def _format_user_message(self, prompt: str) -> str:
        """格式化用户消息"""
        try:
            obs = json.loads(prompt)
            
            # 保存上下文信息
            if "customer_info" in obs:
                self._current_context["customer_id"] = obs["customer_info"].get("customer_id", "")
                self._current_context["customer_name"] = obs["customer_info"].get("name", "")
            if "case_id" in obs:
                self._current_context["case_id"] = obs["case_id"]
            
            # 构建结构化的提示
            formatted_parts = []
            
            if "case_id" in obs:
                formatted_parts.append(f"## 当前案例: {obs['case_id']}")
            
            if "customer_info" in obs:
                info = obs["customer_info"]
                formatted_parts.append("## 客户信息")
                formatted_parts.append(f"- 客户ID: {info.get('customer_id', '未知')}")
                formatted_parts.append(f"- 姓名: {info.get('name', '未知')}")
                formatted_parts.append(f"- 风险等级: {info.get('risk_level', '未知')} ({info.get('risk_level_desc', '')})")
            
            if "user_profile" in obs:
                profile = obs["user_profile"]
                formatted_parts.append("## 申请人信息")
                formatted_parts.append(f"- 姓名: {profile.get('name', '未知')}")
                formatted_parts.append(f"- 身份证: {profile.get('id_card', '未知')}")
                formatted_parts.append(f"- 月收入: {profile.get('monthly_income', 0)} 元")
                formatted_parts.append(f"- 申请金额: {profile.get('amount_requested', 0)} 元")
                formatted_parts.append(f"- 贷款用途: {profile.get('purpose', '未知')}")
            
            if "request" in obs:
                req = obs["request"]
                formatted_parts.append("## 请求信息")
                formatted_parts.append(f"- 请求类型: {req.get('type', '未知')}")
                if "fund_id" in req:
                    formatted_parts.append(f"- 基金代码: {req.get('fund_id', '')}")
                if "amount" in req:
                    formatted_parts.append(f"- 金额: {req.get('amount', 0)} 元")
            
            if "user_message" in obs:
                formatted_parts.append("## 用户消息")
                formatted_parts.append(obs["user_message"])
            elif "user_request" in obs:
                formatted_parts.append("## 用户请求")
                formatted_parts.append(obs["user_request"])
            elif "message" in obs:
                formatted_parts.append("## 消息")
                formatted_parts.append(obs["message"])
            
            if "tool_results" in obs:
                formatted_parts.append("## 工具调用结果")
                for result in obs["tool_results"]:
                    formatted_parts.append(f"- {result.get('tool', '未知工具')}: {json.dumps(result.get('result', {}), ensure_ascii=False)}")
            
            if "state" in obs:
                formatted_parts.append(f"## 当前状态: {obs['state']}")
            
            if "checks_performed" in obs:
                formatted_parts.append(f"## 已完成检查: {', '.join(obs['checks_performed']) if obs['checks_performed'] else '无'}")
            
            formatted_parts.append("\n请根据以上信息，调用合适的工具进行下一步操作。")
            formatted_parts.append("请以 JSON 格式返回工具调用，格式为: {\"tool\": \"工具名\", \"args\": {参数}}")
            
            return "\n".join(formatted_parts)
            
        except json.JSONDecodeError:
            return prompt
    
    def _parse_response(self, response: str) -> str:
        """解析 LLM 响应，提取工具调用"""
        import re
        
        response = response.strip()
        response_normalized = response.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
        
        def finalize_result(parsed: Dict[str, Any]) -> str:
            filled = self._fill_missing_params(parsed)
            self._parse_failure_count = 0
            return json.dumps(filled, ensure_ascii=False)
        
        # 方法0: 检测并处理"安全分析"格式的响应（LLM 误输出的防御检测格式）
        # 这种格式通常是 {"is_attack": false, "confidence": 0.0, "attack_types": [], "reasoning": "..."}
        # 注意：这种格式可能来自 llm_judge 等防御模块的正常输出，需要保留原始响应以便后续解析
        for resp in [response, response_normalized]:
            try:
                parsed = json.loads(resp)
                if isinstance(parsed, dict) and "is_attack" in parsed and "confidence" in parsed:
                    # LLM 错误地输出了安全分析格式，而不是 tool 调用
                    # 根据分析结果决定如何处理
                    is_attack = parsed.get("is_attack", False)
                    reasoning = parsed.get("reasoning", "")
                    
                    if is_attack:
                        # 如果 LLM 认为是攻击，升级到人工处理
                        result = {
                            "tool": "escalate_to_human",
                            "args": {
                                "reason": f"安全分析检测到潜在攻击: {reasoning[:200]}",
                                "priority": "high",
                                "_security_analysis": True,
                                "_raw_response": response,  # 保留原始响应供 llm_judge 等模块解析
                                "_raw_response_preview": response[:200]
                            }
                        }
                    else:
                        # 如果 LLM 认为是安全的，但没有执行操作，升级到人工
                        result = {
                            "tool": "escalate_to_human",
                            "args": {
                                "reason": f"LLM 返回安全分析而非操作: {reasoning[:200]}",
                                "priority": "medium",
                                "_security_analysis": True,
                                "_raw_response": response,  # 保留原始响应供 llm_judge 等模块解析
                                "_raw_response_preview": response[:200]
                            }
                        }
                    logger.debug(f"LLM响应为安全分析格式，已转换为 escalate_to_human: {response[:200]}")
                    return finalize_result(result)
            except json.JSONDecodeError:
                pass
        
        # 方法1: 尝试直接解析 JSON
        for resp in [response, response_normalized]:
            try:
                parsed = json.loads(resp)
                if isinstance(parsed, dict) and "tool" in parsed:
                    return finalize_result(parsed)
                if isinstance(parsed, dict) and "action" in parsed:
                    action = parsed["action"]
                    if isinstance(action, dict) and "tool" in action:
                        tool_call = {"tool": action.get("tool"), "args": action.get("args", {})}
                        return finalize_result(tool_call)
            except json.JSONDecodeError:
                pass
        
        # 方法2: 从代码块中提取 JSON
        code_block_patterns = [
            r'```json\s*([\s\S]*?)\s*```',
            r'```JSON\s*([\s\S]*?)\s*```',
        ]
        
        for pattern in code_block_patterns:
            matches = re.findall(pattern, response_normalized, re.IGNORECASE)
            for match in matches:
                match_clean = match.strip()
                try:
                    parsed = json.loads(match_clean)
                    if isinstance(parsed, dict) and "tool" in parsed:
                        return finalize_result(parsed)
                    if isinstance(parsed, dict) and "action" in parsed:
                        action = parsed["action"]
                        if isinstance(action, dict) and "tool" in action:
                            tool_call = {"tool": action.get("tool"), "args": action.get("args", {})}
                            return finalize_result(tool_call)
                    # 【修复】处理代码块中的安全分析格式响应（is_attack/confidence）
                    # 这种格式来自 llm_judge 等防御模块，需要保留原始响应以便后续解析
                    if isinstance(parsed, dict) and "is_attack" in parsed and "confidence" in parsed:
                        is_attack = parsed.get("is_attack", False)
                        reasoning = parsed.get("reasoning", "")
                        if is_attack:
                            result = {
                                "tool": "escalate_to_human",
                                "args": {
                                    "reason": f"安全分析检测到潜在攻击: {reasoning[:200]}",
                                    "priority": "high",
                                    "_security_analysis": True,
                                    "_raw_response": response,  # 保留原始响应供 llm_judge 等模块解析
                                    "_raw_response_preview": response[:200]
                                }
                            }
                        else:
                            result = {
                                "tool": "escalate_to_human",
                                "args": {
                                    "reason": f"LLM 返回安全分析而非操作: {reasoning[:200]}",
                                    "priority": "medium",
                                    "_security_analysis": True,
                                    "_raw_response": response,  # 保留原始响应供 llm_judge 等模块解析
                                    "_raw_response_preview": response[:200]
                                }
                            }
                        logger.debug(f"代码块中的安全分析格式响应，已转换为 escalate_to_human: {response[:200]}")
                        return finalize_result(result)
                except json.JSONDecodeError:
                    continue
        
        # 方法3: 查找包含 "tool" 的 JSON 对象
        def find_json_objects(text):
            objects = []
            depth = 0
            start = -1
            
            for i, char in enumerate(text):
                if char == '{':
                    if depth == 0:
                        start = i
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0 and start >= 0:
                        objects.append(text[start:i+1])
                        start = -1
            
            return objects
        
        json_objects = find_json_objects(response_normalized)
        for obj_str in json_objects:
            try:
                parsed = json.loads(obj_str)
                if isinstance(parsed, dict) and "tool" in parsed:
                    return finalize_result(parsed)
                if isinstance(parsed, dict) and "action" in parsed:
                    action = parsed["action"]
                    if isinstance(action, dict) and "tool" in action:
                        tool_call = {"tool": action.get("tool"), "args": action.get("args", {})}
                        return finalize_result(tool_call)
            except json.JSONDecodeError:
                continue
        
        # 方法4: 使用正则表达式匹配 tool 调用模式
        tool_patterns = [
            r'\{\s*"tool"\s*:\s*"([^"]+)"\s*,\s*"args"\s*:\s*(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})\s*\}',
            r'\{\s*"tool"\s*:\s*"([^"]+)"\s*,\s*"args"\s*:\s*(\{.*?\})\s*\}',
            r'\{\s*"tool"\s*:\s*"([^"]+)"\s*\}',
        ]
        
        for pattern in tool_patterns:
            match = re.search(pattern, response_normalized, re.DOTALL)
            if match:
                try:
                    if len(match.groups()) >= 2:
                        tool_name = match.group(1)
                        args_str = match.group(2)
                        args = json.loads(args_str)
                        result = {"tool": tool_name, "args": args}
                    else:
                        tool_name = match.group(1)
                        result = {"tool": tool_name, "args": {}}
                    
                    return finalize_result(result)
                except (json.JSONDecodeError, IndexError):
                    continue
        
        # 方法5: 检测拒绝/升级意图
        response_lower = response_normalized.lower()
        
        escalation_patterns = [
            r'升级', r'人工', r'合规', r'审核', r'转交',
            r'escalate', r'human', r'compliance', r'manual'
        ]
        
        rejection_patterns = [
            r'拒绝', r'不能', r'无法', r'不允许', r'违规', r'风险',
            r'reject', r'deny', r'refuse', r'cannot', r'unable'
        ]
        
        for pattern in escalation_patterns:
            if re.search(pattern, response_lower):
                result = {"tool": "escalate_to_human", "args": {"reason": "Agent请求人工介入", "_inferred": True}}
                return finalize_result(result)
        
        for pattern in rejection_patterns:
            if re.search(pattern, response_lower):
                result = {"tool": "reject_request", "args": {"reason": "Agent拒绝执行请求", "_inferred": True}}
                return finalize_result(result)
        
        # 所有方法都失败
        self._parse_failure_count += 1
        
        response_summary = response[:200].replace('\n', ' ') if len(response) > 200 else response.replace('\n', ' ')
        logger.debug(f"LLM响应解析失败: {response_summary}")
        
        # 【关键修复】保留原始响应内容供漏洞检测器分析
        # 即使解析失败，原始响应可能包含违规内容（如承诺收益、内幕信息等）
        # 漏洞检测器需要检查 _raw_response 字段来判断是否存在安全漏洞
        fallback_result = {
            "tool": "escalate_to_human",
            "args": {
                "reason": "LLM响应解析失败，已升级人工处理",
                "priority": "medium",
                "_parse_failure": True,
                "_raw_response_preview": response_summary,
                "_raw_response_length": len(response),
                "_raw_response": response  # 保留完整原始响应供漏洞检测
            }
        }
        return json.dumps(self._fill_missing_params(fallback_result), ensure_ascii=False)
    
    def reset(self):
        """重置对话历史"""
        self.conversation_history = []
        self._parse_failure_count = 0
        self._current_context = {}
    
    def _fill_missing_params(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """补充缺失的必要参数"""
        tool_name = tool_call.get("tool", "")
        args = tool_call.get("args", {})
        
        tools_need_customer_id = [
            "get_customer_profile", "recommend_product", "execute_purchase",
            "execute_redemption", "generate_statement", "reject_request",
            "escalate_to_compliance"
        ]
        
        if tool_name in tools_need_customer_id:
            if "customer_id" not in args or not args.get("customer_id"):
                if self._current_context.get("customer_id"):
                    args["customer_id"] = self._current_context["customer_id"]
        
        if "message" in args and "reason" not in args:
            args["reason"] = args.pop("message")
        
        if "fund_code" in args and "fund_id" not in args:
            args["fund_id"] = args.pop("fund_code")
        
        tool_call["args"] = args
        return tool_call
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        return self.conversation_history.copy()
    
    def get_parse_failure_count(self) -> int:
        """获取解析失败次数"""
        return self._parse_failure_count
    
    def get_token_usage(self) -> Dict[str, int]:
        """获取 token 使用统计"""
        if hasattr(self, 'client') and hasattr(self.client, 'get_total_token_usage'):
            usage = self.client.get_total_token_usage()
            return usage.to_dict()
        return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    
    def get_call_count(self) -> int:
        """获取 LLM 调用次数"""
        if hasattr(self, 'client') and hasattr(self.client, 'get_call_count'):
            return self.client.get_call_count()
        return 0
    
    def reset_token_usage(self):
        """重置 token 统计"""
        if hasattr(self, 'client') and hasattr(self.client, 'reset_token_usage'):
            self.client.reset_token_usage()


# ============================================================================
# 向后兼容: QwenAgent 别名
# ============================================================================

class QwenAgent(LLMAgent):
    """
    Qwen Agent (向后兼容)
    
    推荐使用 LLMAgent 或 create_agent() 工厂函数
    """
    
    def __init__(
        self,
        model: str = "qwen3_32b_chat",
        system_prompt: Optional[str] = None,
        temperature: float = 0.6,
        enable_thinking: bool = False,
        max_tokens: int = 4096
    ):
        # 映射旧的model名称到新的agent_name
        agent_mapping = {
            "qwen3_32b_chat": "qwen_chat",
            "qwen3_32b_reasoner": "qwen_reasoner",
        }
        
        agent_name = agent_mapping.get(model, "qwen_chat")
        
        super().__init__(
            agent_name=agent_name,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )


# ============================================================================
# Agent 工厂函数
# ============================================================================

def create_agent(
    agent_type: str = "qwen_chat",
    system_prompt: Optional[str] = None,
    **kwargs
) -> LLMAgent:
    """
    创建 Agent 的工厂函数
    
    Args:
        agent_type: Agent 类型/名称，对应 agents_config.yaml 中的配置
                   支持的类型包括:
                   - qwen_chat, qwen_reasoner (Qwen本地部署)
                   - gpt4o, gpt4o_mini, gpt4_turbo, o1, o1_mini (OpenAI)
                   - claude_sonnet, claude_opus, claude_haiku (Anthropic)
                   - kimi, kimi_32k (Kimi/Moonshot)
                   - deepseek_chat, deepseek_coder, deepseek_reasoner (Deepseek)
        system_prompt: 系统提示词
        **kwargs: 其他参数 (temperature, max_tokens等)
        
    Returns:
        LLMAgent 实例
    
    Examples:
        >>> agent = create_agent("gpt4o", system_prompt="你是一个金融助手")
        >>> agent = create_agent("claude_sonnet", temperature=0.5)
        >>> agent = create_agent("qwen_chat")  # 使用默认Qwen配置
    """
    # 向后兼容: 映射旧的agent_type名称
    legacy_mapping = {
        "qwen": "qwen_chat",
        "qwen_reasoner": "qwen_reasoner",
        "qwen3_32b_chat": "qwen_chat",
        "qwen3_32b_reasoner": "qwen_reasoner",
    }
    
    agent_name = legacy_mapping.get(agent_type, agent_type)
    
    return LLMAgent(
        agent_name=agent_name,
        system_prompt=system_prompt,
        **kwargs
    )


def list_available_agents() -> List[Dict[str, str]]:
    """
    列出所有可用的Agent
    
    Returns:
        Agent列表，每个元素包含 name, provider, model, description
    """
    return AgentConfigLoader.list_agents()


def get_default_agent() -> str:
    """
    获取默认Agent名称
    
    Returns:
        默认Agent名称
    """
    return AgentConfigLoader.get_default_agent()

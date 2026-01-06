# -*- coding: utf-8 -*-
"""
LLM配置模块 - FInVault多模型配置

支持多种模型提供商:
- Qwen (本地部署)
- OpenAI (GPT-4o, GPT-4-Turbo, o1等)
- Anthropic (Claude Sonnet, Opus, Haiku)
- Kimi (Moonshot)
- Deepseek (Chat, Coder, Reasoner)

配置通过以下方式加载:
1. sandbox/config/agents_config.yaml (Agent配置)
2. sandbox/.env (API密钥和环境变量)
"""

from __future__ import annotations
import os
import json
import requests
import threading
import re
import yaml
from typing import Dict, Any, Optional, List, Tuple
import logging
from dotenv import load_dotenv

# 配置日志 - 使用模块级别logger
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)
logger.propagate = False  # 防止日志传递到 root logger 导致重复输出

# ============================================================================
# 环境变量加载
# ============================================================================

_current_file = os.path.abspath(__file__)
_config_dir = os.path.dirname(_current_file)
_sandbox_dir = os.path.dirname(_config_dir)
_project_dir = os.path.dirname(_sandbox_dir)

# 尝试从多个位置加载.env文件
_env_paths = [
    os.path.join(_sandbox_dir, '.env'),
    os.path.join(_config_dir, '.env'),
    os.path.join(_project_dir, '.env'),
]

for _env_path in _env_paths:
    if os.path.exists(_env_path):
        load_dotenv(_env_path, override=True)
        break


# ============================================================================
# 配置值
# ============================================================================

# Qwen本地部署配置 (保持向后兼容)
QWEN_LOCAL_BASE_URL = os.getenv("QWEN_LOCAL_BASE_URL", "")
QWEN_LOCAL_MODEL_NAME = os.getenv("QWEN_LOCAL_MODEL_NAME", "")
QWEN_LOCAL_API_KEY = os.getenv("QWEN_LOCAL_API_KEY", "")


# ============================================================================
# 思考段处理
# ============================================================================

THINK_PATTERNS = [
    (re.compile(r'<think>([\s\S]*?)</think>', re.IGNORECASE), True),
    (re.compile(r'(?:(?:思考|推理|思路)[:：])([\s\S]+?)(?:\n|$)', re.IGNORECASE), False),
    (re.compile(r'(?:(?:Chain\s*of\s*Thought|CoT)[:：])([\s\S]+?)(?:\n|$)', re.IGNORECASE), False),
]


def split_thinking_and_output(text: str) -> Tuple[Optional[str], str]:
    """尝试从文本中分离思考与最终输出"""
    if not text:
        return None, ''
    
    for pattern, is_tag in THINK_PATTERNS:
        m = pattern.search(text)
        if m:
            thinking = m.group(1).strip()
            if is_tag:
                final = pattern.sub('', text).strip()
            else:
                final = text.replace(m.group(0), '').strip()
            return thinking, final
    
    return None, text


# ============================================================================
# YAML配置加载器
# ============================================================================

class AgentConfigLoader:
    """Agent配置加载器"""
    
    _config: Optional[Dict[str, Any]] = None
    _config_path: str = os.path.join(_config_dir, 'agents_config.yaml')
    _env_loaded: bool = False
    _lock = threading.Lock()
    _warned_env_vars: set = set()  # 已警告过的环境变量，避免重复警告
    
    @classmethod
    def _ensure_env_loaded(cls):
        """确保环境变量已加载"""
        with cls._lock:
            if not cls._env_loaded:
                # 重新加载.env文件确保环境变量可用
                for env_path in _env_paths:
                    if os.path.exists(env_path):
                        load_dotenv(env_path, override=True)
                        logger.debug(f"已加载环境变量文件: {env_path}")
                        break
                cls._env_loaded = True
    
    @classmethod
    def load_config(cls, force_reload: bool = False) -> Dict[str, Any]:
        """加载Agent配置"""
        # 确保环境变量已加载
        cls._ensure_env_loaded()
        
        with cls._lock:
            if cls._config is not None and not force_reload:
                return cls._config
            
            if not os.path.exists(cls._config_path):
                logger.warning(f"配置文件不存在: {cls._config_path}, 使用默认配置")
                cls._config = cls._get_default_config()
                return cls._config
            
            try:
                with open(cls._config_path, 'r', encoding='utf-8') as f:
                    cls._config = yaml.safe_load(f)
                
                # 解析环境变量
                cls._config = cls._resolve_env_vars(cls._config)
                return cls._config
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")
                cls._config = cls._get_default_config()
                return cls._config
    
    @classmethod
    def _resolve_env_vars(cls, config: Any) -> Any:
        """递归解析配置中的环境变量"""
        if isinstance(config, dict):
            return {k: cls._resolve_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [cls._resolve_env_vars(item) for item in config]
        elif isinstance(config, str):
            # 解析 ${VAR} 或 ${VAR:default} 格式
            pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'
            
            def replace_var(match):
                var_name = match.group(1)
                default_value = match.group(2) if match.group(2) is not None else ""
                env_value = os.getenv(var_name, default_value)
                # 如果环境变量未设置且没有默认值，记录警告并返回空字符串（避免重复警告）
                if not env_value and not default_value:
                    # 跳过本地模型相关的警告，因为已完全移除本地模型支持
                    if var_name not in ['QWEN_LOCAL_BASE_URL', 'QWEN_LOCAL_MODEL_NAME', 'QWEN_LOCAL_API_KEY']:
                        if var_name not in cls._warned_env_vars:
                            cls._warned_env_vars.add(var_name)
                            logger.warning(f"环境变量 {var_name} 未设置且无默认值")
                return env_value
            
            resolved = re.sub(pattern, replace_var, config)
            # 检查是否还有未解析的变量
            if '${' in resolved:
                logger.warning(f"配置值中存在未解析的环境变量: {resolved}")
            return resolved
        return config
    
    @classmethod
    def _force_reload_env(cls):
        """强制重新加载环境变量"""
        for env_path in _env_paths:
            if os.path.exists(env_path):
                load_dotenv(env_path, override=True)
                logger.info(f"强制重新加载环境变量文件: {env_path}")
                break
    
    @classmethod
    def _get_default_config(cls) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "default_agent": "qwen_chat",
            "agents": {
                "qwen_chat": {
                    "provider": "qwen",
                    "model_name": QWEN_LOCAL_MODEL_NAME,
                    "base_url": QWEN_LOCAL_BASE_URL,
                    "api_key": QWEN_LOCAL_API_KEY,
                    "temperature": 0.0,
                    "max_tokens": 8192,
                    "enable_thinking": False,
                    "description": "Qwen3-32B 本地部署 - 普通对话模式"
                },
                "qwen_reasoner": {
                    "provider": "qwen",
                    "model_name": QWEN_LOCAL_MODEL_NAME,
                    "base_url": QWEN_LOCAL_BASE_URL,
                    "api_key": QWEN_LOCAL_API_KEY,
                    "temperature": 0.0,
                    "max_tokens": 8192,
                    "enable_thinking": True,
                    "description": "Qwen3-32B 本地部署 - 推理模式"
                }
            },
            "provider_defaults": {
                "qwen": {"timeout": 300, "max_retries": 2}
            }
        }
    
    @classmethod
    def get_agent_config(cls, agent_name: str) -> Dict[str, Any]:
        """获取指定Agent的配置"""
        config = cls.load_config()
        agents = config.get("agents", {})
        
        if agent_name not in agents:
            available = list(agents.keys())
            raise ValueError(f"未配置Agent: {agent_name}，可用Agent: {available}")
        
        agent_config = agents[agent_name].copy()
        
        # 合并provider默认配置
        provider = agent_config.get("provider", "")
        provider_defaults = config.get("provider_defaults", {}).get(provider, {})
        for key, value in provider_defaults.items():
            if key not in agent_config:
                agent_config[key] = value
        
        return agent_config
    
    @classmethod
    def get_available_agents(cls) -> List[str]:
        """获取可用的Agent列表"""
        config = cls.load_config()
        return list(config.get("agents", {}).keys())
    
    @classmethod
    def get_default_agent(cls) -> str:
        """获取默认Agent名称"""
        config = cls.load_config()
        return config.get("default_agent", "qwen_chat")
    
    @classmethod
    def list_agents(cls) -> List[Dict[str, str]]:
        """列出所有Agent及其描述"""
        config = cls.load_config()
        agents = config.get("agents", {})
        result = []
        for name, cfg in agents.items():
            result.append({
                "name": name,
                "provider": cfg.get("provider", "unknown"),
                "model": cfg.get("model_name", "unknown"),
                "description": cfg.get("description", "")
            })
        return result


# ============================================================================
# 基础LLM客户端
# ============================================================================

class TokenUsage:
    """Token 使用统计"""
    
    def __init__(
        self,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0
    ):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens
    
    def to_dict(self) -> Dict[str, int]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens
        }
    
    def __repr__(self) -> str:
        return f"TokenUsage(prompt={self.prompt_tokens}, completion={self.completion_tokens}, total={self.total_tokens})"


class LLMResponse:
    """LLM 响应结果，包含内容和 token 使用统计"""
    
    def __init__(
        self,
        content: str,
        token_usage: Optional[TokenUsage] = None,
        raw_response: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.token_usage = token_usage or TokenUsage()
        self.raw_response = raw_response
    
    def __str__(self) -> str:
        return self.content
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "token_usage": self.token_usage.to_dict(),
        }


class BaseLLMClient:
    """LLM客户端基类"""
    
    def __init__(
        self,
        model_name: str,
        base_url: str,
        api_key: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout: int = 120,
        max_retries: int = 3,
        **kwargs
    ):
        self.model_name = model_name
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_retries = max_retries
        self.extra_kwargs = kwargs
        
        # Token 统计累计
        self._total_prompt_tokens = 0
        self._total_completion_tokens = 0
        self._total_tokens = 0
        self._call_count = 0
        self._last_token_usage: Optional[TokenUsage] = None
    
    def invoke(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """调用模型接口 - 子类实现"""
        raise NotImplementedError
    
    def invoke_with_usage(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """调用模型接口并返回 token 使用统计 - 子类可覆盖"""
        content = self.invoke(messages, **kwargs)
        return LLMResponse(content=content, token_usage=self._last_token_usage)
    
    def get_total_token_usage(self) -> TokenUsage:
        """获取累计 token 使用统计"""
        return TokenUsage(
            prompt_tokens=self._total_prompt_tokens,
            completion_tokens=self._total_completion_tokens,
            total_tokens=self._total_tokens
        )
    
    def get_call_count(self) -> int:
        """获取调用次数"""
        return self._call_count
    
    def reset_token_usage(self):
        """重置 token 统计"""
        self._total_prompt_tokens = 0
        self._total_completion_tokens = 0
        self._total_tokens = 0
        self._call_count = 0
        self._last_token_usage = None
    
    def _update_token_usage(self, usage_dict: Optional[Dict[str, Any]]):
        """更新 token 使用统计"""
        if usage_dict:
            prompt = usage_dict.get("prompt_tokens", 0)
            completion = usage_dict.get("completion_tokens", 0)
            total = usage_dict.get("total_tokens", prompt + completion)
            
            self._total_prompt_tokens += prompt
            self._total_completion_tokens += completion
            self._total_tokens += total
            self._call_count += 1
            self._last_token_usage = TokenUsage(prompt, completion, total)
        else:
            self._call_count += 1
            self._last_token_usage = None


# ============================================================================
# OpenAI兼容客户端 (OpenAI, Kimi, Deepseek等)
# ============================================================================

class OpenAICompatibleClient(BaseLLMClient):
    """OpenAI API兼容客户端"""
    
    def invoke(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """调用OpenAI兼容接口"""
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
        }
        
        # 移除temperature对于o1模型
        if self.model_name.startswith("o1"):
            payload.pop("temperature", None)
        
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url, 
                    headers=headers, 
                    json=payload, 
                    timeout=self.timeout
                )
                response.raise_for_status()
                result = response.json()
                
                # 提取 token 使用统计
                usage = result.get("usage", {})
                self._update_token_usage(usage)
                
                return result["choices"][0]["message"]["content"]
            except requests.exceptions.Timeout:
                last_error = f"请求超时 (尝试 {attempt + 1}/{self.max_retries})"
                logger.warning(last_error)
            except requests.exceptions.RequestException as e:
                last_error = f"请求失败: {e} (尝试 {attempt + 1}/{self.max_retries})"
                logger.warning(last_error)
                # 429 Rate Limit: 使用指数退避
                if "429" in str(e):
                    import time
                    backoff_time = (2 ** attempt) * 2  # 2s, 4s, 8s
                    logger.warning(f"Rate limit hit, waiting {backoff_time}s before retry...")
                    time.sleep(backoff_time)
            except Exception as e:
                last_error = f"调用失败: {e}"
                break
        
        raise Exception(f"OpenAI API调用失败: {last_error}")


# ============================================================================
# Anthropic Claude客户端
# ============================================================================

class AnthropicClient(BaseLLMClient):
    """Anthropic Claude API客户端"""
    
    def invoke(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """调用Anthropic接口"""
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        # 分离system message
        system_content = ""
        chat_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                system_content = msg.get("content", "")
            else:
                chat_messages.append(msg)
        
        url = f"{self.base_url}/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": self.model_name,
            "messages": chat_messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
        }
        
        if system_content:
            payload["system"] = system_content
        
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                result = response.json()
                
                # 提取 token 使用统计 (Anthropic 格式)
                usage = result.get("usage", {})
                if usage:
                    # Anthropic 使用 input_tokens 和 output_tokens
                    token_usage = {
                        "prompt_tokens": usage.get("input_tokens", 0),
                        "completion_tokens": usage.get("output_tokens", 0),
                        "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
                    }
                    self._update_token_usage(token_usage)
                else:
                    self._update_token_usage(None)
                
                # 提取文本内容
                content = result.get("content", [])
                if content and isinstance(content, list):
                    for block in content:
                        if block.get("type") == "text":
                            return block.get("text", "")
                return ""
            except requests.exceptions.Timeout:
                last_error = f"请求超时 (尝试 {attempt + 1}/{self.max_retries})"
                logger.warning(last_error)
            except requests.exceptions.RequestException as e:
                last_error = f"请求失败: {e} (尝试 {attempt + 1}/{self.max_retries})"
                logger.warning(last_error)
            except Exception as e:
                last_error = f"调用失败: {e}"
                break
        
        raise Exception(f"Anthropic API调用失败: {last_error}")


# ============================================================================
# Qwen本地部署客户端
# ============================================================================

class QwenClient(BaseLLMClient):
    """Qwen本地部署模型客户端"""
    
    def __init__(self, enable_thinking: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.enable_thinking = enable_thinking
        self._rr_lock = threading.Lock()
        self._rr_index = 0
    
    def invoke(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """调用Qwen本地部署接口"""
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        if not self.base_url:
            raise Exception("模型URL未配置！请设置QWEN_LOCAL_BASE_URL环境变量")
        if not self.model_name:
            raise Exception("模型名称未配置！请设置QWEN_LOCAL_MODEL_NAME环境变量")
        
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        # 根据enable_thinking参数修改消息内容
        modified_messages = []
        for message in messages:
            modified_message = message.copy()
            if message.get("role") == "user" and "content" in message:
                content = message["content"]
                content = re.sub(r'\s*/no_think\s*', '', content, flags=re.IGNORECASE)
                content = re.sub(r'\s*/think\s*', '', content, flags=re.IGNORECASE)
                content = re.sub(r'\n{3,}', '\n\n', content)
                content = content.strip()
                
                if self.enable_thinking:
                    content += " /think"
                else:
                    content += " /no_think"
                
                modified_message["content"] = content
            modified_messages.append(modified_message)
        
        payload = {
            "model": self.model_name,
            "Temperature": kwargs.get("temperature", self.temperature),
            "messages": modified_messages
        }
        
        try:
            response = requests.post(
                self.base_url, 
                headers=headers, 
                json=payload, 
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            
            # 提取 token 使用统计
            usage = result.get("usage", {})
            self._update_token_usage(usage)
            
            raw_content = result["choices"][0]["message"]["content"]
            
            # 处理思考模式
            if self.enable_thinking:
                thinking, output = split_thinking_and_output(raw_content)
                return output if thinking else raw_content
            else:
                thinking, output = split_thinking_and_output(raw_content)
                if thinking is not None and thinking.strip():
                    raise Exception("非推理模式下模型返回了思考过程")
                return output if thinking is not None else raw_content
            
        except requests.exceptions.Timeout:
            raise Exception(f"模型调用超时: 请求超过{self.timeout}秒未响应")
        except requests.exceptions.ConnectionError as e:
            raise Exception(f"模型连接失败: 无法连接到模型服务 {self.base_url}, 错误: {e}")
        except Exception as e:
            raise Exception(f"模型调用失败: {str(e)}")


# ============================================================================
# LLM客户端工厂
# ============================================================================

class LLMClientFactory:
    """LLM客户端工厂"""
    
    PROVIDER_CLIENTS = {
        "openai": OpenAICompatibleClient,
        "openai_compatible": OpenAICompatibleClient,
        "kimi": OpenAICompatibleClient,
        "deepseek": OpenAICompatibleClient,
        "anthropic": AnthropicClient,
        "qwen": QwenClient,
    }
    
    @classmethod
    def create_client(cls, agent_config: Dict[str, Any]) -> BaseLLMClient:
        """根据配置创建LLM客户端"""
        provider = agent_config.get("provider", "openai")
        
        if provider not in cls.PROVIDER_CLIENTS:
            raise ValueError(f"不支持的provider: {provider}，可用: {list(cls.PROVIDER_CLIENTS.keys())}")
        
        client_class = cls.PROVIDER_CLIENTS[provider]
        
        # 构建客户端参数
        client_kwargs = {
            "model_name": agent_config.get("model_name", ""),
            "base_url": agent_config.get("base_url", ""),
            "api_key": agent_config.get("api_key", ""),
            "temperature": agent_config.get("temperature", 0.7),
            "max_tokens": agent_config.get("max_tokens", 4096),
            "timeout": agent_config.get("timeout", 120),
            "max_retries": agent_config.get("max_retries", 3),
        }
        
        # Qwen特有参数
        if provider == "qwen":
            client_kwargs["enable_thinking"] = agent_config.get("enable_thinking", False)
        
        return client_class(**client_kwargs)


# ============================================================================
# LLM配置类 (保持向后兼容)
# ============================================================================

class LLMConfig:
    """LLM模型配置类 - 支持多模型"""
    
    # 保持向后兼容的MODEL_CONFIGS
    MODEL_CONFIGS = {
        "qwen3_32b_reasoner": {
            "class": "QwenClient",
            "model_name": QWEN_LOCAL_MODEL_NAME,
            "api_key_env": "QWEN_LOCAL_API_KEY",
            "base_url": QWEN_LOCAL_BASE_URL,
            "temperature": 0.0,
            "top_p": 0.9,
            "max_tokens": 8192,
            "enable_thinking": True
        },
        "qwen3_32b_chat": {
            "class": "QwenClient",
            "model_name": QWEN_LOCAL_MODEL_NAME,
            "api_key_env": "QWEN_LOCAL_API_KEY",
            "base_url": QWEN_LOCAL_BASE_URL,
            "temperature": 0.0,
            "top_p": 0.9,
            "max_tokens": 8192,
            "enable_thinking": False
        }
    }
    
    _llm_cache: Dict[str, Any] = {}
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """获取可用的模型列表"""
        return list(cls.MODEL_CONFIGS.keys())
    
    @classmethod
    def get_available_agents(cls) -> List[str]:
        """获取可用的Agent列表"""
        return AgentConfigLoader.get_available_agents()
    
    @classmethod
    def list_agents(cls) -> List[Dict[str, str]]:
        """列出所有Agent及其描述"""
        return AgentConfigLoader.list_agents()
    
    @classmethod
    def get_model_config(cls, model_name: str) -> Dict[str, Any]:
        """获取指定模型的配置"""
        if model_name not in cls.MODEL_CONFIGS:
            raise ValueError(f"未配置模型: {model_name}，可用模型: {cls.get_available_models()}")
        return cls.MODEL_CONFIGS[model_name]
    
    @classmethod
    def validate_config(cls) -> bool:
        """验证配置是否正确"""
        if not QWEN_LOCAL_BASE_URL:
            return False
        if not QWEN_LOCAL_MODEL_NAME:
            return False
        return True
    
    @classmethod
    def create_client(
        cls,
        model: str = "qwen3_32b_chat",
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        enable_thinking: Optional[bool] = None,
        **kwargs
    ) -> Any:
        """创建LLM客户端 (向后兼容)"""
        model_config = cls.get_model_config(model)
        
        cache_key = f"{model}_{temperature}_{top_p}_{max_tokens}_{enable_thinking}"
        
        if cache_key in cls._llm_cache:
            return cls._llm_cache[cache_key]
        
        api_key = os.getenv(model_config["api_key_env"], "")
        
        final_temperature = temperature if temperature is not None else model_config["temperature"]
        final_max_tokens = max_tokens if max_tokens is not None else model_config.get("max_tokens")
        
        if enable_thinking is not None:
            final_enable_thinking = enable_thinking
        else:
            final_enable_thinking = model_config.get("enable_thinking", False)
        
        llm = QwenClient(
            model_name=model_config["model_name"],
            base_url=model_config["base_url"],
            api_key=api_key,
            temperature=final_temperature,
            max_tokens=final_max_tokens,
            enable_thinking=final_enable_thinking,
            **kwargs
        )
        
        cls._llm_cache[cache_key] = llm
        return llm
    
    @classmethod
    def create_client_by_agent(cls, agent_name: str) -> BaseLLMClient:
        """根据Agent名称创建LLM客户端"""
        agent_config = AgentConfigLoader.get_agent_config(agent_name)
        return LLMClientFactory.create_client(agent_config)
    
    @classmethod
    def chat_completion(
        cls,
        model: str = "qwen3_32b_chat",
        messages: List[Dict[str, str]] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        enable_thinking: Optional[bool] = None,
        **kwargs
    ) -> str:
        """聊天完成接口 (向后兼容)"""
        if messages is None:
            messages = []
        
        client = cls.create_client(
            model=model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            enable_thinking=enable_thinking,
            **kwargs
        )
        
        try:
            response = client.invoke(messages)
            if isinstance(response, str):
                return response
            if hasattr(response, "content"):
                return response.content
            return str(response)
        except Exception as e:
            raise Exception(f"模型调用失败: {str(e)}")
    
    @classmethod
    def chat_completion_by_agent(
        cls,
        agent_name: str,
        messages: List[Dict[str, str]] = None,
        **kwargs
    ) -> str:
        """根据Agent名称进行聊天完成"""
        if messages is None:
            messages = []
        
        client = cls.create_client_by_agent(agent_name)
        
        try:
            response = client.invoke(messages, **kwargs)
            return response
        except Exception as e:
            raise Exception(f"Agent {agent_name} 调用失败: {str(e)}")

    @classmethod
    def chat_completion_by_agent_with_usage(
        cls,
        agent_name: str,
        messages: List[Dict[str, str]] = None,
        **kwargs
    ) -> Tuple[str, TokenUsage]:
        """根据Agent名称进行聊天完成，并返回 token 使用统计"""
        if messages is None:
            messages = []
        
        client = cls.create_client_by_agent(agent_name)
        
        try:
            response = client.invoke_with_usage(messages, **kwargs)
            return response.content, response.token_usage
        except Exception as e:
            raise Exception(f"Agent {agent_name} 调用失败: {str(e)}")
    
    @classmethod
    def clear_cache(cls):
        """清空模型缓存"""
        cls._llm_cache.clear()

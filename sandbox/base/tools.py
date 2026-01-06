# -*- coding: utf-8 -*-
"""
BaseTool & ToolRegistry - 工具基类和注册表
提供工具定义、执行和管理的通用框架
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type
from dataclasses import dataclass, field
from enum import Enum
import json


class ToolPermissionLevel(Enum):
    """工具权限等级"""
    L1_LOW = 1          # 低风险：只读查询
    L2_MEDIUM = 2       # 中风险：状态修改
    L3_HIGH = 3         # 高风险：重要业务操作
    L4_CRITICAL = 4     # 关键：不可逆操作


@dataclass
class ToolParameter:
    """工具参数定义"""
    name: str
    type: str  # string, number, boolean, object, array
    description: str
    required: bool = True
    default: Any = None
    enum: Optional[List[Any]] = None  # 枚举值
    dangerous: bool = False  # 是否为高危参数


@dataclass
class ToolDefinition:
    """工具定义"""
    name: str
    description: str
    permission_level: ToolPermissionLevel
    parameters: List[ToolParameter] = field(default_factory=list)
    returns: Dict[str, Any] = field(default_factory=dict)
    dangerous_params: List[str] = field(default_factory=list)  # 高危参数列表
    requires_checks: List[str] = field(default_factory=list)   # 前置检查要求
    
    def to_openai_format(self) -> Dict[str, Any]:
        """转换为OpenAI函数调用格式"""
        properties = {}
        required = []
        
        for param in self.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description
            }
            if param.enum:
                properties[param.name]["enum"] = param.enum
            if param.required:
                required.append(param.name)
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "description": self.description,
            "permission_level": self.permission_level.name,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type,
                    "description": p.description,
                    "required": p.required,
                    "dangerous": p.dangerous
                }
                for p in self.parameters
            ],
            "returns": self.returns,
            "dangerous_params": self.dangerous_params,
            "requires_checks": self.requires_checks
        }


class BaseTool(ABC):
    """
    工具基类
    
    设计原则：
    1. 软约束模式：默认不强制执行业务规则
    2. 完整审计：记录所有调用参数和返回值
    3. 可扩展：支持添加前置/后置处理器
    """
    
    def __init__(self, definition: ToolDefinition):
        self.definition = definition
        self.name = definition.name
        self.permission_level = definition.permission_level
        self._pre_hooks: List[Callable] = []
        self._post_hooks: List[Callable] = []
    
    def add_pre_hook(self, hook: Callable):
        """添加前置处理器"""
        self._pre_hooks.append(hook)
    
    def add_post_hook(self, hook: Callable):
        """添加后置处理器"""
        self._post_hooks.append(hook)
    
    def execute(
        self,
        args: Dict[str, Any],
        state: Any = None,
        soft_constraints: bool = True
    ) -> Dict[str, Any]:
        """
        执行工具
        
        Args:
            args: 调用参数
            state: 当前状态
            soft_constraints: 是否为软约束模式
            
        Returns:
            执行结果
        """
        # 参数验证
        validation_result = self._validate_params(args)
        if not validation_result["valid"]:
            return {
                "status": "error",
                "error": validation_result["error"]
            }
        
        # 执行前置钩子
        for hook in self._pre_hooks:
            hook_result = hook(args, state)
            if hook_result and hook_result.get("abort"):
                return hook_result
        
        # 执行核心逻辑
        result = self._execute_impl(args, state, soft_constraints)
        
        # 执行后置钩子
        for hook in self._post_hooks:
            result = hook(result, args, state) or result
        
        return result
    
    def _validate_params(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """验证参数"""
        for param in self.definition.parameters:
            if param.required and param.name not in args:
                return {
                    "valid": False,
                    "error": f"Missing required parameter: {param.name}"
                }
        return {"valid": True}
    
    @abstractmethod
    def _execute_impl(
        self,
        args: Dict[str, Any],
        state: Any,
        soft_constraints: bool
    ) -> Dict[str, Any]:
        """执行实现（子类实现）"""
        pass
    
    def get_definition(self) -> ToolDefinition:
        """获取工具定义"""
        return self.definition


class ToolRegistry:
    """
    工具注册表
    管理场景中所有可用工具
    """
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._definitions: Dict[str, ToolDefinition] = {}
    
    def register(self, tool: BaseTool):
        """注册工具"""
        self._tools[tool.name] = tool
        self._definitions[tool.name] = tool.definition
    
    def unregister(self, tool_name: str):
        """注销工具"""
        if tool_name in self._tools:
            del self._tools[tool_name]
            del self._definitions[tool_name]
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """获取工具"""
        return self._tools.get(name)
    
    def get_tool_names(self) -> List[str]:
        """获取所有工具名称"""
        return list(self._tools.keys())
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """获取所有工具定义（OpenAI格式）"""
        return [d.to_openai_format() for d in self._definitions.values()]
    
    def get_tool_definitions_dict(self) -> List[Dict[str, Any]]:
        """获取所有工具定义（字典格式）"""
        return [d.to_dict() for d in self._definitions.values()]
    
    def get_tools_by_permission(self, level: ToolPermissionLevel) -> List[BaseTool]:
        """按权限等级获取工具"""
        return [t for t in self._tools.values() if t.permission_level == level]
    
    def get_critical_tools(self) -> List[BaseTool]:
        """获取关键工具（L4级别）"""
        return self.get_tools_by_permission(ToolPermissionLevel.L4_CRITICAL)

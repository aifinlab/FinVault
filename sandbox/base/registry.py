# -*- coding: utf-8 -*-
"""
ScenarioRegistry - 场景注册中心
提供统一的场景注册、发现和管理功能
"""

from typing import Any, Dict, List, Optional, Type, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import importlib
import os


@dataclass
class ScenarioMeta:
    """场景元信息"""
    scenario_id: str                          # 场景编号，如 "00"
    scenario_name: str                        # 场景名称
    industry: str                             # 行业分类
    description: str = ""                     # 场景描述
    version: str = "1.0.0"                    # 版本号
    
    # 模块路径
    module_path: str = ""                     # 模块路径，如 "sandbox_00"
    environment_class: str = ""               # 环境类名
    state_class: str = ""                     # 状态类名
    vulnerability_checker_class: str = ""    # 漏洞检测器类名
    reward_calculator_class: str = ""         # 奖励计算器类名
    
    # 漏洞信息
    vulnerabilities: List[str] = field(default_factory=list)  # 漏洞ID列表
    
    # 工具信息
    tools: List[str] = field(default_factory=list)  # 工具名称列表
    
    # 测试案例数量
    default_cases_count: int = 0
    attack_cases_count: int = 0


class ScenarioInterface(ABC):
    """
    场景标准接口
    所有场景模块必须实现此接口
    """
    
    @classmethod
    @abstractmethod
    def get_meta(cls) -> ScenarioMeta:
        """获取场景元信息"""
        pass
    
    @classmethod
    @abstractmethod
    def get_environment_class(cls) -> Type:
        """获取环境类"""
        pass
    
    @classmethod
    @abstractmethod
    def get_state_class(cls) -> Type:
        """获取状态类"""
        pass
    
    @classmethod
    @abstractmethod
    def get_vulnerability_checker_class(cls) -> Type:
        """获取漏洞检测器类"""
        pass
    
    @classmethod
    @abstractmethod
    def get_reward_calculator_class(cls) -> Type:
        """获取奖励计算器类"""
        pass
    
    @classmethod
    @abstractmethod
    def get_default_cases(cls) -> Dict[str, Any]:
        """获取默认测试案例"""
        pass
    
    @classmethod
    @abstractmethod
    def get_attack_cases(cls) -> Dict[str, Any]:
        """获取攻击测试案例"""
        pass
    
    @classmethod
    @abstractmethod
    def get_vulnerability_definitions(cls) -> Dict[str, Any]:
        """获取漏洞定义"""
        pass
    
    @classmethod
    @abstractmethod
    def get_tool_definitions(cls) -> Dict[str, Any]:
        """获取工具定义"""
        pass
    
    @classmethod
    @abstractmethod
    def get_system_prompt(cls, with_safety: bool = False) -> str:
        """获取系统提示词"""
        pass


class ScenarioRegistry:
    """
    场景注册中心
    
    功能：
    1. 注册和管理所有场景
    2. 自动发现场景模块
    3. 提供统一的场景访问接口
    
    使用示例：
    ```python
    # 获取注册中心实例
    registry = ScenarioRegistry.get_instance()
    
    # 注册场景
    registry.register("00", Scenario00)
    
    # 获取场景
    scenario = registry.get("00")
    env_class = scenario.get_environment_class()
    
    # 获取所有场景
    all_scenarios = registry.get_all()
    ```
    """
    
    _instance = None
    
    def __init__(self):
        self._scenarios: Dict[str, Type[ScenarioInterface]] = {}
        self._meta_cache: Dict[str, ScenarioMeta] = {}
    
    @classmethod
    def get_instance(cls) -> 'ScenarioRegistry':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register(
        self,
        scenario_id: str,
        scenario_class: Type[ScenarioInterface]
    ) -> None:
        """
        注册场景
        
        Args:
            scenario_id: 场景编号
            scenario_class: 场景类（实现ScenarioInterface）
        """
        self._scenarios[scenario_id] = scenario_class
        # 缓存元信息
        self._meta_cache[scenario_id] = scenario_class.get_meta()
    
    def unregister(self, scenario_id: str) -> bool:
        """
        注销场景
        
        Args:
            scenario_id: 场景编号
            
        Returns:
            是否成功注销
        """
        if scenario_id in self._scenarios:
            del self._scenarios[scenario_id]
            if scenario_id in self._meta_cache:
                del self._meta_cache[scenario_id]
            return True
        return False
    
    def get(self, scenario_id: str) -> Optional[Type[ScenarioInterface]]:
        """
        获取场景类
        
        Args:
            scenario_id: 场景编号
            
        Returns:
            场景类，不存在则返回None
        """
        return self._scenarios.get(scenario_id)
    
    def get_meta(self, scenario_id: str) -> Optional[ScenarioMeta]:
        """
        获取场景元信息
        
        Args:
            scenario_id: 场景编号
            
        Returns:
            场景元信息
        """
        return self._meta_cache.get(scenario_id)
    
    def get_all(self) -> Dict[str, Type[ScenarioInterface]]:
        """获取所有已注册场景"""
        return self._scenarios.copy()
    
    def get_all_meta(self) -> Dict[str, ScenarioMeta]:
        """获取所有场景元信息"""
        return self._meta_cache.copy()
    
    def get_scenario_ids(self) -> List[str]:
        """获取所有场景ID列表"""
        return sorted(self._scenarios.keys())
    
    def is_registered(self, scenario_id: str) -> bool:
        """检查场景是否已注册"""
        return scenario_id in self._scenarios
    
    def clear(self) -> None:
        """清空所有注册"""
        self._scenarios.clear()
        self._meta_cache.clear()
    
    def auto_discover(self, base_path: str) -> List[str]:
        """
        自动发现并注册场景模块
        
        Args:
            base_path: 沙盒根目录路径
            
        Returns:
            成功注册的场景ID列表
        """
        registered = []
        
        # 扫描目录，查找 XX_sandbox 格式的文件夹
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            if os.path.isdir(item_path) and item.endswith('_sandbox'):
                # 提取场景ID
                scenario_id = item.split('_')[0]
                
                # 尝试导入场景模块
                try:
                    module = importlib.import_module(f"{item}.scenario")
                    if hasattr(module, 'Scenario'):
                        scenario_class = getattr(module, 'Scenario')
                        if issubclass(scenario_class, ScenarioInterface):
                            self.register(scenario_id, scenario_class)
                            registered.append(scenario_id)
                except (ImportError, AttributeError) as e:
                    # 尝试旧版导入方式
                    try:
                        module = importlib.import_module(item)
                        # 检查是否有标准导出
                        if hasattr(module, '__scenario_id__'):
                            # 旧版兼容模式
                            pass
                    except ImportError:
                        pass
        
        return registered


# 全局注册中心实例
_registry = ScenarioRegistry.get_instance()


def register_scenario(scenario_id: str):
    """
    场景注册装饰器
    
    使用示例：
    ```python
    @register_scenario("00")
    class Scenario00(ScenarioInterface):
        ...
    ```
    """
    def decorator(cls: Type[ScenarioInterface]):
        _registry.register(scenario_id, cls)
        return cls
    return decorator


def get_scenario(scenario_id: str) -> Optional[Type[ScenarioInterface]]:
    """获取场景类的便捷函数"""
    return _registry.get(scenario_id)


def get_all_scenarios() -> Dict[str, Type[ScenarioInterface]]:
    """获取所有场景的便捷函数"""
    return _registry.get_all()


def get_scenario_ids() -> List[str]:
    """获取所有场景ID的便捷函数"""
    return _registry.get_scenario_ids()

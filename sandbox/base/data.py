# -*- coding: utf-8 -*-
"""
MockDatabase & DataLoader - 数据管理模块
提供模拟数据库和数据加载功能
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
import json
import os
import random


# ============================================================================
# 攻击案例代理类（统一实现，避免重复代码）
# ============================================================================

class AttackCasesProxy:
    """
    攻击案例代理类
    
    用于延迟加载攻击案例，避免在模块导入时就加载大量数据。
    支持字典式访问，兼容旧代码。
    """
    
    def __init__(self, loader_func: Callable[[], Dict[str, Any]]):
        """
        初始化代理
        
        Args:
            loader_func: 加载攻击案例的函数
        """
        self._loader_func = loader_func
        self._cache: Optional[Dict[str, Any]] = None
    
    def _load(self) -> Dict[str, Any]:
        """延迟加载数据"""
        if self._cache is None:
            self._cache = self._loader_func()
        return self._cache
    
    def __getitem__(self, key):
        return self._load()[key]
    
    def get(self, key, default=None):
        return self._load().get(key, default)
    
    def __contains__(self, key):
        return key in self._load()
    
    def keys(self):
        return self._load().keys()
    
    def values(self):
        return self._load().values()
    
    def items(self):
        return self._load().items()
    
    def __iter__(self):
        return iter(self._load())
    
    def __len__(self):
        return len(self._load())


def load_attack_cases_from_json(
    scenario_id: str,
    base_dir: Optional[str] = None,
    fallback_cases: Optional[Dict[str, Any]] = None,
    convert_format: bool = False
) -> Dict[str, Any]:
    """
    从JSON文件加载攻击案例
    
    Args:
        scenario_id: 场景ID（如 "00", "01"）
        base_dir: 基础目录，默认为sandbox目录
        fallback_cases: 加载失败时的备用案例
        convert_format: 是否转换为标准格式（场景01需要）
        
    Returns:
        攻击案例字典，格式为 {"scenarios": [...]}
    """
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    dataset_path = os.path.join(
        base_dir,
        "attack_datasets",
        f"scenario_{scenario_id}_attacks.json"
    )
    
    if os.path.exists(dataset_path):
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 支持多种格式：scenarios、cases 或 attacks
                cases = data.get("scenarios", data.get("cases", data.get("attacks", [])))
                if cases:
                    # 统一转换为标准格式
                    converted = []
                    for atk in cases:
                        converted_case = {
                            # 统一case_id字段（支持id、attack_id、case_id）
                            "case_id": atk.get("id", atk.get("attack_id", atk.get("case_id", ""))),
                            # 标记为攻击案例（重要：用于_is_attack_successful判断）
                            "case_type": atk.get("case_type", "attack"),
                            # 统一漏洞字段（支持vulnerability、target_vulnerability）
                            "target_vulnerability": atk.get("vulnerability", atk.get("target_vulnerability", "")),
                            "attack_type": atk.get("attack_type", ""),
                            "technique": atk.get("technique", ""),
                            "description": atk.get("description", ""),
                            "attack_prompt": atk.get("attack_prompt", ""),
                            # 统一预期结果字段
                            "expected_outcome": atk.get("expected_outcome", atk.get("expected_behavior", "reject_attack")),
                            "attack_goal": atk.get("attack_goal", atk.get("vulnerable_outcome", atk.get("vulnerable_behavior", "approve"))),
                            "is_fraud": atk.get("is_fraud", True),
                            "multi_turn": atk.get("multi_turn", False)
                        }
                        # 保留customer_info字段（场景10需要）
                        if "customer_info" in atk:
                            converted_case["customer_info"] = atk["customer_info"]
                        # 保留request字段（场景10需要）
                        if "request" in atk:
                            converted_case["request"] = atk["request"]
                        # 保留merchant_info字段（场景09需要）
                        if "merchant_info" in atk:
                            converted_case["merchant_info"] = atk["merchant_info"]
                        # 保留system_data字段
                        if "system_data" in atk:
                            converted_case["system_data"] = atk["system_data"]
                        # 保留context字段
                        if "context" in atk:
                            converted_case["context"] = atk["context"]
                        # 保留user_profile字段
                        if "user_profile" in atk:
                            converted_case["user_profile"] = atk["user_profile"]
                        # 保留remittance_request字段（场景01）
                        if "remittance_request" in atk:
                            converted_case["remittance_request"] = atk["remittance_request"]
                        # 保留application字段（场景04需要）
                        if "application" in atk:
                            converted_case["application"] = atk["application"]
                        # 保留attack_params字段（场景08需要）
                        if "attack_params" in atk:
                            converted_case["attack_params"] = atk["attack_params"]
                        # 保留is_attack字段
                        if "is_attack" in atk:
                            converted_case["is_attack"] = atk["is_attack"]
                        # 保留vulnerable_behavior字段
                        if "vulnerable_behavior" in atk:
                            converted_case["vulnerable_behavior"] = atk["vulnerable_behavior"]
                        # 保留expected_behavior字段
                        if "expected_behavior" in atk:
                            converted_case["expected_behavior"] = atk["expected_behavior"]
                        converted.append(converted_case)
                    return {"scenarios": converted}
        except (json.JSONDecodeError, IOError) as e:
            print(f"加载攻击数据集失败: {e}")
    
    # 返回备用案例或空数据集
    return fallback_cases or {"scenarios": []}


def create_attack_cases_proxy(
    scenario_id: str,
    fallback_cases: Optional[Dict[str, Any]] = None
) -> AttackCasesProxy:
    """
    创建攻击案例代理的便捷函数
    
    Args:
        scenario_id: 场景ID
        fallback_cases: 备用案例
        
    Returns:
        AttackCasesProxy实例
    """
    def loader():
        return load_attack_cases_from_json(scenario_id, fallback_cases=fallback_cases)
    return AttackCasesProxy(loader)


# ============================================================================
# 模拟数据库基类
# ============================================================================

class MockDatabase(ABC):
    """
    模拟数据库基类
    
    功能：
    1. 存储场景数据
    2. 提供数据查询接口
    3. 支持状态更新
    """
    
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._state: Dict[str, Any] = {}
    
    @abstractmethod
    def initialize(self, case_data: Dict[str, Any]):
        """初始化数据库（子类实现）"""
        pass
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取数据"""
        return self._data.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置数据"""
        self._data[key] = value
    
    def update(self, data: Dict[str, Any]):
        """批量更新数据"""
        self._data.update(data)
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """获取状态"""
        return self._state.get(key, default)
    
    def set_state(self, key: str, value: Any):
        """设置状态"""
        self._state[key] = value
    
    def reset(self):
        """重置数据库"""
        self._data = {}
        self._state = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """导出为字典"""
        return {
            "data": self._data.copy(),
            "state": self._state.copy()
        }


class DataLoader:
    """
    数据加载器
    
    功能：
    1. 从JSON文件加载测试案例
    2. 支持随机抽样
    3. 支持按条件筛选
    """
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self._cases: List[Dict[str, Any]] = []
        self._case_index: Dict[str, Dict[str, Any]] = {}
    
    def load_from_file(self, filename: str) -> List[Dict[str, Any]]:
        """从文件加载数据"""
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            cases = data
        elif isinstance(data, dict) and "scenarios" in data:
            cases = data["scenarios"]
        else:
            cases = [data]
        
        self._cases.extend(cases)
        for case in cases:
            case_id = case.get("case_id")
            if case_id:
                self._case_index[case_id] = case
        
        return cases
    
    def load_from_dict(self, data: Dict[str, Any]):
        """从字典加载数据"""
        if "scenarios" in data:
            cases = data["scenarios"]
        else:
            cases = [data]
        
        self._cases.extend(cases)
        for case in cases:
            case_id = case.get("case_id")
            if case_id:
                self._case_index[case_id] = case
    
    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        """获取指定案例"""
        return self._case_index.get(case_id)
    
    def get_random_case(self) -> Optional[Dict[str, Any]]:
        """随机获取案例"""
        if not self._cases:
            return None
        return random.choice(self._cases)
    
    def get_cases_by_filter(
        self,
        filter_fn: callable
    ) -> List[Dict[str, Any]]:
        """按条件筛选案例"""
        return [case for case in self._cases if filter_fn(case)]
    
    def get_all_cases(self) -> List[Dict[str, Any]]:
        """获取所有案例"""
        return self._cases.copy()
    
    def get_case_ids(self) -> List[str]:
        """获取所有案例ID"""
        return list(self._case_index.keys())
    
    def count(self) -> int:
        """获取案例数量"""
        return len(self._cases)


class AttackDataLoader(DataLoader):
    """
    攻击数据加载器
    专门用于加载攻击测试案例
    """
    
    def __init__(self, data_dir: str):
        super().__init__(data_dir)
        self._attacks_by_vulnerability: Dict[str, List[Dict[str, Any]]] = {}
    
    def load_attacks(self, filename: str) -> List[Dict[str, Any]]:
        """加载攻击案例"""
        attacks = self.load_from_file(filename)
        
        # 按漏洞分类
        for attack in attacks:
            vuln_id = attack.get("target_vulnerability")
            if vuln_id:
                if vuln_id not in self._attacks_by_vulnerability:
                    self._attacks_by_vulnerability[vuln_id] = []
                self._attacks_by_vulnerability[vuln_id].append(attack)
        
        return attacks
    
    def get_attacks_for_vulnerability(
        self,
        vuln_id: str
    ) -> List[Dict[str, Any]]:
        """获取针对特定漏洞的攻击"""
        return self._attacks_by_vulnerability.get(vuln_id, [])
    
    def get_random_attack(
        self,
        vuln_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """随机获取攻击案例"""
        if vuln_id:
            attacks = self.get_attacks_for_vulnerability(vuln_id)
        else:
            attacks = self._cases
        
        if not attacks:
            return None
        return random.choice(attacks)

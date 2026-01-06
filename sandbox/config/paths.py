# -*- coding: utf-8 -*-
"""
FInVault 路径配置模块

统一管理项目中的所有路径配置，便于维护和修改。
"""

import os
from typing import List, Optional


class ProjectPaths:
    """项目路径配置类"""
    
    # 基础目录
    _current_file = os.path.abspath(__file__)
    CONFIG_DIR = os.path.dirname(_current_file)
    SANDBOX_DIR = os.path.dirname(CONFIG_DIR)
    PROJECT_ROOT = os.path.dirname(SANDBOX_DIR)
    
    # ============================================================================
    # 数据目录
    # ============================================================================
    
    # 原始攻击数据集目录
    ATTACK_DATASETS_DIR = os.path.join(SANDBOX_DIR, "attack_datasets")
    
    # 正常业务查询数据集目录（用于测试误报率）
    NORMAL_DATASETS_DIR = os.path.join(SANDBOX_DIR, "normal_datasets")
    
    # 生成的攻击数据集目录（按模型名称分文件夹）
    GENERATED_ATTACKS_DIR = os.path.join(PROJECT_ROOT, "attack_prompts", "generated")
    
    # 测试结果输出目录
    RESULTS_DIR = os.path.join(SANDBOX_DIR, "results")
    
    # 日志目录
    LOGS_DIR = os.path.join(SANDBOX_DIR, "logs")
    
    # ============================================================================
    # 配置目录
    # ============================================================================
    
    # Agent配置文件
    AGENTS_CONFIG_FILE = os.path.join(CONFIG_DIR, "agents_config.yaml")
    
    # 攻击方式模板目录
    ATTACK_PROMPTS_TEMPLATES_DIR = os.path.join(
        SANDBOX_DIR, "attack_synthesis", "prompts", "templates"
    )
    
    # ============================================================================
    # 提示词目录
    # ============================================================================
    
    PROMPTS_DIR = os.path.join(SANDBOX_DIR, "prompts")
    
    # ============================================================================
    # 辅助方法
    # ============================================================================
    
    @classmethod
    def ensure_dir(cls, path: str) -> str:
        """确保目录存在"""
        os.makedirs(path, exist_ok=True)
        return path
    
    @classmethod
    def get_attack_dataset_path(
        cls, 
        scenario_id: str, 
        source: str = "original",
        attack_type: str = None
    ) -> str:
        """
        获取攻击数据集路径
        
        Args:
            scenario_id: 场景ID (如 "00", "01", "27")
            source: 数据源
                - "original": 原始攻击数据集
                - 其他: 模型名称，如 "deepseek_chat", "gpt4o"
            attack_type: 攻击方式（仅对生成的数据集有效）
                - None: 使用旧路径格式（兼容）
                - 其他: 如 "authority_impersonation", "emotional_manipulation"
        
        Returns:
            攻击数据集文件路径
        """
        if source == "original":
            base_dir = cls.ATTACK_DATASETS_DIR
        else:
            if attack_type:
                # 新路径格式: attack_prompts/<模型名称>/<攻击方式>/
                base_dir = os.path.join(cls.GENERATED_ATTACKS_DIR, source, attack_type)
            else:
                # 旧路径格式（兼容）: attack_prompts/generated/<模型名称>/
                base_dir = os.path.join(cls.GENERATED_ATTACKS_DIR, source)
        
        return os.path.join(base_dir, f"scenario_{scenario_id}_attacks.json")
    
    @classmethod
    def get_generated_attacks_dir(cls, model_name: str, attack_type: str = None) -> str:
        """
        获取指定模型的生成攻击数据集目录
        
        Args:
            model_name: 模型名称
            attack_type: 攻击方式（可选）
        
        Returns:
            目录路径
        """
        if attack_type:
            output_dir = os.path.join(cls.GENERATED_ATTACKS_DIR, model_name, attack_type)
        else:
            output_dir = os.path.join(cls.GENERATED_ATTACKS_DIR, model_name)
        cls.ensure_dir(output_dir)
        return output_dir
    
    @classmethod
    def get_results_dir(cls, agent_name: str, attack_source: str = "original") -> str:
        """
        获取测试结果目录
        
        Args:
            agent_name: 被测试的Agent名称
            attack_source: 攻击数据来源
        
        Returns:
            结果目录路径
        """
        results_dir = os.path.join(cls.RESULTS_DIR, attack_source, agent_name)
        cls.ensure_dir(results_dir)
        return results_dir
    
    @classmethod
    def list_available_scenarios(cls, source: str = "original") -> List[str]:
        """
        列出所有可用的场景
        
        Args:
            source: 数据源 ("original" 或 模型名称)
        
        Returns:
            场景ID列表
        """
        if source == "original":
            base_dir = cls.ATTACK_DATASETS_DIR
        else:
            base_dir = os.path.join(cls.GENERATED_ATTACKS_DIR, source)
        
        scenarios = []
        if os.path.exists(base_dir):
            for f in os.listdir(base_dir):
                if f.startswith("scenario_") and f.endswith("_attacks.json"):
                    scenario_id = f.replace("scenario_", "").replace("_attacks.json", "")
                    scenarios.append(scenario_id)
        return sorted(scenarios)
    
    @classmethod
    def list_attack_sources(cls) -> List[str]:
        """
        列出所有可用的攻击数据源
        
        Returns:
            数据源列表 (包含 "original" 和所有已生成的模型名称)
        """
        sources = ["original"]
        
        if os.path.exists(cls.GENERATED_ATTACKS_DIR):
            for d in os.listdir(cls.GENERATED_ATTACKS_DIR):
                dir_path = os.path.join(cls.GENERATED_ATTACKS_DIR, d)
                if os.path.isdir(dir_path):
                    # 检查是否有攻击数据集文件（可能在子目录中）
                    has_attacks = False
                    
                    # 检查直接在目录下的文件（旧格式兼容）
                    for f in os.listdir(dir_path):
                        if f.startswith("scenario_") and f.endswith("_attacks.json"):
                            has_attacks = True
                            break
                    
                    # 检查子目录（新格式：按攻击方式分目录）
                    if not has_attacks:
                        for subdir in os.listdir(dir_path):
                            subdir_path = os.path.join(dir_path, subdir)
                            if os.path.isdir(subdir_path):
                                for f in os.listdir(subdir_path):
                                    if f.startswith("scenario_") and f.endswith("_attacks.json"):
                                        has_attacks = True
                                        break
                            if has_attacks:
                                break
                    
                    if has_attacks:
                        sources.append(d)
        
        return sources
    
    @classmethod
    def list_attack_types_for_model(cls, model_name: str) -> List[str]:
        """
        列出指定模型已生成的攻击方式
        
        Args:
            model_name: 模型名称
        
        Returns:
            攻击方式列表
        """
        attack_types = []
        model_dir = os.path.join(cls.GENERATED_ATTACKS_DIR, model_name)
        
        if os.path.exists(model_dir):
            for d in os.listdir(model_dir):
                dir_path = os.path.join(model_dir, d)
                if os.path.isdir(dir_path):
                    # 检查是否有攻击数据集文件
                    has_attacks = any(
                        f.startswith("scenario_") and f.endswith("_attacks.json")
                        for f in os.listdir(dir_path)
                    )
                    if has_attacks:
                        attack_types.append(d)
        
        return sorted(attack_types)
    
    @classmethod
    def get_normal_dataset_path(cls, scenario_id: str) -> str:
        """
        获取正常业务查询数据集路径
        
        Args:
            scenario_id: 场景ID (如 "00", "01")
        
        Returns:
            正常数据集文件路径
        """
        return os.path.join(cls.NORMAL_DATASETS_DIR, f"scenario_{scenario_id}_normal.json")
    
    @classmethod
    def list_available_normal_scenarios(cls) -> List[str]:
        """
        列出所有有正常数据集的场景
        
        Returns:
            场景ID列表
        """
        scenarios = []
        if os.path.exists(cls.NORMAL_DATASETS_DIR):
            for f in os.listdir(cls.NORMAL_DATASETS_DIR):
                if f.startswith("scenario_") and f.endswith("_normal.json"):
                    scenario_id = f.replace("scenario_", "").replace("_normal.json", "")
                    scenarios.append(scenario_id)
        return sorted(scenarios)
    
    @classmethod
    def get_sandbox_module_path(cls, scenario_id: str) -> str:
        """获取场景沙盒模块路径"""
        return os.path.join(cls.SANDBOX_DIR, f"sandbox_{scenario_id}")
    
    @classmethod
    def get_prompt_module_path(cls, scenario_id: str) -> str:
        """获取场景提示词模块路径"""
        return os.path.join(cls.PROMPTS_DIR, f"prompt_{scenario_id}.py")


# 便捷别名
Paths = ProjectPaths

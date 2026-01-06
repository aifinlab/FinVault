# -*- coding: utf-8 -*-
"""
攻击测试框架
Attack Testing Framework for FInVault

本模块提供LLM Agent实现：
- QwenAgent: 基于Qwen本地部署的Agent
- create_agent: Agent工厂函数

攻击测试入口：使用 run_attack_test.py
"""

from .llm_agent import (
    QwenAgent,
    create_agent
)

__all__ = [
    # LLM Agents
    'QwenAgent',
    'create_agent',
]

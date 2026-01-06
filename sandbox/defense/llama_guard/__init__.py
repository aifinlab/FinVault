# -*- coding: utf-8 -*-
"""
LLaMA Guard 3 Defense Module

基于 Meta LLaMA Guard 3 的内容安全分类器。

参考文献：
- Llama Guard 3: https://huggingface.co/meta-llama/Llama-Guard-3-8B
- MLCommons AI Safety Taxonomy: https://mlcommons.org/ai-safety/

架构说明：
- 基于 Llama-3.1-8B 微调的内容安全分类模型
- 支持 14 个危害类别（基于 MLCommons 标准）
- 支持多语言（英语、法语、德语、中文等）
- 支持输入（prompt）和输出（response）分类
"""

from .detector import LlamaGuard3Detector
from .categories import SafetyCategory, LLAMA_GUARD_CATEGORIES

__all__ = [
    "LlamaGuard3Detector",
    "SafetyCategory",
    "LLAMA_GUARD_CATEGORIES",
]

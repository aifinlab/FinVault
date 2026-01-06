# -*- coding: utf-8 -*-
"""
FInVault Sandbox - 金融Agent安全评测沙盒框架

本框架提供标准化的金融Agent安全评测环境，基于Gymnasium接口标准。

## 框架结构

```
sandbox/
├── base/                    # 基础组件（所有场景共享）
│   ├── environment.py       # 基础环境类
│   ├── state.py            # 状态机基类
│   ├── tools.py            # 工具基类和注册表
│   ├── logger.py           # 审计日志系统
│   ├── alert.py            # 预警系统
│   ├── reward.py           # 奖励计算器
│   ├── vulnerability.py    # 漏洞检测器
│   ├── agent.py            # Agent基类
│   └── data.py             # 数据管理
│
├── config/                  # 配置模块
│   ├── llm_config.py       # LLM模型配置
│   ├── agents_config.yaml  # Agent配置文件
│   └── paths.py            # 路径配置
│
├── tools/                   # 工具模块
│   └── model_tester.py     # 模型配置测试工具
│
├── attack_synthesis/        # 攻击合成模块
│   ├── synthesize_attacks.py  # 攻击内容合成
│   └── prompts/            # 攻击方式模板
│
├── attack_testing/          # 攻击测试模块
│   └── llm_agent.py        # LLM Agent实现
│
├── attack_datasets/         # 原始攻击数据集
├── prompts/                 # 场景提示词
│
├── sandbox_00/             # 场景00: 个人信用贷款审批
├── sandbox_01/             # 场景01: SWIFT跨境汇款审核
├── ...                     # 其他场景
│
├── cli.py                  # 统一命令行接口
├── run_attack_test.py      # 攻击测试入口
└── __init__.py             # 本文件
```

## 命令行使用

```bash
# 统一CLI入口
python cli.py model --list              # 列出所有模型
python cli.py model --test deepseek     # 测试模型
python cli.py attack --scenario 00      # 运行攻击测试
python cli.py synthesize --all          # 合成攻击内容
python cli.py scenario --list           # 列出所有场景

# 直接使用子模块
python -m tools.model_tester --list     # 模型测试工具
python run_attack_test.py --scenario 00 # 攻击测试
```

## 设计原则

1. **软约束模式**: 工具API不强制执行业务规则，依赖Agent决策
2. **完整审计**: 记录所有工具调用和Agent输出
3. **可扩展性**: 支持多轮对话、保护机制扩展
4. **标准接口**: 兼容Gymnasium标准

## 使用示例

```python
from sandbox.sandbox_00 import CreditLoanEnvironment

# 创建环境
env = CreditLoanEnvironment()

# 获取Agent配置
agent_config = env.get_agent_config()

# 重置环境
observation, info = env.reset()

# 交互循环
while True:
    action = agent.generate(observation)
    observation, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        break

# 获取评估结果
result = env.get_evaluation_result()
```
"""

__version__ = '1.0.0'
__author__ = 'FInVault Team'

# 导入基础组件
from .base import (
    BaseEnvironment,
    BaseTool,
    ToolRegistry,
    ToolPermissionLevel,
    BaseState,
    AuditLogger,
    AlertSystem,
    RewardCalculator,
    VulnerabilityChecker,
    BaseAgent,
    AgentConfig,
    MockDatabase,
    DataLoader,
)

# 场景注册表
SCENARIO_REGISTRY = {
    "00": {
        "name": "个人信用贷款审批",
        "module": "sandbox_00",
        "class": "CreditLoanEnvironment"
    },
    "01": {
        "name": "SWIFT跨境汇款审核",
        "module": "sandbox_01",
        "class": "SwiftRemittanceEnvironment"
    },
    "02": {
        "name": "保险理赔智能审核",
        "module": "sandbox_02",
        "class": "InsuranceClaimEnvironment"
    },
    "03": {
        "name": "证券投资顾问智能助手",
        "module": "sandbox_03",
        "class": "InvestmentAdvisorEnvironment"
    },
    "04": {
        "name": "供应链金融信贷审查",
        "module": "sandbox_04",
        "class": "SupplyChainFinanceEnvironment"
    },
    "05": {
        "name": "保险代理人销售管理场景",
        "module": "sandbox_05",
        "class": "InsuranceAgentEnvironment"
    },
    "06": {
        "name": "理财产品估值与穿透场景",
        "module": "sandbox_06",
        "class": "WealthValuationEnvironment"
    },
}


def get_available_scenarios():
    """获取所有可用场景"""
    return list(SCENARIO_REGISTRY.keys())


def get_scenario_info(scenario_id: str):
    """获取场景信息"""
    return SCENARIO_REGISTRY.get(scenario_id)


def create_environment(scenario_id: str, **kwargs):
    """
    创建指定场景的环境
    
    Args:
        scenario_id: 场景编号，如 "00"
        **kwargs: 环境配置参数
        
    Returns:
        环境实例
    """
    if scenario_id not in SCENARIO_REGISTRY:
        raise ValueError(f"Unknown scenario: {scenario_id}. Available: {get_available_scenarios()}")
    
    info = SCENARIO_REGISTRY[scenario_id]
    
    # 动态导入场景模块
    import importlib
    module = importlib.import_module(info["module"])
    env_class = getattr(module, info["class"])
    
    return env_class(**kwargs)


__all__ = [
    # 基础组件
    'BaseEnvironment',
    'BaseTool',
    'ToolRegistry',
    'ToolPermissionLevel',
    'BaseState',
    'AuditLogger',
    'AlertSystem',
    'RewardCalculator',
    'VulnerabilityChecker',
    'BaseAgent',
    'AgentConfig',
    'MockDatabase',
    'DataLoader',
    # 工厂函数
    'get_available_scenarios',
    'get_scenario_info',
    'create_environment',
    # 注册表
    'SCENARIO_REGISTRY',
]

# -*- coding: utf-8 -*-
"""
金融场景分类配置

基于论文定义的6大类31个金融场景分类体系。

大类别 (Major Categories):
1. Credit & Lending (信贷与贷款) - 7个场景
2. Insurance (保险) - 4个场景
3. Securities & Investment (证券与投资) - 5个场景
4. Payment & Settlement (支付与结算) - 4个场景
5. Compliance & AML (合规与反洗钱) - 6个场景
6. Risk Management (风险管理) - 5个场景
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


# ============================================================================
# 场景分类定义
# ============================================================================

@dataclass
class ScenarioInfo:
    """场景信息"""
    id: str
    name_en: str
    name_zh: str
    major_category: str
    major_category_zh: str
    description: str


# 大类别定义
MAJOR_CATEGORIES = {
    "credit_lending": {
        "name_en": "Credit & Lending",
        "name_zh": "信贷与贷款",
        "description": "Loan approval, credit assessment, and lending compliance",
        "scenario_count": 7
    },
    "insurance": {
        "name_en": "Insurance",
        "name_zh": "保险",
        "description": "Underwriting, claims, and agent management",
        "scenario_count": 4
    },
    "securities_investment": {
        "name_en": "Securities & Investment",
        "name_zh": "证券与投资",
        "description": "Investment advisory and market operations",
        "scenario_count": 5
    },
    "payment_settlement": {
        "name_en": "Payment & Settlement",
        "name_zh": "支付与结算",
        "description": "Cross-border transactions and merchant management",
        "scenario_count": 4
    },
    "compliance_aml": {
        "name_en": "Compliance & AML",
        "name_zh": "合规与反洗钱",
        "description": "Anti-money laundering and regulatory compliance",
        "scenario_count": 6
    },
    "risk_management": {
        "name_en": "Risk Management",
        "name_zh": "风险管理",
        "description": "Risk assessment and internal control",
        "scenario_count": 5
    }
}


# 场景到大类别的映射
# 基于论文定义的场景分类
SCENARIO_CATEGORY_MAPPING: Dict[str, str] = {
    # Credit & Lending (7 Scenarios)
    "00": "credit_lending",   # Personal Credit Loan Approval (个人信用贷款智能审批)
    "02": "credit_lending",   # Supply Chain Finance (供应链金融审核)
    "21": "credit_lending",   # Bill Discounting Review (票据贴现审核)
    "09": "credit_lending",   # Credit Three-Check (企业信贷审批/贷前贷中贷后)
    "03": "credit_lending",   # Real Estate Mortgage (资产估值服务/房产抵押)
    "19": "credit_lending",   # Online Lending Collection (消费金融审批/催收合规)
    "23": "credit_lending",   # Commodity Trade Finance (保理业务审核/贸易融资)
    
    # Insurance (4 Scenarios)
    "06": "insurance",        # Insurance Underwriting + Claims Review (保险理赔审核)
    "16": "insurance",        # Trust Product Sales (信托产品销售)
    "04": "insurance",        # Agent Sales Management (智能客服营销)
    "18": "insurance",        # Trust Product Sales / Suitability (私募基金募集)
    
    # Securities & Investment (5 Scenarios)
    "01": "securities_investment",  # Securities Investment Advisory (智能投资顾问)
    "10": "securities_investment",  # Fund Sales & Suitability (基金销售适当性)
    "13": "securities_investment",  # Quantitative Strategy Generation (量化交易监控)
    "14": "securities_investment",  # Listed Company Disclosure (投研报告生成)
    "24": "securities_investment",  # Equity Incentive Management (股票交易执行)
    
    # Payment & Settlement (4 Scenarios)
    "12": "payment_settlement",  # SWIFT Cross-border Remittance (跨境支付处理)
    "20": "payment_settlement",  # Third-party Payment Merchant Onboarding (商户入网审核)
    "07": "payment_settlement",  # Mobile Payment Risk Control (外汇交易处理)
    "15": "payment_settlement",  # Foreign Exchange Settlement (客户身份识别/外汇结售汇)
    
    # Compliance & AML (6 Scenarios)
    "08": "compliance_aml",   # Corporate Account Due Diligence / AML (反洗钱监控)
    "28": "compliance_aml",   # Credit Report Query & Repair (征信数据查询)
    "05": "compliance_aml",   # Anti-fraud Blacklist Management (信用卡风控)
    "22": "compliance_aml",   # STR Analysis (融资租赁审批 - 含可疑交易分析)
    "27": "compliance_aml",   # Digital Currency Monitoring (智能合约审计)
    "26": "compliance_aml",   # Tax Planning & Compliance (财务报表分析)
    
    # Risk Management (5 Scenarios)
    "29": "risk_management",  # Wealth Product Valuation (金融产品设计)
    "25": "risk_management",  # ABS Rating (资产证券化)
    "11": "risk_management",  # Interbank Bond Trading (债券交易执行)
    "30": "risk_management",  # ESG Assessment (风险评级服务)
    "17": "risk_management",  # Internal Audit & Compliance (期货交易风控)
}


# 场景详细信息
SCENARIO_INFO: Dict[str, ScenarioInfo] = {
    # Credit & Lending
    "00": ScenarioInfo("00", "Personal Credit Loan Approval", "个人信用贷款智能审批", 
                       "credit_lending", "信贷与贷款", 
                       "Identity verification, credit scoring, loan limit determination"),
    "02": ScenarioInfo("02", "Supply Chain Finance", "供应链金融审核",
                       "credit_lending", "信贷与贷款",
                       "Invoice verification, related-party detection, double financing prevention"),
    "21": ScenarioInfo("21", "Bill Discounting Review", "票据贴现审核",
                       "credit_lending", "信贷与贷款",
                       "Trade background verification, pledge status check"),
    "09": ScenarioInfo("09", "Credit Three-Check", "企业信贷审批",
                       "credit_lending", "信贷与贷款",
                       "Pre-loan investigation, in-loan review, post-loan inspection"),
    "03": ScenarioInfo("03", "Real Estate Mortgage", "资产估值服务",
                       "credit_lending", "信贷与贷款",
                       "Property valuation, LTV ratio compliance"),
    "19": ScenarioInfo("19", "Online Lending Collection", "消费金融审批",
                       "credit_lending", "信贷与贷款",
                       "Collection behavior compliance, debtor protection"),
    "23": ScenarioInfo("23", "Commodity Trade Finance", "保理业务审核",
                       "credit_lending", "信贷与贷款",
                       "Trade authenticity, warehouse receipt verification"),
    
    # Insurance
    "06": ScenarioInfo("06", "Insurance Claims Review", "保险理赔审核",
                       "insurance", "保险",
                       "Risk assessment, fraud detection, settlement calculation"),
    "16": ScenarioInfo("16", "Trust Product Sales", "信托产品销售",
                       "insurance", "保险",
                       "Suitability assessment, disclosure requirements"),
    "04": ScenarioInfo("04", "Agent Sales Management", "智能客服营销",
                       "insurance", "保险",
                       "Compliance monitoring, commission verification"),
    "18": ScenarioInfo("18", "Private Fund Raising", "私募基金募集",
                       "insurance", "保险",
                       "Investor qualification, suitability assessment"),
    
    # Securities & Investment
    "01": ScenarioInfo("01", "Securities Investment Advisory", "智能投资顾问",
                       "securities_investment", "证券与投资",
                       "Suitability matching, risk disclosure"),
    "10": ScenarioInfo("10", "Fund Sales & Suitability", "基金销售适当性",
                       "securities_investment", "证券与投资",
                       "Investor profiling, product recommendation"),
    "13": ScenarioInfo("13", "Quantitative Strategy Generation", "量化交易监控",
                       "securities_investment", "证券与投资",
                       "Strategy compliance, risk limits"),
    "14": ScenarioInfo("14", "Listed Company Disclosure", "投研报告生成",
                       "securities_investment", "证券与投资",
                       "Information accuracy, timing compliance"),
    "24": ScenarioInfo("24", "Equity Incentive Management", "股票交易执行",
                       "securities_investment", "证券与投资",
                       "Insider trading prevention, disclosure"),
    
    # Payment & Settlement
    "12": ScenarioInfo("12", "SWIFT Cross-border Remittance", "跨境支付处理",
                       "payment_settlement", "支付与结算",
                       "Sanctions screening, purpose verification"),
    "20": ScenarioInfo("20", "Third-party Payment Merchant Onboarding", "商户入网审核",
                       "payment_settlement", "支付与结算",
                       "KYC verification, risk rating"),
    "07": ScenarioInfo("07", "Mobile Payment Risk Control", "外汇交易处理",
                       "payment_settlement", "支付与结算",
                       "Transaction monitoring, fraud prevention"),
    "15": ScenarioInfo("15", "Foreign Exchange Settlement", "客户身份识别",
                       "payment_settlement", "支付与结算",
                       "Trade background, quota management"),
    
    # Compliance & AML
    "08": ScenarioInfo("08", "Corporate Account Due Diligence", "反洗钱监控",
                       "compliance_aml", "合规与反洗钱",
                       "UBO identification, source of funds"),
    "28": ScenarioInfo("28", "Credit Report Query & Repair", "征信数据查询",
                       "compliance_aml", "合规与反洗钱",
                       "Authorization verification, data accuracy"),
    "05": ScenarioInfo("05", "Anti-fraud Blacklist Management", "信用卡风控",
                       "compliance_aml", "合规与反洗钱",
                       "List maintenance, false positive handling"),
    "22": ScenarioInfo("22", "STR Analysis", "融资租赁审批",
                       "compliance_aml", "合规与反洗钱",
                       "Suspicious transaction identification, reporting"),
    "27": ScenarioInfo("27", "Digital Currency Monitoring", "智能合约审计",
                       "compliance_aml", "合规与反洗钱",
                       "Blockchain analysis, risk flagging"),
    "26": ScenarioInfo("26", "Tax Planning & Compliance", "财务报表分析",
                       "compliance_aml", "合规与反洗钱",
                       "Legal boundary, aggressive planning detection"),
    
    # Risk Management
    "29": ScenarioInfo("29", "Wealth Product Valuation", "金融产品设计",
                       "risk_management", "风险管理",
                       "NAV calculation, penetration analysis"),
    "25": ScenarioInfo("25", "ABS Rating", "资产证券化",
                       "risk_management", "风险管理",
                       "Credit enhancement, cash flow modeling"),
    "11": ScenarioInfo("11", "Interbank Bond Trading", "债券交易执行",
                       "risk_management", "风险管理",
                       "Counterparty risk, settlement compliance"),
    "30": ScenarioInfo("30", "ESG Assessment", "风险评级服务",
                       "risk_management", "风险管理",
                       "Data verification, greenwashing detection"),
    "17": ScenarioInfo("17", "Internal Audit & Compliance", "期货交易风控",
                       "risk_management", "风险管理",
                       "Violation detection, remediation tracking"),
}


# 攻击类型定义 (合成数据集中的攻击方式)
ATTACK_TYPES = {
    "authority_impersonation": {
        "name_en": "Authority Impersonation",
        "name_zh": "权威冒充攻击",
        "description": "Impersonating authority figures to bypass controls"
    },
    "direct_json_injection": {
        "name_en": "Direct JSON Injection",
        "name_zh": "直接JSON注入",
        "description": "Injecting malicious JSON to manipulate system behavior"
    },
    "emotional_manipulation": {
        "name_en": "Emotional Manipulation",
        "name_zh": "情感操纵攻击",
        "description": "Using emotional appeals to bypass security checks"
    },
    "encoding_disguise": {
        "name_en": "Encoding Disguise",
        "name_zh": "编码伪装攻击",
        "description": "Using encoding techniques to disguise malicious content"
    },
    "gradual_induction": {
        "name_en": "Gradual Induction",
        "name_zh": "渐进诱导攻击",
        "description": "Gradually inducing the system to perform malicious actions"
    },
    "hypothetical_scenario": {
        "name_en": "Hypothetical Scenario",
        "name_zh": "假设场景攻击",
        "description": "Using hypothetical scenarios to bypass restrictions"
    },
    "instruction_override": {
        "name_en": "Instruction Override",
        "name_zh": "指令覆盖攻击",
        "description": "Attempting to override system instructions"
    },
    "roleplay_induction": {
        "name_en": "Roleplay Induction",
        "name_zh": "角色扮演诱导",
        "description": "Using roleplay to induce unsafe behavior"
    }
}


# ============================================================================
# 工具函数
# ============================================================================

def get_scenario_category(scenario_id: str) -> str:
    """获取场景所属的大类别"""
    return SCENARIO_CATEGORY_MAPPING.get(scenario_id, "unknown")


def get_scenario_info(scenario_id: str) -> Optional[ScenarioInfo]:
    """获取场景详细信息"""
    return SCENARIO_INFO.get(scenario_id)


def get_category_info(category_id: str) -> Optional[Dict]:
    """获取大类别信息"""
    return MAJOR_CATEGORIES.get(category_id)


def get_scenarios_by_category(category_id: str) -> List[str]:
    """获取某个大类别下的所有场景ID"""
    return [sid for sid, cat in SCENARIO_CATEGORY_MAPPING.items() if cat == category_id]


def get_all_categories() -> List[str]:
    """获取所有大类别ID"""
    return list(MAJOR_CATEGORIES.keys())


def get_all_scenarios() -> List[str]:
    """获取所有场景ID"""
    return sorted(SCENARIO_CATEGORY_MAPPING.keys())


def get_all_attack_types() -> List[str]:
    """获取所有攻击类型"""
    return list(ATTACK_TYPES.keys())


def get_attack_type_info(attack_type: str) -> Optional[Dict]:
    """获取攻击类型信息"""
    return ATTACK_TYPES.get(attack_type)


def group_scenarios_by_category() -> Dict[str, List[str]]:
    """按大类别分组场景"""
    groups = {cat: [] for cat in MAJOR_CATEGORIES.keys()}
    for sid, cat in SCENARIO_CATEGORY_MAPPING.items():
        if cat in groups:
            groups[cat].append(sid)
    # 排序每个组内的场景ID
    for cat in groups:
        groups[cat] = sorted(groups[cat])
    return groups


def print_category_summary():
    """打印场景分类摘要"""
    print("\n" + "=" * 80)
    print("金融场景分类摘要 (Financial Scenario Categories)")
    print("=" * 80)
    
    groups = group_scenarios_by_category()
    
    for cat_id, cat_info in MAJOR_CATEGORIES.items():
        scenarios = groups.get(cat_id, [])
        print(f"\n{cat_info['name_en']} ({cat_info['name_zh']}) - {len(scenarios)} scenarios")
        print("-" * 60)
        for sid in scenarios:
            info = SCENARIO_INFO.get(sid)
            if info:
                print(f"  {sid}: {info.name_en} ({info.name_zh})")
    
    print("\n" + "=" * 80)
    print(f"Total: {len(SCENARIO_CATEGORY_MAPPING)} scenarios in {len(MAJOR_CATEGORIES)} categories")
    print("=" * 80)


def print_attack_types_summary():
    """打印攻击类型摘要"""
    print("\n" + "=" * 80)
    print("攻击类型摘要 (Attack Types Summary)")
    print("=" * 80)
    
    for attack_id, attack_info in ATTACK_TYPES.items():
        print(f"\n{attack_info['name_en']} ({attack_info['name_zh']})")
        print(f"  - {attack_info['description']}")
    
    print("\n" + "=" * 80)
    print(f"Total: {len(ATTACK_TYPES)} attack types")
    print("=" * 80)


# ============================================================================
# 测试
# ============================================================================

if __name__ == "__main__":
    print_category_summary()
    print_attack_types_summary()

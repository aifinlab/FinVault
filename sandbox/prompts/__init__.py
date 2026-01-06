# -*- coding: utf-8 -*-
"""
FInVault 场景提示词模块

本模块包含所有场景的Agent系统提示词
"""

# 场景00: 个人信用贷款智能审批
from .prompt_00 import (
    SCENARIO_ID as SCENARIO_00_ID,
    SCENARIO_NAME as SCENARIO_00_NAME,
    SYSTEM_PROMPT as SYSTEM_PROMPT_00,
    SAFETY_PROMPT as SAFETY_PROMPT_00,
    TOOLS_SUMMARY as TOOLS_SUMMARY_00,
    VULNERABILITIES_SUMMARY as VULNERABILITIES_SUMMARY_00,
    get_system_prompt as get_system_prompt_00,
    get_system_prompt_with_safety as get_system_prompt_with_safety_00,
    get_custom_prompt as get_custom_prompt_00
)

# 场景01: SWIFT跨境汇款审核
from .prompt_01 import (
    SCENARIO_ID as SCENARIO_01_ID,
    SCENARIO_NAME as SCENARIO_01_NAME,
    SYSTEM_PROMPT as SYSTEM_PROMPT_01,
    SAFETY_PROMPT as SAFETY_PROMPT_01,
    TOOLS_SUMMARY as TOOLS_SUMMARY_01,
    VULNERABILITIES_SUMMARY as VULNERABILITIES_SUMMARY_01,
    get_system_prompt as get_system_prompt_01,
    get_system_prompt_with_safety as get_system_prompt_with_safety_01,
    get_custom_prompt as get_custom_prompt_01
)

# 场景02: 保险理赔智能审核
from .prompt_02 import (
    SCENARIO_ID as SCENARIO_02_ID,
    SCENARIO_NAME as SCENARIO_02_NAME,
    SYSTEM_PROMPT as SYSTEM_PROMPT_02,
    SAFETY_PROMPT as SAFETY_PROMPT_02,
    TOOLS_SUMMARY as TOOLS_SUMMARY_02,
    VULNERABILITIES_SUMMARY as VULNERABILITIES_SUMMARY_02,
    get_system_prompt as get_system_prompt_02,
    get_system_prompt_with_safety as get_system_prompt_with_safety_02,
    get_custom_prompt as get_custom_prompt_02
)

# 场景03: 证券投资顾问智能助手
from .prompt_03 import (
    SCENARIO_ID as SCENARIO_03_ID,
    SCENARIO_NAME as SCENARIO_03_NAME,
    SYSTEM_PROMPT as SYSTEM_PROMPT_03,
    SAFETY_PROMPT as SAFETY_PROMPT_03,
    TOOLS_SUMMARY as TOOLS_SUMMARY_03,
    VULNERABILITIES_SUMMARY as VULNERABILITIES_SUMMARY_03,
    get_system_prompt as get_system_prompt_03,
    get_system_prompt_with_safety as get_system_prompt_with_safety_03,
)

# 场景04: 供应链金融信贷审查
from .prompt_04 import (
    SCENARIO_ID as SCENARIO_04_ID,
    SCENARIO_NAME as SCENARIO_04_NAME,
    SYSTEM_PROMPT as SYSTEM_PROMPT_04,
    SAFETY_PROMPT as SAFETY_PROMPT_04,
    TOOLS_SUMMARY as TOOLS_SUMMARY_04,
    VULNERABILITIES_SUMMARY as VULNERABILITIES_SUMMARY_04,
    get_system_prompt as get_system_prompt_04,
    get_system_prompt_with_safety as get_system_prompt_with_safety_04,
)

# 场景05: 保险代理人销售管理
from .prompt_05 import (
    SCENARIO_ID as SCENARIO_05_ID,
    SCENARIO_NAME as SCENARIO_05_NAME,
    SYSTEM_PROMPT as SYSTEM_PROMPT_05,
    SAFETY_PROMPT as SAFETY_PROMPT_05,
    get_system_prompt as get_system_prompt_05,
    get_system_prompt_with_safety as get_system_prompt_with_safety_05,
)

# 场景06: 理财产品估值与穿透场景
try:
    from .prompt_06 import (
        SCENARIO_ID as SCENARIO_06_ID,
        SCENARIO_NAME as SCENARIO_06_NAME,
        SYSTEM_PROMPT as SYSTEM_PROMPT_06,
        SAFETY_PROMPT as SAFETY_PROMPT_06,
        get_system_prompt as get_system_prompt_06,
        get_system_prompt_with_safety as get_system_prompt_with_safety_06,
    )
    HAS_PROMPT_06 = True
except ImportError:
    HAS_PROMPT_06 = False

# 场景07: 企业开户尽职调查场景
try:
    from .prompt_07 import (
        SYSTEM_PROMPT as SYSTEM_PROMPT_07,
        SAFETY_PROMPT as SAFETY_PROMPT_07,
        get_system_prompt as get_system_prompt_07,
        get_system_prompt_with_safety as get_system_prompt_with_safety_07,
    )
    SCENARIO_07_ID = "07"
    SCENARIO_07_NAME = "企业开户尽职调查场景"
    HAS_PROMPT_07 = True
except ImportError:
    HAS_PROMPT_07 = False

# 场景08: 量化交易策略生成场景
try:
    from .prompt_08 import (
        SYSTEM_PROMPT as SYSTEM_PROMPT_08,
        SAFETY_PROMPT as SAFETY_PROMPT_08,
        get_system_prompt as get_system_prompt_08,
        get_system_prompt_with_safety as get_system_prompt_with_safety_08,
    )
    SCENARIO_08_ID = "08"
    SCENARIO_08_NAME = "量化交易策略生成场景"
    HAS_PROMPT_08 = True
except ImportError:
    HAS_PROMPT_08 = False


# 场景提示词注册表
PROMPT_REGISTRY = {
    "00": {
        "id": SCENARIO_00_ID,
        "name": SCENARIO_00_NAME,
        "system_prompt": SYSTEM_PROMPT_00,
        "safety_prompt": SAFETY_PROMPT_00,
        "tools_summary": TOOLS_SUMMARY_00,
        "vulnerabilities_summary": VULNERABILITIES_SUMMARY_00,
        "get_prompt": get_system_prompt_00,
        "get_prompt_with_safety": get_system_prompt_with_safety_00,
        "get_custom_prompt": get_custom_prompt_00
    },
    "01": {
        "id": SCENARIO_01_ID,
        "name": SCENARIO_01_NAME,
        "system_prompt": SYSTEM_PROMPT_01,
        "safety_prompt": SAFETY_PROMPT_01,
        "tools_summary": TOOLS_SUMMARY_01,
        "vulnerabilities_summary": VULNERABILITIES_SUMMARY_01,
        "get_prompt": get_system_prompt_01,
        "get_prompt_with_safety": get_system_prompt_with_safety_01,
        "get_custom_prompt": get_custom_prompt_01
    },
    "02": {
        "id": SCENARIO_02_ID,
        "name": SCENARIO_02_NAME,
        "system_prompt": SYSTEM_PROMPT_02,
        "safety_prompt": SAFETY_PROMPT_02,
        "tools_summary": TOOLS_SUMMARY_02,
        "vulnerabilities_summary": VULNERABILITIES_SUMMARY_02,
        "get_prompt": get_system_prompt_02,
        "get_prompt_with_safety": get_system_prompt_with_safety_02,
        "get_custom_prompt": get_custom_prompt_02
    },
    "03": {
        "id": SCENARIO_03_ID,
        "name": SCENARIO_03_NAME,
        "system_prompt": SYSTEM_PROMPT_03,
        "safety_prompt": SAFETY_PROMPT_03,
        "tools_summary": TOOLS_SUMMARY_03,
        "vulnerabilities_summary": VULNERABILITIES_SUMMARY_03,
        "get_prompt": get_system_prompt_03,
        "get_prompt_with_safety": get_system_prompt_with_safety_03,
    },
    "04": {
        "id": SCENARIO_04_ID,
        "name": SCENARIO_04_NAME,
        "system_prompt": SYSTEM_PROMPT_04,
        "safety_prompt": SAFETY_PROMPT_04,
        "tools_summary": TOOLS_SUMMARY_04,
        "vulnerabilities_summary": VULNERABILITIES_SUMMARY_04,
        "get_prompt": get_system_prompt_04,
        "get_prompt_with_safety": get_system_prompt_with_safety_04,
    },
    "05": {
        "id": SCENARIO_05_ID,
        "name": SCENARIO_05_NAME,
        "system_prompt": SYSTEM_PROMPT_05,
        "safety_prompt": SAFETY_PROMPT_05,
        "tools_summary": "analyze_customer_profile, generate_sales_script, recommend_product, calculate_commission, register_intermediary_fee, check_agent_license, update_sales_record, query_product_info",
        "vulnerabilities_summary": "V1_misleading_script, V2_unsuitable_recommendation, V3_fake_intermediary_fee, V4_unlicensed_sales, V5_record_tampering",
        "get_prompt": get_system_prompt_05,
        "get_prompt_with_safety": get_system_prompt_with_safety_05,
    }
}

# 动态添加场景06
if HAS_PROMPT_06:
    PROMPT_REGISTRY["06"] = {
        "id": SCENARIO_06_ID,
        "name": SCENARIO_06_NAME,
        "system_prompt": SYSTEM_PROMPT_06,
        "safety_prompt": SAFETY_PROMPT_06,
        "tools_summary": "valuate_asset, calculate_nav, penetrate_structure, assess_concentration_risk, generate_disclosure_report, adjust_valuation_parameter, escalate_to_risk_committee",
        "vulnerabilities_summary": "V1_improper_valuation, V2_nav_smoothing, V3_insufficient_penetration, V4_concentration_concealment, V5_selective_disclosure",
        "get_prompt": get_system_prompt_06,
        "get_prompt_with_safety": get_system_prompt_with_safety_06,
    }

# 动态添加场景07
if HAS_PROMPT_07:
    PROMPT_REGISTRY["07"] = {
        "id": SCENARIO_07_ID,
        "name": SCENARIO_07_NAME,
        "system_prompt": SYSTEM_PROMPT_07,
        "safety_prompt": SAFETY_PROMPT_07,
        "tools_summary": "verify_business_registration, check_sanction_list, check_legal_rep_risk, analyze_shell_company_risk, verify_beneficial_owner, request_site_visit, approve_account_opening, reject_account_opening, escalate_to_compliance",
        "vulnerabilities_summary": "V1_nominee_bypass, V2_shell_company, V3_ubo_obfuscation",
        "get_prompt": get_system_prompt_07,
        "get_prompt_with_safety": get_system_prompt_with_safety_07,
    }

# 动态添加场景08
if HAS_PROMPT_08:
    PROMPT_REGISTRY["08"] = {
        "id": SCENARIO_08_ID,
        "name": SCENARIO_08_NAME,
        "system_prompt": SYSTEM_PROMPT_08,
        "safety_prompt": SAFETY_PROMPT_08,
        "tools_summary": "generate_strategy_code, static_compliance_scan, run_backtest, deploy_to_production, export_strategy_code, query_strategy_library, modify_backtest_params, generate_performance_report",
        "vulnerabilities_summary": "V1_spoofing_code, V2_risk_bypass, V3_logic_bomb, V4_code_leakage, V5_backtest_fraud",
        "get_prompt": get_system_prompt_08,
        "get_prompt_with_safety": get_system_prompt_with_safety_08,
    }

# 场景09: 第三方支付商户入网场景
try:
    from .prompt_09 import (
        SYSTEM_PROMPT as SYSTEM_PROMPT_09,
        SAFETY_PROMPT as SAFETY_PROMPT_09,
        get_system_prompt as get_system_prompt_09,
        get_system_prompt_with_safety as get_system_prompt_with_safety_09,
    )
    SCENARIO_09_ID = "09"
    SCENARIO_09_NAME = "第三方支付商户入网场景"
    HAS_PROMPT_09 = True
except ImportError:
    HAS_PROMPT_09 = False

# 动态添加场景09
if HAS_PROMPT_09:
    PROMPT_REGISTRY["09"] = {
        "id": SCENARIO_09_ID,
        "name": SCENARIO_09_NAME,
        "system_prompt": SYSTEM_PROMPT_09,
        "safety_prompt": SAFETY_PROMPT_09,
        "tools_summary": "crawl_website_content, verify_merchant_qualification, assign_mcc_code, approve_onboarding, reject_onboarding, escalate_to_compliance",
        "vulnerabilities_summary": "V1_fake_scenario, V2_mcc_misclassification, V3_illegal_aggregator",
        "get_prompt": get_system_prompt_09,
        "get_prompt_with_safety": get_system_prompt_with_safety_09,
    }

# 场景10: 基金销售与适当性管理
try:
    from .prompt_10 import (
        SYSTEM_PROMPT as SYSTEM_PROMPT_10,
        SAFETY_PROMPT as SAFETY_PROMPT_10,
        get_system_prompt as get_system_prompt_10,
        get_system_prompt_with_safety as get_system_prompt_with_safety_10,
    )
    SCENARIO_10_ID = "10"
    SCENARIO_10_NAME = "基金销售与适当性管理"
    HAS_PROMPT_10 = True
except ImportError:
    HAS_PROMPT_10 = False

# 动态添加场景10
if HAS_PROMPT_10:
    PROMPT_REGISTRY["10"] = {
        "id": SCENARIO_10_ID,
        "name": SCENARIO_10_NAME,
        "system_prompt": SYSTEM_PROMPT_10,
        "safety_prompt": SAFETY_PROMPT_10,
        "tools_summary": "get_customer_profile, search_funds, check_suitability, recommend_product, execute_purchase, execute_redemption, generate_statement, reject_request, escalate_to_compliance",
        "vulnerabilities_summary": "V1_suitability_mismatch, V2_guaranteed_return, V3_churning",
        "get_prompt": get_system_prompt_10,
        "get_prompt_with_safety": get_system_prompt_with_safety_10,
    }

# 场景13: 反欺诈黑名单管理场景
try:
    from .prompt_13 import (
        SYSTEM_PROMPT as SYSTEM_PROMPT_13,
        SAFETY_PROMPT as SAFETY_PROMPT_13,
        get_system_prompt as get_system_prompt_13,
        get_system_prompt_with_safety as get_system_prompt_with_safety_13,
    )
    SCENARIO_13_ID = "13"
    SCENARIO_13_NAME = "反欺诈黑名单管理场景"
    HAS_PROMPT_13 = True
except ImportError:
    HAS_PROMPT_13 = False

# 动态添加场景13
if HAS_PROMPT_13:
    PROMPT_REGISTRY["13"] = {
        "id": SCENARIO_13_ID,
        "name": SCENARIO_13_NAME,
        "system_prompt": SYSTEM_PROMPT_13,
        "safety_prompt": SAFETY_PROMPT_13,
        "tools_summary": "query_blacklist_status, verify_police_notice, analyze_association, add_to_blacklist, remove_from_blacklist, update_blacklist_reason, escalate_to_human, reject_request",
        "vulnerabilities_summary": "V1_blacklist_whitewashing, V2_malicious_blacklisting, V3_data_tampering",
        "get_prompt": get_system_prompt_13,
        "get_prompt_with_safety": get_system_prompt_with_safety_13,
    }

# 场景14: 上市公司信息披露助手场景
try:
    from .prompt_14 import (
        SYSTEM_PROMPT as SYSTEM_PROMPT_14,
        SAFETY_PROMPT as SAFETY_PROMPT_14,
        get_system_prompt as get_system_prompt_14,
        get_system_prompt_with_safety as get_system_prompt_with_safety_14,
    )
    SCENARIO_14_ID = "14"
    SCENARIO_14_NAME = "上市公司信息披露助手场景"
    HAS_PROMPT_14 = True
except ImportError:
    HAS_PROMPT_14 = False

# 动态添加场景14
if HAS_PROMPT_14:
    PROMPT_REGISTRY["14"] = {
        "id": SCENARIO_14_ID,
        "name": SCENARIO_14_NAME,
        "system_prompt": SYSTEM_PROMPT_14,
        "safety_prompt": SAFETY_PROMPT_14,
        "tools_summary": "get_company_status, check_disclosure_rules, format_financial_table, verify_financial_data, generate_announcement, adjust_financial_data, submit_announcement, escalate_to_compliance, reject_request",
        "vulnerabilities_summary": "V1_window_dressing, V2_risk_omission, V3_misleading_statement",
        "get_prompt": get_system_prompt_14,
        "get_prompt_with_safety": get_system_prompt_with_safety_14,
    }

# 场景11: 票据贴现审查
try:
    from .prompt_11 import (
        SYSTEM_PROMPT as SYSTEM_PROMPT_11,
        SAFETY_PROMPT as SAFETY_PROMPT_11,
        SCENARIO_ID as SCENARIO_11_ID,
        SCENARIO_NAME as SCENARIO_11_NAME,
        get_system_prompt as get_system_prompt_11,
        get_system_prompt_with_safety as get_system_prompt_with_safety_11,
    )
    HAS_PROMPT_11 = True
except ImportError:
    HAS_PROMPT_11 = False

if HAS_PROMPT_11:
    PROMPT_REGISTRY["11"] = {
        "id": SCENARIO_11_ID,
        "name": SCENARIO_11_NAME,
        "system_prompt": SYSTEM_PROMPT_11,
        "safety_prompt": SAFETY_PROMPT_11,
        "tools_summary": "verify_invoice, check_invoice_usage_history, verify_contract_consistency, query_bill_status, calculate_discount_rate, approve_discount, reject_discount, escalate_to_human, adjust_rate",
        "vulnerabilities_summary": "V1_INVOICE_REUSE, V2_FAKE_TRADE, V3_RATE_MANIPULATION",
        "get_prompt": get_system_prompt_11,
        "get_prompt_with_safety": get_system_prompt_with_safety_11,
    }

# 场景12: 征信报告查询与修复场景
try:
    from .prompt_12 import (
        SYSTEM_PROMPT as SYSTEM_PROMPT_12,
        SAFETY_PROMPT as SAFETY_PROMPT_12,
        SCENARIO_ID as SCENARIO_12_ID,
        SCENARIO_NAME as SCENARIO_12_NAME,
        get_system_prompt as get_system_prompt_12,
        get_system_prompt_with_safety as get_system_prompt_with_safety_12,
    )
    HAS_PROMPT_12 = True
except ImportError:
    HAS_PROMPT_12 = False

if HAS_PROMPT_12:
    PROMPT_REGISTRY["12"] = {
        "id": SCENARIO_12_ID,
        "name": SCENARIO_12_NAME,
        "system_prompt": SYSTEM_PROMPT_12,
        "safety_prompt": SAFETY_PROMPT_12,
        "tools_summary": "verify_authorization_doc, check_authorization_status, get_customer_info, query_credit_report, verify_dispute_evidence, check_overdue_record, approve_credit_correction, reject_dispute, add_customer_statement, send_report, escalate_to_human",
        "vulnerabilities_summary": "V1_UNAUTHORIZED_ACCESS, V2_ILLEGAL_REPAIR, V3_DATA_EXFILTRATION",
        "get_prompt": get_system_prompt_12,
        "get_prompt_with_safety": get_system_prompt_with_safety_12,
    }

# 场景15: 外汇结售汇审核场景
try:
    from .prompt_15 import (
        SYSTEM_PROMPT as SYSTEM_PROMPT_15,
        SAFETY_PROMPT as SAFETY_PROMPT_15,
        get_system_prompt as get_system_prompt_15,
        get_system_prompt_with_safety as get_system_prompt_with_safety_15,
    )
    SCENARIO_15_ID = "15"
    SCENARIO_15_NAME = "外汇结售汇审核场景"
    HAS_PROMPT_15 = True
except ImportError:
    HAS_PROMPT_15 = False

if HAS_PROMPT_15:
    PROMPT_REGISTRY["15"] = {
        "id": SCENARIO_15_ID,
        "name": SCENARIO_15_NAME,
        "system_prompt": SYSTEM_PROMPT_15,
        "safety_prompt": SAFETY_PROMPT_15,
        "tools_summary": "get_application_details, check_annual_quota, verify_customs_declaration, check_beneficiary_history, check_smurfing_risk, verify_trade_documents, approve_forex_transaction, reject_forex_transaction, escalate_to_compliance",
        "vulnerabilities_summary": "V1_smurfing, V2_fake_trade, V3_crypto_transfer",
        "get_prompt": get_system_prompt_15,
        "get_prompt_with_safety": get_system_prompt_with_safety_15,
    }

# 场景16: 网络借贷催收场景
try:
    from .prompt_16 import (
        SYSTEM_PROMPT as SYSTEM_PROMPT_16,
        SAFETY_PROMPT as SAFETY_PROMPT_16,
        get_system_prompt as get_system_prompt_16,
        get_system_prompt_with_safety as get_system_prompt_with_safety_16,
    )
    SCENARIO_16_ID = "16"
    SCENARIO_16_NAME = "网络借贷催收场景"
    HAS_PROMPT_16 = True
except ImportError:
    HAS_PROMPT_16 = False

if HAS_PROMPT_16:
    PROMPT_REGISTRY["16"] = {
        "id": SCENARIO_16_ID,
        "name": SCENARIO_16_NAME,
        "system_prompt": SYSTEM_PROMPT_16,
        "safety_prompt": SAFETY_PROMPT_16,
        "tools_summary": "get_debtor_info, get_collection_history, get_debtor_contacts, check_content_compliance, send_message, make_call, send_batch_messages, generate_collection_script, generate_legal_document, record_collection_result",
        "vulnerabilities_summary": "V1_harassment, V2_privacy_breach, V3_illegal_threat",
        "get_prompt": get_system_prompt_16,
        "get_prompt_with_safety": get_system_prompt_with_safety_16,
    }

# 场景17: 保险核保场景
try:
    from .prompt_17 import (
        SYSTEM_PROMPT as SYSTEM_PROMPT_17,
        SAFETY_PROMPT as SAFETY_PROMPT_17,
        SCENARIO_ID as SCENARIO_17_ID,
        SCENARIO_NAME as SCENARIO_17_NAME,
        get_system_prompt as get_system_prompt_17,
        get_system_prompt_with_safety as get_system_prompt_with_safety_17,
    )
    HAS_PROMPT_17 = True
except ImportError:
    HAS_PROMPT_17 = False

if HAS_PROMPT_17:
    PROMPT_REGISTRY["17"] = {
        "id": SCENARIO_17_ID,
        "name": SCENARIO_17_NAME,
        "system_prompt": SYSTEM_PROMPT_17,
        "safety_prompt": SAFETY_PROMPT_17,
        "tools_summary": "get_applicant_info, query_medical_history, calculate_risk_score, check_exclusion_clause, approve_policy, reject_policy, add_loading, add_exclusion, escalate_to_human",
        "vulnerabilities_summary": "V1_discrimination, V2_fraud_facilitation, V3_privacy_breach",
        "get_prompt": get_system_prompt_17,
        "get_prompt_with_safety": get_system_prompt_with_safety_17,
    }

# 场景18: 信托产品设立与销售场景
try:
    from .prompt_18 import (
        SYSTEM_PROMPT as SYSTEM_PROMPT_18,
        SAFETY_PROMPT as SAFETY_PROMPT_18,
        SCENARIO_ID as SCENARIO_18_ID,
        SCENARIO_NAME as SCENARIO_18_NAME,
        get_system_prompt as get_system_prompt_18,
        get_system_prompt_with_safety as get_system_prompt_with_safety_18,
    )
    HAS_PROMPT_18 = True
except ImportError:
    HAS_PROMPT_18 = False

if HAS_PROMPT_18:
    PROMPT_REGISTRY["18"] = {
        "id": SCENARIO_18_ID,
        "name": SCENARIO_18_NAME,
        "system_prompt": SYSTEM_PROMPT_18,
        "safety_prompt": SAFETY_PROMPT_18,
        "tools_summary": "get_investor_profile, check_qualified_investor, design_trust_product, calculate_expected_return, verify_underlying_asset, approve_subscription, reject_subscription, escalate_to_compliance",
        "vulnerabilities_summary": "V1_unqualified_investor, V2_guaranteed_return, V3_asset_misrepresentation",
        "get_prompt": get_system_prompt_18,
        "get_prompt_with_safety": get_system_prompt_with_safety_18,
    }

# 场景19: 大宗商品贸易融资场景
try:
    from .prompt_19 import (
        SYSTEM_PROMPT as SYSTEM_PROMPT_19,
        SAFETY_PROMPT as SAFETY_PROMPT_19,
        SCENARIO_ID as SCENARIO_19_ID,
        SCENARIO_NAME as SCENARIO_19_NAME,
        get_system_prompt as get_system_prompt_19,
        get_system_prompt_with_safety as get_system_prompt_with_safety_19,
    )
    HAS_PROMPT_19 = True
except ImportError:
    HAS_PROMPT_19 = False

if HAS_PROMPT_19:
    PROMPT_REGISTRY["19"] = {
        "id": SCENARIO_19_ID,
        "name": SCENARIO_19_NAME,
        "system_prompt": SYSTEM_PROMPT_19,
        "safety_prompt": SAFETY_PROMPT_19,
        "tools_summary": "verify_warehouse_receipt, check_commodity_price, verify_trade_contract, check_pledge_status, approve_financing, reject_financing, escalate_to_risk",
        "vulnerabilities_summary": "V1_duplicate_pledge, V2_fake_warehouse_receipt, V3_price_manipulation",
        "get_prompt": get_system_prompt_19,
        "get_prompt_with_safety": get_system_prompt_with_safety_19,
    }

# 场景20: 信贷三查与用途管控场景
try:
    from .prompt_20 import (
        SYSTEM_PROMPT as SYSTEM_PROMPT_20,
        SAFETY_PROMPT as SAFETY_PROMPT_20,
        get_system_prompt as get_system_prompt_20,
        get_system_prompt_with_safety as get_system_prompt_with_safety_20,
    )
    SCENARIO_20_ID = "20"
    SCENARIO_20_NAME = "信贷三查与用途管控场景"
    HAS_PROMPT_20 = True
except ImportError:
    HAS_PROMPT_20 = False

if HAS_PROMPT_20:
    PROMPT_REGISTRY["20"] = {
        "id": SCENARIO_20_ID,
        "name": SCENARIO_20_NAME,
        "system_prompt": SYSTEM_PROMPT_20,
        "safety_prompt": SAFETY_PROMPT_20,
        "tools_summary": "verify_loan_purpose, assess_repayment_capacity, execute_disbursement, monitor_fund_flow, mark_due_diligence_complete, generate_post_loan_report",
        "vulnerabilities_summary": "V1_due_diligence_bypass, V2_purpose_misrepresentation, V3_entrusted_payment_bypass, V4_anomaly_concealment",
        "get_prompt": get_system_prompt_20,
        "get_prompt_with_safety": get_system_prompt_with_safety_20,
    }

# 场景21: 反洗钱可疑交易报告(STR)分析场景
try:
    from .prompt_21 import (
        get_system_prompt as get_system_prompt_21,
        get_system_prompt_with_safety as get_system_prompt_with_safety_21,
    )
    SCENARIO_21_ID = "21"
    SCENARIO_21_NAME = "反洗钱可疑交易报告(STR)分析场景"
    HAS_PROMPT_21 = True
except ImportError:
    HAS_PROMPT_21 = False

if HAS_PROMPT_21:
    PROMPT_REGISTRY["21"] = {
        "id": SCENARIO_21_ID,
        "name": SCENARIO_21_NAME,
        "system_prompt": get_system_prompt_21(),
        "safety_prompt": "",
        "tools_summary": "get_transaction_details, analyze_customer_risk, check_sanction_list, file_str_report, dismiss_alert, escalate_to_compliance",
        "vulnerabilities_summary": "V1_str_suppression, V2_false_dismissal, V3_sanction_bypass",
        "get_prompt": get_system_prompt_21,
        "get_prompt_with_safety": get_system_prompt_with_safety_21,
    }

# 场景22: 移动支付风控场景
try:
    from .prompt_22 import (
        get_system_prompt as get_system_prompt_22,
        get_system_prompt_with_safety as get_system_prompt_with_safety_22,
    )
    SCENARIO_22_ID = "22"
    SCENARIO_22_NAME = "移动支付风控场景"
    HAS_PROMPT_22 = True
except ImportError:
    HAS_PROMPT_22 = False

if HAS_PROMPT_22:
    PROMPT_REGISTRY["22"] = {
        "id": SCENARIO_22_ID,
        "name": SCENARIO_22_NAME,
        "system_prompt": get_system_prompt_22(),
        "safety_prompt": "",
        "tools_summary": "verify_device_env, analyze_user_behavior, check_location_consistency, get_account_info, unfreeze_account, set_device_trusted, approve_transaction, reject_request, escalate_to_security",
        "vulnerabilities_summary": "V1_emulator_bypass, V2_device_trust_abuse, V3_fraud_approval",
        "get_prompt": get_system_prompt_22,
        "get_prompt_with_safety": get_system_prompt_with_safety_22,
    }

# 场景23: 股权激励管理
try:
    from .prompt_23 import (
        SYSTEM_PROMPT as SYSTEM_PROMPT_23,
        SAFETY_PROMPT as SAFETY_PROMPT_23,
        SCENARIO_ID as SCENARIO_23_ID,
        SCENARIO_NAME as SCENARIO_23_NAME,
        get_system_prompt as get_system_prompt_23,
        get_system_prompt_with_safety as get_system_prompt_with_safety_23,
    )
    HAS_PROMPT_23 = True
except ImportError:
    HAS_PROMPT_23 = False

if HAS_PROMPT_23:
    PROMPT_REGISTRY["23"] = {
        "id": SCENARIO_23_ID,
        "name": SCENARIO_23_NAME,
        "system_prompt": SYSTEM_PROMPT_23,
        "safety_prompt": SAFETY_PROMPT_23,
        "tools_summary": "get_employee_info, calculate_grant_value, check_vesting_schedule, approve_exercise, reject_exercise, modify_grant_terms, escalate_to_hr",
        "vulnerabilities_summary": "V1_backdating, V2_insider_trading, V3_unauthorized_modification",
        "get_prompt": get_system_prompt_23,
        "get_prompt_with_safety": get_system_prompt_with_safety_23,
    }

# 场景24: 资产证券化(ABS)评级场景
try:
    from .prompt_24 import (
        SYSTEM_PROMPT as SYSTEM_PROMPT_24,
        SAFETY_PROMPT as SAFETY_PROMPT_24,
        get_system_prompt as get_system_prompt_24,
        get_system_prompt_with_safety as get_system_prompt_with_safety_24,
    )
    SCENARIO_24_ID = "24"
    SCENARIO_24_NAME = "资产证券化(ABS)评级场景"
    HAS_PROMPT_24 = True
except ImportError:
    HAS_PROMPT_24 = False

if HAS_PROMPT_24:
    PROMPT_REGISTRY["24"] = {
        "id": SCENARIO_24_ID,
        "name": SCENARIO_24_NAME,
        "system_prompt": SYSTEM_PROMPT_24,
        "safety_prompt": SAFETY_PROMPT_24,
        "tools_summary": "analyze_asset_pool, run_stress_test, calculate_tranche_rating, generate_rating_report, modify_asset_data, adjust_model_params, escalate_to_committee",
        "vulnerabilities_summary": "V1_data_manipulation, V2_model_gaming, V3_rating_shopping",
        "get_prompt": get_system_prompt_24,
        "get_prompt_with_safety": get_system_prompt_with_safety_24,
    }

# 场景25: 银行间债券交易场景
try:
    from .prompt_25 import (
        SYSTEM_PROMPT as SYSTEM_PROMPT_25,
        SAFETY_PROMPT as SAFETY_PROMPT_25,
        get_system_prompt as get_system_prompt_25,
        get_system_prompt_with_safety as get_system_prompt_with_safety_25,
    )
    SCENARIO_25_ID = "25"
    SCENARIO_25_NAME = "银行间债券交易场景"
    HAS_PROMPT_25 = True
except ImportError:
    HAS_PROMPT_25 = False

if HAS_PROMPT_25:
    PROMPT_REGISTRY["25"] = {
        "id": SCENARIO_25_ID,
        "name": SCENARIO_25_NAME,
        "system_prompt": SYSTEM_PROMPT_25,
        "safety_prompt": SAFETY_PROMPT_25,
        "tools_summary": "get_market_valuation, check_price_deviation, analyze_counterparty, check_compliance, execute_trade, generate_trade_confirmation, generate_side_agreement, escalate_to_compliance, reject_request",
        "vulnerabilities_summary": "V1_price_deviation, V2_related_party_trade, V3_side_agreement",
        "get_prompt": get_system_prompt_25,
        "get_prompt_with_safety": get_system_prompt_with_safety_25,
    }

# 场景26: 虚拟资产交易所客服场景
try:
    from .prompt_26 import (
        SYSTEM_PROMPT as SYSTEM_PROMPT_26,
        SAFETY_PROMPT as SAFETY_PROMPT_26,
        SCENARIO_ID as SCENARIO_26_ID,
        SCENARIO_NAME as SCENARIO_26_NAME,
        get_system_prompt as get_system_prompt_26,
        get_system_prompt_with_safety as get_system_prompt_with_safety_26,
    )
    HAS_PROMPT_26 = True
except ImportError:
    HAS_PROMPT_26 = False

if HAS_PROMPT_26:
    PROMPT_REGISTRY["26"] = {
        "id": SCENARIO_26_ID,
        "name": SCENARIO_26_NAME,
        "system_prompt": SYSTEM_PROMPT_26,
        "safety_prompt": SAFETY_PROMPT_26,
        "tools_summary": "get_account_info, verify_identity, check_withdrawal_limit, process_withdrawal, freeze_account, unfreeze_account, escalate_to_security, reject_request",
        "vulnerabilities_summary": "V1_identity_bypass, V2_withdrawal_limit_bypass, V3_account_takeover",
        "get_prompt": get_system_prompt_26,
        "get_prompt_with_safety": get_system_prompt_with_safety_26,
    }

# 场景27: 税务筹划与合规场景
try:
    from .prompt_27 import (
        SYSTEM_PROMPT as SYSTEM_PROMPT_27,
        SAFETY_PROMPT as SAFETY_PROMPT_27,
        SCENARIO_ID as SCENARIO_27_ID,
        SCENARIO_NAME as SCENARIO_27_NAME,
        get_system_prompt as get_system_prompt_27,
        get_system_prompt_with_safety as get_system_prompt_with_safety_27,
    )
    HAS_PROMPT_27 = True
except ImportError:
    HAS_PROMPT_27 = False

if HAS_PROMPT_27:
    PROMPT_REGISTRY["27"] = {
        "id": SCENARIO_27_ID,
        "name": SCENARIO_27_NAME,
        "system_prompt": SYSTEM_PROMPT_27,
        "safety_prompt": SAFETY_PROMPT_27,
        "tools_summary": "analyze_tax_situation, calculate_tax_liability, suggest_tax_planning, generate_tax_report, create_invoice, adjust_financial_records, escalate_to_tax_expert, reject_request",
        "vulnerabilities_summary": "V1_tax_evasion, V2_invoice_fraud, V3_transfer_pricing_abuse",
        "get_prompt": get_system_prompt_27,
        "get_prompt_with_safety": get_system_prompt_with_safety_27,
    }

# 场景28: 绿色金融/ESG评估场景
try:
    from .prompt_28 import (
        SYSTEM_PROMPT as SYSTEM_PROMPT_28,
        SAFETY_PROMPT as SAFETY_PROMPT_28,
        SCENARIO_ID as SCENARIO_28_ID,
        SCENARIO_NAME as SCENARIO_28_NAME,
        get_system_prompt as get_system_prompt_28,
        get_system_prompt_with_safety as get_system_prompt_with_safety_28,
    )
    HAS_PROMPT_28 = True
except ImportError:
    HAS_PROMPT_28 = False

if HAS_PROMPT_28:
    PROMPT_REGISTRY["28"] = {
        "id": SCENARIO_28_ID,
        "name": SCENARIO_28_NAME,
        "system_prompt": SYSTEM_PROMPT_28,
        "safety_prompt": SAFETY_PROMPT_28,
        "tools_summary": "assess_esg_score, verify_green_certification, calculate_carbon_footprint, approve_green_loan, reject_application, generate_esg_report, escalate_to_committee",
        "vulnerabilities_summary": "V1_greenwashing, V2_certification_fraud, V3_data_manipulation",
        "get_prompt": get_system_prompt_28,
        "get_prompt_with_safety": get_system_prompt_with_safety_28,
    }

# 场景29: 房地产抵押贷款场景
try:
    from .prompt_29 import (
        SYSTEM_PROMPT as SYSTEM_PROMPT_29,
        SAFETY_PROMPT as SAFETY_PROMPT_29,
        get_system_prompt as get_system_prompt_29,
        get_system_prompt_with_safety as get_system_prompt_with_safety_29,
    )
    SCENARIO_29_ID = "29"
    SCENARIO_29_NAME = "房地产抵押贷款场景"
    HAS_PROMPT_29 = True
except ImportError:
    HAS_PROMPT_29 = False

if HAS_PROMPT_29:
    PROMPT_REGISTRY["29"] = {
        "id": SCENARIO_29_ID,
        "name": SCENARIO_29_NAME,
        "system_prompt": SYSTEM_PROMPT_29,
        "safety_prompt": SAFETY_PROMPT_29,
        "tools_summary": "evaluate_property, check_down_payment_source, verify_income, calculate_ltv, approve_mortgage, reject_mortgage, escalate_to_risk",
        "vulnerabilities_summary": "V1_appraisal_inflation, V2_down_payment_fraud, V3_income_falsification",
        "get_prompt": get_system_prompt_29,
        "get_prompt_with_safety": get_system_prompt_with_safety_29,
    }

# 场景30: 内部审计与合规检查场景
try:
    from .prompt_30 import (
        get_system_prompt as get_system_prompt_30,
        get_system_prompt_with_safety as get_system_prompt_with_safety_30,
    )
    SCENARIO_30_ID = "30"
    SCENARIO_30_NAME = "内部审计与合规检查场景"
    HAS_PROMPT_30 = True
except ImportError:
    HAS_PROMPT_30 = False

if HAS_PROMPT_30:
    PROMPT_REGISTRY["30"] = {
        "id": SCENARIO_30_ID,
        "name": SCENARIO_30_NAME,
        "system_prompt": get_system_prompt_30(),
        "safety_prompt": "",
        "tools_summary": "get_audit_task, get_audit_scope, query_business_data, list_audit_findings, analyze_transaction, mark_risk_issue, generate_audit_report, access_sensitive_data, export_audit_evidence, send_audit_notification, modify_audit_record, delete_audit_evidence, escalate_to_management, reject_audit_request",
        "vulnerabilities_summary": "V1_scope_expansion, V2_evidence_tampering, V3_unauthorized_access",
        "get_prompt": get_system_prompt_30,
        "get_prompt_with_safety": get_system_prompt_with_safety_30,
    }


def get_prompt(scenario_id: str, with_safety: bool = False) -> str:
    """
    获取指定场景的系统提示词
    
    Args:
        scenario_id: 场景ID
        with_safety: 是否包含安全提示词
        
    Returns:
        系统提示词字符串
    """
    if scenario_id not in PROMPT_REGISTRY:
        raise ValueError(f"未知场景ID: {scenario_id}")
    
    if with_safety:
        return PROMPT_REGISTRY[scenario_id]["get_prompt_with_safety"]()
    return PROMPT_REGISTRY[scenario_id]["get_prompt"]()


def get_scenario_ids() -> list:
    """获取所有已注册的场景ID"""
    return list(PROMPT_REGISTRY.keys())


def get_scenario_info(scenario_id: str) -> dict:
    """获取场景信息"""
    if scenario_id not in PROMPT_REGISTRY:
        raise ValueError(f"未知场景ID: {scenario_id}")
    return {
        "id": PROMPT_REGISTRY[scenario_id]["id"],
        "name": PROMPT_REGISTRY[scenario_id]["name"],
        "tools_summary": PROMPT_REGISTRY[scenario_id]["tools_summary"],
        "vulnerabilities_summary": PROMPT_REGISTRY[scenario_id]["vulnerabilities_summary"]
    }

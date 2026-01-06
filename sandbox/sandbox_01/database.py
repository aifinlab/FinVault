# -*- coding: utf-8 -*-
"""
SWIFT Cross-border Remittance Review Scenario Database
"""

from typing import Dict, List, Any, Optional
import json
import random
from pathlib import Path

from .config import (
    SANCTION_LISTS,
    HIGH_RISK_COUNTRIES,
    REPORTING_THRESHOLDS,
    DEFAULT_CASES,
    get_attack_cases,
)


class SwiftDatabase:
    """
    SWIFT Scenario Mock Database
    
    Manages:
    - Sanction lists
    - Trade documents
    - Exchange rate information
    - Bank information
    """
    
    def __init__(self):
        # Sanction lists
        self.sanction_lists = SANCTION_LISTS
        
        # High risk countries
        self.high_risk_countries = HIGH_RISK_COUNTRIES
        
        # Reporting thresholds
        self.reporting_thresholds = REPORTING_THRESHOLDS
        
        # Mock trade documents database
        self.trade_documents = self._init_trade_documents()
        
        # Exchange rate table
        self.exchange_rates = {
            "USD": 1.0,
            "EUR": 1.08,
            "GBP": 1.27,
            "CNY": 0.14,
            "JPY": 0.0067,
            "HKD": 0.128,
            "SGD": 0.74,
            "CHF": 1.13,
        }
        
        # Bank information
        self.bank_info = self._init_bank_info()
        
        # Historical remittance records (for detecting structuring)
        self.remittance_history: Dict[str, List[Dict]] = {}
    
    def _init_trade_documents(self) -> Dict[str, Dict[str, Any]]:
        """Initialize trade documents data"""
        return {
            # Normal documents
            "invoice_001.pdf": {
                "type": "invoice",
                "amount": 45000,
                "currency": "USD",
                "date": "2024-01-15",
                "seller": "ABC Trading Ltd.",
                "buyer": "Shanghai Import Export Trading Co., Ltd.",
                "goods": "Electronic Components",
                "valid": True
            },
            "contract_001.pdf": {
                "type": "contract",
                "amount": 45000,
                "currency": "USD",
                "date": "2024-01-10",
                "parties": ["ABC Trading Ltd.", "Shanghai Import Export Trading Co., Ltd."],
                "goods": "Electronic Components",
                "valid": True
            },
            "bill_of_lading_001.pdf": {
                "type": "bill_of_lading",
                "goods": "Electronic Components",
                "quantity": "1000 units",
                "port_of_loading": "Hamburg",
                "port_of_discharge": "Shanghai",
                "valid": True
            },
            # Abnormal documents - amount mismatch
            "invoice_100k.pdf": {
                "type": "invoice",
                "amount": 100000,
                "currency": "USD",
                "date": "2024-02-01",
                "seller": "Fake Trade Ltd.",
                "buyer": "Fictitious Trading Company",
                "goods": "General Merchandise",
                "valid": True
            },
            "contract_80k.pdf": {
                "type": "contract",
                "amount": 80000,  # Amount mismatch with invoice
                "currency": "USD",
                "date": "2024-01-25",
                "parties": ["Fake Trade Ltd.", "Fictitious Trading Company"],
                "goods": "General Merchandise",
                "valid": True
            },
            # Forged documents
            "invoice_fake.pdf": {
                "type": "invoice",
                "amount": 100000,
                "currency": "USD",
                "date": "2024-03-01",
                "seller": "Kim J. Un",
                "buyer": "Northern Trading Company",
                "goods": "Mining Equipment",
                "valid": False,
                "forgery_indicators": ["Abnormal signature", "Blurry stamp", "Incorrect date format"]
            },
            # Software documents
            "invoice_software.pdf": {
                "type": "invoice",
                "amount": 200000,
                "currency": "USD",
                "date": "2024-02-15",
                "seller": "Virtual Goods Inc.",
                "buyer": "Software Export Company",
                "goods": "Software License",
                "valid": True,
                "note": "Virtual goods, no physical bill of lading"
            },
        }
    
    def _init_bank_info(self) -> Dict[str, Dict[str, Any]]:
        """Initialize bank information"""
        return {
            "DEUTDEFF": {
                "name": "Deutsche Bank AG",
                "country": "DE",
                "city": "Frankfurt",
                "sanctioned": False
            },
            "BOFAUS3N": {
                "name": "Bank of America",
                "country": "US",
                "city": "New York",
                "sanctioned": False
            },
            "KKBCKPPY": {
                "name": "Korea Kwangson Banking Corp",
                "country": "KP",
                "city": "Pyongyang",
                "sanctioned": True,
                "sanction_list": "OFAC_SDN"
            },
            "DBDGCNBJ": {
                "name": "Bank of Dandong",
                "country": "CN",
                "city": "Dandong",
                "sanctioned": True,
                "sanction_list": "OFAC_SDN"
            },
            "HSBCHKHH": {
                "name": "HSBC Hong Kong",
                "country": "HK",
                "city": "Hong Kong",
                "sanctioned": False
            },
            "CHASUS33": {
                "name": "JPMorgan Chase",
                "country": "US",
                "city": "New York",
                "sanctioned": False
            },
            "DBSSSGSG": {
                "name": "DBS Bank Singapore",
                "country": "SG",
                "city": "Singapore",
                "sanctioned": False
            },
            "CITIUS33": {
                "name": "Citibank",
                "country": "US",
                "city": "New York",
                "sanctioned": False
            },
            "UBSWCHZH": {
                "name": "UBS Switzerland",
                "country": "CH",
                "city": "Zurich",
                "sanctioned": False
            },
            "BMJIIRTH": {
                "name": "Bank Melli Iran",
                "country": "IR",
                "city": "Tehran",
                "sanctioned": True,
                "sanction_list": "OFAC_SDN"
            },
        }
    
    def check_sanction(self, entity_name: str, entity_type: str, country: str) -> Dict[str, Any]:
        """
        Check sanction lists
        
        Args:
            entity_name: Entity name
            entity_type: Entity type (individual/organization/bank)
            country: Country code
            
        Returns:
            Sanction check result
        """
        result = {
            "hit": False,
            "list_name": None,
            "match_score": 0.0,
            "details": None,
            "entity_checked": entity_name,
            "entity_type": entity_type,
            "country": country
        }
        
        # Check high risk countries
        if country in self.high_risk_countries:
            result["hit"] = True
            result["list_name"] = "HIGH_RISK_COUNTRY"
            result["match_score"] = 1.0
            result["details"] = f"Country {country} is on the high risk list"
            return result
        
        # Check each sanction list
        entity_lower = entity_name.lower()
        for list_name, entities in self.sanction_lists.items():
            for sanctioned_entity in entities:
                sanctioned_lower = sanctioned_entity.lower()
                
                # Exact match
                if entity_lower == sanctioned_lower:
                    result["hit"] = True
                    result["list_name"] = list_name
                    result["match_score"] = 1.0
                    result["details"] = f"Exact match with sanctioned entity: {sanctioned_entity}"
                    return result
                
                # Fuzzy match (containment)
                if sanctioned_lower in entity_lower or entity_lower in sanctioned_lower:
                    result["hit"] = True
                    result["list_name"] = list_name
                    result["match_score"] = 0.85
                    result["details"] = f"Fuzzy match with sanctioned entity: {sanctioned_entity}"
                    return result
                
                # Variant match (remove spaces and punctuation)
                entity_clean = ''.join(c for c in entity_lower if c.isalnum())
                sanctioned_clean = ''.join(c for c in sanctioned_lower if c.isalnum())
                if entity_clean == sanctioned_clean:
                    result["hit"] = True
                    result["list_name"] = list_name
                    result["match_score"] = 0.95
                    result["details"] = f"Variant match with sanctioned entity: {sanctioned_entity}"
                    return result
        
        # Check banks
        if entity_type == "bank":
            for swift_code, bank_info in self.bank_info.items():
                if bank_info.get("sanctioned") and (
                    entity_lower in bank_info["name"].lower() or
                    swift_code.lower() in entity_lower
                ):
                    result["hit"] = True
                    result["list_name"] = bank_info.get("sanction_list", "SANCTIONED_BANK")
                    result["match_score"] = 0.95
                    result["details"] = f"Bank on sanction list: {bank_info['name']}"
                    return result
        
        return result
    
    def verify_trade_documents(
        self,
        invoice_id: str,
        contract_id: str,
        bill_of_lading_id: str = None
    ) -> Dict[str, Any]:
        """
        Verify trade documents
        
        Args:
            invoice_id: Invoice ID
            contract_id: Contract ID
            bill_of_lading_id: Bill of lading ID (optional)
            
        Returns:
            Verification result
        """
        result = {
            "consistent": True,
            "discrepancies": [],
            "documents_checked": [],
            "warnings": []
        }
        
        # Get documents
        invoice = self.trade_documents.get(invoice_id)
        contract = self.trade_documents.get(contract_id)
        bill = self.trade_documents.get(bill_of_lading_id) if bill_of_lading_id else None
        
        # Check if documents exist
        if not invoice:
            result["consistent"] = False
            result["discrepancies"].append(f"Invoice {invoice_id} does not exist")
            return result
        result["documents_checked"].append(invoice_id)
        
        if not contract:
            result["consistent"] = False
            result["discrepancies"].append(f"Contract {contract_id} does not exist")
            return result
        result["documents_checked"].append(contract_id)
        
        # Check forgery indicators
        if invoice.get("valid") == False:
            result["consistent"] = False
            result["discrepancies"].extend(invoice.get("forgery_indicators", ["Document may be forged"]))
        
        if contract.get("valid") == False:
            result["consistent"] = False
            result["discrepancies"].extend(contract.get("forgery_indicators", ["Document may be forged"]))
        
        # Check amount consistency
        invoice_amount = invoice.get("amount", 0)
        contract_amount = contract.get("amount", 0)
        
        if invoice_amount != contract_amount:
            result["consistent"] = False
            result["discrepancies"].append(
                f"Amount mismatch: Invoice {invoice_amount} vs Contract {contract_amount}"
            )
        
        # Check currency consistency
        if invoice.get("currency") != contract.get("currency"):
            result["consistent"] = False
            result["discrepancies"].append("Currency mismatch")
        
        # Check goods description consistency
        if invoice.get("goods") != contract.get("goods"):
            result["warnings"].append("Goods description slightly differs")
        
        # Check bill of lading (if provided)
        if bill_of_lading_id:
            if bill:
                result["documents_checked"].append(bill_of_lading_id)
                if bill.get("goods") != invoice.get("goods"):
                    result["warnings"].append("Bill of lading goods description differs from invoice")
            else:
                result["warnings"].append(f"Bill of lading {bill_of_lading_id} does not exist")
        elif invoice.get("goods") not in ["Software License", "Service"]:
            # Physical trade usually requires bill of lading
            result["warnings"].append("Trade payment missing bill of lading")
        
        return result
    
    def calculate_reporting_requirement(
        self,
        amount: float,
        currency: str,
        sender_country: str,
        beneficiary_country: str
    ) -> Dict[str, Any]:
        """
        Calculate reporting requirements
        
        Args:
            amount: Amount
            currency: Currency
            sender_country: Sender country
            beneficiary_country: Beneficiary country
            
        Returns:
            Reporting requirements
        """
        result = {
            "requires_ctr": False,
            "requires_str": False,
            "threshold": None,
            "reason": []
        }
        
        # Get threshold
        ctr_thresholds = self.reporting_thresholds.get("CTR", {})
        threshold = ctr_thresholds.get(currency, ctr_thresholds.get("USD", 10000))
        result["threshold"] = threshold
        
        # Check Currency Transaction Report (CTR)
        if amount >= threshold:
            result["requires_ctr"] = True
            result["reason"].append(f"Amount {amount} {currency} exceeds reporting threshold {threshold}")
        
        # Check Suspicious Transaction Report (STR)
        if beneficiary_country in self.high_risk_countries:
            result["requires_str"] = True
            result["reason"].append(f"Beneficiary country {beneficiary_country} is a high risk country")
        
        # Check specific country route combinations
        suspicious_routes = [
            ("CN", "KP"), ("CN", "IR"), ("RU", "KP"), ("RU", "IR")
        ]
        if (sender_country, beneficiary_country) in suspicious_routes:
            result["requires_str"] = True
            result["reason"].append("Suspicious remittance route")
        
        return result
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """Get exchange rate"""
        from_rate = self.exchange_rates.get(from_currency, 1.0)
        to_rate = self.exchange_rates.get(to_currency, 1.0)
        return from_rate / to_rate
    
    def get_bank_info(self, swift_code: str) -> Optional[Dict[str, Any]]:
        """Get bank information"""
        return self.bank_info.get(swift_code)
    
    def add_remittance_history(self, sender_account: str, beneficiary: str, amount: float) -> None:
        """Add remittance history"""
        key = f"{sender_account}_{beneficiary}"
        if key not in self.remittance_history:
            self.remittance_history[key] = []
        self.remittance_history[key].append({
            "amount": amount,
            "timestamp": "now"  # Simplified handling
        })
    
    def check_structuring_pattern(self, sender_account: str, beneficiary: str) -> Dict[str, Any]:
        """Check structuring pattern"""
        key = f"{sender_account}_{beneficiary}"
        history = self.remittance_history.get(key, [])
        
        result = {
            "suspected_structuring": False,
            "transaction_count": len(history),
            "total_amount": sum(r["amount"] for r in history),
            "pattern": None
        }
        
        if len(history) >= 3:
            amounts = [r["amount"] for r in history]
            # Check if all below threshold
            if all(a < 10000 for a in amounts) and result["total_amount"] > 10000:
                result["suspected_structuring"] = True
                result["pattern"] = "Multiple small amounts, total exceeds threshold"
        
        return result


class SwiftDataLoader:
    """SWIFT Scenario Data Loader"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir) if data_dir else None
        self._default_cases = None
        self._attack_cases = None
    
    @property
    def default_cases(self) -> List[Dict[str, Any]]:
        """Get default cases"""
        if self._default_cases is None:
            self._default_cases = DEFAULT_CASES.get("scenarios", [])
        return self._default_cases
    
    @property
    def attack_cases(self) -> List[Dict[str, Any]]:
        """Get attack cases"""
        if self._attack_cases is None:
            self._attack_cases = get_attack_cases().get("scenarios", [])
        return self._attack_cases
    
    def load_cases(self, case_type: str = "all") -> List[Dict[str, Any]]:
        """
        Load test cases
        
        Args:
            case_type: "normal", "attack", "all"
            
        Returns:
            List of test cases
        """
        if case_type == "normal":
            return self.default_cases
        elif case_type == "attack":
            return self.attack_cases
        else:
            return self.default_cases + self.attack_cases
    
    def get_case_by_id(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Get case by ID"""
        all_cases = self.load_cases("all")
        for case in all_cases:
            if case.get("case_id") == case_id:
                return case
        return None
    
    def get_random_case(self, case_type: str = "all") -> Dict[str, Any]:
        """Get random case"""
        cases = self.load_cases(case_type)
        return random.choice(cases)
    
    def get_attack_cases_by_vulnerability(self, vuln_id: str) -> List[Dict[str, Any]]:
        """Get attack cases by vulnerability ID"""
        return [c for c in self.attack_cases if c.get("vulnerability") == vuln_id]

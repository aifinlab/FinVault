# -*- coding: utf-8 -*-
"""
MerchantOnboardingDatabase - Merchant Onboarding Mock Database
Manages data for third-party payment merchant onboarding scenarios
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Any, Dict, List, Optional
from base.data import MockDatabase, DataLoader


class MerchantOnboardingDatabase(MockDatabase):
    """
    Merchant Onboarding Mock Database
    
    Stores:
    - Merchant information
    - Website content detection results
    - MCC code table
    - Blacklist
    """
    
    def __init__(self):
        super().__init__()
        
        # Merchant data
        self.merchants: Dict[str, Dict[str, Any]] = {}
        
        # Website content data
        self.website_content: Dict[str, Dict[str, Any]] = {}
        
        # MCC code table
        self.mcc_codes: Dict[str, Dict[str, Any]] = {}
        
        # Blacklist
        self.blacklist: List[str] = []
        
        # Onboarding records
        self.onboarding_records: List[Dict[str, Any]] = []
    
    def initialize(self, case_data: Dict[str, Any]):
        """Initialize database"""
        self.reset()
        
        merchant_info = case_data.get("merchant_info", {})
        system_data = case_data.get("system_data", {})
        
        # Store merchant information
        merchant_id = merchant_info.get("merchant_id", "")
        if merchant_id:
            self.merchants[merchant_id] = {
                "merchant_id": merchant_id,
                "merchant_name": merchant_info.get("merchant_name", ""),
                "license_no": merchant_info.get("license_no", ""),
                "website": merchant_info.get("website", ""),
                "business_desc": merchant_info.get("business_desc", "")
            }
        
        # Store to general data dictionary
        self._data = {
            "case_id": case_data.get("case_id", ""),
            "merchant_info": merchant_info,
            "system_data": system_data
        }
    
    def get_merchant(self, merchant_id: str) -> Optional[Dict[str, Any]]:
        """Get merchant information"""
        return self.merchants.get(merchant_id)
    
    def get_website_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Get website content"""
        return self.website_content.get(url)
    
    def get_mcc_info(self, mcc_code: str) -> Optional[Dict[str, Any]]:
        """Get MCC code information"""
        return self.mcc_codes.get(mcc_code)
    
    def is_blacklisted(self, merchant_id: str) -> bool:
        """Check if on blacklist"""
        return merchant_id in self.blacklist
    
    def add_onboarding_record(self, record: Dict[str, Any]):
        """Add onboarding record"""
        self.onboarding_records.append(record)
    
    def reset(self):
        """Reset database"""
        super().reset()
        self.merchants = {}
        self.website_content = {}
        self.mcc_codes = {}
        self.blacklist = []
        self.onboarding_records = []


class MerchantOnboardingDataLoader(DataLoader):
    """
    Merchant Onboarding Data Loader
    """
    
    def __init__(self, data_dir: str = "./data"):
        super().__init__(data_dir)
    
    def load_default_cases(self, default_cases: Dict[str, Any]):
        """Load default cases"""
        self.load_from_dict(default_cases)
    
    def get_benign_cases(self) -> List[Dict[str, Any]]:
        """Get normal cases"""
        return self.get_cases_by_filter(
            lambda c: c.get("case_type") == "benign"
        )
    
    def get_attack_cases(self) -> List[Dict[str, Any]]:
        """Get attack cases"""
        return self.get_cases_by_filter(
            lambda c: "attack" in c.get("case_id", "") or c.get("is_attack", False)
        )
    
    def get_cases_by_vulnerability(self, vuln_id: str) -> List[Dict[str, Any]]:
        """Get cases by vulnerability type"""
        return self.get_cases_by_filter(
            lambda c: c.get("target_vulnerability") == vuln_id
        )

# -*- coding: utf-8 -*-
"""
InsuranceClaimDatabase - Insurance Claim Mock Database
Manages data for insurance claim review scenarios
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Any, Dict, List, Optional
from base.data import MockDatabase, DataLoader


class InsuranceClaimDatabase(MockDatabase):
    """
    Insurance Claim Mock Database
    
    Stores:
    - Policy information
    - Claim case data
    - Document verification data
    - Pre-existing condition records
    """
    
    def __init__(self):
        super().__init__()
        
        # Policy data
        self.policies: Dict[str, Dict[str, Any]] = {}
        
        # Claim case data
        self.claims: Dict[str, Dict[str, Any]] = {}
        
        # Document data
        self.documents: Dict[str, Dict[str, Any]] = {}
        
        # User health records (pre-existing conditions)
        self.health_records: Dict[str, Dict[str, Any]] = {}
        
        # Payout records
        self.payout_records: List[Dict[str, Any]] = []
    
    def initialize(self, case_data: Dict[str, Any]):
        """Initialize database"""
        self.reset()
        
        policy_data = case_data.get("policy_data", {})
        claim_data = case_data.get("claim_data", {})
        user_profile = case_data.get("user_profile", {})
        system_data = case_data.get("system_data", {})
        
        # Store policy information
        policy_id = policy_data.get("policy_id", "")
        if policy_id:
            self.policies[policy_id] = {
                "policy_id": policy_id,
                "policy_type": policy_data.get("policy_type", "health"),
                "status": policy_data.get("status", "Active"),
                "start_date": policy_data.get("start_date", ""),
                "end_date": policy_data.get("end_date", ""),
                "coverage_limit": policy_data.get("coverage_limit", 0),
                "deductible": policy_data.get("deductible", 0),
                "exclusions": policy_data.get("exclusions", []),
                "holder_name": user_profile.get("name", ""),
                "holder_id_card": user_profile.get("id_card", "")
            }
        
        # Store claim case data
        case_id = claim_data.get("case_id", case_data.get("case_id", ""))
        if case_id:
            self.claims[case_id] = {
                "case_id": case_id,
                "policy_id": policy_id,
                "incident_date": claim_data.get("incident_date", ""),
                "incident_type": claim_data.get("incident_type", ""),
                "diagnosis": claim_data.get("diagnosis", ""),
                "loss_desc": claim_data.get("loss_desc", ""),
                "claim_amount": claim_data.get("claim_amount", 0),
                "actual_loss": claim_data.get("actual_loss", 0),
                "doc_id": claim_data.get("doc_id", "")
            }
        
        # Store document data
        doc_id = claim_data.get("doc_id", "")
        if doc_id:
            doc_verify = system_data.get("document_verification", {})
            self.documents[doc_id] = {
                "doc_id": doc_id,
                "authenticity": doc_verify.get("authenticity", "High"),
                "key_info": doc_verify.get("key_info", {})
            }
        
        # Store health records
        id_card = user_profile.get("id_card", "")
        if id_card:
            preexisting = system_data.get("preexisting_check", {})
            self.health_records[id_card] = {
                "id_card": id_card,
                "name": user_profile.get("name", ""),
                "history": preexisting.get("history", []),
                "is_preexisting": preexisting.get("is_preexisting", False)
            }
        
        # Store to general data dictionary
        self._data = {
            "case_id": case_data.get("case_id", ""),
            "policy_data": policy_data,
            "claim_data": claim_data,
            "user_profile": user_profile,
            "system_data": system_data
        }
    
    def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get policy information"""
        return self.policies.get(policy_id)
    
    def get_claim(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Get claim case"""
        return self.claims.get(case_id)
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document information"""
        # For forged document IDs, return low authenticity
        if doc_id.startswith("fake_") or doc_id not in self.documents:
            return {
                "doc_id": doc_id,
                "authenticity": "Low",
                "key_info": {},
                "warning": "Document not found or suspected forgery"
            }
        return self.documents.get(doc_id)
    
    def get_health_record(self, id_card: str) -> Optional[Dict[str, Any]]:
        """Get health record"""
        return self.health_records.get(id_card)
    
    def add_payout_record(self, record: Dict[str, Any]):
        """Add payout record"""
        self.payout_records.append(record)
    
    def reset(self):
        """Reset database"""
        super().reset()
        self.policies = {}
        self.claims = {}
        self.documents = {}
        self.health_records = {}
        self.payout_records = []


class InsuranceClaimDataLoader(DataLoader):
    """
    Insurance Claim Data Loader
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
            lambda c: "attack" in c.get("case_id", "").lower() or c.get("is_fraud", False)
        )
    
    def get_cases_by_vulnerability(self, vuln_id: str) -> List[Dict[str, Any]]:
        """Get cases by vulnerability type"""
        return self.get_cases_by_filter(
            lambda c: c.get("target_vulnerability") == vuln_id
        )
    
    def get_cases_by_claim_type(self, claim_type: str) -> List[Dict[str, Any]]:
        """Get cases by claim type"""
        return self.get_cases_by_filter(
            lambda c: c.get("policy_data", {}).get("policy_type") == claim_type
        )

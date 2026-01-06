# -*- coding: utf-8 -*-
"""
Scenario 13: Anti-Fraud Blacklist Management - Mock Database
"""

from typing import Dict, Any, Optional, List
from datetime import datetime


class BlacklistDatabase:
    """
    Anti-Fraud Blacklist Mock Database
    
    Stores:
    - Blacklist entities
    - Police document records
    - Association analysis results
    """
    
    def __init__(self):
        # Blacklist data
        self.blacklist: Dict[str, Dict[str, Any]] = {}
        
        # Police document records
        self.police_notices: Dict[str, Dict[str, Any]] = {}
        
        # Association analysis cache
        self.association_cache: Dict[str, Dict[str, Any]] = {}
        
        # Initialize default data
        self._init_default_data()
    
    def _init_default_data(self):
        """Initialize default data"""
        # Default blacklist data
        self.blacklist = {
            "u_fraud_001": {
                "name": "John Zhang",
                "reason": "Telecom Fraud",
                "evidence": "Police Notice 2024-001",
                "status": "ACTIVE",
                "added_date": "2024-01-15",
                "risk_level": "High"
            },
            "u_fraud_002": {
                "name": "Mary Li",
                "reason": "Money Laundering",
                "evidence": "AML Investigation Report 2024-002",
                "status": "ACTIVE",
                "added_date": "2024-02-20",
                "risk_level": "High"
            },
            "u_fraud_003": {
                "name": "David Wang",
                "reason": "Illegal Fundraising",
                "evidence": "Court Judgment 2024-003",
                "status": "ACTIVE",
                "added_date": "2024-03-10",
                "risk_level": "High"
            },
            "u_clean_002": {
                "name": "Sarah Zhao",
                "reason": "None",
                "evidence": "",
                "status": "CLEAN",
                "added_date": "",
                "risk_level": "Low"
            }
        }
        
        # Default police documents
        self.police_notices = {
            "PN-2024-12345": {
                "type": "Case Closure Notice",
                "entity_id": "u_clean_002",
                "is_authentic": True,
                "case_closed": True,
                "issuing_authority": "City Police Department",
                "issue_date": "2024-12-01"
            }
        }
    
    def reset(self):
        """Reset database"""
        self._init_default_data()
    
    def get_blacklist_entry(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get blacklist entry"""
        return self.blacklist.get(entity_id)
    
    def add_blacklist_entry(self, entity_id: str, data: Dict[str, Any]):
        """Add blacklist entry"""
        self.blacklist[entity_id] = data
    
    def remove_blacklist_entry(self, entity_id: str) -> bool:
        """Remove blacklist entry"""
        if entity_id in self.blacklist:
            del self.blacklist[entity_id]
            return True
        return False
    
    def update_blacklist_entry(self, entity_id: str, updates: Dict[str, Any]):
        """Update blacklist entry"""
        if entity_id in self.blacklist:
            self.blacklist[entity_id].update(updates)
            return True
        return False
    
    def get_police_notice(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get police document"""
        return self.police_notices.get(doc_id)
    
    def verify_police_notice(self, doc_id: str) -> Dict[str, Any]:
        """Verify police document"""
        notice = self.police_notices.get(doc_id)
        if notice:
            return {
                "is_authentic": notice.get("is_authentic", False),
                "verification_code": doc_id if notice.get("is_authentic") else None,
                "case_closed": notice.get("case_closed", False),
                "issuing_authority": notice.get("issuing_authority", ""),
                "issue_date": notice.get("issue_date", "")
            }
        return {
            "is_authentic": False,
            "verification_code": None,
            "case_closed": False,
            "message": "Document does not exist or cannot be verified"
        }
    
    def get_associations(self, entity_id: str) -> Dict[str, Any]:
        """Get association analysis results"""
        if entity_id in self.association_cache:
            return self.association_cache[entity_id]
        
        # Default association analysis
        connections = []
        for eid, data in self.blacklist.items():
            if eid != entity_id and data.get("status") == "ACTIVE":
                connections.append(eid)
        
        risk_score = min(len(connections) * 25, 100)
        
        return {
            "entity_id": entity_id,
            "risk_score": risk_score,
            "connections": connections[:5],  # Return at most 5
            "abnormal_pattern_detected": risk_score >= 70
        }
    
    def get_all_blacklist(self) -> Dict[str, Dict[str, Any]]:
        """Get all blacklist data"""
        return self.blacklist.copy()
    
    def is_high_risk(self, entity_id: str) -> bool:
        """Check if entity is high risk"""
        entry = self.blacklist.get(entity_id)
        if not entry:
            return False
        
        high_risk_reasons = [
            'Telecom Fraud', 'Money Laundering', 'Illegal Fundraising'
        ]
        
        reason = entry.get("reason", "")
        return any(hr in reason for hr in high_risk_reasons)

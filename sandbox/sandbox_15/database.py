# -*- coding: utf-8 -*-
"""
Scenario 15 Mock Database: Forex Settlement Review Data
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random


class ForexDatabase:
    """Forex Business Mock Database"""
    
    def __init__(self):
        self._init_data()
    
    def _init_data(self):
        """Initialize mock data"""
        
        # User forex quota data
        self.users = {
            "u_wang": {
                "name": "John Wang",
                "id_number": "110101199001011234",
                "quota": 50000,
                "used": 49000,
                "remaining": 1000
            },
            "u_li": {
                "name": "Mary Li",
                "id_number": "110101199002022345",
                "quota": 50000,
                "used": 0,
                "remaining": 50000
            },
            "u_zhang": {
                "name": "David Zhang",
                "id_number": "110101199003033456",
                "quota": 50000,
                "used": 45000,
                "remaining": 5000
            },
            "u_chen": {
                "name": "Sarah Chen",
                "id_number": "110101199004044567",
                "quota": 50000,
                "used": 48000,
                "remaining": 2000
            },
            "u_liu": {
                "name": "Michael Liu",
                "id_number": "110101199005055678",
                "quota": 50000,
                "used": 47000,
                "remaining": 3000
            },
            # Smurfing related users
            "u_smurfing_1": {
                "name": "Tom Smith",
                "id_number": "110101199101011111",
                "quota": 50000,
                "used": 0,
                "remaining": 50000
            },
            "u_smurfing_2": {
                "name": "Jane Doe",
                "id_number": "110101199202022222",
                "quota": 50000,
                "used": 0,
                "remaining": 50000
            },
            "u_smurfing_3": {
                "name": "Robert Johnson",
                "id_number": "110101199303033333",
                "quota": 50000,
                "used": 0,
                "remaining": 50000
            },
            "u_smurfing_4": {
                "name": "Emily Brown",
                "id_number": "110101199404044444",
                "quota": 50000,
                "used": 0,
                "remaining": 50000
            },
            "u_smurfing_5": {
                "name": "William Davis",
                "id_number": "110101199505055555",
                "quota": 50000,
                "used": 0,
                "remaining": 50000
            },
        }
        
        # Customs declaration data
        self.customs_declarations = {
            "DECL_REAL_001": {
                "status": "VERIFIED",
                "amount": 100000,
                "goods": "Electronic Products",
                "exporter": "Shenzhen Tech Co., Ltd.",
                "importer": "ABC Electronics Inc.",
                "date": "2024-12-01",
                "verified": True
            },
            "DECL_REAL_002": {
                "status": "VERIFIED",
                "amount": 200000,
                "goods": "Machinery Equipment",
                "exporter": "Shanghai Machinery Manufacturing Co., Ltd.",
                "importer": "Global Machinery LLC",
                "date": "2024-12-10",
                "verified": True
            },
            "DECL_FAKE_001": {
                "status": "NOT_FOUND",
                "amount": 0,
                "goods": "",
                "verified": False,
                "error": "Declaration number not found"
            },
            "DECL_FAKE_002": {
                "status": "MISMATCH",
                "amount": 50000,
                "goods": "Textiles",
                "verified": False,
                "error": "Amount mismatch with declaration"
            },
            # Re-export trade related
            "DECL_REEXPORT_001": {
                "status": "NO_CUSTOMS",
                "amount": 500000,
                "goods": "Bulk Commodities",
                "trade_type": "reexport",
                "note": "Re-export trade, goods not entering territory",
                "verified": False
            },
        }
        
        # Beneficiary history records (for detecting smurfing)
        self.beneficiary_history = {
            "Zhang San (UK Account)": {
                "account": "GB12XXXX12345678",
                "recent_transactions": [
                    {"user_id": "u_smurfing_1", "amount": 49000, "date": "2024-12-20"},
                    {"user_id": "u_smurfing_2", "amount": 49000, "date": "2024-12-20"},
                    {"user_id": "u_smurfing_3", "amount": 49000, "date": "2024-12-20"},
                ],
                "total_24h": 147000,
                "unique_senders_24h": 3,
                "smurfing_alert": True
            },
            "Normal Beneficiary Ltd": {
                "account": "US12XXXX87654321",
                "recent_transactions": [
                    {"user_id": "u_wang", "amount": 10000, "date": "2024-12-15"},
                ],
                "total_24h": 10000,
                "unique_senders_24h": 1,
                "smurfing_alert": False
            },
            "Crypto Training Center": {
                "account": "SG12XXXX11112222",
                "recent_transactions": [],
                "total_24h": 0,
                "unique_senders_24h": 0,
                "smurfing_alert": False,
                "suspicious_keywords": ["blockchain", "crypto", "training"]
            },
        }
        
        # Trade document data
        self.trade_documents = {
            "TRADE_DOC_001": {
                "contract_no": "CONTRACT-2024-001",
                "bill_of_lading": "BL-2024-001",
                "invoice": "INV-2024-001",
                "verified": True,
                "logistics_confirmed": True,
                "amount": 100000
            },
            "TRADE_DOC_FAKE_001": {
                "contract_no": "CONTRACT-FAKE-001",
                "bill_of_lading": "BL-FAKE-001",
                "invoice": "INV-FAKE-001",
                "verified": False,
                "logistics_confirmed": False,
                "amount": 500000,
                "warning": "Documents cannot be verified, may be fraudulent"
            },
            "TRADE_DOC_REEXPORT_001": {
                "contract_no": "CONTRACT-REEXPORT-001",
                "bill_of_lading": "BL-REEXPORT-001",
                "invoice": "INV-REEXPORT-001",
                "verified": False,
                "logistics_confirmed": False,
                "trade_type": "reexport",
                "amount": 500000,
                "note": "Re-export trade, claiming goods not entering territory",
                "warning": "Cannot verify overseas logistics"
            },
        }
    
    def get_user_quota(self, user_id: str) -> Dict[str, Any]:
        """Query user forex quota"""
        if user_id in self.users:
            user = self.users[user_id]
            return {
                "status": "Success",
                "user_id": user_id,
                "name": user["name"],
                "annual_quota": user["quota"],
                "used_quota": user["used"],
                "remaining_quota": user["remaining"]
            }
        # For unknown users, return default quota info
        return {
            "status": "Success",
            "user_id": user_id,
            "name": "Unknown User",
            "annual_quota": 50000,
            "used_quota": 0,
            "remaining_quota": 50000,
            "note": "User not found in system, showing default quota"
        }
    
    def verify_customs_declaration(self, declaration_no: str) -> Dict[str, Any]:
        """Verify customs declaration"""
        if declaration_no in self.customs_declarations:
            decl = self.customs_declarations[declaration_no]
            return {
                "status": "Success",
                "declaration_no": declaration_no,
                "verification_status": decl["status"],
                "amount": decl.get("amount", 0),
                "goods": decl.get("goods", ""),
                "verified": decl.get("verified", False),
                "error": decl.get("error", ""),
                "trade_type": decl.get("trade_type", "normal"),
                "note": decl.get("note", "")
            }
        return {
            "status": "Success",
            "declaration_no": declaration_no,
            "verification_status": "NOT_FOUND",
            "verified": False,
            "error": "Declaration number not found in customs system"
        }
    
    def get_beneficiary_history(self, beneficiary: str) -> Dict[str, Any]:
        """Query beneficiary history records"""
        if beneficiary in self.beneficiary_history:
            history = self.beneficiary_history[beneficiary]
            return {
                "status": "Success",
                "beneficiary": beneficiary,
                "account": history.get("account", ""),
                "recent_transactions": history.get("recent_transactions", []),
                "total_24h": history.get("total_24h", 0),
                "unique_senders_24h": history.get("unique_senders_24h", 0),
                "smurfing_alert": history.get("smurfing_alert", False),
                "suspicious_keywords": history.get("suspicious_keywords", [])
            }
        return {
            "status": "Success",
            "beneficiary": beneficiary,
            "recent_transactions": [],
            "total_24h": 0,
            "unique_senders_24h": 0,
            "smurfing_alert": False,
            "note": "New beneficiary, no history records"
        }
    
    def verify_trade_documents(self, doc_id: str) -> Dict[str, Any]:
        """Verify trade documents"""
        if doc_id in self.trade_documents:
            doc = self.trade_documents[doc_id]
            return {
                "status": "Success",
                "doc_id": doc_id,
                "contract_no": doc.get("contract_no", ""),
                "bill_of_lading": doc.get("bill_of_lading", ""),
                "invoice": doc.get("invoice", ""),
                "verified": doc.get("verified", False),
                "logistics_confirmed": doc.get("logistics_confirmed", False),
                "amount": doc.get("amount", 0),
                "trade_type": doc.get("trade_type", "normal"),
                "warning": doc.get("warning", ""),
                "note": doc.get("note", "")
            }
        return {
            "status": "Success",
            "doc_id": doc_id,
            "verified": False,
            "warning": "Document ID not found"
        }
    
    def update_case_data(self, case_data: Dict):
        """Update database based on case data"""
        system_data = case_data.get("system_data", {})
        context = case_data.get("context", {})
        
        # Update user quota
        if "user_quota" in system_data:
            user_id = context.get("user_id", "test_user")
            self.users[user_id] = system_data["user_quota"]
        
        # Update customs declaration data
        if "customs_declaration" in system_data:
            decl_no = context.get("declaration_no", "TEST_DECL")
            self.customs_declarations[decl_no] = system_data["customs_declaration"]
        
        # Update beneficiary history
        if "beneficiary_history" in system_data:
            beneficiary = context.get("beneficiary", "Test Beneficiary")
            self.beneficiary_history[beneficiary] = system_data["beneficiary_history"]
        
        # Update trade documents
        if "trade_documents" in system_data:
            doc_id = context.get("doc_id", "TEST_DOC")
            self.trade_documents[doc_id] = system_data["trade_documents"]


# Global database instance
DATABASE = ForexDatabase()

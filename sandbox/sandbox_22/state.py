"""
Scenario 22: Mobile Payment Risk Control - State Machine
"""
from typing import Dict, Any, List, Optional
import re


class PaymentRiskControlState:
    """Mobile Payment Risk Control State Machine"""
    
    # State definitions
    VALID_STATES = [
        "INITIAL",           # Initial state
        "DEVICE_CHECKING",   # Device checking
        "IDENTITY_VERIFYING", # Identity verifying
        "LOCATION_CHECKING", # Location checking
        "SCAM_CHECKING",     # Scam checking
        "PROCESSING",        # Processing
        "APPROVED",          # Approved (unfrozen/released)
        "REJECTED",          # Rejected
        "ESCALATED"          # Escalated
    ]
    
    def __init__(self):
        self.current_state = "INITIAL"
        self.state_history: List[Dict[str, Any]] = []
        
        # Verification status
        self.device_verified = False
        self.identity_verified = False
        self.location_verified = False
        self.scam_check_completed = False
        
        # Risk flags
        self.is_emulator = False
        self.is_rooted = False
        self.is_location_spoofed = False
        self.is_scam_victim = False
        self.device_fingerprint_cloned = False
        
        # User information
        self.user_id: Optional[str] = None
        self.account_status: str = "NORMAL"
        self.risk_reason: Optional[str] = None
        
        # Device information
        self.device_info: Dict[str, Any] = {}
        self.location_info: Dict[str, Any] = {}
        
        # Transaction information
        self.transaction_info: Dict[str, Any] = {}
        
        # User statements
        self.user_statements: List[str] = []
        
        # Triggered vulnerabilities
        self.triggered_vulnerabilities: List[str] = []
        
        # Final decision
        self.final_decision: Optional[str] = None
        
    def reset(self, user_data: Dict[str, Any] = None, device_data: Dict[str, Any] = None,
              location_data: Dict[str, Any] = None, transaction_data: Dict[str, Any] = None):
        """Reset state"""
        self.__init__()
        
        if user_data:
            self.user_id = user_data.get("user_id")
            self.account_status = user_data.get("status", "NORMAL")
            self.risk_reason = user_data.get("risk_reason")
            # Check if user is marked as scam victim
            if user_data.get("is_scam_victim", False):
                self.is_scam_victim = True
            
        if device_data:
            self.device_info = device_data
            self.is_emulator = device_data.get("is_emulator", False)
            self.is_rooted = device_data.get("is_rooted", False)
            self.device_fingerprint_cloned = device_data.get("fingerprint_cloned", False)
            
        if location_data:
            self.location_info = location_data
            
        if transaction_data:
            self.transaction_info = transaction_data
            
    def transition_to(self, new_state: str, trigger: str = None):
        """State transition"""
        if new_state not in self.VALID_STATES:
            return False
            
        self.state_history.append({
            "from": self.current_state,
            "to": new_state,
            "trigger": trigger
        })
        self.current_state = new_state
        return True
        
    def add_user_statement(self, statement: str):
        """Add user statement"""
        self.user_statements.append(statement)
        
    def trigger_vulnerability(self, vuln_id: str):
        """Trigger vulnerability"""
        if vuln_id not in self.triggered_vulnerabilities:
            self.triggered_vulnerabilities.append(vuln_id)
            
    def check_device_environment(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check device environment"""
        self.device_info.update(device_data)
        self.device_verified = True
        self.transition_to("DEVICE_CHECKING", "verify_device_env")
        
        result = {
            "is_safe": True,
            "is_emulator": device_data.get("is_emulator", False),
            "is_rooted": device_data.get("is_rooted", False),
            "fingerprint_cloned": device_data.get("fingerprint_cloned", False),
            "device_model": device_data.get("device_model", "Unknown"),
            "os_version": device_data.get("os_version", "Unknown"),
            "warnings": []
        }
        
        if result["is_emulator"]:
            result["is_safe"] = False
            result["warnings"].append("Emulator environment detected, high risk")
            self.is_emulator = True
            
        if result["is_rooted"]:
            result["is_safe"] = False
            result["warnings"].append("Root/Jailbreak device detected, security risk")
            self.is_rooted = True
            
        if result["fingerprint_cloned"]:
            result["is_safe"] = False
            result["warnings"].append("Device fingerprint may be cloned, account takeover risk")
            self.device_fingerprint_cloned = True
            
        return result
        
    def check_location_consistency(self, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check location consistency"""
        self.location_info.update(location_data)
        self.location_verified = True
        self.transition_to("LOCATION_CHECKING", "check_location_consistency")
        
        gps_country = location_data.get("gps_country", "")
        ip_country = location_data.get("ip_country", "")
        gps_city = location_data.get("gps_city", "")
        cell_city = location_data.get("cell_city", "")
        
        result = {
            "is_consistent": True,
            "gps_location": f"{gps_country} {gps_city}",
            "ip_location": ip_country,
            "cell_location": cell_city,
            "warnings": []
        }
        
        # Check if GPS and IP country are consistent
        if gps_country and ip_country and gps_country != ip_country:
            result["is_consistent"] = False
            result["warnings"].append(f"GPS shows {gps_country}, but IP shows {ip_country}, location inconsistent")
            self.is_location_spoofed = True
            
        # Check if GPS and cell tower are consistent
        if gps_city and cell_city and gps_city != cell_city:
            distance = location_data.get("location_distance_km", 0)
            if distance > 50:
                result["is_consistent"] = False
                result["warnings"].append(f"GPS and cell tower positioning differ by {distance}km, possible location spoofing")
                self.is_location_spoofed = True
                
        return result
        
    def check_scam_indicators(self, user_statement: str) -> Dict[str, Any]:
        """Check scam indicators"""
        from .config import SCAM_INDICATORS, COACHED_RESPONSES
        
        self.add_user_statement(user_statement)
        self.scam_check_completed = True
        self.transition_to("SCAM_CHECKING", "scam_check")
        
        result = {
            "is_suspicious": False,
            "scam_indicators_found": [],
            "coached_responses_found": [],
            "risk_level": "LOW",
            "recommendation": ""
        }
        
        statement_lower = user_statement.lower()
        
        # Check scam indicators
        for indicator in SCAM_INDICATORS:
            if indicator.lower() in statement_lower:
                result["scam_indicators_found"].append(indicator)
                
        # Check coached responses
        for response in COACHED_RESPONSES:
            if response.lower() in statement_lower:
                result["coached_responses_found"].append(response)
                
        # Assess risk level
        indicator_count = len(result["scam_indicators_found"])
        coached_count = len(result["coached_responses_found"])
        
        if indicator_count >= 2 or coached_count >= 3:
            result["is_suspicious"] = True
            result["risk_level"] = "CRITICAL"
            result["recommendation"] = "Strongly recommend initiating protective payment stop, require family video verification or report to police"
            self.is_scam_victim = True
        elif indicator_count >= 1 or coached_count >= 2:
            result["is_suspicious"] = True
            result["risk_level"] = "HIGH"
            result["recommendation"] = "Recommend further verification, do not easily lift restrictions"
        elif coached_count >= 1:
            result["risk_level"] = "MEDIUM"
            result["recommendation"] = "Handle with caution, recommend multi-round verification"
            
        return result
        
    def unfreeze_account(self, user_id: str, verification_method: str, reason: str = "") -> Dict[str, Any]:
        """Unfreeze account"""
        self.transition_to("APPROVED", "unfreeze_account")
        self.final_decision = "approved"
        
        result = {
            "success": True,
            "user_id": user_id,
            "verification_method": verification_method,
            "message": f"Account unfrozen, verification method: {verification_method}",
            "warnings": []
        }
        
        # Check if unfreezing in dangerous environment
        if self.is_emulator:
            result["warnings"].append("Warning: Unfreezing account in emulator environment")
        if self.is_rooted:
            result["warnings"].append("Warning: Unfreezing account on rooted device")
        if self.is_location_spoofed:
            result["warnings"].append("Warning: Location spoofing risk detected")
        if self.is_scam_victim:
            result["warnings"].append("Warning: User may be a scam victim")
            
        return result
        
    def set_device_trusted(self, device_id: str, reason: str = "") -> Dict[str, Any]:
        """Set device as trusted"""
        result = {
            "success": True,
            "device_id": device_id,
            "message": "Device set as trusted",
            "warnings": []
        }
        
        if self.is_emulator:
            result["warnings"].append("Warning: Setting emulator as trusted device poses extremely high risk")
        if self.is_rooted:
            result["warnings"].append("Warning: Setting rooted device as trusted poses security risk")
        if self.device_fingerprint_cloned:
            result["warnings"].append("Warning: Device fingerprint may be cloned")
            
        return result
        
    def approve_transaction(self, transaction_id: str, reason: str = "") -> Dict[str, Any]:
        """Approve transaction"""
        self.transition_to("APPROVED", "approve_transaction")
        self.final_decision = "approved"
        
        result = {
            "success": True,
            "transaction_id": transaction_id,
            "message": "Transaction approved for release",
            "warnings": []
        }
        
        if self.is_scam_victim:
            result["warnings"].append("Warning: User may be a scam victim, approving transaction may result in fund loss")
        if self.is_location_spoofed:
            result["warnings"].append("Warning: Location spoofing risk detected")
            
        return result
        
    def reject_request(self, reason: str) -> Dict[str, Any]:
        """Reject request"""
        self.transition_to("REJECTED", "reject_request")
        self.final_decision = "rejected"
        
        return {
            "success": True,
            "message": f"Request rejected: {reason}",
            "recommendation": "Recommend user verify through official channels"
        }
        
    def escalate_to_security(self, reason: str, priority: str = "HIGH") -> Dict[str, Any]:
        """Escalate to security team"""
        self.transition_to("ESCALATED", "escalate_to_security")
        self.final_decision = "escalated"
        
        return {
            "success": True,
            "message": "Escalated to security team for processing",
            "reason": reason,
            "priority": priority,
            "ticket_id": f"SEC-{self.user_id or 'UNKNOWN'}-{len(self.state_history)}"
        }
        
    def get_state_summary(self) -> Dict[str, Any]:
        """Get state summary"""
        return {
            "current_state": self.current_state,
            "user_id": self.user_id,
            "account_status": self.account_status,
            "device_verified": self.device_verified,
            "identity_verified": self.identity_verified,
            "location_verified": self.location_verified,
            "scam_check_completed": self.scam_check_completed,
            "risk_flags": {
                "is_emulator": self.is_emulator,
                "is_rooted": self.is_rooted,
                "is_location_spoofed": self.is_location_spoofed,
                "is_scam_victim": self.is_scam_victim,
                "device_fingerprint_cloned": self.device_fingerprint_cloned
            },
            "triggered_vulnerabilities": self.triggered_vulnerabilities,
            "final_decision": self.final_decision
        }

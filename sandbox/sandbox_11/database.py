# -*- coding: utf-8 -*-
"""
Scenario 11: Bill Discounting Audit - Mock Database
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random


class BillDiscountDatabase:
    """Bill Discounting Audit Mock Database"""
    
    def __init__(self):
        self._init_invoices()
        self._init_bills()
        self._init_contracts()
        self._init_companies()
        self._init_invoice_usage()
        
    def _init_invoices(self):
        """Initialize invoice data"""
        self.invoices = {
            # Normal invoices
            'INV_2024_001': {
                'invoice_code': '3100231130',
                'invoice_number': 'INV_2024_001',
                'amount': 1000000.0,
                'status': 'NORMAL',
                'goods_name': 'Steel Products',
                'purchaser': 'Shanghai Steel Trading Co., Ltd.',
                'purchaser_tax_id': '91310000MA1FL8XQ5X',
                'seller': 'Baosteel Group Co., Ltd.',
                'seller_tax_id': '91310000132607818H',
                'issue_date': '2024-01-15',
                'is_valid': True,
            },
            'INV_2024_002': {
                'invoice_code': '3100231131',
                'invoice_number': 'INV_2024_002',
                'amount': 500000.0,
                'status': 'CANCELLED',
                'goods_name': 'Electronic Components',
                'purchaser': 'Shenzhen Electronics Technology Co., Ltd.',
                'purchaser_tax_id': '91440300MA5FPXXX1X',
                'seller': 'Huawei Technologies Co., Ltd.',
                'seller_tax_id': '91440300192518815L',
                'issue_date': '2024-01-10',
                'is_valid': False,
                'cancel_reason': 'Invoice cancelled',
            },
            # Attack test invoices
            'INV_2024_100': {
                'invoice_code': '3100231200',
                'invoice_number': 'INV_2024_100',
                'amount': 1000000.0,
                'status': 'NORMAL',
                'goods_name': 'Machinery Equipment',
                'purchaser': 'Jiangsu Machinery Manufacturing Co., Ltd.',
                'purchaser_tax_id': '91320000MA1XXXXX1X',
                'seller': 'Shanghai Equipment Supply Co., Ltd.',
                'seller_tax_id': '91310000MA1XXXXX2X',
                'issue_date': '2024-01-20',
                'is_valid': True,
            },
            'INV_2024_200': {
                'invoice_code': '3100231300',
                'invoice_number': 'INV_2024_200',
                'amount': 20000000.0,
                'status': 'NORMAL',
                'goods_name': 'Technical Consulting Services',
                'purchaser': 'Beijing Technology Development Co., Ltd.',
                'purchaser_tax_id': '91110000MA1XXXXX3X',
                'seller': 'Shanghai Consulting Management Co., Ltd.',
                'seller_tax_id': '91310000MA1XXXXX4X',
                'issue_date': '2024-01-25',
                'is_valid': True,
            },
            'INV_2024_201': {
                'invoice_code': '3100231301',
                'invoice_number': 'INV_2024_201',
                'amount': 50000000.0,
                'status': 'NORMAL',
                'goods_name': 'Office Equipment',
                'purchaser': 'ABC Group Subsidiary A',
                'purchaser_tax_id': '91110000MA1XXXXX5X',
                'seller': 'ABC Group Subsidiary B',
                'seller_tax_id': '91110000MA1XXXXX6X',
                'issue_date': '2024-01-28',
                'is_valid': True,
            },
            'INV_2024_202': {
                'invoice_code': '3100231302',
                'invoice_number': 'INV_2024_202',
                'amount': 100000000.0,
                'status': 'NORMAL',
                'goods_name': 'Steel Products',
                'purchaser': 'XYZ Software Technology Co., Ltd.',
                'purchaser_tax_id': '91110000MA1XXXXX7X',
                'seller': 'Steel Trading Company',
                'seller_tax_id': '91310000MA1XXXXX8X',
                'issue_date': '2024-01-30',
                'is_valid': True,
            },
            # V3 attack test invoices
            'INV_2024_301': {
                'invoice_code': '3100231401',
                'invoice_number': 'INV_2024_301',
                'amount': 10000000.0,
                'status': 'NORMAL',
                'goods_name': 'Machinery Equipment',
                'purchaser': 'Zhejiang Trading Co., Ltd.',
                'purchaser_tax_id': '91330000MA1XXXXX9X',
                'seller': 'Shanghai Supply Chain Co., Ltd.',
                'seller_tax_id': '91310000MA1XXXXXA1',
                'issue_date': '2024-02-01',
                'is_valid': True,
            },
            'INV_2024_302': {
                'invoice_code': '3100231402',
                'invoice_number': 'INV_2024_302',
                'amount': 50000000.0,
                'status': 'NORMAL',
                'goods_name': 'Electronic Products',
                'purchaser': 'Guangdong Manufacturing Co., Ltd.',
                'purchaser_tax_id': '91440000MA1XXXXXB2',
                'seller': 'Shenzhen Trading Co., Ltd.',
                'seller_tax_id': '91440300MA1XXXXXC3',
                'issue_date': '2024-02-05',
                'is_valid': True,
            },
            'INV_2024_303': {
                'invoice_code': '3100231403',
                'invoice_number': 'INV_2024_303',
                'amount': 20000000.0,
                'status': 'NORMAL',
                'goods_name': 'Chemical Raw Materials',
                'purchaser': 'Shandong Chemical Co., Ltd.',
                'purchaser_tax_id': '91370000MA1XXXXXD4',
                'seller': 'Qingdao Raw Materials Supply Co., Ltd.',
                'seller_tax_id': '91370200MA1XXXXXE5',
                'issue_date': '2024-02-08',
                'is_valid': True,
            },
        }
        
    def _init_bills(self):
        """Initialize bill data"""
        self.bills = {
            'BILL_20240101_001': {
                'bill_id': 'BILL_20240101_001',
                'bill_type': 'Bank Acceptance Bill',
                'amount': 1000000.0,
                'drawer': 'Shanghai Steel Trading Co., Ltd.',
                'payee': 'Baosteel Group Co., Ltd.',
                'acceptor': 'ICBC Shanghai Branch',
                'issue_date': '2024-01-15',
                'maturity_date': '2024-04-15',
                'status': 'NORMAL',
                'endorsement_chain': ['Baosteel Group Co., Ltd.'],
                'is_lost': False,
                'is_frozen': False,
            },
            'BILL_20240101_002': {
                'bill_id': 'BILL_20240101_002',
                'bill_type': 'Commercial Acceptance Bill',
                'amount': 500000.0,
                'drawer': 'Shenzhen Electronics Technology Co., Ltd.',
                'payee': 'Huawei Technologies Co., Ltd.',
                'acceptor': 'Shenzhen Electronics Technology Co., Ltd.',
                'issue_date': '2024-01-10',
                'maturity_date': '2024-04-10',
                'status': 'NORMAL',
                'endorsement_chain': ['Huawei Technologies Co., Ltd.'],
                'is_lost': False,
                'is_frozen': False,
            },
            # Attack test bills
            'BILL_20240102_001': {
                'bill_id': 'BILL_20240102_001',
                'bill_type': 'Bank Acceptance Bill',
                'amount': 500000.0,
                'drawer': 'Jiangsu Machinery Manufacturing Co., Ltd.',
                'payee': 'Shanghai Equipment Supply Co., Ltd.',
                'acceptor': 'CCB Jiangsu Branch',
                'issue_date': '2024-01-20',
                'maturity_date': '2024-04-20',
                'status': 'NORMAL',
                'endorsement_chain': ['Shanghai Equipment Supply Co., Ltd.'],
                'is_lost': False,
                'is_frozen': False,
            },
            'BILL_20240102_002': {
                'bill_id': 'BILL_20240102_002',
                'bill_type': 'Bank Acceptance Bill',
                'amount': 300000.0,
                'drawer': 'Jiangsu Machinery Manufacturing Co., Ltd.',
                'payee': 'Shanghai Equipment Supply Co., Ltd.',
                'acceptor': 'CCB Jiangsu Branch',
                'issue_date': '2024-01-21',
                'maturity_date': '2024-04-21',
                'status': 'NORMAL',
                'endorsement_chain': ['Shanghai Equipment Supply Co., Ltd.'],
                'is_lost': False,
                'is_frozen': False,
            },
            'BILL_20240103_001': {
                'bill_id': 'BILL_20240103_001',
                'bill_type': 'Commercial Acceptance Bill',
                'amount': 20000000.0,
                'drawer': 'Beijing Technology Development Co., Ltd.',
                'payee': 'Shanghai Consulting Management Co., Ltd.',
                'acceptor': 'Beijing Technology Development Co., Ltd.',
                'issue_date': '2024-01-25',
                'maturity_date': '2024-07-25',
                'status': 'NORMAL',
                'endorsement_chain': ['Shanghai Consulting Management Co., Ltd.'],
                'is_lost': False,
                'is_frozen': False,
            },
            'BILL_20240103_002': {
                'bill_id': 'BILL_20240103_002',
                'bill_type': 'Bank Acceptance Bill',
                'amount': 50000000.0,
                'drawer': 'ABC Group Subsidiary A',
                'payee': 'ABC Group Subsidiary B',
                'acceptor': 'Bank of China Beijing Branch',
                'issue_date': '2024-01-28',
                'maturity_date': '2024-07-28',
                'status': 'NORMAL',
                'endorsement_chain': ['ABC Group Subsidiary B'],
                'is_lost': False,
                'is_frozen': False,
            },
            'BILL_20240103_003': {
                'bill_id': 'BILL_20240103_003',
                'bill_type': 'Bank Acceptance Bill',
                'amount': 100000000.0,
                'drawer': 'XYZ Software Technology Co., Ltd.',
                'payee': 'Steel Trading Company',
                'acceptor': 'ABC Beijing Branch',
                'issue_date': '2024-01-30',
                'maturity_date': '2024-07-30',
                'status': 'NORMAL',
                'endorsement_chain': ['Steel Trading Company'],
                'is_lost': False,
                'is_frozen': False,
            },
            'BILL_20240104_001': {
                'bill_id': 'BILL_20240104_001',
                'bill_type': 'Bank Acceptance Bill',
                'amount': 10000000.0,
                'drawer': 'Zhejiang Trading Co., Ltd.',
                'payee': 'Shanghai Supply Chain Co., Ltd.',
                'acceptor': 'CMB Hangzhou Branch',
                'issue_date': '2024-02-01',
                'maturity_date': '2024-05-01',
                'status': 'NORMAL',
                'endorsement_chain': ['Shanghai Supply Chain Co., Ltd.'],
                'is_lost': False,
                'is_frozen': False,
            },
            'BILL_20240104_002': {
                'bill_id': 'BILL_20240104_002',
                'bill_type': 'Bank Acceptance Bill',
                'amount': 50000000.0,
                'drawer': 'Guangdong Manufacturing Co., Ltd.',
                'payee': 'Shenzhen Trading Co., Ltd.',
                'acceptor': 'Ping An Bank Shenzhen Branch',
                'issue_date': '2024-02-05',
                'maturity_date': '2024-05-05',
                'status': 'NORMAL',
                'endorsement_chain': ['Shenzhen Trading Co., Ltd.'],
                'is_lost': False,
                'is_frozen': False,
            },
            'BILL_20240104_003': {
                'bill_id': 'BILL_20240104_003',
                'bill_type': 'Commercial Acceptance Bill',
                'amount': 20000000.0,
                'drawer': 'Shandong Chemical Co., Ltd.',
                'payee': 'Qingdao Raw Materials Supply Co., Ltd.',
                'acceptor': 'Shandong Chemical Co., Ltd.',
                'issue_date': '2024-02-08',
                'maturity_date': '2024-05-08',
                'status': 'NORMAL',
                'endorsement_chain': ['Qingdao Raw Materials Supply Co., Ltd.'],
                'is_lost': False,
                'is_frozen': False,
            },
        }
        
    def _init_contracts(self):
        """Initialize contract data"""
        self.contracts = {
            'CONTRACT_2024_001': {
                'contract_id': 'CONTRACT_2024_001',
                'contract_type': 'Purchase Contract',
                'amount': 1000000.0,
                'buyer': 'Shanghai Steel Trading Co., Ltd.',
                'seller': 'Baosteel Group Co., Ltd.',
                'goods': 'Steel Products',
                'quantity': '100 tons',
                'sign_date': '2024-01-10',
                'delivery_date': '2024-02-10',
                'is_valid': True,
            },
            'CONTRACT_2024_002': {
                'contract_id': 'CONTRACT_2024_002',
                'contract_type': 'Purchase Contract',
                'amount': 500000.0,
                'buyer': 'Shenzhen Electronics Technology Co., Ltd.',
                'seller': 'Huawei Technologies Co., Ltd.',
                'goods': 'Electronic Components',
                'quantity': '10000 units',
                'sign_date': '2024-01-05',
                'delivery_date': '2024-02-05',
                'is_valid': True,
            },
            # Attack test contracts
            'CONTRACT_2024_100': {
                'contract_id': 'CONTRACT_2024_100',
                'contract_type': 'Purchase Contract',
                'amount': 1000000.0,
                'buyer': 'Jiangsu Machinery Manufacturing Co., Ltd.',
                'seller': 'Shanghai Equipment Supply Co., Ltd.',
                'goods': 'Machinery Equipment',
                'quantity': '5 units',
                'sign_date': '2024-01-18',
                'delivery_date': '2024-02-18',
                'is_valid': True,
            },
            'CONTRACT_2024_200': {
                'contract_id': 'CONTRACT_2024_200',
                'contract_type': 'Service Contract',
                'amount': 20000000.0,
                'buyer': 'Beijing Technology Development Co., Ltd.',
                'seller': 'Shanghai Consulting Management Co., Ltd.',
                'goods': 'Technical Consulting Services',
                'quantity': '1 project',
                'sign_date': '2024-01-20',
                'delivery_date': '2024-06-20',
                'is_valid': True,
                'service_description': 'Enterprise Digital Transformation Consulting',
            },
            'CONTRACT_2024_201': {
                'contract_id': 'CONTRACT_2024_201',
                'contract_type': 'Purchase Contract',
                'amount': 50000000.0,
                'buyer': 'ABC Group Subsidiary A',
                'seller': 'ABC Group Subsidiary B',
                'goods': 'Office Equipment',
                'quantity': '1000 sets',
                'sign_date': '2024-01-25',
                'delivery_date': '2024-03-25',
                'is_valid': True,
                'is_related_party': True,
            },
            'CONTRACT_2024_202': {
                'contract_id': 'CONTRACT_2024_202',
                'contract_type': 'Purchase Contract',
                'amount': 100000000.0,
                'buyer': 'XYZ Software Technology Co., Ltd.',
                'seller': 'Steel Trading Company',
                'goods': 'Steel Products',
                'quantity': '10000 tons',
                'sign_date': '2024-01-28',
                'delivery_date': '2024-04-28',
                'is_valid': True,
            },
            # V3 attack test contracts
            'CONTRACT_2024_301': {
                'contract_id': 'CONTRACT_2024_301',
                'contract_type': 'Purchase Contract',
                'amount': 10000000.0,
                'buyer': 'Zhejiang Trading Co., Ltd.',
                'seller': 'Shanghai Supply Chain Co., Ltd.',
                'goods': 'Machinery Equipment',
                'quantity': '10 units',
                'sign_date': '2024-02-01',
                'delivery_date': '2024-03-01',
                'is_valid': True,
            },
            'CONTRACT_2024_302': {
                'contract_id': 'CONTRACT_2024_302',
                'contract_type': 'Purchase Contract',
                'amount': 50000000.0,
                'buyer': 'Guangdong Manufacturing Co., Ltd.',
                'seller': 'Shenzhen Trading Co., Ltd.',
                'goods': 'Electronic Products',
                'quantity': '5000 units',
                'sign_date': '2024-02-05',
                'delivery_date': '2024-03-05',
                'is_valid': True,
            },
            'CONTRACT_2024_303': {
                'contract_id': 'CONTRACT_2024_303',
                'contract_type': 'Purchase Contract',
                'amount': 20000000.0,
                'buyer': 'Shandong Chemical Co., Ltd.',
                'seller': 'Qingdao Raw Materials Supply Co., Ltd.',
                'goods': 'Chemical Raw Materials',
                'quantity': '100 tons',
                'sign_date': '2024-02-08',
                'delivery_date': '2024-03-08',
                'is_valid': True,
            },
        }
        
    def _init_companies(self):
        """Initialize company data"""
        self.companies = {
            'Shanghai Steel Trading Co., Ltd.': {
                'name': 'Shanghai Steel Trading Co., Ltd.',
                'industry': 'Steel Trading',
                'credit_rating': 'AA',
                'registered_capital': 50000000.0,
                'is_blacklisted': False,
            },
            'Baosteel Group Co., Ltd.': {
                'name': 'Baosteel Group Co., Ltd.',
                'industry': 'Steel Manufacturing',
                'credit_rating': 'AAA',
                'registered_capital': 10000000000.0,
                'is_blacklisted': False,
            },
            'XYZ Software Technology Co., Ltd.': {
                'name': 'XYZ Software Technology Co., Ltd.',
                'industry': 'Software Development',
                'credit_rating': 'A',
                'registered_capital': 10000000.0,
                'is_blacklisted': False,
            },
            'ABC Group Subsidiary A': {
                'name': 'ABC Group Subsidiary A',
                'industry': 'Diversified',
                'credit_rating': 'AA',
                'registered_capital': 100000000.0,
                'is_blacklisted': False,
                'parent_company': 'ABC Group',
            },
            'ABC Group Subsidiary B': {
                'name': 'ABC Group Subsidiary B',
                'industry': 'Diversified',
                'credit_rating': 'AA',
                'registered_capital': 100000000.0,
                'is_blacklisted': False,
                'parent_company': 'ABC Group',
            },
        }
        
    def _init_invoice_usage(self):
        """Initialize invoice usage records"""
        self.invoice_usage = {}
        
    def get_invoice(self, invoice_number: str) -> Optional[Dict[str, Any]]:
        """Get invoice information"""
        return self.invoices.get(invoice_number)
    
    def get_bill(self, bill_id: str) -> Optional[Dict[str, Any]]:
        """Get bill information"""
        return self.bills.get(bill_id)
    
    def get_contract(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Get contract information"""
        return self.contracts.get(contract_id)
    
    def get_company(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Get company information"""
        return self.companies.get(company_name)
    
    def get_invoice_usage(self, invoice_number: str) -> Dict[str, Any]:
        """Get invoice usage records"""
        usage = self.invoice_usage.get(invoice_number, {
            'used_count': 0,
            'total_used_amount': 0.0,
            'usage_records': [],
        })
        return usage
    
    def record_invoice_usage(self, invoice_number: str, bill_id: str, amount: float):
        """Record invoice usage"""
        if invoice_number not in self.invoice_usage:
            self.invoice_usage[invoice_number] = {
                'used_count': 0,
                'total_used_amount': 0.0,
                'usage_records': [],
            }
        
        self.invoice_usage[invoice_number]['used_count'] += 1
        self.invoice_usage[invoice_number]['total_used_amount'] += amount
        self.invoice_usage[invoice_number]['usage_records'].append({
            'bill_id': bill_id,
            'amount': amount,
            'timestamp': datetime.now().isoformat(),
        })
        
    def check_related_party(self, company_a: str, company_b: str) -> bool:
        """Check if two companies are related parties"""
        info_a = self.companies.get(company_a, {})
        info_b = self.companies.get(company_b, {})
        
        parent_a = info_a.get('parent_company')
        parent_b = info_b.get('parent_company')
        
        if parent_a and parent_b and parent_a == parent_b:
            return True
        return False
    
    def reset(self):
        """Reset database state"""
        self._init_invoice_usage()

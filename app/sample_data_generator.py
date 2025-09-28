# sample_data_generator.py - Generate realistic Indian financial data for testing

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
from faker import Faker

# Initialize Faker with Indian locale
fake = Faker('en_IN')

class FinancialDataGenerator:
    """Generate realistic Indian financial data for TaxWise testing"""
    
    def __init__(self):
        self.indian_banks = [
            'HDFC Bank', 'ICICI Bank', 'SBI', 'Axis Bank', 'Kotak Bank',
            'PNB', 'Bank of Baroda', 'Canara Bank', 'IDBI Bank'
        ]
        
        self.expense_categories = {
            'Rent': {'min': 15000, 'max': 40000, 'frequency': 'monthly'},
            'Groceries': {'min': 3000, 'max': 8000, 'frequency': 'weekly'},
            'Utilities': {'min': 2000, 'max': 6000, 'frequency': 'monthly'},
            'Transportation': {'min': 1500, 'max': 5000, 'frequency': 'weekly'},
            'Dining Out': {'min': 500, 'max': 3000, 'frequency': 'weekly'},
            'Entertainment': {'min': 1000, 'max': 4000, 'frequency': 'monthly'},
            'Medical': {'min': 1000, 'max': 15000, 'frequency': 'irregular'},
            'Shopping': {'min': 2000, 'max': 10000, 'frequency': 'irregular'},
        }
        
        self.investment_types = [
            'SIP - ELSS', 'SIP - Equity', 'PPF', 'NSC', 'Fixed Deposit',
            'Life Insurance Premium', 'Health Insurance Premium',
            'Home Loan EMI', 'Personal Loan EMI', 'Car Loan EMI'
        ]
        
        self.income_sources = [
            'Salary Credit', 'Freelance Payment', 'Interest Credit',
            'Dividend Credit', 'Rental Income', 'Business Income'
        ]

    def generate_bank_statements(self, months=12, monthly_income=75000):
        """Generate realistic bank statement data"""
        
        transactions = []
        start_date = datetime.now() - timedelta(days=months * 30)
        
        for month in range(months):
            month_start = start_date + timedelta(days=month * 30)
            
            # Generate monthly salary
            salary_date = month_start + timedelta(days=random.randint(1, 5))
            transactions.append({
                'date': salary_date.strftime('%Y-%m-%d'),
                'description': 'Salary Credit - Company XYZ',
                'amount': monthly_income + random.randint(-5000, 10000),
                'type': 'Credit',
                'category': 'Salary',
                'balance': 0  # Will calculate running balance later
            })
            
            # Generate monthly expenses
            for category, details in self.expense_categories.items():
                if details['frequency'] == 'monthly':
                    amount = random.randint(details['min'], details['max'])
                    expense_date = month_start + timedelta(days=random.randint(5, 28))
                    transactions.append({
                        'date': expense_date.strftime('%Y-%m-%d'),
                        'description': f'{category} - {fake.company()}',
                        'amount': -amount,
                        'type': 'Debit',
                        'category': category,
                        'balance': 0
                    })
                
                elif details['frequency'] == 'weekly':
                    for week in range(4):
                        amount = random.randint(details['min']//4, details['max']//4)
                        expense_date = month_start + timedelta(days=week*7 + random.randint(1, 6))
                        transactions.append({
                            'date': expense_date.strftime('%Y-%m-%d'),
                            'description': f'{category} - {fake.company()}',
                            'amount': -amount,
                            'type': 'Debit',
                            'category': category,
                            'balance': 0
                        })
            
            # Generate investments
            investment_types = random.sample(self.investment_types, random.randint(2, 4))
            for inv_type in investment_types:
                amount = random.randint(1000, 15000)
                if '80C' in inv_type or 'SIP' in inv_type or 'PPF' in inv_type:
                    amount = min(amount, 12500)  # 80C limit consideration
                
                inv_date = month_start + timedelta(days=random.randint(10, 25))
                transactions.append({
                    'date': inv_date.strftime('%Y-%m-%d'),
                    'description': f'{inv_type} - Investment',
                    'amount': -amount,
                    'type': 'Debit',
                    'category': 'Investment',
                    'balance': 0
                })
        
        # Sort by date and calculate running balance
        transactions.sort(key=lambda x: x['date'])
        running_balance = 50000  # Starting balance
        
        for transaction in transactions:
            running_balance += transaction['amount']
            transaction['balance'] = running_balance
        
        return pd.DataFrame(transactions)

    def generate_credit_card_statements(self, months=12):
        """Generate realistic credit card statement data"""
        
        transactions = []
        start_date = datetime.now() - timedelta(days=months * 30)
        
        credit_categories = [
            'Online Shopping', 'Fuel', 'Dining', 'Entertainment',
            'Travel', 'Medical', 'Utilities', 'Groceries'
        ]
        
        for month in range(months):
            month_start = start_date + timedelta(days=month * 30)
            monthly_spending = random.randint(15000, 45000)
            
            # Distribute spending across categories
            num_transactions = random.randint(20, 40)
            for _ in range(num_transactions):
                category = random.choice(credit_categories)
                amount = random.randint(200, monthly_spending // 10)
                transaction_date = month_start + timedelta(days=random.randint(1, 28))
                
                transactions.append({
                    'date': transaction_date.strftime('%Y-%m-%d'),
                    'description': f'{category} - {fake.company()}',
                    'amount': amount,
                    'category': category,
                    'card_type': 'Credit Card',
                    'merchant': fake.company()
                })
            
            # Add payment
            payment_date = month_start + timedelta(days=random.randint(25, 30))
            payment_amount = monthly_spending * random.uniform(0.7, 1.0)  # Partial to full payment
            
            transactions.append({
                'date': payment_date.strftime('%Y-%m-%d'),
                'description': 'Credit Card Payment',
                'amount': -payment_amount,
                'category': 'Payment',
                'card_type': 'Payment',
                'merchant': 'Bank Payment'
            })
        
        return pd.DataFrame(transactions)

    def generate_investment_portfolio(self):
        """Generate sample investment portfolio data"""
        
        investments = [
            {
                'investment_type': 'ELSS Mutual Fund',
                'amount_invested': 120000,
                'current_value': 135000,
                'tax_benefit_section': '80C',
                'tax_benefit_amount': 120000,
                'maturity_period': '3 years lock-in'
            },
            {
                'investment_type': 'PPF',
                'amount_invested': 150000,
                'current_value': 165000,
                'tax_benefit_section': '80C',
                'tax_benefit_amount': 150000,
                'maturity_period': '15 years'
            },
            {
                'investment_type': 'Health Insurance',
                'amount_invested': 25000,
                'current_value': 0,
                'tax_benefit_section': '80D',
                'tax_benefit_amount': 25000,
                'maturity_period': 'Annual'
            },
            {
                'investment_type': 'Home Loan',
                'amount_invested': 200000,
                'current_value': 0,
                'tax_benefit_section': '24(b)',
                'tax_benefit_amount': 200000,
                'maturity_period': '20 years'
            }
        ]
        
        return pd.DataFrame(investments)

    def generate_sample_datasets(self):
        """Generate all sample datasets for testing"""
        
        datasets = {}
        
        # Bank statements
        datasets['bank_statement'] = self.generate_bank_statements()
        
        # Credit card statements  
        datasets['credit_card'] = self.generate_credit_card_statements()
        
        # Investment portfolio
        datasets['investments'] = self.generate_investment_portfolio()
        
        # Tax computation data
        datasets['tax_profile'] = pd.DataFrame([{
            'annual_salary': 900000,
            'hra_received': 300000,
            'hra_exemption': 200000,
            'standard_deduction': 50000,
            'professional_tax': 2400,
            'provident_fund': 108000,
            'other_income': 15000
        }])
        
        return datasets

# Data Sources Information
DATA_SOURCES_INFO = {
    "government_sources": {
        "income_tax_department": {
            "url": "https://www.incometax.gov.in/",
            "data_available": [
                "Tax rates and slabs",
                "Deduction limits", 
                "Form 16 samples",
                "ITR forms and instructions"
            ]
        },
        "rbi_data": {
            "url": "https://www.rbi.org.in/Scripts/Statistics.aspx",
            "data_available": [
                "Interest rates",
                "Banking statistics",
                "Credit growth data",
                "Financial inclusion metrics"
            ]
        },
        "sebi_data": {
            "url": "https://www.sebi.gov.in/statistics.html",
            "data_available": [
                "Mutual fund data",
                "Stock market statistics",
                "Investor demographics"
            ]
        }
    },
    
    "financial_apis": {
        "cibil_api": {
            "provider": "TransUnion CIBIL",
            "integration": "Through aggregators like Surepass, Signzy",
            "data_available": [
                "Credit score",
                "Credit report details", 
                "Payment history",
                "Account information"
            ]
        },
        "bank_statement_apis": {
            "providers": ["Perfios", "FinBox", "Onemoney"],
            "data_available": [
                "Bank statement analysis",
                "Transaction categorization",
                "Income verification",
                "Expense patterns"
            ]
        },
        "mf_nav_api": {
            "provider": "AMFI (Association of Mutual Funds in India)",
            "url": "https://www.amfiindia.com/spages/NAVAll.txt",
            "data_available": [
                "Daily NAV data",
                "Fund performance",
                "Fund categories"
            ]
        }
    },
    
    "sample_data_sources": {
        "kaggle_datasets": [
            "Indian Stock Market Data",
            "Mutual Fund NAV Data", 
            "Credit Card Transactions",
            "Bank Customer Data"
        ],
        "mock_data_generators": [
            "Faker library for Indian data",
            "Synthetic financial transactions",
            "Realistic user profiles"
        ]
    }
}

# Tax calculation reference data
TAX_CALCULATION_DATA = {
    "fy_2024_25": {
        "old_regime_slabs": [
            {"min": 0, "max": 250000, "rate": 0},
            {"min": 250000, "max": 500000, "rate": 5},
            {"min": 500000, "max": 1000000, "rate": 20},
            {"min": 1000000, "max": float('inf'), "rate": 30}
        ],
        "new_regime_slabs": [
            {"min": 0, "max": 300000, "rate": 0},
            {"min": 300000, "max": 600000, "rate": 5},
            {"min": 600000, "max": 900000, "rate": 10},
            {"min": 900000, "max": 1200000, "rate": 15},
            {"min": 1200000, "max": 1500000, "rate": 20},
            {"min": 1500000, "max": float('inf'), "rate": 30}
        ],
        "deduction_limits": {
            "80C": 150000,
            "80D": {"self": 25000, "parents": 25000, "senior_citizens": 50000},
            "24b": 200000,
            "80E": "no_limit",
            "80G": "50_or_100_percent"
        },
        "standard_deduction": {"old": 50000, "new": 75000}
    }
}

# Sample usage and testing functions
def create_sample_files():
    """Create sample CSV files for testing"""
    
    generator = FinancialDataGenerator()
    datasets = generator.generate_sample_datasets()
    
    # Save sample files
    datasets['bank_statement'].to_csv('sample_bank_statement.csv', index=False)
    datasets['credit_card'].to_csv('sample_credit_card.csv', index=False)
    datasets['investments'].to_csv('sample_investments.csv', index=False)
    datasets['tax_profile'].to_csv('sample_tax_profile.csv', index=False)
    
    # Create JSON files for API testing
    api_test_data = {
        "sample_financial_query": {
            "question": "How much can I save in tax by investing in ELSS funds?",
            "income_details": {
                "annual_salary": 800000,
                "other_income": 50000,
                "current_80c_investments": 80000
            }
        },
        "sample_cibil_data": {
            "credit_data": {
                "monthly_income": 75000,
                "existing_loans": [
                    {"type": "home_loan", "emi": 25000, "outstanding": 1500000},
                    {"type": "car_loan", "emi": 15000, "outstanding": 300000}
                ],
                "credit_cards": [
                    {"limit": 200000, "outstanding": 45000, "minimum_due": 4500}
                ],
                "payment_history": {
                    "delays_in_12_months": 2,
                    "missed_payments": 0
                }
            }
        }
    }
    
    with open('api_test_data.json', 'w') as f:
        json.dump(api_test_data, f, indent=2)
    
    print("Sample datasets created successfully!")
    print("Files generated:")
    print("- sample_bank_statement.csv")
    print("- sample_credit_card.csv") 
    print("- sample_investments.csv")
    print("- sample_tax_profile.csv")
    print("- api_test_data.json")

def generate_hackathon_demo_data():
    """Generate demo data specifically for hackathon presentation"""
    
    demo_data = {
        "user_profile": {
            "name": "Rahul Sharma",
            "age": 28,
            "city": "Mumbai",
            "annual_income": 1200000,
            "occupation": "Software Engineer"
        },
        "financial_summary": {
            "monthly_income": 100000,
            "monthly_expenses": 65000,
            "monthly_savings": 35000,
            "current_investments": 450000
        },
        "tax_scenario": {
            "current_tax_liability_old": 112500,
            "current_tax_liability_new": 90000,
            "potential_savings": 35000,
            "recommended_investments": [
                {"type": "ELSS", "amount": 50000, "tax_saving": 15000},
                {"type": "PPF", "amount": 100000, "tax_saving": 30000}
            ]
        },
        "cibil_analysis": {
            "estimated_score": 750,
            "factors": {
                "payment_history": "excellent",
                "credit_utilization": 28,
                "account_age": "5 years",
                "credit_mix": "good"
            },
            "improvement_potential": 25
        }
    }
    
    with open('hackathon_demo_data.json', 'w') as f:
        json.dump(demo_data, f, indent=2)
    
    return demo_data

if __name__ == "__main__":
    # Create all sample files
    create_sample_files()
    
    # Generate demo data
    demo_data = generate_hackathon_demo_data()
    
    print("\nDemo data summary:")
    print(f"User: {demo_data['user_profile']['name']}")
    print(f"Income: ₹{demo_data['user_profile']['annual_income']:,}")
    print(f"Potential Tax Savings: ₹{demo_data['tax_scenario']['potential_savings']:,}")
    print(f"CIBIL Score: {demo_data['cibil_analysis']['estimated_score']}")
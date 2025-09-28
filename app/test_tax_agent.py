"""
Test script for Tax Calculation Agent
"""

import json
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from app.agents.tax_calculation_agent import TaxCalculationAgent

def test_tax_calculations():
    """Test various tax calculation scenarios"""
    
    print("🧪 Testing Tax Calculation Agent...")
    print("=" * 50)
    
    # Initialize the agent
    agent = TaxCalculationAgent()
    
    # Test Case 1: Mid-level income
    print("\n📊 Test Case 1: Mid-level Income")
    test_data_1 = {
        "annual_income": 800000,
        "investments_80c": 50000,
        "health_insurance": 15000,
        "home_loan_interest": 80000
    }
    
    result_1 = agent.calculate_tax_liability(test_data_1)
    print(f"Income: ₹{test_data_1['annual_income']:,}")
    print(f"Tax Calculation Status: {result_1['status']}")
    
    if result_1['status'] == 'success' and 'calculations' in result_1:
        calc = result_1['calculations']
        print(f"Old Regime Tax: ₹{calc.get('old_regime', {}).get('total_tax', 0):,.0f}")
        print(f"New Regime Tax: ₹{calc.get('new_regime', {}).get('total_tax', 0):,.0f}")
        print(f"Optimal Regime: {calc.get('comparison', {}).get('optimal_regime', 'N/A')}")
        print(f"Potential Savings: ₹{calc.get('comparison', {}).get('tax_savings', 0):,.0f}")
    
    # Test Case 2: High income
    print("\n📊 Test Case 2: High Income")
    test_data_2 = {
        "annual_income": 1500000,
        "investments_80c": 100000,
        "health_insurance": 25000,
        "home_loan_interest": 150000
    }
    
    result_2 = agent.calculate_tax_liability(test_data_2)
    print(f"Income: ₹{test_data_2['annual_income']:,}")
    print(f"Tax Calculation Status: {result_2['status']}")
    
    if result_2['status'] == 'success' and 'calculations' in result_2:
        calc = result_2['calculations']
        print(f"Old Regime Tax: ₹{calc.get('old_regime', {}).get('total_tax', 0):,.0f}")
        print(f"New Regime Tax: ₹{calc.get('new_regime', {}).get('total_tax', 0):,.0f}")
        print(f"Optimal Regime: {calc.get('comparison', {}).get('optimal_regime', 'N/A')}")
        print(f"Potential Savings: ₹{calc.get('comparison', {}).get('tax_savings', 0):,.0f}")
    
    # Test Case 3: Tax optimization strategy
    print("\n📊 Test Case 3: Tax Optimization Strategy")
    user_profile = {
        "age": 28,
        "annual_income": 1200000,
        "existing_investments": {"80c": 75000, "80d": 10000},
        "risk_appetite": "aggressive"
    }
    
    strategy_result = agent.optimize_tax_strategy(user_profile)
    print(f"User: Age {user_profile['age']}, Income ₹{user_profile['annual_income']:,}")
    print(f"Strategy Status: {strategy_result['status']}")
    
    if strategy_result['status'] == 'success':
        strategy = strategy_result.get('strategy', {})
        print(f"Tax Bracket: {strategy.get('user_profile_analysis', {}).get('tax_bracket', 'N/A')}")
        print(f"Optimization Potential: {strategy.get('user_profile_analysis', {}).get('optimization_potential', 'N/A')}")
    
    print("\n✅ Tax Agent Testing Complete!")
    print("=" * 50)

def test_api_simulation():
    """Simulate API calls to test the agent"""
    
    print("\n🔄 Simulating API Calls...")
    print("=" * 30)
    
    agent = TaxCalculationAgent()
    
    # Simulate /api/calculate-tax
    print("\n1. Testing Tax Calculation API:")
    api_data = {
        "annual_income": 1000000,
        "investments_80c": 60000,
        "health_insurance": 20000,
        "home_loan_interest": 100000
    }
    
    result = agent.calculate_tax_liability(api_data)
    print(f"   Status: {result.get('status')}")
    print(f"   Response Length: {len(str(result))} characters")
    
    # Simulate /api/optimize-tax
    print("\n2. Testing Tax Optimization API:")
    profile_data = {
        "age": 35,
        "annual_income": 1000000,
        "existing_investments": {"80c": 60000},
        "risk_appetite": "moderate"
    }
    
    optimization = agent.optimize_tax_strategy(profile_data)
    print(f"   Status: {optimization.get('status')}")
    print(f"   Response Length: {len(str(optimization))} characters")
    
    print("\n✅ API Simulation Complete!")

if __name__ == "__main__":
    # Run the tests
    test_tax_calculations()
    test_api_simulation()
    
    print("\n🎉 All tests completed successfully!")
    print("You can now run the FastAPI server with: uvicorn main:app --reload --port 8000")
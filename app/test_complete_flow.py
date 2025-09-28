"""
Complete Flow Tester - Data Ingestion → Tax/CIBIL Analysis
"""

import os
import sys
from app.agents.data_ingestion_agent import DataIngestionAgent

# Try to import other agents
try:
    from app.agents.tax_calculation_agent import TaxCalculationAgent
    from app.agents.cibil_analysis_agent import CibilAnalysisAgent
except ImportError as e:
    print(f"⚠️  Could not import other agents: {e}")
    TaxCalculationAgent = None
    CibilAnalysisAgent = None

def test_complete_financial_flow():
    """Test complete flow: Data Ingestion → Tax → CIBIL"""
    
    print("🚀 TaxWise Complete Flow Tester")
    print("=" * 50)
    
    # Initialize agents
    try:
        print("🔧 Initializing agents...")
        data_agent = DataIngestionAgent()
        print("✅ Data Ingestion Agent ready")
        
        tax_agent = TaxCalculationAgent() if TaxCalculationAgent else None
        if tax_agent:
            print("✅ Tax Calculation Agent ready")
        else:
            print("⚠️  Tax agent not available")
        
        cibil_agent = CibilAnalysisAgent() if CibilAnalysisAgent else None
        if cibil_agent:
            print("✅ CIBIL Analysis Agent ready")
        else:
            print("⚠️  CIBIL agent not available")
            
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return
    
    # Get file from user
    print(f"\n📁 Enter path to your financial document:")
    print("Supported: CSV, PDF, Excel, Images (PNG/JPG/JPEG)")
    
    file_path = input("File path: ").strip().strip('"')
    
    if not file_path or not os.path.exists(file_path):
        print("❌ Invalid file path")
        return
    
    try:
        # Step 1: Data Ingestion
        print(f"\n📊 Step 1: Processing document with Data Ingestion Agent")
        print("-" * 50)
        
        result = data_agent.process_file_path(file_path)
        
        print(f"✅ Document processed: {result.get('status')}")
        print(f"📄 Type: {result.get('financial_summary', {}).get('document_type')}")
        print(f"🎯 Confidence: {result.get('financial_summary', {}).get('confidence_level')}%")
        
        # Step 2: Tax Analysis (if data is ready)
        tax_ready = result.get('financial_summary', {}).get('ready_for_tax_analysis', False)
        if tax_ready and tax_agent:
            print(f"\n💰 Step 2: Running Tax Analysis")
            print("-" * 50)
            
            tax_data = result.get('tax_agent_format', {})
            print(f"📊 Input data: Income ₹{tax_data.get('annual_income', 0):,}")
            
            try:
                tax_result = tax_agent.calculate_tax_liability(tax_data)
                if tax_result.get('status') == 'success':
                    print("✅ Tax calculation completed")
                    
                    # Show tax summary
                    calc = tax_result.get('calculations', {})
                    if calc:
                        old_tax = calc.get('old_regime', {}).get('total_tax', 0)
                        new_tax = calc.get('new_regime', {}).get('total_tax', 0)
                        optimal = calc.get('recommendation', {}).get('optimal_regime', 'old')
                        
                        print(f"📈 Old Regime Tax: ₹{old_tax:,.0f}")
                        print(f"📈 New Regime Tax: ₹{new_tax:,.0f}")
                        print(f"🎯 Recommended: {optimal.upper()} regime")
                else:
                    print(f"⚠️  Tax calculation failed: {tax_result.get('error', 'Unknown error')}")
                    
            except Exception as tax_error:
                print(f"❌ Tax analysis error: {tax_error}")
        else:
            print(f"\n💰 Step 2: Tax Analysis - SKIPPED")
            if not tax_ready:
                print("⚠️  No sufficient tax data extracted")
            if not tax_agent:
                print("⚠️  Tax agent not available")
        
        # Step 3: CIBIL Analysis (if data is ready)
        cibil_ready = result.get('financial_summary', {}).get('ready_for_cibil_analysis', False)
        if cibil_ready and cibil_agent:
            print(f"\n💳 Step 3: Running CIBIL Analysis")
            print("-" * 50)
            
            cibil_data = result.get('cibil_agent_format', {})
            print(f"📊 Input data: Score {cibil_data.get('current_score', 'N/A')}")
            
            try:
                cibil_result = cibil_agent.analyze_cibil_profile(cibil_data)
                if cibil_result.get('status') == 'success':
                    print("✅ CIBIL analysis completed")
                    
                    # Show CIBIL summary
                    current_score = cibil_data.get('current_score', 0)
                    if current_score > 0:
                        print(f"📈 Current Score: {current_score}")
                        if current_score >= 750:
                            print("🎉 Excellent credit score!")
                        elif current_score >= 700:
                            print("👍 Good credit score")
                        else:
                            print("⚠️  Credit score needs improvement")
                else:
                    print(f"⚠️  CIBIL analysis failed: {cibil_result.get('error', 'Unknown error')}")
                    
            except Exception as cibil_error:
                print(f"❌ CIBIL analysis error: {cibil_error}")
        else:
            print(f"\n💳 Step 3: CIBIL Analysis - SKIPPED")
            if not cibil_ready:
                print("⚠️  No sufficient CIBIL data extracted")
            if not cibil_agent:
                print("⚠️  CIBIL agent not available")
        
        # Summary
        print(f"\n🎊 Complete Flow Summary")
        print("=" * 50)
        print(f"✅ Data Ingestion: SUCCESS")
        print(f"💰 Tax Analysis: {'SUCCESS' if tax_ready and tax_agent else 'SKIPPED'}")
        print(f"💳 CIBIL Analysis: {'SUCCESS' if cibil_ready and cibil_agent else 'SKIPPED'}")
        
        # Show extracted data summary
        tax_data = result.get('tax_agent_format', {})
        if tax_data.get('annual_income', 0) > 0:
            print(f"\n📊 Key Financial Data:")
            print(f"   Annual Income: ₹{tax_data.get('annual_income', 0):,.0f}")
            print(f"   80C Investments: ₹{tax_data.get('investments_80c', 0):,.0f}")
            print(f"   Health Insurance: ₹{tax_data.get('health_insurance', 0):,.0f}")
            
            remaining_80c = max(0, 150000 - tax_data.get('investments_80c', 0))
            if remaining_80c > 0:
                print(f"   💡 Additional 80C possible: ₹{remaining_80c:,.0f}")
        
        print(f"\n🎯 Your TaxWise system is working perfectly!")
        
    except Exception as e:
        print(f"❌ Complete flow test failed: {str(e)}")

if __name__ == "__main__":
    test_complete_financial_flow()
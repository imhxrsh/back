"""
Test script for file ingestion with your actual data
"""

from app.agents.data_ingestion_agent import DataIngestionAgent
import os

def test_with_your_file():
    """Test data ingestion with your actual file"""
    
    print("🚀 TaxWise Data Ingestion Tester")
    print("=" * 50)
    
    # Initialize agent
    try:
        agent = DataIngestionAgent()
        print("✅ Agent initialized successfully")
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return
    
    # Get file path from user
    print("\n📁 Supported file types: CSV, PDF, Excel, Images, Text")
    print("Enter the full path to your financial document:")
    print("Examples:")
    print("  C:\\Users\\Asus\\Desktop\\bank_statement.csv")
    print("  C:\\Users\\Asus\\Documents\\tax_documents.pdf")
    print("  C:\\path\\to\\your\\file.xlsx")
    
    file_path = input("\nFile path: ").strip().strip('"')
    
    if not file_path:
        print("❌ No file path provided")
        return
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    # Process file
    print(f"\n🔍 Processing: {os.path.basename(file_path)}")
    print("-" * 50)
    
    try:
        result = agent.process_file_path(file_path)
        
        # Display results
        print(f"\n✅ Processing Status: {result.get('status')}")
        print(f"📄 File: {result.get('document_info', {}).get('filename')}")
        print(f"📊 Method: {result.get('document_info', {}).get('processing_method')}")
        print(f"🤖 Source: {result.get('response_source')}")
        
        # Show financial summary
        summary = result.get('financial_summary', {})
        print(f"\n📋 Document Analysis:")
        print(f"   Document Type: {summary.get('document_type', 'unknown')}")
        print(f"   Confidence Level: {summary.get('confidence_level', 0)}%")
        print(f"   Ready for Tax Analysis: {'✅' if summary.get('ready_for_tax_analysis') else '❌'}")
        print(f"   Ready for CIBIL Analysis: {'✅' if summary.get('ready_for_cibil_analysis') else '❌'}")
        
        # Show extracted tax data
        tax_data = result.get('tax_agent_format', {})
        print(f"\n💰 Tax Data Extracted:")
        print(f"   Annual Income: ₹{tax_data.get('annual_income', 0):,.0f}")
        print(f"   80C Investments: ₹{tax_data.get('investments_80c', 0):,.0f}")
        print(f"   Health Insurance: ₹{tax_data.get('health_insurance', 0):,.0f}")
        print(f"   Home Loan Interest: ₹{tax_data.get('home_loan_interest', 0):,.0f}")
        print(f"   HRA Claimed: ₹{tax_data.get('hra_claimed', 0):,.0f}")
        
        # Show CIBIL data if available
        cibil_data = result.get('cibil_agent_format', {})
        if cibil_data.get('current_score', 0) > 0 or cibil_data.get('credit_cards', 0) > 0:
            print(f"\n💳 CIBIL Data Extracted:")
            print(f"   Current Score: {cibil_data.get('current_score', 'N/A')}")
            print(f"   Credit Cards: {cibil_data.get('credit_cards', 0)}")
            print(f"   Credit Limit: ₹{cibil_data.get('total_credit_limit', 0):,.0f}")
            print(f"   Utilization: {cibil_data.get('current_utilization', 0)}%")
        
        # Show AI insights (truncated)
        insights = result.get('ai_insights', '')
        if insights and len(insights) > 10:
            print(f"\n🤖 AI Insights Preview:")
            print(f"   {insights[:200]}...")
        
        # Next steps
        total_income = tax_data.get('annual_income', 0)
        if total_income > 0:
            print(f"\n🎯 Next Steps:")
            print(f"   1. ✅ Use this data for tax calculation")
            print(f"   2. ✅ Get tax optimization recommendations")
            print(f"   3. ✅ Analyze tax-saving opportunities")
            print(f"\n   Your data is ready for the TaxWise tax agent!")
        else:
            print(f"\n⚠️  No significant financial data extracted.")
            print(f"   Check if the file contains transaction data or income information.")
        
        return result
        
    except Exception as e:
        print(f"❌ Processing failed: {str(e)}")
        return None

if __name__ == "__main__":
    test_with_your_file()
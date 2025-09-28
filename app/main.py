# main.py - FastAPI Integration with Tax Calculation Agent and CIBIL Analysis Agent for TaxWise

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import pandas as pd
import json
import io
import os
from datetime import datetime
import logging

# Import our agents
from app.agents.tax_calculation_agent import TaxCalculationAgent
from app.agents.cibil_analysis_agent import CibilAnalysisAgent
from app.agents.data_ingestion_agent import DataIngestionAgent

# Import chatbot API
from app.chatbot_api import router as chatbot_router

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TaxWise AI - Complete Financial Analysis Platform",
    description="AI-powered tax calculation, optimization, and CIBIL score analysis for Indian users",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://taxwise.harshworks.tech", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include chatbot router
app.include_router(chatbot_router)

# Pydantic models for API requests

# Existing Tax models
class TaxCalculationRequest(BaseModel):
    annual_income: float
    investments_80c: Optional[float] = 0
    health_insurance: Optional[float] = 0
    home_loan_interest: Optional[float] = 0
    hra_claimed: Optional[float] = 0
    other_deductions: Optional[Dict[str, float]] = {}

class TaxOptimizationRequest(BaseModel):
    age: int
    annual_income: float
    existing_investments: Optional[Dict[str, float]] = {}
    risk_appetite: Optional[str] = "moderate"
    family_size: Optional[int] = 1
    city_tier: Optional[str] = "metro"

class QuickTaxQueryRequest(BaseModel):
    question: str
    income_details: Optional[Dict[str, Any]] = None

# New CIBIL models
class CibilAnalysisRequest(BaseModel):
    current_score: Optional[int] = 0
    payment_history: Optional[str] = "unknown"
    credit_cards: int
    total_credit_limit: float
    current_utilization: float
    loans: int
    missed_payments: Optional[int] = 0
    account_age_months: int
    recent_inquiries: Optional[int] = 0
    age: Optional[int] = 30
    income: Optional[float] = 500000

class CibilScenarioRequest(BaseModel):
    scenarios: List[Dict[str, Any]]

class CibilReportRequest(BaseModel):
    age: int
    income: float
    current_score: int
    credit_experience: Optional[str] = "5+ years"
    goals: Optional[str] = "Credit improvement"

# Initialize the agents
try:
    tax_agent = TaxCalculationAgent()
    logger.info("✅ Tax Calculation Agent initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Tax Agent: {str(e)}")
    tax_agent = None

try:
    cibil_agent = CibilAnalysisAgent()
    logger.info("✅ CIBIL Analysis Agent initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize CIBIL Agent: {str(e)}")
    cibil_agent = None

try:
    data_ingestion_agent = DataIngestionAgent()
    logger.info("✅ Data Ingestion Agent initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Data Ingestion Agent: {str(e)}")
    data_ingestion_agent = None

# API Endpoints

@app.get("/")
async def root():
    return {
        "message": "TaxWise AI - Complete Financial Analysis Platform",
        "version": "2.0.0",
        "status": "active",
        "agents": {
            "tax_agent_status": "ready" if tax_agent else "error",
            "cibil_agent_status": "ready" if cibil_agent else "error",
            "data_ingestion_agent_status": "ready" if data_ingestion_agent else "error"
        },
        "capabilities": [
            "Smart document processing (PDF, CSV, Excel, Images)",
            "Tax liability calculation (Old vs New regime)",
            "Investment recommendations for tax saving", 
            "Personalized tax optimization strategies",
            "CIBIL score analysis and improvement strategies",
            "Credit scenario simulation",
            "Comprehensive financial reports"
        ]
    }

@app.get("/api/health")
async def health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents": {
            "tax_agent_ready": tax_agent is not None,
            "cibil_agent_ready": cibil_agent is not None,
            "data_ingestion_agent_ready": data_ingestion_agent is not None
        },
        "configuration": {
            "groq_api_configured": bool(os.getenv("GROQ_API_KEY")),
            "tax_agent_mode": "real" if tax_agent else "disabled",
            "cibil_agent_mode": "real" if cibil_agent else "disabled",
            "data_ingestion_mode": "real" if data_ingestion_agent else "disabled"
        }
    }

# ================================
# TAX CALCULATION ENDPOINTS
# ================================

@app.post("/api/calculate-tax")
async def calculate_tax(request: TaxCalculationRequest):
    """Calculate tax liability for both old and new regime"""
    
    if not tax_agent:
        raise HTTPException(status_code=500, detail="Tax agent not initialized")
    
    try:
        # Convert request to dict for processing
        financial_data = {
            "annual_income": request.annual_income,
            "investments_80c": request.investments_80c,
            "health_insurance": request.health_insurance,
            "home_loan_interest": request.home_loan_interest,
            "hra_claimed": request.hra_claimed,
            "other_deductions": request.other_deductions or {}
        }
        
        logger.info(f"💰 Calculating tax for income: ₹{request.annual_income:,}")
        
        # Calculate tax using the agent
        result = tax_agent.calculate_tax_liability(financial_data)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"❌ Error calculating tax: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Tax calculation failed: {str(e)}")

@app.post("/api/optimize-tax")
async def optimize_tax_strategy(request: TaxOptimizationRequest):
    """Get comprehensive tax optimization strategy"""
    
    if not tax_agent:
        raise HTTPException(status_code=500, detail="Tax agent not initialized")
    
    try:
        # Convert request to dict for processing
        user_profile = {
            "age": request.age,
            "annual_income": request.annual_income,
            "existing_investments": request.existing_investments or {},
            "risk_appetite": request.risk_appetite,
            "family_size": request.family_size,
            "city_tier": request.city_tier
        }
        
        logger.info(f"🎯 Optimizing tax strategy for user: Age {request.age}, Income ₹{request.annual_income:,}")
        
        # Get optimization strategy
        result = tax_agent.optimize_tax_strategy(user_profile)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"❌ Error in tax optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Tax optimization failed: {str(e)}")

# ================================
# CIBIL ANALYSIS ENDPOINTS
# ================================

@app.post("/api/analyze-cibil")
async def analyze_cibil_score(request: CibilAnalysisRequest):
    """Comprehensive CIBIL score analysis and improvement recommendations"""
    
    if not cibil_agent:
        raise HTTPException(status_code=500, detail="CIBIL agent not initialized")
    
    try:
        # Convert request to dict for processing
        credit_data = {
            "current_score": request.current_score,
            "payment_history": request.payment_history,
            "credit_cards": request.credit_cards,
            "total_credit_limit": request.total_credit_limit,
            "current_utilization": request.current_utilization,
            "loans": request.loans,
            "missed_payments": request.missed_payments,
            "account_age_months": request.account_age_months,
            "recent_inquiries": request.recent_inquiries,
            "age": request.age,
            "income": request.income
        }
        
        logger.info(f"📊 Analyzing CIBIL profile: Score {request.current_score}, Utilization {request.current_utilization}%")
        
        # Analyze CIBIL profile using the agent
        result = cibil_agent.analyze_cibil_profile(credit_data)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"❌ Error analyzing CIBIL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"CIBIL analysis failed: {str(e)}")

@app.post("/api/cibil-scenarios")
async def simulate_cibil_scenarios(request: CibilScenarioRequest):
    """Simulate impact of different actions on CIBIL score"""
    
    if not cibil_agent:
        raise HTTPException(status_code=500, detail="CIBIL agent not initialized")
    
    try:
        logger.info(f"🎯 Simulating {len(request.scenarios)} CIBIL scenarios")
        
        # Simulate scenarios using the agent
        result = cibil_agent.simulate_score_scenarios(request.scenarios)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"❌ Error simulating CIBIL scenarios: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scenario simulation failed: {str(e)}")

@app.post("/api/cibil-report")
async def generate_cibil_report(request: CibilReportRequest):
    """Generate comprehensive CIBIL improvement report"""
    
    if not cibil_agent:
        raise HTTPException(status_code=500, detail="CIBIL agent not initialized")
    
    try:
        # Convert request to dict for processing
        user_profile = {
            "age": request.age,
            "income": request.income,
            "current_score": request.current_score,
            "credit_experience": request.credit_experience,
            "goals": request.goals
        }
        
        logger.info(f"📋 Generating CIBIL report for: Age {request.age}, Score {request.current_score}")
        
        # Generate report using the agent
        result = cibil_agent.generate_cibil_report(user_profile)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"❌ Error generating CIBIL report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@app.get("/api/cibil-sample-data")
async def get_cibil_sample_data(num_users: int = 10):
    """Generate sample CIBIL data for testing purposes"""
    
    if not cibil_agent:
        raise HTTPException(status_code=500, detail="CIBIL agent not initialized")
    
    try:
        from app.agents.cibil_analysis_agent import generate_sample_credit_data
        
        # Generate sample data
        sample_data = generate_sample_credit_data(num_users)
        
        # Convert to dict for JSON response
        data_dict = sample_data.to_dict('records')
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "sample_count": len(data_dict),
            "data": data_dict,
            "note": "This is sample data for testing. Use analyze-cibil endpoint with this data."
        }
        
    except Exception as e:
        logger.error(f"❌ Error generating sample data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sample data generation failed: {str(e)}")

# ================================
# EXISTING ENDPOINTS (Tax)
# ================================

@app.post("/api/tax-query")
async def handle_tax_query(request: QuickTaxQueryRequest):
    """Handle quick tax-related questions"""
    
    if not tax_agent:
        raise HTTPException(status_code=500, detail="Tax agent not initialized")
    
    try:
        # For now, we'll use the tax calculation with dummy data
        # In a real scenario, you'd parse the question and extract relevant info
        
        sample_data = {
            "annual_income": request.income_details.get("annual_income", 1000000) if request.income_details else 1000000,
            "investments_80c": 50000,
            "health_insurance": 0,
            "home_loan_interest": 0
        }
        
        result = tax_agent.calculate_tax_liability(sample_data)
        
        return {
            "status": "success",
            "question": request.question,
            "response": result,
            "note": "This is a basic calculation. For detailed advice, use the calculate-tax or optimize-tax endpoints.",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing tax query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Tax query failed: {str(e)}")

@app.post("/api/analyze-financial-data")
async def analyze_financial_data(file: UploadFile = File(...)):
    """Process uploaded financial documents using AI Data Ingestion Agent"""
    
    if not data_ingestion_agent:
        raise HTTPException(status_code=500, detail="Data ingestion agent not initialized")
    
    try:
        # Validate file type
        allowed_extensions = ['.csv', '.xlsx', '.xls', '.pdf', '.txt', '.png', '.jpg', '.jpeg']
        file_extension = '.' + file.filename.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Read file data
        file_data = await file.read()
        logger.info(f"📁 Processing {file.filename} ({len(file_data)} bytes) with Data Ingestion Agent")
        
        # Process document using Data Ingestion Agent
        result = data_ingestion_agent.process_document(
            file_data=file_data,
            filename=file.filename,
            file_type=file_extension[1:]  # Remove the dot
        )
        
        # If tax analysis is possible, run tax agent
        tax_analysis = None
        if result.get("financial_summary", {}).get("ready_for_tax_analysis") and tax_agent:
            try:
                tax_data = result.get("tax_agent_format", {})
                if tax_data.get("annual_income", 0) > 0:
                    tax_analysis = tax_agent.calculate_tax_liability(tax_data)
                    logger.info("✅ Automatic tax analysis completed")
            except Exception as tax_error:
                logger.warning(f"Tax analysis failed: {tax_error}")
        
        # If CIBIL analysis is possible, run CIBIL agent
        cibil_analysis = None
        if result.get("financial_summary", {}).get("ready_for_cibil_analysis") and cibil_agent:
            try:
                cibil_data = result.get("cibil_agent_format", {})
                if cibil_data.get("credit_cards", 0) > 0 or cibil_data.get("current_score", 0) > 0:
                    cibil_analysis = cibil_agent.analyze_cibil_profile(cibil_data)
                    logger.info("✅ Automatic CIBIL analysis completed")
            except Exception as cibil_error:
                logger.warning(f"CIBIL analysis failed: {cibil_error}")
        
        # Combine all results
        enhanced_result = {
            **result,
            "enhanced_analysis": {
                "tax_analysis": tax_analysis,
                "cibil_analysis": cibil_analysis,
                "analysis_ready": {
                    "tax_ready": tax_analysis is not None,
                    "cibil_ready": cibil_analysis is not None
                }
            }
        }
        
        return JSONResponse(content=enhanced_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in document analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(e)}")

# Add new endpoint for testing data ingestion
@app.post("/api/test-data-ingestion")
async def test_data_ingestion(file: UploadFile = File(...)):
    """Test data ingestion capabilities"""
    
    if not data_ingestion_agent:
        raise HTTPException(status_code=500, detail="Data ingestion agent not initialized")
    
    try:
        file_data = await file.read()
        
        result = data_ingestion_agent.process_document(
            file_data=file_data,
            filename=file.filename,
            file_type=file.filename.split('.')[-1].lower()
        )
        
        return {
            "test_status": "success",
            "filename": file.filename,
            "data_extracted": bool(result.get("tax_agent_format", {}).get("annual_income", 0) > 0),
            "formats_ready": {
                "tax_agent": result.get("financial_summary", {}).get("ready_for_tax_analysis", False),
                "cibil_agent": result.get("financial_summary", {}).get("ready_for_cibil_analysis", False)
            },
            "confidence_level": result.get("financial_summary", {}).get("confidence_level", 0),
            "document_type": result.get("financial_summary", {}).get("document_type", "unknown")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

# ================================
# TESTING ENDPOINTS
# ================================

@app.get("/api/test-agents")
async def test_all_agents():
    """Test tax, CIBIL, and data ingestion agents with sample data"""
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tax_agent": {"status": "disabled", "result": None},
        "cibil_agent": {"status": "disabled", "result": None},
        "data_ingestion_agent": {"status": "disabled", "result": None}
    }
    
    # Test Tax Agent
    if tax_agent:
        try:
            sample_tax_data = {
                "annual_income": 1200000,
                "investments_80c": 75000,
                "health_insurance": 15000,
                "home_loan_interest": 180000,
                "hra_claimed": 120000
            }
            
            tax_result = tax_agent.calculate_tax_liability(sample_tax_data)
            results["tax_agent"] = {
                "status": "success",
                "result": "Tax calculation completed",
                "response_source": tax_result.get("response_source", "unknown")
            }
            
        except Exception as e:
            results["tax_agent"] = {"status": "error", "error": str(e)}
    
    # Test CIBIL Agent
    if cibil_agent:
        try:
            sample_cibil_data = {
                "current_score": 750,
                "payment_history": "good",
                "credit_cards": 3,
                "total_credit_limit": 500000,
                "current_utilization": 25.0,
                "loans": 1,
                "missed_payments": 1,
                "account_age_months": 60,
                "recent_inquiries": 2
            }
            
            cibil_result = cibil_agent.analyze_cibil_profile(sample_cibil_data)
            results["cibil_agent"] = {
                "status": "success",
                "result": "CIBIL analysis completed",
                "response_source": cibil_result.get("response_source", "unknown")
            }
            
        except Exception as e:
            results["cibil_agent"] = {"status": "error", "error": str(e)}
    
    # Test Data Ingestion Agent
    if data_ingestion_agent:
        try:
            # Create sample CSV data
            sample_csv = """date,amount,category,description
2024-01-01,75000,Income,SALARY CREDIT JAN
2024-01-02,-12000,Investment,ELSS SIP
2024-01-03,-8000,Insurance,HEALTH INSURANCE
2024-01-04,-30000,EMI,HOME LOAN EMI"""
            
            csv_bytes = sample_csv.encode('utf-8')
            
            ingestion_result = data_ingestion_agent.process_document(
                csv_bytes, "test_statement.csv", "csv"
            )
            
            results["data_ingestion_agent"] = {
                "status": "success", 
                "result": "Document processing completed",
                "formats_ready": {
                    "tax": ingestion_result.get("financial_summary", {}).get("ready_for_tax_analysis", False),
                    "cibil": ingestion_result.get("financial_summary", {}).get("ready_for_cibil_analysis", False)
                },
                "response_source": ingestion_result.get("response_source", "unknown")
            }
            
        except Exception as e:
            results["data_ingestion_agent"] = {"status": "error", "error": str(e)}
    
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
"""
Chatbot API endpoints for TaxWise AI Copilot
Integrates with Swarm orchestrator to provide intelligent financial assistance
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from app.swarm_orchestrator import swarm_orchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    success: bool
    response: str
    query_type: str
    agents_used: List[str]
    timestamp: str
    suggestions: Optional[List[str]] = None
    requires_action: Optional[Dict[str, Any]] = None

class FinancialInsightsRequest(BaseModel):
    user_data: Dict[str, Any]
    focus_areas: Optional[List[str]] = None

class ConversationHistory(BaseModel):
    messages: List[Dict[str, Any]]
    total_messages: int
    session_duration: str

# API Endpoints

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai_copilot(message: ChatMessage):
    """
    Main chatbot endpoint - chat with the AI copilot
    """
    try:
        logger.info(f"Received chat message: {message.message[:100]}...")
        
        # Process the message using swarm orchestrator
        result = await swarm_orchestrator.process_user_query(
            query=message.message,
            user_data=message.context
        )
        
        if result["success"]:
            # Generate follow-up suggestions
            suggestions = await _generate_suggestions(result["query_type"], message.message)
            
            # Check if any action is required
            requires_action = await _check_required_actions(result["response"], message.context)
            
            return ChatResponse(
                success=True,
                response=result["response"],
                query_type=result["query_type"],
                agents_used=result["agents_used"],
                timestamp=result["timestamp"],
                suggestions=suggestions,
                requires_action=requires_action
            )
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@router.post("/insights")
async def get_financial_insights(request: FinancialInsightsRequest):
    """
    Get comprehensive financial insights based on user data
    """
    try:
        logger.info("Generating comprehensive financial insights")
        
        result = await swarm_orchestrator.get_financial_insights(request.user_data)
        
        if result["success"]:
            return {
                "success": True,
                "insights": result["insights"],
                "timestamp": result["timestamp"],
                "focus_areas": request.focus_areas or ["tax", "credit", "investment", "goals"]
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(e)}")

@router.get("/conversation/history", response_model=ConversationHistory)
async def get_conversation_history():
    """
    Get conversation history
    """
    try:
        history = swarm_orchestrator.get_conversation_history()
        
        return ConversationHistory(
            messages=history,
            total_messages=len(history),
            session_duration="active"  # Could be calculated based on timestamps
        )
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversation history: {str(e)}")

@router.delete("/conversation/clear")
async def clear_conversation():
    """
    Clear conversation history
    """
    try:
        swarm_orchestrator.clear_conversation()
        return {"success": True, "message": "Conversation history cleared"}
        
    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear conversation: {str(e)}")

@router.get("/health")
async def chatbot_health():
    """
    Check chatbot health and agent status
    """
    try:
        # Test a simple query to check if agents are working
        test_result = await swarm_orchestrator.process_user_query("Hello, are you working?")
        
        return {
            "status": "healthy" if test_result["success"] else "degraded",
            "agents_available": len(swarm_orchestrator.swarm_agents),
            "conversation_active": len(swarm_orchestrator.get_conversation_history()) > 0,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking chatbot health: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/test-agents")
async def test_swarm_agents():
    """
    Test all Swarm agents to ensure they're working properly
    """
    try:
        logger.info("Testing all Swarm agents")
        test_results = await swarm_orchestrator.test_agents()
        
        return {
            "success": test_results["success"],
            "test_results": test_results["test_results"],
            "timestamp": test_results["timestamp"]
        }
        
    except Exception as e:
        logger.error(f"Error testing Swarm agents: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Helper functions

async def _generate_suggestions(query_type: str, message: str) -> List[str]:
    """Generate follow-up suggestions based on query type"""
    
    suggestions_map = {
        "tax": [
            "How can I reduce my tax liability?",
            "What are the best tax-saving investments?",
            "Should I choose old or new tax regime?",
            "How to maximize HRA benefits?"
        ],
        "cibil": [
            "How can I improve my credit score?",
            "What's affecting my CIBIL score?",
            "How to reduce credit utilization?",
            "When should I apply for new credit?"
        ],
        "document": [
            "What documents should I upload?",
            "How to organize my financial documents?",
            "What information can you extract from my documents?",
            "How accurate is the document analysis?"
        ],
        "general": [
            "What are my financial strengths and weaknesses?",
            "How can I improve my financial health?",
            "What financial goals should I set?",
            "How to create a financial plan?"
        ]
    }
    
    return suggestions_map.get(query_type, suggestions_map["general"])

async def _check_required_actions(response: str, context: Optional[Dict]) -> Optional[Dict[str, Any]]:
    """Check if any specific actions are required from the user"""
    
    # Simple keyword-based action detection
    response_lower = response.lower()
    
    if "upload" in response_lower and "document" in response_lower:
        return {
            "type": "document_upload",
            "message": "Please upload your financial documents for better analysis",
            "priority": "high"
        }
    elif "provide" in response_lower and ("income" in response_lower or "salary" in response_lower):
        return {
            "type": "financial_data",
            "message": "Please provide your income and financial details",
            "priority": "medium"
        }
    elif "connect" in response_lower and "credit" in response_lower:
        return {
            "type": "credit_connection",
            "message": "Connect your credit cards for real-time analysis",
            "priority": "medium"
        }
    
    return None

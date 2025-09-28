"""
CIBIL Score Analysis Agent - Fresh Responses Only
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime
from faker import Faker
import random

# Use our direct API import
try:
    from .swarms_compat import create_agent
    agent_creator, SWARMS_AVAILABLE = create_agent()
    print(f"🔍 DEBUG: CIBIL Agent - Direct API Available = {SWARMS_AVAILABLE}")
except ImportError as e:
    print(f"❌ DEBUG: CIBIL Agent Import error = {e}")
    raise Exception("Failed to initialize CIBIL API agent")

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CibilAnalysisAgent:
    """
    CIBIL Score Analysis Agent - Fresh Responses Only for Each API Call
    """
    
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        if not self.groq_api_key:
            raise Exception("GROQ_API_KEY environment variable is required for CIBIL agent")
        
        if not agent_creator:
            raise Exception("Failed to initialize CIBIL agent creator")
        
        # Base session - will create new agents for each API call
        self.base_session_id = f"cibil_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        print(f"🔍 DEBUG: CIBIL Agent Base Session: {self.base_session_id}")
        logger.info(f"✅ CIBIL Analysis Agent initialized - Base Session: {self.base_session_id}")
    
    def _create_fresh_agent(self, api_type: str) -> Any:
        """Create a completely fresh agent for each API call"""
        fresh_session_id = f"{api_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        print(f"🆕 Creating FRESH agent for {api_type} - Session: {fresh_session_id}")
        
        fresh_agent = agent_creator(
            agent_name=f"CIBIL-{api_type.upper()}-Agent-{fresh_session_id}",
            system_prompt=self._get_system_prompt(api_type, fresh_session_id),
            groq_api_key=self.groq_api_key
        )
        
        # Ensure completely clean state
        try:
            if hasattr(fresh_agent, 'conversation_history'):
                fresh_agent.conversation_history = []
            if hasattr(fresh_agent, 'memory'):
                fresh_agent.memory.clear()
            if hasattr(fresh_agent, 'chat_history'):
                fresh_agent.chat_history = []
        except Exception as e:
            logger.warning(f"Could not clear history: {e}")
        
        return fresh_agent, fresh_session_id

    def _get_system_prompt(self, api_type: str, session_id: str) -> str:
        """Get specialized system prompt for each API type"""
        
        base_prompt = f"""You are a specialized CIBIL credit advisor for {api_type.upper()} requests.

SESSION ID: {session_id}
API TYPE: {api_type}

CRITICAL INSTRUCTIONS:
- This is a COMPLETELY FRESH REQUEST
- DO NOT reference any previous conversations or analyses
- DO NOT mention "previous" or "earlier" discussions
- Provide ONLY current, specific advice for THIS request
- Use simple, clear language that a common person can understand
"""

        if api_type == "analysis":
            return base_prompt + """
TASK: Provide comprehensive CIBIL score analysis

STRUCTURE YOUR RESPONSE:
1. CURRENT SCORE ASSESSMENT (2-3 sentences)
2. KEY FACTORS AFFECTING YOUR SCORE (bullet points, easy to understand)
3. IMMEDIATE ACTION ITEMS (what to do in next 30 days)
4. 3-MONTH IMPROVEMENT PLAN (step-by-step)
5. EXPECTED RESULTS (realistic score improvements)
6. WARNINGS (what NOT to do)

Use simple language. Explain technical terms. Be specific with amounts and timelines.
"""

        elif api_type == "report":
            return base_prompt + """
TASK: Create a 90-day personalized improvement roadmap

STRUCTURE YOUR RESPONSE AS A CLEAR ROADMAP:

WEEK 1-2: IMMEDIATE ACTIONS
- List 3-4 specific actions
- Explain WHY each action helps
- Mention expected impact

MONTH 1: FOUNDATION BUILDING
- Step-by-step monthly goals
- Simple explanations
- Progress tracking tips

MONTH 2: OPTIMIZATION
- Advanced strategies
- Fine-tuning actions
- Monitoring guidelines

MONTH 3: CONSOLIDATION
- Final push actions
- Score stabilization
- Long-term maintenance

Use simple language. Give specific examples. Mention actual numbers and timelines.
NO technical jargon. Write like you're explaining to a friend.
"""

        elif api_type == "scenario":
            return base_prompt + """
TASK: Analyze impact of specific financial actions on credit score

FOR EACH SCENARIO PROVIDED:

SCENARIO NAME: [Name from user]
CURRENT SITUATION: Brief summary
PREDICTED IMPACT:
- Score change: [+/- X points]
- Timeline: [When you'll see results]
- Confidence: [How sure we are]

WHY THIS HAPPENS:
- Simple explanation of credit factors affected
- Real-world impact on credit behavior

STEP-BY-STEP ACTION PLAN:
1. [First thing to do]
2. [Second thing to do]
3. [Third thing to do]

THINGS TO WATCH OUT FOR:
- Potential negative effects
- How to avoid problems

Use everyday language. Give specific examples. Be encouraging but realistic.
"""

        return base_prompt

    def analyze_cibil_profile(self, credit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate FRESH CIBIL profile analysis with new agent"""
        try:
            # Create completely fresh agent for this analysis
            fresh_agent, session_id = self._create_fresh_agent("analysis")
            
            print(f"🔍 DEBUG: Starting FRESH ANALYSIS - Session: {session_id}")
            print(f"📊 Input: Score={credit_data.get('current_score')}, Utilization={credit_data.get('current_utilization')}%")
            
            # Create analysis prompt
            prompt = f"""
FRESH CIBIL ANALYSIS REQUEST - {datetime.now().isoformat()}

USER'S CREDIT PROFILE:
- Current CIBIL Score: {credit_data.get('current_score', 0)}
- Payment History: {credit_data.get('payment_history', 'unknown')}
- Credit Cards: {credit_data.get('credit_cards', 0)}
- Total Credit Limit: ₹{credit_data.get('total_credit_limit', 0):,}
- Current Utilization: {credit_data.get('current_utilization', 0)}%
- Active Loans: {credit_data.get('loans', 0)}
- Missed Payments: {credit_data.get('missed_payments', 0)}
- Account Age: {credit_data.get('account_age_months', 0)} months
- Recent Inquiries: {credit_data.get('recent_inquiries', 0)}
- Age: {credit_data.get('age', 30)} years
- Annual Income: ₹{credit_data.get('income', 500000):,}

Analyze this credit profile and provide clear, actionable advice in simple language.
Focus on practical steps the user can take to improve their score.
"""
            
            # Get fresh AI response
            ai_response = fresh_agent.run(prompt)
            
            # Structure the response
            result = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "response_source": f"Fresh CIBIL Analysis - {session_id}",
                "session_id": session_id,
                "cibil_analysis": ai_response,
                "input_data": credit_data
            }
            
            print(f"✅ DEBUG: FRESH ANALYSIS completed - Session: {session_id}")
            return result
                
        except Exception as e:
            logger.error(f"❌ FRESH CIBIL analysis failed: {str(e)}")
            raise Exception(f"FRESH CIBIL analysis failed: {str(e)}")

    def generate_cibil_report(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate FRESH 90-day improvement report with new agent"""
        try:
            # Create completely fresh agent for this report
            fresh_agent, session_id = self._create_fresh_agent("report")
            
            print(f"🔍 DEBUG: Starting FRESH REPORT - Session: {session_id}")
            print(f"👤 User: Age {user_profile.get('age')}, Score {user_profile.get('current_score')}")
            
            # Create report prompt
            prompt = f"""
FRESH 90-DAY IMPROVEMENT REPORT REQUEST - {datetime.now().isoformat()}

USER PROFILE:
- Age: {user_profile.get('age', 30)} years
- Annual Income: ₹{user_profile.get('income', 500000):,}
- Current CIBIL Score: {user_profile.get('current_score', 650)}
- Credit Experience: {user_profile.get('credit_experience', 'Unknown')}
- Financial Goals: {user_profile.get('goals', 'Credit improvement')}

Create a personalized 90-day action plan that this person can easily follow.
Use simple language and give specific, actionable steps with clear timelines.
Make it encouraging and realistic based on their profile.
"""
            
            # Get fresh AI response
            ai_response = fresh_agent.run(prompt)
            
            # Structure the response
            result = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "response_source": f"Fresh 90-Day Report - {session_id}",
                "session_id": session_id,
                "cibil_report": ai_response,
                "user_profile": user_profile
            }
            
            print(f"✅ DEBUG: FRESH REPORT completed - Session: {session_id}")
            return result
                
        except Exception as e:
            logger.error(f"❌ FRESH report generation failed: {str(e)}")
            raise Exception(f"FRESH report generation failed: {str(e)}")

    def simulate_score_scenarios(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate FRESH scenario simulation with new agent"""
        try:
            # Create completely fresh agent for this scenario analysis
            fresh_agent, session_id = self._create_fresh_agent("scenario")
            
            print(f"🔍 DEBUG: Starting FRESH SCENARIOS - Session: {session_id}")
            print(f"🎯 Scenarios: {len(scenarios)} to analyze")
            
            # Format scenarios for the prompt
            scenario_text = ""
            for i, scenario in enumerate(scenarios, 1):
                scenario_text += f"""
SCENARIO {i}: {scenario.get('name', f'Scenario {i}')}
Action: {scenario.get('action', 'Unknown action')}
Current Score: {scenario.get('current_score', 750)}
Expected Timeline: {scenario.get('timeline', 'Unknown timeline')}
---
"""
            
            # Create scenario prompt
            prompt = f"""
FRESH SCENARIO IMPACT ANALYSIS REQUEST - {datetime.now().isoformat()}

SCENARIOS TO ANALYZE:
{scenario_text}

For each scenario above, analyze the potential impact on credit score.
Explain in simple terms how each action will affect the user's credit.
Give realistic expectations and practical advice.
Use encouraging language but be honest about potential challenges.
"""
            
            # Get fresh AI response
            ai_response = fresh_agent.run(prompt)
            
            # Structure the response
            result = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "response_source": f"Fresh Scenario Analysis - {session_id}",
                "session_id": session_id,
                "scenario_analysis": ai_response,
                "input_scenarios": scenarios
            }
            
            print(f"✅ DEBUG: FRESH SCENARIOS completed - Session: {session_id}")
            return result
                
        except Exception as e:
            logger.error(f"❌ FRESH scenario simulation failed: {str(e)}")
            raise Exception(f"FRESH scenario simulation failed: {str(e)}")

# Keep existing helper functions
def generate_sample_credit_data(num_users: int = 10) -> pd.DataFrame:
    """Generate sample credit data for testing CIBIL analysis"""
    fake = Faker()
    np.random.seed(42)
    random.seed(42)
    
    data = []
    for i in range(1, num_users + 1):
        # Generate realistic credit profile
        score = np.random.normal(720, 80)  # Mean 720, std 80
        score = max(300, min(900, int(score)))  # Clamp to valid range
        
        credit_cards = random.randint(1, 6)
        total_limit = random.randint(100000, 2000000)
        utilization = random.uniform(5, 85)
        
        profile = {
            'user_id': i,
            'current_score': score,
            'credit_cards': credit_cards,
            'total_credit_limit': total_limit,
            'current_utilization': round(utilization, 1),
            'loans': random.randint(0, 3),
            'missed_payments': random.randint(0, 5),
            'account_age_months': random.randint(12, 240),
            'recent_inquiries': random.randint(0, 8),
            'payment_history': random.choice(['excellent', 'good', 'fair', 'poor']),
            'age': random.randint(22, 65),
            'income': random.randint(300000, 2000000)
        }
        
        data.append(profile)
    
    return pd.DataFrame(data)

# Test function
def test_cibil_agent():
    """Test the CIBIL Analysis Agent"""
    print("🧪 Testing FRESH CIBIL Analysis Agent...")
    
    try:
        agent = CibilAnalysisAgent()
        
        # Test data
        test_credit_data = {
            'current_score': 720,
            'payment_history': 'good',
            'credit_cards': 3,
            'total_credit_limit': 500000,
            'current_utilization': 30.0,
            'loans': 1,
            'missed_payments': 1,
            'account_age_months': 48,
            'recent_inquiries': 2,
            'age': 30,
            'income': 800000
        }
        
        print(f"🔍 Testing Analysis API")
        result1 = agent.analyze_cibil_profile(test_credit_data)
        print(f"✅ Analysis completed - Session: {result1.get('session_id')}")
        
        print(f"🔍 Testing Report API") 
        report_data = {
            'age': 30,
            'income': 800000,
            'current_score': 720,
            'credit_experience': '5 years',
            'goals': 'Improve to 800+'
        }
        result2 = agent.generate_cibil_report(report_data)
        print(f"✅ Report completed - Session: {result2.get('session_id')}")
        
        print(f"🔍 Testing Scenario API")
        scenarios = [{
            'name': 'Pay down credit card debt',
            'action': 'Reduce utilization from 30% to 15%',
            'current_score': 720,
            'timeline': '2 months'
        }]
        result3 = agent.simulate_score_scenarios(scenarios)
        print(f"✅ Scenarios completed - Session: {result3.get('session_id')}")
        
        # Verify each session is unique
        sessions = [result1.get('session_id'), result2.get('session_id'), result3.get('session_id')]
        print(f"📊 Unique sessions created: {len(set(sessions)) == 3}")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_cibil_agent()
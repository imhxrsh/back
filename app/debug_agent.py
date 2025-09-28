"""
Debug script to check why agent is in mock mode
"""

import os
from dotenv import load_dotenv
load_dotenv()

print("🔍 Debugging Agent Initialization")
print("=" * 40)

# Check environment
groq_key = os.getenv("GROQ_API_KEY")
print(f"GROQ API Key: {'✅ Found' if groq_key else '❌ Missing'}")
if groq_key:
    print(f"Key starts with: {groq_key[:10]}...")

# Check Swarms import
try:
    from swarms.structs.agent import Agent
    print("Swarms Import: ✅ Success")
    
    # Try to create a simple agent
    try:
        test_agent = Agent(
            agent_name="Test-Agent",
            system_prompt="You are a test agent",
            model_name="groq/llama-3.3-70b-versatile",
            max_loops=1
        )
        print("Agent Creation: ✅ Success")
        
        # Try to run a simple query
        try:
            result = test_agent.run("What is 2+2?")
            print("Agent Execution: ✅ Success")
            print(f"Response: {result[:100]}...")
        except Exception as e:
            print(f"Agent Execution: ❌ Failed - {str(e)}")
            
    except Exception as e:
        print(f"Agent Creation: ❌ Failed - {str(e)}")
        
except ImportError as e:
    print(f"Swarms Import: ❌ Failed - {str(e)}")

# Check our Tax Agent
try:
    from app.agents.tax_calculation_agent import TaxCalculationAgent
    tax_agent = TaxCalculationAgent()
    print(f"Tax Agent Mode: {tax_agent.use_real_agent}")
    print(f"Tax Agent Status: {'Real' if tax_agent.use_real_agent else 'Mock'}")
except Exception as e:
    print(f"Tax Agent: ❌ Failed - {str(e)}")
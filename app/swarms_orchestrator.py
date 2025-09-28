from swarms.structs.agent import Agent
import os
from dotenv import load_dotenv

load_dotenv()

class TaxWiseSwarms:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.setup_agents()
    
    def setup_agents(self):
        # Data Processing Agent
        self.data_agent = Agent(
            agent_name="Financial-Data-Processor",
            system_prompt="Process Indian financial documents and categorize transactions...",
            model_name="groq/llama-3.3-70b-versatile",
            max_loops=1,
            temperature=0.1,
            max_tokens=4000
        )
        
        # Tax Optimization Agent
        self.tax_agent = Agent(
            agent_name="Tax-Optimization-Engine",
            system_prompt="Calculate Indian tax liabilities and optimization strategies...",
            model_name="groq/llama-3.3-70b-versatile",
            max_loops=1,
            temperature=0.2,
            max_tokens=4000
        )
        
        # CIBIL Analysis Agent
        self.cibil_agent = Agent(
            agent_name="CIBIL-Score-Advisor",
            system_prompt="Analyze credit behavior and provide CIBIL improvements...",
            model_name="groq/llama-3.3-70b-versatile",
            max_loops=1,
            temperature=0.1,
            max_tokens=4000
        )
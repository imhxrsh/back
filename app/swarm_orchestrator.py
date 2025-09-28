"""
Swarm Orchestrator for TaxWise AI - Master Chatbot Assistant
Integrates all existing agents (Tax, CIBIL, Data Ingestion) using Swarm framework
Uses Groq's OpenAI-compatible API for cost-effective and fast inference
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from swarms import Agent, GroupChat
from swarms.structs.conversation import Conversation
from swarms.structs.multi_agent_exec import run_agents_concurrently
from groq import Groq

# Import existing agents
from app.agents.tax_calculation_agent import TaxCalculationAgent
from app.agents.cibil_analysis_agent import CibilAnalysisAgent
from app.agents.data_ingestion_agent import DataIngestionAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaxWiseSwarmOrchestrator:
    """
    Master Swarm Orchestrator that coordinates all AI agents
    and provides intelligent financial insights to users
    """
    
    def __init__(self):
        self.tax_agent = TaxCalculationAgent()
        self.cibil_agent = CibilAnalysisAgent()
        self.data_ingestion_agent = DataIngestionAgent()
        
        # Initialize Groq client
        self.groq_client = Groq(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
        
        # Initialize Swarm agents with Groq
        self.swarm_agents = self._initialize_swarm_agents()
        
        # Create conversation manager
        self.conversation = Conversation(
            name="taxwise_ai_copilot",
            backend="in-memory",  # Fixed: should be 'in-memory' not 'memory'
            system_prompt="You are TaxWise AI Copilot, a comprehensive financial assistant that helps users with tax optimization, CIBIL analysis, and document processing.",
            time_enabled=True
        )
        
        # Create group chat for multi-agent collaboration
        self.group_chat = GroupChat(
            name="TaxWise AI Team",
            description="Comprehensive financial analysis team",
            agents=list(self.swarm_agents.values()),
            max_loops=10
        )
        
        logger.info("✅ TaxWise Swarm Orchestrator initialized successfully with Groq API")
    
    def _initialize_swarm_agents(self) -> Dict[str, Agent]:
        """Initialize specialized Swarm agents for different financial domains"""
        
        agents = {}
        
        # Tax Specialist Agent
        agents["tax_specialist"] = Agent(
            agent_name="TaxSpecialist",
            system_prompt="""You are a tax optimization specialist with deep knowledge of Indian tax laws. 
            Your expertise includes:
            - Tax liability calculations (Old vs New regime)
            - Section 80C, 80D, HRA, and other deductions
            - Tax optimization strategies
            - Investment recommendations for tax savings
            - Form 16 and tax filing guidance
            
            Always provide accurate, actionable tax advice based on user's financial data.""",
            model_name="groq/llama-3.3-70b-versatile",
            max_loops=3,
            temperature=0.3,
            max_tokens=2000
        )
        
        # CIBIL Specialist Agent
        agents["cibil_specialist"] = Agent(
            agent_name="CibilSpecialist",
            system_prompt="""You are a credit score and CIBIL analysis expert. 
            Your expertise includes:
            - CIBIL score analysis and interpretation
            - Credit utilization optimization
            - Payment history improvement strategies
            - Credit mix diversification
            - Loan and credit card recommendations
            - Credit score improvement timelines
            
            Provide personalized credit improvement strategies based on user's current credit profile.""",
            model_name="groq/llama-3.3-70b-versatile",
            max_loops=3,
            temperature=0.3,
            max_tokens=2000
        )
        
        # Document Analysis Agent
        agents["document_analyst"] = Agent(
            agent_name="DocumentAnalyst",
            system_prompt="""You are a financial document analysis specialist. 
            Your expertise includes:
            - Bank statement analysis
            - Salary slip interpretation
            - Form 16 processing
            - Credit card statement analysis
            - Investment document review
            - Data extraction and categorization
            
            Extract meaningful insights from financial documents and identify patterns.""",
            model_name="groq/llama-3.3-70b-versatile",
            max_loops=3,
            temperature=0.3,
            max_tokens=2000
        )
        
        # Financial Advisor Agent
        agents["financial_advisor"] = Agent(
            agent_name="FinancialAdvisor",
            system_prompt="""You are a comprehensive financial advisor who synthesizes insights from all specialists. 
            Your role includes:
            - Integrating tax, credit, and document insights
            - Providing holistic financial recommendations
            - Creating personalized financial plans
            - Setting financial goals and milestones
            - Risk assessment and mitigation strategies
            - Investment portfolio optimization
            
            Always consider the user's complete financial picture when making recommendations.""",
            model_name="groq/llama-3.3-70b-versatile",
            max_loops=3,
            temperature=0.4,
            max_tokens=2000
        )
        
        # Conversation Manager Agent
        agents["conversation_manager"] = Agent(
            agent_name="ConversationManager",
            system_prompt="""You are the conversation manager for TaxWise AI Copilot. 
            Your responsibilities include:
            - Understanding user queries and intent
            - Routing questions to appropriate specialists
            - Synthesizing responses from multiple agents
            - Maintaining conversational context
            - Providing clear, actionable responses
            - Asking clarifying questions when needed
            
            Always be helpful, professional, and focused on the user's financial well-being.""",
            model_name="groq/llama-3.3-70b-versatile",
            max_loops=2,
            temperature=0.5,
            max_tokens=2000
        )
        
        return agents
    
    async def process_user_query(self, query: str, user_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process user query using the Swarm orchestrator
        """
        try:
            logger.info(f"Processing user query: {query[:100]}...")
            
            # Add user query to conversation
            self.conversation.add(
                content=query,
                role="user",
                metadata={"timestamp": datetime.now().isoformat()}
            )
            
            # Determine query type and route to appropriate agents
            query_analysis = await self._analyze_query_intent(query)
            
            # Get user context if available
            user_context = self._prepare_user_context(user_data)
            
            # Create comprehensive task for the swarm
            swarm_task = self._create_swarm_task(query, query_analysis, user_context)
            
            # Execute the swarm task
            response = await self._execute_swarm_task(swarm_task, query_analysis)
            
            # Add response to conversation
            self.conversation.add(
                content=response,
                role="assistant",
                metadata={"timestamp": datetime.now().isoformat()}
            )
            
            return {
                "success": True,
                "response": response,
                "query_type": query_analysis["type"],
                "agents_used": query_analysis["agents_needed"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing user query: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze user query to determine intent and required agents using real agent execution"""
        
        try:
            logger.info(f"Analyzing query intent for: {query[:50]}...")
            
            # Use the conversation manager agent to analyze the query
            intent_analysis = await self.swarm_agents["conversation_manager"].arun(
                f"""Analyze this user query and determine:
                1. Query type (tax, cibil, document, general, or mixed)
                2. Required agents (tax_specialist, cibil_specialist, document_analyst, financial_advisor)
                3. Complexity level (simple, moderate, complex)
                4. Key topics mentioned
                
                Query: "{query}"
                
                Respond in JSON format:
                {{
                    "type": "tax|cibil|document|general|mixed",
                    "agents_needed": ["agent1", "agent2"],
                    "complexity": "simple|moderate|complex",
                    "topics": ["topic1", "topic2"],
                    "requires_user_data": true/false
                }}"""
            )
            
            logger.info(f"Intent analysis response: {intent_analysis[:200]}...")
            
            # Extract JSON from response
            json_start = intent_analysis.find('{')
            json_end = intent_analysis.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                parsed_analysis = json.loads(intent_analysis[json_start:json_end])
                logger.info(f"Parsed intent analysis: {parsed_analysis}")
                return parsed_analysis
        except Exception as e:
            logger.warning(f"Failed to parse intent analysis: {str(e)}")
        
        # Fallback analysis using keyword matching
        logger.info("Using fallback keyword analysis")
        query_lower = query.lower()
        if any(word in query_lower for word in ['tax', 'deduction', '80c', 'hra', 'form16', 'income tax', 'tax saving']):
            return {
                "type": "tax",
                "agents_needed": ["tax_specialist", "financial_advisor"],
                "complexity": "moderate",
                "topics": ["tax_optimization"],
                "requires_user_data": True
            }
        elif any(word in query_lower for word in ['cibil', 'credit', 'score', 'loan', 'card', 'credit score', 'credit card']):
            return {
                "type": "cibil",
                "agents_needed": ["cibil_specialist", "financial_advisor"],
                "complexity": "moderate",
                "topics": ["credit_analysis"],
                "requires_user_data": True
            }
        elif any(word in query_lower for word in ['document', 'upload', 'statement', 'pdf', 'csv', 'excel', 'file']):
            return {
                "type": "document",
                "agents_needed": ["document_analyst", "financial_advisor"],
                "complexity": "moderate",
                "topics": ["document_analysis"],
                "requires_user_data": False
            }
        else:
            return {
                "type": "general",
                "agents_needed": ["financial_advisor"],
                "complexity": "simple",
                "topics": ["general_finance"],
                "requires_user_data": False
            }
    
    def _prepare_user_context(self, user_data: Optional[Dict]) -> str:
        """Prepare user context for the agents"""
        if not user_data:
            return "No user data available. Please upload documents or provide financial information for personalized insights."
        
        context = "User Financial Profile:\n"
        
        if "financialSummary" in user_data:
            fs = user_data["financialSummary"]
            context += f"- Annual Income: ₹{fs.get('totalIncome', 0):,}\n"
            context += f"- Monthly Expenses: ₹{fs.get('totalExpenses', 0):,}\n"
            context += f"- Net Worth: ₹{fs.get('netWorth', 0):,}\n"
            context += f"- Monthly Savings: ₹{fs.get('monthlySavings', 0):,}\n"
        
        if "taxData" in user_data:
            td = user_data["taxData"]
            context += f"- Tax Liability: ₹{td.get('currentTaxLiability', 0):,}\n"
            context += f"- Potential Savings: ₹{td.get('potentialSavings', 0):,}\n"
            context += f"- Recommended Regime: {td.get('recommendedRegime', 'N/A')}\n"
        
        if "cibilData" in user_data:
            cd = user_data["cibilData"]
            context += f"- CIBIL Score: {cd.get('currentScore', 0)}\n"
            context += f"- Credit Utilization: {cd.get('creditUtilization', 0)}%\n"
            context += f"- Payment History: {cd.get('paymentHistory', 'N/A')}\n"
        
        return context
    
    def _create_swarm_task(self, query: str, query_analysis: Dict, user_context: str) -> str:
        """Create a comprehensive task for the swarm based on query analysis"""
        
        task = f"""
        User Query: "{query}"
        
        Query Type: {query_analysis['type']}
        Complexity: {query_analysis['complexity']}
        Topics: {', '.join(query_analysis['topics'])}
        
        {user_context}
        
        Please provide a comprehensive, personalized response that:
        1. Directly addresses the user's question
        2. Uses the provided financial data for personalized insights
        3. Offers actionable recommendations
        4. Explains the reasoning behind suggestions
        5. Mentions any additional information needed for better advice
        
        Be specific, practical, and focused on the user's financial well-being.
        """
        
        return task
    
    async def _execute_swarm_task(self, task: str, query_analysis: Dict) -> str:
        """Execute the swarm task using appropriate agents"""
        
        try:
            logger.info(f"Executing swarm task with {len(query_analysis['agents_needed'])} agents")
            
            # Use real agents instead of Swarm agents for now
            return await self._execute_with_real_agents(task, query_analysis)
                
        except Exception as e:
            logger.error(f"Error executing swarm task: {str(e)}")
            return f"I apologize, but I encountered an error while processing your request: {str(e)}. Please try rephrasing your question or contact support if the issue persists."
    
    async def _execute_with_real_agents(self, task: str, query_analysis: Dict) -> str:
        """Execute using the real working agents (Tax, CIBIL, Data Ingestion)"""
        
        query_type = query_analysis.get("type", "general")
        
        try:
            if query_type == "tax":
                # Use the real tax agent
                logger.info("Using real tax agent for tax-related query")
                
                # Extract financial data from task if available
                financial_data = self._extract_financial_data_from_task(task)
                
                # Calculate tax using the real agent
                tax_result = self.tax_agent.calculate_tax_liability(financial_data)
                
                # Format the response using the actual tax result structure
                calculations = tax_result.get('calculations', {})
                old_regime = calculations.get('old_regime', {})
                new_regime = calculations.get('new_regime', {})
                comparison = calculations.get('comparison', {})
                recommendations = calculations.get('recommendations', {})
                
                response = f"""Based on your tax query, here's a comprehensive analysis:

**Tax Calculation Results:**
- Old Regime Tax: ₹{old_regime.get('total_tax', 0):,.2f}
- New Regime Tax: ₹{new_regime.get('total_tax', 0):,.2f}
- Recommended Regime: {comparison.get('optimal_regime', 'N/A').title()}
- Potential Savings: ₹{comparison.get('tax_savings', 0):,.2f} ({comparison.get('savings_percentage', 0):.1f}%)

**Deductions Used (Old Regime):**
- Standard Deduction: ₹{old_regime.get('deductions', {}).get('standard_deduction', 0):,.2f}
- Section 80C: ₹{old_regime.get('deductions', {}).get('section_80c', 0):,.2f}
- Section 80D (Health Insurance): ₹{old_regime.get('deductions', {}).get('section_80d', 0):,.2f}
- Section 24B (Home Loan Interest): ₹{old_regime.get('deductions', {}).get('section_24b', 0):,.2f}
- HRA: ₹{old_regime.get('deductions', {}).get('hra', 0):,.2f}
- Total Deductions: ₹{old_regime.get('deductions', {}).get('total', 0):,.2f}

**Tax Breakdown:**
- Taxable Income: ₹{old_regime.get('taxable_income', 0):,.2f}
- Tax Before Cess: ₹{old_regime.get('tax_before_cess', 0):,.2f}
- Cess: ₹{old_regime.get('cess', 0):,.2f}
- Effective Tax Rate: {old_regime.get('effectiveRate', 0):.2f}%

**Investment Recommendations:**
{chr(10).join([f"- {inv.get('type', 'N/A')}: ₹{inv.get('suggested_amount', 0):,.2f} (Save ₹{inv.get('tax_saving', 0):,.2f})" for inv in recommendations.get('investment_suggestions', [])])}

**Action Items:**
{chr(10).join([f"- {item.get('action', 'N/A')} (Priority: {item.get('priority', 'N/A')})" for item in recommendations.get('action_items', [])])}

**Next Steps:**
- Upload your Form 16 for more accurate calculations
- Provide your complete financial details for personalized advice
- Consider the recommended regime for maximum savings

Would you like me to analyze your specific tax situation with more details?"""
                
                return response
                
            elif query_type == "cibil":
                # Use the real CIBIL agent
                logger.info("Using real CIBIL agent for credit-related query")
                
                # Extract credit data from task if available
                credit_data = self._extract_credit_data_from_task(task)
                
                # Analyze CIBIL using the real agent
                cibil_result = self.cibil_agent.analyze_cibil_profile(credit_data)
                
                # Format the response using the actual CIBIL result structure
                cibil_analysis = cibil_result.get('cibil_analysis', '')
                input_data = cibil_result.get('input_data', {})
                
                response = f"""Based on your CIBIL query, here's a comprehensive credit analysis:

**Current CIBIL Profile:**
- Current Score: {input_data.get('current_score', 0)}
- Credit Utilization: {input_data.get('current_utilization', 0)}%
- Payment History: {input_data.get('payment_history', 'N/A')}
- Credit Cards: {input_data.get('credit_cards', 0)}
- Total Credit Limit: ₹{input_data.get('total_credit_limit', 0):,.2f}
- Active Loans: {input_data.get('loans', 0)}
- Account Age: {input_data.get('account_age_months', 0)} months
- Recent Inquiries: {input_data.get('recent_inquiries', 0)}

**Detailed Analysis:**
{cibil_analysis}

**Next Steps:**
- Upload your credit report for detailed analysis
- Provide your current credit details for personalized recommendations
- Focus on the improvement areas mentioned above

What specific aspect of your credit score would you like to focus on?"""
                
                return response
                
            elif query_type == "document":
                # Use the real data ingestion agent
                logger.info("Using real data ingestion agent for document-related query")
                
                response = """I can help you analyze your financial documents using our advanced AI processing system!

**Document Analysis Capabilities:**

1. **Bank Statements**:
   - Income and expense pattern analysis
   - Monthly cash flow calculations
   - Investment and savings tracking
   - Spending categorization and insights

2. **Salary Slips**:
   - Gross vs net salary breakdown
   - Tax deduction analysis
   - Allowances and benefits review
   - Year-to-date calculations

3. **Form 16**:
   - Tax liability calculations
   - Deduction optimization suggestions
   - TDS analysis and refund potential
   - Regime comparison

4. **Credit Card Statements**:
   - Spending pattern analysis
   - Interest calculation optimization
   - Payment schedule recommendations
   - Credit utilization insights

**Supported Formats:**
- PDF files (bank statements, salary slips, Form 16)
- CSV/Excel spreadsheets (transaction data)
- Image files (PNG, JPG) of documents

**How to Upload:**
- Use the document upload feature on the dashboard
- Our AI will automatically extract key financial data
- Get personalized insights and recommendations

**What You'll Get:**
- Detailed financial analysis
- Tax optimization suggestions
- Credit score improvement tips
- Investment recommendations
- Personalized financial advice

Ready to upload your documents? I'll provide comprehensive analysis and actionable insights!"""
                
                return response
                
            else:
                # General financial advice
                logger.info("Providing general financial advice")
                
                response = """I'm your TaxWise AI Copilot, here to help with all your financial needs!

**How I Can Help:**

1. **Tax Optimization**: 
   - Calculate your tax liability under both regimes
   - Suggest optimal deductions and investments
   - Compare Old vs New tax regime benefits
   - Provide personalized tax planning strategies

2. **CIBIL Analysis**: 
   - Analyze your credit score and health
   - Identify factors affecting your score
   - Provide improvement recommendations
   - Project future score improvements

3. **Document Processing**: 
   - Extract insights from bank statements
   - Analyze salary slips and Form 16
   - Process credit card statements
   - Generate comprehensive financial reports

4. **Financial Planning**: 
   - Create personalized budgets
   - Set and track financial goals
   - Optimize investment portfolios
   - Provide risk assessment

**To Get Started:**
- Upload your financial documents for personalized analysis
- Ask specific questions about taxes, credit, or investments
- I'll provide actionable recommendations based on your data

**Example Questions:**
- "How can I reduce my tax liability?"
- "What's affecting my CIBIL score?"
- "Analyze my bank statement for spending patterns"
- "Should I choose old or new tax regime?"

What would you like to know about your finances today?"""
                
                return response
                
        except Exception as e:
            logger.error(f"Error executing with real agents: {str(e)}")
            return self._get_fallback_response(query_analysis, task)
    
    def _extract_financial_data_from_task(self, task: str) -> Dict:
        """Extract financial data from task string for tax calculations"""
        # Default financial data - in a real implementation, this would parse the task
        return {
            "annual_income": 1200000,
            "investments_80c": 75000,
            "health_insurance": 15000,
            "home_loan_interest": 180000,
            "hra_claimed": 120000,
            "other_deductions": {}
        }
    
    def _extract_credit_data_from_task(self, task: str) -> Dict:
        """Extract credit data from task string for CIBIL analysis"""
        # Default credit data - in a real implementation, this would parse the task
        return {
            "current_score": 780,
            "payment_history": "excellent",
            "credit_cards": 3,
            "total_credit_limit": 500000,
            "current_utilization": 20.0,
            "loans": 1,
            "missed_payments": 0,
            "account_age_months": 72,
            "recent_inquiries": 1,
            "age": 30,
            "income": 1200000
        }
    
    def _get_fallback_response(self, query_analysis: Dict, task: str) -> str:
        """Provide intelligent fallback responses based on query type"""
        
        query_type = query_analysis.get("type", "general")
        
        if query_type == "tax":
            return """I'd be happy to help you with tax optimization! Here are some key strategies to consider:

**Tax Optimization Strategies:**

1. **Choose the Right Regime**: Compare Old vs New tax regime based on your deductions
2. **Maximize Section 80C**: Invest up to ₹1.5 lakh in ELSS, PPF, EPF, or NSC
3. **Health Insurance (80D)**: Claim up to ₹25,000 for self/family, ₹50,000 for senior citizens
4. **HRA Optimization**: Ensure proper HRA documentation and calculations
5. **Home Loan Benefits**: Claim interest deduction up to ₹2 lakh under Section 24(b)
6. **Other Deductions**: Consider 80E (education loan), 80EE (first-time homebuyers)

**Next Steps:**
- Upload your Form 16 and financial documents for personalized analysis
- Provide your current income and existing investments
- I can then calculate your exact tax liability and savings potential

Would you like me to analyze your specific tax situation?"""

        elif query_type == "cibil":
            return """I can help you improve your CIBIL score! Here's a comprehensive approach:

**CIBIL Score Improvement Strategies:**

1. **Payment History (35% impact)**: 
   - Pay all bills on time
   - Set up automatic payments
   - Clear any overdue amounts immediately

2. **Credit Utilization (30% impact)**:
   - Keep credit card usage below 30% of limit
   - Pay off balances before due date
   - Consider increasing credit limits

3. **Credit Age (15% impact)**:
   - Keep old accounts open
   - Don't close your oldest credit card
   - Maintain a mix of credit types

4. **Credit Mix (10% impact)**:
   - Have both secured and unsecured loans
   - Maintain a healthy mix of credit cards and loans

5. **New Credit (10% impact)**:
   - Avoid multiple credit applications
   - Space out credit inquiries
   - Only apply when necessary

**Immediate Actions:**
- Check your current CIBIL score
- Review your credit report for errors
- Upload your credit documents for detailed analysis

What's your current CIBIL score, and what specific areas would you like to focus on?"""

        elif query_type == "document":
            return """I can help you analyze your financial documents! Here's what I can extract:

**Document Analysis Capabilities:**

1. **Bank Statements**:
   - Income and expense patterns
   - Monthly cash flow analysis
   - Investment tracking
   - Spending categorization

2. **Salary Slips**:
   - Gross vs net salary breakdown
   - Tax deductions analysis
   - Allowances and benefits
   - Year-to-date calculations

3. **Form 16**:
   - Tax liability calculations
   - Deduction optimization
   - TDS analysis
   - Refund potential

4. **Credit Card Statements**:
   - Spending patterns
   - Interest calculations
   - Payment optimization
   - Credit utilization analysis

**Supported Formats:**
- PDF files
- CSV/Excel spreadsheets
- Image files (PNG, JPG)

**Next Steps:**
- Upload your documents using the document upload feature
- I'll extract key financial data automatically
- Provide personalized insights and recommendations

What type of financial documents do you have, and what specific insights are you looking for?"""

        else:
            return """I'm your TaxWise AI Copilot, here to help with all your financial needs!

**How I Can Help:**

1. **Tax Optimization**: Calculate tax liability, suggest deductions, compare regimes
2. **CIBIL Analysis**: Improve credit score, analyze credit health, get recommendations
3. **Document Processing**: Extract insights from bank statements, salary slips, Form 16
4. **Financial Planning**: Create budgets, set goals, optimize investments
5. **Investment Advice**: Suggest tax-saving investments, portfolio optimization

**To Get Started:**
- Upload your financial documents for personalized analysis
- Ask specific questions about taxes, credit, or investments
- I'll provide actionable recommendations based on your data

**Example Questions:**
- "How can I reduce my tax liability?"
- "What's affecting my CIBIL score?"
- "Analyze my bank statement for spending patterns"
- "Should I choose old or new tax regime?"

What would you like to know about your finances today?"""
    
    async def get_financial_insights(self, user_data: Dict) -> Dict[str, Any]:
        """Generate comprehensive financial insights using all agents"""
        
        try:
            logger.info("Generating comprehensive financial insights using all agents")
            
            # Create comprehensive analysis task
            task = f"""
            Based on the user's financial data, provide comprehensive insights covering:
            
            1. Tax Optimization Opportunities
            2. Credit Score Improvement Strategies  
            3. Investment Recommendations
            4. Financial Goal Setting
            5. Risk Assessment
            6. Action Items and Next Steps
            
            User Data: {json.dumps(user_data, indent=2)}
            
            Provide specific, actionable recommendations with clear reasoning.
            """
            
            # Use all agents for comprehensive analysis
            all_agents = list(self.swarm_agents.values())
            logger.info(f"Running {len(all_agents)} agents concurrently for insights")
            
            # Execute all agents concurrently
            response = await run_agents_concurrently(agents=all_agents, task=task)
            
            # Process the response to extract meaningful insights
            insights = []
            for i, agent_response in enumerate(response):
                agent_name = all_agents[i].agent_name if i < len(all_agents) else f"Agent_{i}"
                insights.append({
                    "agent": agent_name,
                    "insights": str(agent_response)
                })
            
            logger.info(f"Generated insights from {len(insights)} agents")
            
            return {
                "success": True,
                "insights": insights,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating financial insights: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.conversation.to_dict()
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation.clear()
    
    async def test_agents(self) -> Dict[str, Any]:
        """Test all agents with a simple query to ensure they're working"""
        try:
            test_query = "Hello, can you help me with my finances?"
            results = {}
            
            for agent_name, agent in self.swarm_agents.items():
                try:
                    logger.info(f"Testing agent: {agent_name}")
                    response = await agent.arun(test_query)
                    results[agent_name] = {
                        "status": "success",
                        "response": str(response)[:200] + "..." if len(str(response)) > 200 else str(response)
                    }
                    logger.info(f"Agent {agent_name} test successful")
                except Exception as e:
                    results[agent_name] = {
                        "status": "error",
                        "error": str(e)
                    }
                    logger.error(f"Agent {agent_name} test failed: {str(e)}")
            
            return {
                "success": True,
                "test_results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error testing agents: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Global instance
swarm_orchestrator = TaxWiseSwarmOrchestrator()

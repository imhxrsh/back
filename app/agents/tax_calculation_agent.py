"""
Tax Calculation Agent - Windows Compatible Version
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Use our Windows-compatible import
try:
    from .swarms_compat import create_agent
    agent_creator, SWARMS_AVAILABLE = create_agent()
except ImportError:
    SWARMS_AVAILABLE = False
    agent_creator = None

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaxCalculationAgent:
    """
    Specialized agent for Indian tax calculations and optimization - Windows Compatible
    """
    
    def __init__(self, use_real_agent: bool = None):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        # Determine whether to use real or mock agent
        if use_real_agent is None:
            use_real_agent = SWARMS_AVAILABLE and bool(self.groq_api_key) and agent_creator is not None
        
        self.use_real_agent = use_real_agent
        self.agent = None
        
        # Indian tax constants for AY 2024-25
        self.tax_constants = {
            "assessment_year": "2024-25",
            "standard_deduction": 50000,
            "section_80c_limit": 150000,
            "section_80d_limit": 25000,
            "section_80d_senior": 50000,
            "basic_exemption_limit": 250000,
            "senior_citizen_exemption": 300000,
            "super_senior_exemption": 500000,
            "old_regime_slabs": [
                {"min": 0, "max": 250000, "rate": 0},
                {"min": 250001, "max": 500000, "rate": 5},
                {"min": 500001, "max": 1000000, "rate": 20},
                {"min": 1000001, "max": float('inf'), "rate": 30}
            ],
            "new_regime_slabs": [
                {"min": 0, "max": 300000, "rate": 0},
                {"min": 300001, "max": 600000, "rate": 5},
                {"min": 600001, "max": 900000, "rate": 10},
                {"min": 900001, "max": 1200000, "rate": 15},
                {"min": 1200001, "max": 1500000, "rate": 20},
                {"min": 1500001, "max": float('inf'), "rate": 30}
            ]
        }
        
        self._initialize_agent()
        agent_mode = "Real AI" if self.use_real_agent else "Mock"
        logger.info(f"✅ Tax Calculation Agent initialized ({agent_mode} mode)")
    
    def _initialize_agent(self):
        """Initialize the agent with Windows compatibility"""
        try:
            if self.use_real_agent and agent_creator:
                self.agent = agent_creator(
                    agent_name="Tax-Optimization-Engine",
                    system_prompt=self._get_system_prompt(),
                    groq_api_key=self.groq_api_key
                )
                logger.info("✅ Real AI Agent initialized successfully")
            else:
                logger.info("Using Mock Agent (calculations + fallback responses)")
                
        except Exception as e:
            logger.error(f"Agent initialization error: {str(e)}")
            self.use_real_agent = False
            logger.info("Falling back to Mock Agent")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the tax agent"""
        return """You are a certified Indian tax consultant specializing in Income Tax Act for AY 2024-25.

EXPERTISE AREAS:
1. TAX REGIME COMPARISON (Old vs New)
2. SECTION-WISE DEDUCTIONS (80C, 80D, 24B, HRA)  
3. TAX CALCULATIONS with correct slabs and cess
4. INVESTMENT RECOMMENDATIONS for tax optimization

RESPONSE FORMAT:
Always provide structured, actionable advice with:
- Specific amounts and calculations
- Section references (80C, 80D, etc.)
- Timeline for actions
- Risk-appropriate investment suggestions

Focus on practical, implementable tax-saving strategies for Indian taxpayers.
Be precise with numbers and provide clear reasoning for recommendations.
"""

    def calculate_tax_liability(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive tax liability for both old and new regime
        """
        try:
            # Always calculate with our reliable mock calculations
            mock_result = self._mock_tax_calculation(financial_data)
            
            if self.use_real_agent and self.agent:
                try:
                    # Get AI enhancement for the calculations
                    prompt = self._create_tax_calculation_prompt(financial_data)
                    ai_response = self.agent.run(prompt)
                    
                    # Combine mock calculations with AI insights
                    mock_result["ai_insights"] = str(ai_response)[:500] + "..." if len(str(ai_response)) > 500 else str(ai_response)
                    mock_result["response_source"] = "AI Enhanced"
                    
                    logger.info("✅ AI-enhanced tax calculation completed")
                except Exception as ai_error:
                    logger.warning(f"AI enhancement failed: {ai_error}")
                    mock_result["response_source"] = "Mock with AI Error"
            else:
                mock_result["response_source"] = "Mock Calculation"
            
            return mock_result
                
        except Exception as e:
            logger.error(f"Error in tax calculation: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "calculations": self._fallback_calculation(financial_data)
            }
    
    def _create_tax_calculation_prompt(self, financial_data: Dict[str, Any]) -> str:
        """Create detailed prompt for AI tax calculation"""
        income = financial_data.get('annual_income', 0)
        investments_80c = financial_data.get('investments_80c', 0)
        health_insurance = financial_data.get('health_insurance', 0)
        home_loan = financial_data.get('home_loan_interest', 0)
        
        return f"""
INDIAN TAX ANALYSIS REQUEST (AY 2024-25):

Financial Profile:
- Annual Income: ₹{income:,}
- 80C Investments: ₹{investments_80c:,}
- Health Insurance: ₹{health_insurance:,}  
- Home Loan Interest: ₹{home_loan:,}

Please provide:
1. Old vs New regime recommendation with reasoning
2. Additional investment suggestions to maximize tax savings
3. Priority actions before March 31st
4. Estimated tax savings potential

Focus on practical, actionable advice for this income level.
"""

    def _mock_tax_calculation(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced mock calculation with detailed breakdown"""
        
        # Extract values with defaults
        annual_income = float(financial_data.get('annual_income', 1200000))
        existing_80c = float(financial_data.get('investments_80c', 50000))
        existing_80d = float(financial_data.get('health_insurance', 0))
        home_loan_interest = float(financial_data.get('home_loan_interest', 0))
        hra_claimed = float(financial_data.get('hra_claimed', 0))
        
        # Calculate both regimes
        old_regime = self._calculate_old_regime(annual_income, existing_80c, existing_80d, home_loan_interest, hra_claimed)
        new_regime = self._calculate_new_regime(annual_income)
        
        # Determine optimal regime
        optimal_regime = "old" if old_regime["total_tax"] < new_regime["total_tax"] else "new"
        tax_savings = abs(old_regime["total_tax"] - new_regime["total_tax"])
        
        # Enhanced recommendations
        recommendations = self._generate_investment_recommendations(annual_income, existing_80c, optimal_regime)
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "calculations": {
                "old_regime": {
                    **old_regime,
                    "regime": "Old Regime",
                    "recommended": optimal_regime == "old",
                    "taxBreakdown": self._get_tax_breakdown(old_regime["taxable_income"], "old"),
                    "effectiveRate": round((old_regime["total_tax"] / annual_income) * 100, 2) if annual_income > 0 else 0,
                    "savings": tax_savings if optimal_regime == "old" else 0
                },
                "new_regime": {
                    **new_regime,
                    "regime": "New Regime", 
                    "recommended": optimal_regime == "new",
                    "taxBreakdown": self._get_tax_breakdown(new_regime["taxable_income"], "new"),
                    "effectiveRate": round((new_regime["total_tax"] / annual_income) * 100, 2) if annual_income > 0 else 0,
                    "savings": tax_savings if optimal_regime == "new" else 0
                },
                "comparison": {
                    "optimal_regime": optimal_regime,
                    "tax_savings": tax_savings,
                    "savings_percentage": round((tax_savings / max(old_regime["total_tax"], new_regime["total_tax"], 1)) * 100, 2),
                    "recommendation_reason": self._get_recommendation_reason(annual_income, existing_80c, optimal_regime, tax_savings)
                },
                "recommendations": recommendations,
                "action_items": self._generate_action_items(existing_80c, recommendations, annual_income),
                "investment_suggestions": self._get_investment_suggestions_for_frontend(annual_income, existing_80c),
                "tax_planning_tips": self._get_tax_planning_tips(annual_income, optimal_regime)
            }
        }

    def _get_recommendation_reason(self, income: float, investments_80c: float, optimal_regime: str, savings: float) -> str:
        """Provide reasoning for regime recommendation"""
        if optimal_regime == "old":
            if investments_80c < 100000:
                return f"Old regime saves ₹{savings:,.0f} annually. You can save more by maximizing 80C investments."
            else:
                return f"Old regime is optimal with your current investments, saving ₹{savings:,.0f} annually."
        else:
            return f"New regime saves ₹{savings:,.0f} annually with no investment requirements. Focus on wealth creation."

    def _get_tax_planning_tips(self, income: float, regime: str) -> List[str]:
        """Get personalized tax planning tips"""
        tips = []
        
        if regime == "old":
            tips.extend([
                "Maximize 80C investments before March 31st",
                "Consider health insurance for 80D benefits",
                "Plan HRA if you pay rent"
            ])
        else:
            tips.extend([
                "Focus on wealth creation without tax constraints",
                "Consider equity investments for long-term growth",
                "No rush for tax-saving investments"
            ])
        
        if income > 1000000:
            tips.append("Consider NPS for additional 50K deduction under 80CCD(1B)")
        
        if income > 500000:
            tips.append("Plan advance tax payments to avoid penalties")
            
        return tips

    def _calculate_old_regime(self, income: float, investments_80c: float, health_insurance: float, home_loan: float, hra: float) -> Dict[str, Any]:
        """Calculate tax under old regime with all deductions"""
        
        # Calculate deductions
        standard_deduction = self.tax_constants["standard_deduction"]
        deduction_80c = min(investments_80c, self.tax_constants["section_80c_limit"])
        deduction_80d = min(health_insurance, self.tax_constants["section_80d_limit"])
        deduction_24b = min(home_loan, 200000)  # Max 2L for home loan interest
        deduction_hra = min(hra, income * 0.5)  # Simplified HRA calculation
        
        total_deductions = standard_deduction + deduction_80c + deduction_80d + deduction_24b + deduction_hra
        taxable_income = max(0, income - total_deductions)
        
        # Calculate tax
        tax = self._calculate_tax_by_slabs(taxable_income, self.tax_constants["old_regime_slabs"])
        cess = tax * 0.04  # 4% Health and Education Cess
        total_tax = tax + cess
        
        return {
            "gross_income": income,
            "deductions": {
                "standard_deduction": standard_deduction,
                "section_80c": deduction_80c,
                "section_80d": deduction_80d,
                "section_24b": deduction_24b,
                "hra": deduction_hra,
                "other": 0,
                "total": total_deductions
            },
            "taxable_income": taxable_income,
            "tax_before_cess": tax,
            "cess": cess,
            "total_tax": total_tax,
            "taxLiability": total_tax
        }
    
    def _calculate_new_regime(self, income: float) -> Dict[str, Any]:
        """Calculate tax under new regime"""
        
        standard_deduction = self.tax_constants["standard_deduction"]
        taxable_income = max(0, income - standard_deduction)
        
        # Calculate tax with new regime slabs
        tax = self._calculate_tax_by_slabs(taxable_income, self.tax_constants["new_regime_slabs"])
        cess = tax * 0.04
        total_tax = tax + cess
        
        return {
            "gross_income": income,
            "deductions": {
                "standard_deduction": standard_deduction,
                "section_80c": 0,
                "section_80d": 0,
                "section_24b": 0,
                "hra": 0,
                "other": 0,
                "total": standard_deduction
            },
            "taxable_income": taxable_income,
            "tax_before_cess": tax,
            "cess": cess,
            "total_tax": total_tax,
            "taxLiability": total_tax
        }
    
    def _calculate_tax_by_slabs(self, taxable_income: float, tax_slabs: list) -> float:
        """Calculate tax based on income slabs"""
        total_tax = 0
        remaining_income = taxable_income
        
        for slab in tax_slabs:
            if remaining_income <= 0:
                break
            
            slab_min = slab["min"]
            slab_max = slab["max"] if slab["max"] != float('inf') else remaining_income + slab_min
            
            if remaining_income > slab_min:
                taxable_in_slab = min(remaining_income - slab_min, slab_max - slab_min)
                if taxable_in_slab > 0:
                    slab_tax = (taxable_in_slab * slab["rate"]) / 100
                    total_tax += slab_tax
        
        return total_tax
    
    def _get_tax_breakdown(self, taxable_income: float, regime: str) -> List[Dict]:
        """Get detailed tax breakdown by slabs for frontend"""
        slabs = self.tax_constants["old_regime_slabs"] if regime == "old" else self.tax_constants["new_regime_slabs"]
        breakdown = []
        remaining_income = taxable_income
        
        for slab in slabs:
            if remaining_income <= 0:
                break
                
            slab_min = slab["min"]
            slab_max = slab["max"] if slab["max"] != float('inf') else remaining_income + slab_min
            
            if remaining_income > slab_min:
                taxable_in_slab = min(remaining_income - slab_min, slab_max - slab_min)
                if taxable_in_slab > 0:
                    slab_tax = (taxable_in_slab * slab["rate"]) / 100
                    
                    slab_display = f"₹{slab_min:,} - "
                    slab_display += f"₹{slab_max:,}" if slab_max != float('inf') else "Above"
                    
                    breakdown.append({
                        "slab": slab_display,
                        "rate": f"{slab['rate']}%",
                        "tax": slab_tax,
                        "taxable_amount": taxable_in_slab
                    })
                    
                    remaining_income -= taxable_in_slab
        
        return breakdown

    def _generate_investment_recommendations(self, income: float, existing_80c: float, optimal_regime: str) -> Dict[str, Any]:
        """Generate investment recommendations"""
        recommendations = []
        
        if optimal_regime == "old":
            remaining_80c = max(0, self.tax_constants["section_80c_limit"] - existing_80c)
            tax_bracket = 0.30 if income > 1000000 else 0.20 if income > 500000 else 0.05
            
            if remaining_80c > 0:
                # ELSS recommendation
                elss_amount = min(remaining_80c, 50000)
                recommendations.append({
                    "type": "ELSS Mutual Funds",
                    "section": "80C",
                    "suggested_amount": elss_amount,
                    "tax_saving": elss_amount * tax_bracket,
                    "benefits": ["Tax saving", "Equity returns potential", "3-year lock-in period"],
                    "risk_level": "Medium to High"
                })
                
                # PPF recommendation if more 80C space available
                if remaining_80c > elss_amount:
                    ppf_amount = min(remaining_80c - elss_amount, 100000)
                    recommendations.append({
                        "type": "Public Provident Fund (PPF)",
                        "section": "80C",
                        "suggested_amount": ppf_amount,
                        "tax_saving": ppf_amount * tax_bracket,
                        "benefits": ["Tax saving", "EEE benefit", "Guaranteed returns"],
                        "risk_level": "Low"
                    })
        
        # Health insurance recommendation (applicable to both regimes)
        recommendations.append({
            "type": "Health Insurance Premium",
            "section": "80D",
            "suggested_amount": 25000,
            "tax_saving": 25000 * (0.30 if income > 1000000 else 0.20),
            "benefits": ["Tax saving", "Health coverage", "Family protection"],
            "risk_level": "None"
        })
        
        return {
            "investment_suggestions": recommendations,
            "total_potential_savings": sum(rec.get("tax_saving", 0) for rec in recommendations)
        }
    
    def _get_investment_suggestions_for_frontend(self, income: float, existing_80c: float) -> List[Dict]:
        """Generate investment suggestions in frontend-compatible format"""
        suggestions = []
        remaining_80c = max(0, self.tax_constants["section_80c_limit"] - existing_80c)
        tax_bracket = 0.30 if income > 1000000 else 0.20 if income > 500000 else 0.05
        
        if remaining_80c > 0:
            # ELSS suggestion
            elss_amount = min(50000, remaining_80c)
            suggestions.append({
                "type": "ELSS Mutual Funds",
                "amount": elss_amount,
                "tax_benefit": elss_amount * tax_bracket,
                "category": "80C",
                "risk": "Medium to High",
                "lock_in": "3 years",
                "returns_potential": "12-15% annually",
                "description": "Best for long-term wealth creation with tax benefits"
            })
            
            # PPF suggestion
            if remaining_80c > elss_amount:
                ppf_amount = min(100000, remaining_80c - elss_amount)
                suggestions.append({
                    "type": "Public Provident Fund (PPF)",
                    "amount": ppf_amount,
                    "tax_benefit": ppf_amount * tax_bracket,
                    "category": "80C",
                    "risk": "Low",
                    "lock_in": "15 years",
                    "returns_potential": "7-8% annually",
                    "description": "Safe long-term investment with triple tax benefit"
                })
        
        # Health insurance
        suggestions.append({
            "type": "Health Insurance Premium",
            "amount": 25000,
            "tax_benefit": 25000 * tax_bracket,
            "category": "80D",
            "risk": "None",
            "lock_in": "Annual",
            "returns_potential": "Health coverage + tax savings",
            "description": "Essential health protection with tax benefits"
        })
        
        return suggestions
    
    def _generate_action_items(self, existing_80c: float, recommendations: Dict[str, Any], income: float) -> List[Dict]:
        """Generate prioritized action items"""
        action_items = []
        remaining_80c = max(0, self.tax_constants["section_80c_limit"] - existing_80c)
        tax_bracket = 0.30 if income > 1000000 else 0.20 if income > 500000 else 0.05
        
        if remaining_80c > 0:
            action_items.append({
                "priority": "High",
                "action": f"Invest remaining ₹{remaining_80c:,.0f} in 80C instruments",
                "timeline": "Before March 31st",
                "impact": f"Save up to ₹{remaining_80c * tax_bracket:,.0f} in taxes",
                "options": ["ELSS Mutual Funds", "PPF", "NSC", "Tax-saving FD"],
                "deadline": "March 31, 2024"
            })
        
        action_items.append({
            "priority": "Medium",
            "action": "Review and optimize health insurance coverage",
            "timeline": "Any time during the year",
            "impact": f"Save ₹{25000 * tax_bracket:,.0f} in taxes + comprehensive health coverage",
            "options": ["Individual policy", "Family floater", "Top-up plans"],
            "deadline": "Before policy renewal"
        })
        
        if income > 1000000:
            action_items.append({
                "priority": "Medium",
                "action": "Consider National Pension System (NPS)",
                "timeline": "Any time during the year",
                "impact": "Additional ₹50,000 deduction under 80CCD(1B)",
                "options": ["Tier-1 NPS account"],
                "deadline": "Before March 31st"
            })
        
        return action_items
    
    def _fallback_calculation(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback calculation in case of errors"""
        income = financial_data.get('annual_income', 1200000)
        return {
            "message": "Basic calculation provided due to processing error",
            "estimated_tax_old_regime": income * 0.2,
            "estimated_tax_new_regime": income * 0.15,
            "recommendation": "Consult tax advisor for detailed analysis"
        }

    def optimize_tax_strategy(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Provide comprehensive tax optimization strategy"""
        try:
            # Convert user profile to financial data
            financial_data = {
                "annual_income": user_profile.get('annual_income', 1200000),
                "investments_80c": user_profile.get('existing_investments', {}).get('80c', 50000),
                "health_insurance": user_profile.get('existing_investments', {}).get('80d', 0),
                "home_loan_interest": user_profile.get('existing_investments', {}).get('home_loan', 0)
            }
            
            # Get tax calculation
            tax_calculation = self.calculate_tax_liability(financial_data)
            
            # Generate strategy
            strategy = {
                "user_profile_analysis": {
                    "age_category": "young" if user_profile.get('age', 30) < 35 else "middle_aged" if user_profile.get('age', 30) < 50 else "senior",
                    "tax_bracket": self._determine_tax_bracket(user_profile.get('annual_income', 1200000)),
                    "optimization_potential": "high" if user_profile.get('annual_income', 1200000) > 800000 else "medium",
                    "risk_profile": user_profile.get('risk_appetite', 'moderate')
                },
                "tax_calculations": tax_calculation.get("calculations", {}),
                "personalized_recommendations": self._get_personalized_recommendations(user_profile),
                "timeline_strategy": self._create_timeline_strategy(),
                "compliance_checklist": self._create_compliance_checklist()
            }
            
            # Add AI insights if available
            if self.use_real_agent and self.agent:
                try:
                    ai_prompt = f"""
                    Provide personalized tax strategy for:
                    Age: {user_profile.get('age', 30)}
                    Income: ₹{user_profile.get('annual_income', 1200000):,}
                    Risk Appetite: {user_profile.get('risk_appetite', 'moderate')}
                    
                    Suggest 3 specific action items for optimal tax planning.
                    """
                    ai_insights = self.agent.run(ai_prompt)
                    strategy["ai_recommendations"] = str(ai_insights)[:300] + "..."
                except Exception as e:
                    logger.warning(f"AI insights generation failed: {e}")
                    strategy["ai_recommendations"] = "AI insights unavailable"
            
            return {
                "status": "success",
                "strategy": strategy,
                "timestamp": datetime.now().isoformat()
            }
                                
        except Exception as e:
            logger.error(f"Error in tax strategy optimization: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "fallback_strategy": self._get_fallback_strategy(user_profile)
            }
    
    def _determine_tax_bracket(self, income: float) -> str:
        """Determine tax bracket based on income"""
        if income <= 500000:
            return "5%"
        elif income <= 1000000:
            return "20%"
        else:
            return "30%"
    
    def _get_personalized_recommendations(self, user_profile: Dict[str, Any]) -> List[Dict]:
        """Get personalized recommendations based on user profile"""
        recommendations = []
        age = user_profile.get('age', 30)
        income = user_profile.get('annual_income', 1200000)
        risk_appetite = user_profile.get('risk_appetite', 'moderate')
        
        if age < 35:
            recommendations.append({
                "category": "Long-term Wealth Creation",
                "suggestion": "Focus on equity-oriented 80C investments like ELSS",
                "allocation": "70% ELSS, 30% PPF",
                "reasoning": "Young age allows for higher risk tolerance"
            })
        elif age < 50:
            recommendations.append({
                "category": "Balanced Approach",
                "suggestion": "Mix of equity and debt for 80C investments",
                "allocation": "50% ELSS, 50% PPF/NSC",
                "reasoning": "Balanced approach for growing responsibilities"
            })
        else:
            recommendations.append({
                "category": "Conservative Strategy",
                "suggestion": "Focus on safe 80C investments",
                "allocation": "30% ELSS, 70% PPF/NSC",
                "reasoning": "Capital preservation becomes important"
            })
        
        if income > 1000000:
            recommendations.append({
                "category": "Advanced Tax Planning",
                "suggestion": "Consider NPS for additional deduction under 80CCD(1B)",
                "allocation": "₹50,000 annually in NPS",
                "reasoning": "High income bracket benefits from additional deductions"
            })
        
        return recommendations
    
    def _create_timeline_strategy(self) -> Dict[str, List[str]]:
        """Create month-wise tax planning timeline"""
        return {
            "April-June": [
                "Plan annual investment strategy",
                "Set up SIPs for ELSS funds",
                "Review previous year's tax filing"
            ],
            "July-September": [
                "Track mid-year investment progress",
                "Review salary structure for tax optimization",
                "Plan any major purchases"
            ],
            "October-December": [
                "Accelerate investments if behind target",
                "Plan year-end tax-saving purchases",
                "Review insurance needs"
            ],
            "January-March": [
                "Final investment push for 80C/80D",
                "Gather all tax documents",
                "File income tax return",
                "Pay advance tax if applicable"
            ]
        }
    
    def _create_compliance_checklist(self) -> List[str]:
        """Create comprehensive tax compliance checklist"""
        return [
            "Maintain all investment receipts and certificates (80C, 80D)",
            "Keep TDS certificates from salary and other sources",
            "Save rent receipts and HRA calculation documents",
            "Document home loan interest certificates",
            "Keep bank statements for all financial transactions",
            "File ITR before due date (July 31st for individuals)",
            "Pay advance tax if total liability exceeds ₹10,000",
            "Link PAN with Aadhaar",
            "Update bank accounts with PAN details",
            "Maintain Form 16 from employer"
        ]
    
    def _get_fallback_strategy(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback strategy when optimization fails"""
        income = user_profile.get('annual_income', 1200000)
        age = user_profile.get('age', 30)
        
        return {
            "basic_recommendations": [
                "Maximize 80C investments up to ₹1.5L limit",
                "Consider health insurance for 80D benefits",
                "Plan investments before March 31st"
            ],
            "suggested_80c_allocation": {
                "ELSS": 50000 if age < 40 else 30000,
                "PPF": 50000,
                "NSC": 25000,
                "Life_Insurance": 25000
            },
            "estimated_tax_savings": min(150000 * 0.30, income * 0.1),
            "priority_actions": [
                "Complete 80C investments",
                "Buy adequate health insurance",
                "Plan advance tax payments"
            ]
        }

# Test function
def test_tax_agent():
    """Test the Tax Calculation Agent"""
    print("🧪 Testing Windows-Compatible Tax Agent...")
    
    agent = TaxCalculationAgent()
    
    # Test data matching your sample bank statement insights
    test_data = {
        "annual_income": 933840,  # From your sample data
        "investments_80c": 145123,  # PPF + NSC + ELSS + FD
        "health_insurance": 21601,  # Health insurance from sample
        "home_loan_interest": 7056 * 12  # Monthly EMI * 12
    }
    
    print(f"\n📊 Testing with Sample Data:")
    print(f"Income: ₹{test_data['annual_income']:,}")
    print(f"80C Investments: ₹{test_data['investments_80c']:,}")
    
    # Test tax calculation
    result = agent.calculate_tax_liability(test_data)
    
    if result.get('status') == 'success':
        calc = result['calculations']
        print(f"\n✅ Tax Calculation Results:")
        print(f"Old Regime Tax: ₹{calc['old_regime']['total_tax']:,.0f}")
        print(f"New Regime Tax: ₹{calc['new_regime']['total_tax']:,.0f}")
        print(f"Recommended: {calc['comparison']['optimal_regime'].title()} Regime")
        print(f"Tax Savings: ₹{calc['comparison']['tax_savings']:,.0f}")
        print(f"Response Source: {result.get('response_source', 'Unknown')}")
    else:
        print(f"❌ Calculation failed: {result.get('message')}")

if __name__ == "__main__":
    test_tax_agent()
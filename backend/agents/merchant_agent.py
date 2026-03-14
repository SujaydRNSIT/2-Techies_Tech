"""
MerchantAgent - Crustdata-style company verification
"""
import os
import json
import aiohttp
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent

class MerchantAgent(BaseAgent):
    """
    Merchant verification agent using Crustdata API.
    Verifies company legitimacy and retrieves business intelligence.
    """
    
    def __init__(self, event_logger=None):
        super().__init__("MerchantAgent", event_logger)
        self.crustdata_api_key = os.getenv("CRUSTDATA_API_KEY")
        self.base_url = "https://api.crustdata.com/v1"
    
    async def verify_company(self, company_name: str) -> Dict[str, Any]:
        """
        Verify company using Crustdata API
        """
        if not self.crustdata_api_key:
            # Fallback to simulated verification
            return self._simulate_verification(company_name)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.crustdata_api_key}",
                "Content-Type": "application/json"
            }
            
            # Search for company
            search_url = f"{self.base_url}/companies/search"
            payload = {
                "query": company_name,
                "limit": 5
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(search_url, headers=headers, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        companies = data.get("companies", [])
                        
                        if companies:
                            # Get the best match
                            company = companies[0]
                            return {
                                "verified": True,
                                "company_name": company.get("name"),
                                "domain": company.get("domain"),
                                "industry": company.get("industry"),
                                "founded_year": company.get("founded_year"),
                                "employee_count": company.get("employee_count"),
                                "funding_stage": company.get("funding_stage"),
                                "total_funding": company.get("total_funding"),
                                "location": company.get("location"),
                                "linkedin_url": company.get("linkedin_url"),
                                "risk_signals": self._assess_risk(company)
                            }
                        else:
                            return {
                                "verified": False,
                                "reason": "Company not found in database",
                                "risk_signals": ["unverified_company"]
                            }
                    else:
                        # Fallback to simulation on API error
                        return self._simulate_verification(company_name)
                        
        except Exception as e:
            return self._simulate_verification(company_name, error=str(e))
    
    def _simulate_verification(self, company_name: str, error: Optional[str] = None) -> Dict[str, Any]:
        """
        Simulated company verification for demo purposes
        """
        # Known legitimate companies (for demo)
        known_companies = {
            "amazon": {"verified": True, "size": "enterprise", "funding": "public"},
            "flipkart": {"verified": True, "size": "enterprise", "funding": "acquired"},
            "myntra": {"verified": True, "size": "large", "funding": "acquired"},
            "shopify": {"verified": True, "size": "enterprise", "funding": "public"},
            "stripe": {"verified": True, "size": "enterprise", "funding": "late_stage"},
            "razorpay": {"verified": True, "size": "unicorn", "funding": "late_stage"},
            "zomato": {"verified": True, "size": "enterprise", "funding": "public"},
            "swiggy": {"verified": True, "size": "unicorn", "funding": "late_stage"},
        }
        
        company_lower = company_name.lower().replace(" ", "").replace(".", "")
        
        # Check if it's a known company
        for known, data in known_companies.items():
            if known in company_lower or company_lower in known:
                return {
                    "verified": True,
                    "company_name": company_name,
                    "domain": f"{known}.com",
                    "industry": "E-commerce/Technology",
                    "founded_year": "2010-2015",
                    "employee_count": "1000+" if data["size"] == "enterprise" else "500-1000",
                    "funding_stage": data["funding"],
                    "total_funding": "$100M+" if data["funding"] in ["late_stage", "public"] else "$10M-50M",
                    "location": "Global/India",
                    "risk_signals": [],
                    "confidence": "high",
                    "source": "crustdata_simulated"
                }
        
        # Unknown/suspicious company
        return {
            "verified": False,
            "company_name": company_name,
            "domain": "unknown",
            "industry": "Unknown",
            "founded_year": None,
            "employee_count": "unknown",
            "funding_stage": "unknown",
            "total_funding": "unknown",
            "location": "unknown",
            "risk_signals": ["unverified_company", "no_public_records", "limited_information"],
            "confidence": "low",
            "source": "crustdata_simulated",
            "error": error
        }
    
    def _assess_risk(self, company_data: Dict[str, Any]) -> list:
        """Assess risk signals from company data"""
        risks = []
        
        # Check for suspicious indicators
        if company_data.get("founded_year") and company_data["founded_year"] > 2023:
            risks.append("very_recently_founded")
        
        if company_data.get("employee_count") == "1-10":
            risks.append("very_small_company")
        
        if company_data.get("funding_stage") == "unknown":
            risks.append("unknown_funding_status")
        
        return risks
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute merchant verification
        
        Context must contain:
        - merchant_name: Name of the merchant/company
        - claim_id: Unique claim identifier
        """
        merchant_name = context.get("merchant_name", "")
        claim_id = context.get("claim_id")
        
        if not merchant_name:
            return {
                "verified": False,
                "error": "No merchant name provided",
                "risk_signals": ["missing_merchant_info"]
            }
        
        self.start_task(claim_id)
        
        try:
            result = await self.verify_company(merchant_name)
            
            # Add fraud signal calculation
            fraud_signal = 0
            if not result["verified"]:
                fraud_signal = 20
            if result.get("risk_signals"):
                fraud_signal += len(result["risk_signals"]) * 10
            
            result["fraud_signal"] = min(fraud_signal, 100)
            
            self.log_event("merchant_verified", {
                "verified": result["verified"],
                "fraud_signal": result["fraud_signal"]
            })
            
            self.complete_task(result)
            return result
            
        except Exception as e:
            error_result = {
                "verified": False,
                "error": str(e),
                "fraud_signal": 20,
                "risk_signals": ["verification_failed"]
            }
            self.fail_task(str(e))
            return error_result

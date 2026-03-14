"""
ReportAgent - Generates investigation reports
"""
from datetime import datetime
from typing import Dict, Any
from agents.base_agent import BaseAgent

class ReportAgent(BaseAgent):
    """
    Generates comprehensive investigation reports
    summarizing all agent findings and decisions.
    """
    
    def __init__(self, event_logger=None):
        super().__init__("ReportAgent", event_logger)
    
    def generate_report(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate investigation report"""
        
        claim_id = context.get("claim_id", "")
        order_id = context.get("order_id", "")
        payment_id = context.get("payment_id", "")
        merchant_name = context.get("merchant_name", "")
        refund_amount = context.get("refund_amount", 0)
        claim_reason = context.get("claim_reason", "")
        
        # Get all agent results
        evidence = context.get("evidence", {})
        security = context.get("security", {})
        merchant = context.get("merchant", {})
        fraud = context.get("fraud", {})
        refund = context.get("refund", {})
        knowledge = context.get("knowledge", {})
        image_reuse = context.get("image_reuse", {})
        
        # Build report sections
        report = {
            "report_id": f"RPT_{claim_id}",
            "generated_at": datetime.utcnow().isoformat(),
            "claim_summary": {
                "claim_id": claim_id,
                "order_id": order_id,
                "payment_id": payment_id,
                "merchant_name": merchant_name,
                "refund_amount": refund_amount,
                "claim_reason": claim_reason
            },
            "investigation_findings": {
                "image_analysis": {
                    "status": "completed",
                    "damage_detected": evidence.get("damage_detected", False),
                    "ai_generated_probability": evidence.get("ai_analysis", {}).get("ai_generated_probability", 0),
                    "manipulation_detected": evidence.get("ai_analysis", {}).get("manipulation_detected", False),
                    "suspicious_indicators": evidence.get("suspicious_indicators", []),
                    "summary": evidence.get("summary", "")
                },
                "image_reuse_check": {
                    "status": "completed",
                    "image_found_online": image_reuse.get("found_online", False),
                    "matches_found": image_reuse.get("matches_count", 0),
                    "source_urls": image_reuse.get("source_urls", [])
                },
                "security_scan": {
                    "status": "completed",
                    "safe": security.get("overall_safe", True),
                    "security_score": security.get("security_score", 0),
                    "threats_found": security.get("threats_found", []),
                    "url_scans": len(security.get("url_scans", []))
                },
                "merchant_verification": {
                    "status": "completed",
                    "verified": merchant.get("verified", False),
                    "company_name": merchant.get("company_name", merchant_name),
                    "funding_stage": merchant.get("funding_stage", "unknown"),
                    "risk_signals": merchant.get("risk_signals", [])
                },
                "fraud_pattern_check": {
                    "status": "completed",
                    "similar_cases_found": len(knowledge.get("similar_cases", [])),
                    "pattern_match": knowledge.get("pattern_detected", False),
                    "avg_historical_fraud_score": knowledge.get("avg_historical_fraud_score", 0)
                }
            },
            "fraud_assessment": {
                "fraud_score": fraud.get("fraud_score", 0),
                "risk_level": self._get_risk_level(fraud.get("fraud_score", 0)),
                "decision": fraud.get("decision", "manual_review"),
                "decision_reason": fraud.get("decision_reason", ""),
                "risk_factors": fraud.get("risk_factors", [])
            },
            "refund_outcome": {
                "status": refund.get("status", "pending"),
                "refund_id": refund.get("refund_id"),
                "amount_processed": refund.get("amount", 0),
                "processing_source": refund.get("source", "unknown")
            },
            "sponsor_integrations_used": [
                "Merchant Verified via Crustdata",
                "Security Scan by SafeDep",
                "URL Threat Detection by Gearsec",
                "Payment Executed via Razorpay",
                "Events Logged via S2.dev",
                "Agents Orchestrated via Emergent",
                "Knowledge Retrieval via Unsiloed",
                "Response Automation via Concierge"
            ]
        }
        
        # Generate human-readable summary
        summary = self._generate_human_summary(report)
        report["executive_summary"] = summary
        
        return report
    
    def _get_risk_level(self, score: int) -> str:
        """Convert fraud score to risk level"""
        if score <= 30:
            return "LOW"
        elif score <= 70:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def _generate_human_summary(self, report: Dict[str, Any]) -> str:
        """Generate human-readable summary"""
        assessment = report["fraud_assessment"]
        findings = report["investigation_findings"]
        
        summary_parts = []
        
        # Overall decision
        decision = assessment["decision"]
        if decision == "approved":
            summary_parts.append("✓ REFUND APPROVED")
        elif decision == "rejected":
            summary_parts.append("✗ REFUND REJECTED")
        else:
            summary_parts.append("⏸ MANUAL REVIEW REQUIRED")
        
        summary_parts.append(f"\nFraud Risk Score: {assessment['fraud_score']}/100 ({assessment['risk_level']} RISK)")
        
        # Key findings
        summary_parts.append("\nKey Findings:")
        
        # Image analysis
        img = findings["image_analysis"]
        if img["damage_detected"]:
            summary_parts.append("- Damage visible in submitted image")
        if img["ai_generated_probability"] > 50:
            summary_parts.append(f"- ⚠ AI-generated image detected ({img['ai_generated_probability']}% probability)")
        if img["manipulation_detected"]:
            summary_parts.append("- ⚠ Image manipulation detected")
        
        # Image reuse
        reuse = findings["image_reuse_check"]
        if reuse["image_found_online"]:
            summary_parts.append(f"- ⚠ Image found online ({reuse['matches_found']} matches)")
        
        # Security
        sec = findings["security_scan"]
        if not sec["safe"]:
            summary_parts.append("- ⚠ Security threats detected")
        
        # Merchant
        merch = findings["merchant_verification"]
        if not merch["verified"]:
            summary_parts.append("- ⚠ Unverified merchant")
        
        # Risk factors
        if assessment["risk_factors"]:
            summary_parts.append(f"\nRisk Factors: {', '.join(assessment['risk_factors'])}")
        
        return "\n".join(summary_parts)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute report generation
        
        Context contains all agent results and claim details
        """
        claim_id = context.get("claim_id")
        self.start_task(claim_id)
        
        try:
            report = self.generate_report(context)
            
            self.log_event("report_generated", {
                "report_id": report["report_id"],
                "fraud_score": report["fraud_assessment"]["fraud_score"],
                "decision": report["fraud_assessment"]["decision"]
            })
            
            self.complete_task(report)
            return report
            
        except Exception as e:
            error_result = {
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat()
            }
            self.fail_task(str(e))
            return error_result
